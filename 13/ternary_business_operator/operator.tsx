import React, { useMemo, useRef, useState } from "react";

/**
 * company_operator: ternary trace viewer
 *
 * what this is:
 * - a single-file react app that visualizes 13-stage logs produced by a ternary operator middleware
 * - drop a .jsonl log or paste it into the text area to render a timeline + per-stage detail
 * - zero deps beyond react + tailwind; shadcn/ui optional stubs via plain divs
 *
 * expected log line schema (jsonl):
 * {
 *   "ts": "2025-08-28T16:00:52Z",        // iso timestamp
 *   "trace_id": "abc123",                // optional correlation id
 *   "stage": 1..13,                        // integer stage index
 *   "stage_name": "ingress",              // human label
 *   "decision": "REFRAIN|TEND|AFFIRM",    // ternary outcome
 *   "scalar": 0..13,                        // rail position
 *   "reason": "string",                   // short why
 *   "evidence": { ... },                    // any object, shown in inspector
 *   "flags": ["🟦","🟫"],                 // visual indicators
 *   "latency_ms": 3.7                      // optional
 * }
 *
 * usage:
 * - import and render <TernaryTraceViewer /> in your app or run this file in a react sandbox.
 */

// color helpers
const DECISION_COLOR: Record<string, string> = {
  REFRAIN: "bg-rose-100 border-rose-300 text-rose-900",
  TEND: "bg-amber-100 border-amber-300 text-amber-900",
  AFFIRM: "bg-emerald-100 border-emerald-300 text-emerald-900",
};

const STAGE_NAMES: Record<number, string> = {
  1: "ingress 🟦",
  2: "triage 🟦",
  3: "eco-weights 🟩",
  4: "intent 🟫",
  5: "ambiguity 🟧",
  6: "refrain 🟥",
  7: "affirm ⬛",
  8: "veto 🟧",
  9: "resolve 🟫",
 10: "action 🟩",
 11: "outcome 🟦",
 12: "feedback 🟫",
 13: "reset 🟦",
};

function classNames(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

function Sparkline({ points }: { points: number[] }) {
  const w = 200;
  const h = 40;
  const max = Math.max(1, ...points);
  const step = points.length > 1 ? w / (points.length - 1) : w;
  const d = points
    .map((v, i) => `${i === 0 ? "M" : "L"}${i * step},${h - (v / max) * h}`)
    .join(" ");
  return (
    <svg width={w} height={h} className="overflow-visible">
      <path d={d} fill="none" strokeWidth={2} stroke="currentColor" />
    </svg>
  );
}

function parseJsonl(text: string) {
  const lines = text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l.length > 0);
  const rows: any[] = [];
  const errors: { line: number; error: string }[] = [];
  lines.forEach((l, idx) => {
    try {
      const obj = JSON.parse(l);
      rows.push(obj);
    } catch (e: any) {
      errors.push({ line: idx + 1, error: e?.message || "parse error" });
    }
  });
  return { rows, errors };
}

function FileDrop({ onText }: { onText: (t: string) => void }) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files?.[0];
        if (!f) return;
        f.text().then(onText);
      }}
      className={classNames(
        "border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer",
        dragOver ? "bg-slate-50 border-slate-400" : "border-slate-300"
      )}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (!f) return;
          f.text().then(onText);
        }}
        accept=".jsonl,.log,.txt,application/jsonl,text/plain"
      />
      <div className="text-sm text-slate-600">drop a .jsonl log here or click to upload</div>
    </div>
  );
}

