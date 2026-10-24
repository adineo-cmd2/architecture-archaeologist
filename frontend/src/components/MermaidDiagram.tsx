import { useEffect, useRef, useState } from 'react';

export default function MermaidDiagram({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [fallback, setFallback] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!chart || !ref.current) return;
      try {
        const mod = await import('mermaid');
        const mermaid = mod.default ?? mod;
        (mermaid as { initialize?: (o: unknown) => void }).initialize?.({
          startOnLoad: false,
          theme: 'dark',
        });
        const render = (mermaid as { render?: (...a: unknown[]) => Promise<{ svg: string }> }).render;
        if (!render) throw new Error('no render');
        const id = `mmd-${Date.now()}`;
        const out = await render.call(mermaid, id, chart);
        if (!cancelled && ref.current) ref.current.innerHTML = out.svg;
      } catch {
        if (!cancelled) setFallback(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [chart]);

  if (!chart) return <p className="text-sm text-inksoft">No diagram yet.</p>;
  if (fallback) {
    return (
      <div>
        <p className="mb-2 text-xs text-archamber">Diagram library unavailable — showing source.</p>
        <pre className="overflow-auto border border-edge bg-ink p-3 text-xs">{chart}</pre>
      </div>
    );
  }
  return <div ref={ref} className="overflow-auto border border-edge bg-panel p-3" />;
}
