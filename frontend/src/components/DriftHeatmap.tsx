export interface DriftEntry {
  path: string;
  score: number;
  reasons: string[];
}

function levelFor(score: number): 'high' | 'mid' | 'low' {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'mid';
  return 'low';
}

export default function DriftHeatmap({ drift }: { drift: DriftEntry[] }) {
  if (!drift || drift.length === 0) {
    return <p className="register-empty">No drift data yet.</p>;
  }
  return (
    <ul className="drift-list">
      {drift.map((d) => (
        <li key={d.path} className="drift-entry" data-level={levelFor(d.score)}>
          <div className="drift-line">
            <span className="drift-path">{d.path}</span>
            <span className="drift-score mono-n">{d.score.toFixed(2)}</span>
          </div>
          <div className="drift-meter">
            <span style={{ width: `${Math.max(2, Math.min(100, d.score * 100))}%` }} />
          </div>
          {d.reasons && d.reasons.length > 0 && (
            <p className="drift-reason">{d.reasons.join('; ')}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
