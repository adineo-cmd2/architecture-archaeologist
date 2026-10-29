import { useEffect, useState } from 'react';
import { apiGet, apiPost, apiPostFile } from '../lib/apiClient';
const BASE = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');

interface TreeEntry {
  path: string;
}

export default function UploadZone() {
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [consent, setConsent] = useState(false);
  const [codebaseId, setCodebaseId] = useState<number | null>(null);
  const [tree, setTree] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function refreshTree(id: number) {
    const data = await apiGet(`/api/codebase/${id}/files`);
    const entries = (data.tree ?? []) as TreeEntry[] | string[];
    setTree(
      entries.map((e) => (typeof e === 'string' ? e : e.path)),
    );
  }

  async function handleZipUpload() {
    setError('');
    setMessage('');
    if (!consent) {
      setError('Consent required: confirm you own this code or are authorised to share it.');
      return;
    }
    if (!zipFile) {
      setError('Choose a .zip file first.');
      return;
    }
    setBusy(true);
    try {
      const data = await apiPostFile('/api/codebase/upload', zipFile);
      const id = data.codebase_id as number;
      setCodebaseId(id);
      setMessage(`Uploaded: ${data.files ?? tree.length} files (id ${id}).`);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('codebase_id', String(id));
      }
      await refreshTree(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed.');
    } finally {
      setBusy(false);
    }
  }

  async function handleUrlIngest() {
    setError('');
    setMessage('');
    if (!consent) {
      setError('Consent required: confirm you own this code or are authorised to share it.');
      return;
    }
    if (!url.trim()) {
      setError('Enter a GitHub URL first.');
      return;
    }
    setBusy(true);
    try {
      const data = await apiPost('/api/codebase/github', { url: url.trim() });
      const id = data.codebase_id as number;
      setCodebaseId(id);
      setMessage(`Cloned: id ${id}.`);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('codebase_id', String(id));
      }
      await refreshTree(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'GitHub ingest failed.');
    } finally {
      setBusy(false);
    }
  }

  async function handleAnalyse() {
    setError('');
    setMessage('');
    if (!codebaseId) {
      setError('Upload or ingest a codebase first.');
      return;
    }
    setBusy(true);
    try {
      const data = await apiPost(`/api/codebase/${codebaseId}/analyse`, {});
      setMessage(`Pattern: ${data.pattern}. Drift zones: ${(data.drift_zones ?? []).length}.`);
      if (typeof window !== 'undefined') {
        window.location.href = `${BASE}/report?id=${codebaseId}`;
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analyse failed.');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const saved = window.localStorage.getItem('codebase_id');
    if (saved) setCodebaseId(Number(saved));
  }, []);

  return (
    <div className="sheet-panel">
      <div className="sheet-panel-head">
        <span className="panel-code">Sheet A-02 — Intake</span>
        <span>Form AA-1 · Codebase · Rev 03</span>
      </div>

      <div className="intake-grid">
        <section className="intake-cell">
          <h2><span className="idx">01</span>ZIP upload</h2>
          <p className="hint">A local archive. Parsed in place; nothing is executed.</p>
          <div className="field">
            <label className="label-x" htmlFor="zip-file">Codebase archive (.zip)</label>
            <input
              id="zip-file"
              type="file"
              accept=".zip"
              onChange={(e) => setZipFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <button
            type="button"
            onClick={handleZipUpload}
            disabled={busy}
            className="btn btn-accent"
          >
            Upload zip
          </button>
        </section>

        <section className="intake-cell">
          <h2><span className="idx">02</span>GitHub URL</h2>
          <p className="hint">A public repository. Cloned to the local backend for survey.</p>
          <div className="field">
            <label className="label-x" htmlFor="github-url">Repository address</label>
            <input
              id="github-url"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/org/repo"
              className="input"
            />
          </div>
          <button
            type="button"
            onClick={handleUrlIngest}
            disabled={busy}
            className="btn btn-ghost"
          >
            Ingest URL
          </button>
        </section>
      </div>

      <label className="consent-row">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
        />
        <span>
          <strong>Consent required.</strong> I confirm I own this code or am authorised to share it, and it contains
          no proprietary secrets I lack permission to upload.
        </span>
      </label>

      {tree.length > 0 && (
        <div className="tree-block">
          <h2>Tree preview ({tree.length})</h2>
          <ul className="file-tree">
            {tree.slice(0, 100).map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="intake-actions">
        <button
          type="button"
          onClick={handleAnalyse}
          disabled={busy || codebaseId == null}
          className="btn btn-accent btn-lg"
        >
          Analyse
        </button>
        <p className="action-note">Output / report A-03 · drift · file explorer</p>
      </div>

      {(message || error) && (
        <div className="intake-messages">
          {message && <p className="form-note ok">{message}</p>}
          {error && <p className="form-note error">{error}</p>}
        </div>
      )}
    </div>
  );
}
