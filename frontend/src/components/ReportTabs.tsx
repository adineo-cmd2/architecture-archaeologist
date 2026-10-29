import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';
import MermaidDiagram from './MermaidDiagram';
import DriftHeatmap, { type DriftEntry } from './DriftHeatmap';
import MarkdownReader from './MarkdownReader';

type Tab = 'summary' | 'mermaid' | 'heatmap' | 'document';

export default function ReportTabs() {
  const [tab, setTab] = useState<Tab>('summary');
  const [codebaseId, setCodebaseId] = useState<string>('');
  const [pattern, setPattern] = useState('');
  const [markdown, setMarkdown] = useState('');
  const [mermaid, setMermaid] = useState('');
  const [drift, setDrift] = useState<DriftEntry[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id') ?? window.localStorage.getItem('codebase_id') ?? '';
    setCodebaseId(id);
    if (id) void load(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function load(id: string) {
    setLoading(true);
    setError('');
    try {
      const rep = await apiGet(`/api/codebase/${id}/report`);
      setMarkdown(rep.markdown ?? '');
      setMermaid(rep.mermaid ?? '');
      setPattern(rep.pattern ?? '');
      const d = await apiGet(`/api/codebase/${id}/drift`);
      setDrift(Array.isArray(d) ? d : (d.drift ?? []));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Load failed.');
    } finally {
      setLoading(false);
    }
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: 'summary', label: 'Summary' },
    { key: 'mermaid', label: 'Mermaid' },
    { key: 'heatmap', label: 'Heatmap' },
    { key: 'document', label: 'Document' },
  ];

  return (
    <div className="sheet-panel">
      <div className="sheet-panel-head">
        <span className="panel-code">Sheet A-03 — Report</span>
        <span>Reading · pattern, diagram, drift, document</span>
      </div>

      <div className="workspace-bar">
        <label className="field field-id">
          <span className="label-x">Codebase id</span>
          <input
            value={codebaseId}
            onChange={(e) => setCodebaseId(e.target.value)}
            placeholder="codebase id"
            className="input"
          />
        </label>
        <button
          type="button"
          onClick={() => codebaseId && void load(codebaseId)}
          className="btn btn-accent"
        >
          Load
        </button>
        {pattern && <span className="chip chip-accent pattern-chip">pattern: {pattern}</span>}
      </div>

      <div className="tabs" role="tablist" aria-label="Report sections">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            role="tab"
            aria-selected={tab === t.key}
            onClick={() => setTab(t.key)}
            className={`tab ${tab === t.key ? 'is-active' : ''}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="tab-panel">
        {loading && <p className="register-empty">Loading…</p>}
        {error && <p className="form-note error">{error}</p>}
        {!loading && !error && tab === 'summary' && (
          <div className="data-panel">
            <div className="panel-head"><h2>Summary</h2><span>Survey reading</span></div>
            <div className="panel-body">
              <div className="summary-list">
                <div className="summary-row"><span className="k">Pattern</span><span className="v">{pattern || '—'}</span></div>
                <div className="summary-row"><span className="k">Files scored</span><span className="v">{drift.length}</span></div>
                <div className="summary-row">
                  <span className="k">Top drift</span>
                  <span className="v">
                    {drift.slice(0, 3).map((d) => `${d.path} (${d.score.toFixed(2)})`).join(', ') || '—'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
        {!loading && !error && tab === 'mermaid' && (
          <div className="data-panel">
            <div className="panel-head"><h2>Mermaid diagram</h2><span>Inferred structure</span></div>
            <div className="panel-body"><MermaidDiagram chart={mermaid} /></div>
          </div>
        )}
        {!loading && !error && tab === 'heatmap' && (
          <div className="data-panel">
            <div className="panel-head"><h2>Drift heatmap</h2><span>Per-file distance from the pattern</span></div>
            <div className="panel-body"><DriftHeatmap drift={drift} /></div>
          </div>
        )}
        {!loading && !error && tab === 'document' && (
          <div className="data-panel">
            <div className="panel-head"><h2>Document</h2><span>What was the dev thinking</span></div>
            <div className="panel-body"><MarkdownReader markdown={markdown} /></div>
          </div>
        )}
      </div>
    </div>
  );
}
