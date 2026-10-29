export default function MarkdownReader({ markdown }: { markdown: string }) {
  if (!markdown) return <p className="register-empty">No report yet.</p>;
  const blocks = markdown.split(/\n{2,}/);
  return (
    <div className="doc-block">
      {blocks.map((b, i) => {
        if (b.trimStart().startsWith('```')) {
          return (
            <pre key={i} className="code-block">
              {b.replace(/```/g, '')}
            </pre>
          );
        }
        if (b.trimStart().startsWith('#')) {
          return (
            <h3 key={i}>{b.replace(/^#+\s*/, '')}</h3>
          );
        }
        return (
          <p key={i}>{b}</p>
        );
      })}
    </div>
  );
}
