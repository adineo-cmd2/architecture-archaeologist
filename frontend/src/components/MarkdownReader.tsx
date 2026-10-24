export default function MarkdownReader({ markdown }: { markdown: string }) {
  if (!markdown) return <p className="text-sm text-inksoft">No report yet.</p>;
  const blocks = markdown.split(/\n{2,}/);
  return (
    <div className="space-y-3">
      {blocks.map((b, i) => {
        if (b.trimStart().startsWith('```')) {
          return (
            <pre key={i} className="overflow-auto border border-edge bg-ink p-3 text-xs">
              {b.replace(/```/g, '')}
            </pre>
          );
        }
        if (b.trimStart().startsWith('#')) {
          return (
            <h3 key={i} className="text-base font-bold text-archgreen">
              {b.replace(/^#+\s*/, '')}
            </h3>
          );
        }
        return (
          <p key={i} className="whitespace-pre-wrap text-sm text-zinc-300">
            {b}
          </p>
        );
      })}
    </div>
  );
}
