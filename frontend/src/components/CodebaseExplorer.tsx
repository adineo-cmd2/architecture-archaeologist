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
    <div>
      <div className="flex gap-2">
        <input
          value={codebaseId}
          onChange={(e) => setCodebaseId(e.target.value)}
          placeholder="codebase id"
          className="w-32 border border-edge bg-ink p-1 text-sm"
        />
        <button
          onClick={() => codebaseId && void loadTree(codebaseId)}
          className="bg-archgreen px-3 py-1 text-sm font-bold text-ink"
        >
          Load
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-archamber">{error}</p>}
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="border border-edge bg-panel p-3">
          <h2 className="text-sm font-bold text-archgreen">Tree ({tree.length})</h2>
          <ul className="mt-2 max-h-96 overflow-auto text-xs">
            {tree.map((p) => (
              <li key={p}>
                <button
                  onClick={() => void openFile(p)}
                  className={`text-left hover:text-archgreen ${selected === p ? 'text-archgreen' : 'text-zinc-300'}`}
                >
                  {p}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="border border-edge bg-panel p-3">
          <h2 className="text-sm font-bold text-archgreen">File</h2>
          {selected && (
            <p className="mt-1 text-xs text-inksoft">
              {selected} · {language}
              {drift != null && (
                <span className={`ml-2 border px-1 ${drift >= 0.4 ? 'border-archamber text-archamber' : 'border-archgreen text-archgreen'}`}>
                  drift {drift.toFixed(2)}
                </span>
              )}
            </p>
          )}
          <pre className="mt-2 max-h-96 overflow-auto bg-ink p-2 text-xs">{content || 'Select a file.'}</pre>
        </div>
      </div>
    </div>
  );
}
