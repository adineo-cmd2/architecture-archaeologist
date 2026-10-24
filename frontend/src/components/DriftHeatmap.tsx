export interface DriftEntry {
  path: string;
  score: number;
  reasons: string[];
}

function colorFor(score: number): string {
  if (score >= 0.7) return 'bg-red-900/60 border-red-700';
  if (score >= 0.4) return 'bg-archamber/20 border-archamber';
  return 'bg-archgreen/10 border-archgreen/50';
}

export default function DriftHeatmap({ drift }: { drift: DriftEntry[] }) {
  if (!drift || drift.length === 0) {
    return <p className="text-sm text-inksoft">No drift data yet.</p>;
  }
  return (
    <ul className="space-y-2">
      {drift.map((d) => (
        <li key={d.path} className={`border px-3 py-2 ${colorFor(d.score)}`}>
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm">{d.path}</span>
            <span className="text-sm font-bold">{d.score.toFixed(2)}</span>
          </div>
          {d.reasons && d.reasons.length > 0 && (
            <p className="mt-1 text-xs text-inksoft">{d.reasons.join('; ')}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
