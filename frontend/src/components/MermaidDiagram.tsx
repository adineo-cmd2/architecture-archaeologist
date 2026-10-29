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
          theme: 'base',
          themeVariables: {
            background: '#ffffff',
            primaryColor: '#eaf0f5',
            primaryTextColor: '#14314f',
            primaryBorderColor: '#14314f',
            lineColor: '#5b7185',
            secondaryColor: '#f4f7fa',
            tertiaryColor: '#ffffff',
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: '13px',
          },
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

  if (!chart) return <p className="register-empty">No diagram yet.</p>;
  if (fallback) {
    return (
      <div>
        <p className="form-note error">Diagram library unavailable — showing source.</p>
        <pre className="code-block">{chart}</pre>
      </div>
    );
  }
  return <div ref={ref} className="diagram-frame" />;
}
