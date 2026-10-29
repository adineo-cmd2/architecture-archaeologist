import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

export default function CodebaseExplorer() {
  const [codebaseId, setCodebaseId] = useState('');
  const [tree, setTree] = useState<string[]>([]);
  const [selected, setSelected] = useState('');
  const [content, setContent] = useState('');
  const [language, setLanguage] = useState('');
  const [drift, setDrift] = useState<number | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id') ?? window.localStorage.getItem('codebase_id') ?? '';
    if (id) {
      setCodebaseId(id);
      void loadTree(id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadTree(id: string) {
    setError('');
    try {
      const data = await apiGet(`/api/codebase/${id}/files`);
      const entries = (data.tree ?? []) as { path: string }[] | string[];
      setTree(entries.map((e) => (typeof e === 'string' ? e : e.path)));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Tree load failed.');
    }
  }

  async function openFile(path: string) {
    setSelected(path);
    setError('');
    try {
      const data = await apiGet(`/api/codebase/${codebaseId}/files?path=${encodeURIComponent(path)}`);
      setContent(data.content ?? '');
      setLanguage(data.language ?? '');
      setDrift(typeof data.drift === 'number' ? data.drift : null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'File load failed.');
    }
  }

  return (
    <div className="sheet-panel">
      <div className="sheet-panel-head">
        <span className="panel-code">Sheet A-04 — Explorer</span>
        <span>File tree · source preview · drift context</span>
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
          onClick={() => codebaseId && void loadTree(codebaseId)}
          className="btn btn-accent"
        >
          Load
        </button>
      </div>

      {error && <div className="workspace-alert"><p className="form-note error">{error}</p></div>}

      <div className="workspace-grid">
        <div className="data-panel">
          <div className="panel-head">
            <h2>Tree ({tree.length})</h2>
            <span>Select a file</span>
          </div>
          <div className="panel-body">
            {tree.length === 0 && <p className="register-empty">No files loaded yet.</p>}
            <ul className="tree-list">
              {tree.map((p) => (
                <li key={p}>
                  <button
                    type="button"
                    onClick={() => void openFile(p)}
                    className={`tree-item ${selected === p ? 'is-active' : ''}`}
                  >
                    {p}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="data-panel">
          <div className="panel-head">
            <h2>File</h2>
            <span>{language || 'Preview'}</span>
          </div>
          <div className="panel-body">
            {selected && (
              <div className="file-meta">
                <span>{selected}</span>
                {language && <span>· {language}</span>}
                {drift != null && (
                  <span className={`drift-badge ${drift < 0.4 ? 'low' : ''}`}>
                    drift {drift.toFixed(2)}
                  </span>
                )}
              </div>
            )}
            <pre className="code-block">{content || 'Select a file.'}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
