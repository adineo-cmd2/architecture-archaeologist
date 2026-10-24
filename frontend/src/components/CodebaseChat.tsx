import { useEffect, useState } from 'react';
import { apiPost } from '../lib/apiClient';

interface Ref {
  path: string;
  snippet: string;
}

export default function CodebaseChat() {
  const [codebaseId, setCodebaseId] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [refs, setRefs] = useState<Ref[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const saved = window.localStorage.getItem('codebase_id');
    if (saved) setCodebaseId(saved);
  }, []);

  async function ask() {
    setError('');
    setAnswer('');
    setRefs([]);
    if (!codebaseId) {
      setError('Set a codebase id first (see Ingest).');
      return;
    }
    if (!question.trim()) {
      setError('Enter a question.');
      return;
    }
    setBusy(true);
    try {
      const data = await apiPost(`/api/codebase/${codebaseId}/ask`, { question: question.trim() });
      setAnswer(data.answer ?? '');
      setRefs(data.refs ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ask failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          value={codebaseId}
          onChange={(e) => setCodebaseId(e.target.value)}
          placeholder="codebase id"
          className="w-32 border border-edge bg-ink p-2 text-sm"
        />
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Where is auth handled?"
          className="flex-1 border border-edge bg-ink p-2 text-sm"
        />
        <button
          onClick={() => void ask()}
          disabled={busy}
          className="bg-archgreen px-4 py-1 text-sm font-bold text-ink disabled:opacity-50"
        >
          Ask
        </button>
      </div>
      {error && <p className="text-sm text-archamber">{error}</p>}
      {answer && (
        <div className="border border-edge bg-panel p-4">
          <h2 className="text-sm font-bold text-archgreen">Answer</h2>
          <p className="mt-1 whitespace-pre-wrap text-sm">{answer}</p>
        </div>
      )}
      {refs.length > 0 && (
        <div className="border border-edge bg-panel p-4">
          <h2 className="text-sm font-bold text-archgreen">References</h2>
          <ul className="mt-2 space-y-2">
            {refs.map((r, i) => (
              <li key={`${r.path}-${i}`} className="border border-edge bg-ink p-2">
                <p className="text-xs text-archgreen">{r.path}</p>
                <pre className="mt-1 overflow-auto text-xs text-zinc-300">{r.snippet}</pre>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
