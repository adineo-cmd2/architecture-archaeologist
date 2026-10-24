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
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <input
          value={codebaseId}
          onChange={(e) => setCodebaseId(e.target.value)}
          placeholder="codebase id"
          className="w-32 border border-edge bg-ink p-1 text-sm"
        />
        <button
          onClick={() => codebaseId && void load(codebaseId)}
          className="bg-archgreen px-3 py-1 text-sm font-bold text-ink"
        >
          Load
        </button>
        {pattern && <span className="text-sm text-archgreen">pattern: {pattern}</span>}
      </div>
      <div className="mt-4 flex gap-2 border-b border-edge pb-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-3 py-1 text-sm ${tab === t.key ? 'bg-archgreen font-bold text-ink' : 'border border-edge text-zinc-300'}`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="mt-4">
        {loading && <p className="text-sm">Loading…</p>}
        {error && <p className="text-sm text-archamber">{error}</p>}
        {!loading && !error && tab === 'summary' && (
          <div className="border border-edge bg-panel p-4 text-sm">
            <p><span className="text-archgreen">Pattern:</span> {pattern || '—'}</p>
            <p className="mt-1"><span className="text-archgreen">Files scored:</span> {drift.length}</p>
            <p className="mt-1"><span className="text-archgreen">Top drift:</span> {drift.slice(0, 3).map((d) => `${d.path} (${d.score.toFixed(2)})`).join(', ') || '—'}</p>
          </div>
        )}
        {!loading && !error && tab === 'mermaid' && <MermaidDiagram chart={mermaid} />}
        {!loading && !error && tab === 'heatmap' && <DriftHeatmap drift={drift} />}
        {!loading && !error && tab === 'document' && <MarkdownReader markdown={markdown} />}
      </div>
    </div>
  );
}
