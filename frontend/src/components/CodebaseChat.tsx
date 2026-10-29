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
    <div className="sheet-panel">
      <div className="sheet-panel-head">
        <span className="panel-code">Sheet A-05 — Query</span>
        <span>Grounded Q&amp;A · answers cite source</span>
      </div>

      <div className="query-grid">
        <label className="field">
          <span className="label-x">Codebase id</span>
          <input
            value={codebaseId}
            onChange={(e) => setCodebaseId(e.target.value)}
            placeholder="codebase id"
            className="input"
          />
        </label>
        <label className="field">
          <span className="label-x">Question</span>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Where is auth handled?"
            className="input"
          />
        </label>
        <button
          type="button"
          onClick={() => void ask()}
          disabled={busy}
          className="btn btn-accent"
        >
          Ask
        </button>
      </div>

      <div className="query-body">
        {error && <p className="form-note error">{error}</p>}
        {answer && (
          <div className="data-panel">
            <div className="panel-head"><h2>Answer</h2><span>Retrieved · grounded</span></div>
            <div className="panel-body">
              <p className="answer-text">{answer}</p>
            </div>
          </div>
        )}
        {refs.length > 0 && (
          <div className="data-panel">
            <div className="panel-head"><h2>References</h2><span>{refs.length} source{refs.length === 1 ? '' : 's'}</span></div>
            <div className="panel-body">
              <ul className="ref-list">
                {refs.map((r, i) => (
                  <li key={`${r.path}-${i}`} className="ref-item">
                    <p className="ref-path">{r.path}</p>
                    <pre className="ref-snippet">{r.snippet}</pre>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        {!answer && !error && refs.length === 0 && (
          <p className="register-empty">
            Ask where something lives, why a module exists, or how two parts of the codebase talk to each other.
          </p>
        )}
      </div>
    </div>
  );
}