export default function TernaryTraceViewer() {
  const [raw, setRaw] = useState<string>("");
  const { rows, errors } = useMemo(() => parseJsonl(raw), [raw]);

  // group by trace_id, then order by ts+stage
  const traces = useMemo(() => {
    const byId = new Map<string, any[]>();
    rows.forEach((r) => {
      const id = r.trace_id || "default";
      if (!byId.has(id)) byId.set(id, []);
      byId.get(id)!.push(r);
    });
    Array.from(byId.values()).forEach((arr) =>
      arr.sort((a, b) => (a.ts || "").localeCompare(b.ts || "") || a.stage - b.stage)
    );
    return byId;
  }, [rows]);

  const [activeTraceId, setActiveTraceId] = useState<string | null>(null);
  const activeTrace = activeTraceId ? traces.get(activeTraceId) || [] : (traces.get("default") || []);

  const scalarSeries = activeTrace?.map((x: any) => Number(x.scalar ?? 0));

  return (
    <div className="min-h-screen p-6 bg-white text-slate-900">
      <header className="max-w-6xl mx-auto mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">company_operator • ternary trace viewer ⬛🟫🟩</h1>
        <p className="text-sm text-slate-600 mt-1">visualize 13-stage decisions, flags, and scalars from your ternary operator logs</p>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 space-y-4">
          <FileDrop onText={setRaw} />
          <textarea
            placeholder="or paste jsonl here — one json object per line"
            className="w-full h-40 border rounded-xl p-3 font-mono text-xs border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-400"
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
          />

          {errors.length > 0 && (
            <div className="p-3 rounded-xl border border-rose-300 bg-rose-50 text-rose-900 text-sm">
              parse errors on {errors.length} line(s): {errors.slice(0,3).map(e => `#${e.line}`).join(", ")}
            </div>
          )}

          {/* timeline */}
          <div className="border rounded-2xl p-4 border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <div className="font-medium">timeline</div>
              {scalarSeries?.length > 0 && (
                <div className="flex items-center gap-2 text-slate-500">
                  <span className="text-xs">scalar</span>
                  <div className="text-slate-700"><Sparkline points={scalarSeries} /></div>
                </div>
              )}
            </div>
            <ol className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
              {activeTrace?.map((step: any, idx: number) => (
                <li key={idx} className={classNames("border rounded-xl p-3", DECISION_COLOR[step.decision] || "border-slate-200")}> 
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold">{String(step.stage).padStart(2,'0')} · {STAGE_NAMES[step.stage] || step.stage_name || "stage"}</span>
                    <span>{(step.flags || []).join(" ")}</span>
                  </div>
                  <div className="mt-1 text-xs opacity-80">{new Date(step.ts || Date.now()).toISOString()}</div>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[10px] uppercase tracking-wide px-2 py-0.5 rounded-full border bg-white">{step.decision || "?"}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full border bg-white">scalar {Number(step.scalar ?? 0).toFixed(2)}</span>
                    {typeof step.latency_ms === 'number' && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full border bg-white">{step.latency_ms.toFixed(1)} ms</span>
                    )}
                  </div>
                  {step.reason && (
                    <p className="mt-2 text-sm leading-snug">{step.reason}</p>
                  )}
                  {step.evidence && (
                    <details className="mt-2 text-xs">
                      <summary className="cursor-pointer select-none">evidence</summary>
                      <pre className="text-[11px] whitespace-pre-wrap bg-white/60 border rounded p-2 mt-1 max-h-48 overflow-auto">{JSON.stringify(step.evidence, null, 2)}</pre>
                    </details>
                  )}
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* right rail */}
        <aside className="space-y-4">
          <div className="border rounded-2xl p-4 border-slate-200">
            <div className="font-medium mb-2">traces</div>
            <ul className="space-y-2">
              {Array.from(traces.keys()).map((id) => (
                <li key={id}>
                  <button
                    className={classNames(
                      "w-full text-left border rounded-xl px-3 py-2",
                      id === (activeTraceId || "default") ? "border-slate-600" : "border-slate-300 hover:border-slate-400"
                    )}
                    onClick={() => setActiveTraceId(id === "default" ? null : id)}
                  >
                    <div className="text-xs text-slate-500">trace</div>
                    <div className="text-sm font-mono">{id}</div>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="border rounded-2xl p-4 border-slate-200">
            <div className="font-medium">sample jsonl</div>
            <pre className="mt-2 text-xs bg-slate-50 border rounded p-3 overflow-auto">
{`{"ts":"2025-08-28T16:00:52Z","trace_id":"demo","stage":1,"stage_name":"ingress","decision":"TEND","scalar":2.0,"reason":"raw intake","flags":["🟦"]}
{"ts":"2025-08-28T16:00:52Z","trace_id":"demo","stage":6,"stage_name":"refrain","decision":"REFRAIN","scalar":1.2,"reason":"harm taxonomy match: 'toxicity'","flags":["🟥","🟨"],"evidence":{"terms":["toxicity"]}}
{"ts":"2025-08-28T16:00:53Z","trace_id":"demo","stage":8,"stage_name":"veto","decision":"REFRAIN","scalar":1.0,"reason":"ecocentric red line engaged","flags":["🟧"]}
{"ts":"2025-08-28T16:01:02Z","trace_id":"demo","stage":9,"stage_name":"resolve","decision":"TEND","scalar":5.3,"reason":"collapse to tend","flags":["🟫"]}
{"ts":"2025-08-28T16:01:08Z","trace_id":"demo","stage":10,"stage_name":"action","decision":"AFFIRM","scalar":11.0,"reason":"execute response","flags":["🟩","⬛"],"latency_ms":4.8}
{"ts":"2025-08-28T16:01:12Z","trace_id":"demo","stage":11,"stage_name":"outcome","decision":"TEND","scalar":7.0,"reason":"observed match","flags":["🟦"]}
{"ts":"2025-08-28T16:01:16Z","trace_id":"demo","stage":12,"stage_name":"feedback","decision":"TEND","scalar":6.2,"reason":"attenuate","flags":["🟫"],"evidence":{"reward":0.4}}
{"ts":"2025-08-28T16:01:20Z","trace_id":"demo","stage":13,"stage_name":"reset","decision":"TEND","scalar":5.0,"reason":"soft return to base tend","flags":["🟦"]}`}
            </pre>
          </div>

          <div className="border rounded-2xl p-4 border-slate-200 text-sm">
            <div className="font-medium mb-1">legend</div>
            <div className="space-y-1">
              <div>REFRAIN <span className="text-rose-700">🟥</span></div>
              <div>TEND <span className="text-amber-700">🟫</span></div>
              <div>AFFIRM <span className="text-emerald-700">⬛🟩</span></div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
