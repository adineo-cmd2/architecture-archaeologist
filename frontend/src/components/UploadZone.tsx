import { useEffect, useState } from 'react';
import { apiGet, apiPost, apiPostFile } from '../lib/apiClient';

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
        window.location.href = `/report?id=${codebaseId}`;
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
    <div className="space-y-4">
      <div className="border border-edge bg-panel p-4">
        <h2 className="text-sm font-bold text-archgreen">ZIP upload</h2>
        <input
          type="file"
          accept=".zip"
          onChange={(e) => setZipFile(e.target.files?.[0] ?? null)}
          className="mt-2 w-full text-sm"
        />
        <button
          onClick={handleZipUpload}
          disabled={busy}
          className="mt-2 bg-archgreen px-4 py-1 text-sm font-bold text-ink disabled:opacity-50"
        >
          Upload zip
        </button>
      </div>
      <div className="border border-edge bg-panel p-4">
        <h2 className="text-sm font-bold text-archgreen">GitHub URL</h2>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/org/repo"
          className="mt-2 w-full border border-edge bg-ink p-2 text-sm"
        />
        <button
          onClick={handleUrlIngest}
          disabled={busy}
          className="mt-2 bg-archgreen px-4 py-1 text-sm font-bold text-ink disabled:opacity-50"
        >
          Ingest URL
        </button>
      </div>
      <label className="flex items-start gap-2 border border-archamber/50 bg-panel p-3 text-sm">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
        />
        <span>
          I confirm I own this code or am authorised to share it, and it contains
          no proprietary secrets I lack permission to upload. (Required)
        </span>
      </label>
      {tree.length > 0 && (
        <div className="border border-edge bg-panel p-4">
          <h2 className="text-sm font-bold text-archgreen">Tree preview ({tree.length})</h2>
          <ul className="mt-2 max-h-48 overflow-auto text-xs text-zinc-300">
            {tree.slice(0, 100).map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </div>
      )}
      <button
        onClick={handleAnalyse}
        disabled={busy || codebaseId == null}
        className="bg-archamber px-4 py-1 text-sm font-bold text-ink disabled:opacity-50"
      >
        Analyse
      </button>
      {message && <p className="text-sm text-archgreen">{message}</p>}
      {error && <p className="text-sm text-archamber">{error}</p>}
    </div>
  );
}
