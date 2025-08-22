/*
 * OIUIDI · Ternary Logic Core v1.0
 * (a ⊕ b ⊕ c)^{t̂}  — plug‑and‑play ternary overlay for agents/LLMs
 * 
 * License: MIT. Drop-in via <script src> or ESM import.
 * Exposes a tiny, composable API:
 *   - score(inputs, weights?) -> scalar in [-1, 0, +1]
 *   - decide(inputs, weights?, thresholds?) -> {-1|0|+1}
 *   - flag(decision|scalar) -> {emoji, color, label}
 *   - reduce(stream, opts) -> rolling state with hysteresis (t̂)
 *   - badge(element, value, opts?) -> attach visual badge
 *   - explain(inputs, weights?, thresholds?) -> structured rationale
 *
 * Inputs can be numbers in [-1,0,+1] or objects {v, w}.
 *
 * t̂ (temporal exponent) is modeled as hysteresis + momentum so decisions
 * don’t flap on noise: we weight recent history and require margin to flip.
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.TernaryCore = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  const CLAMP = (x, a, b) => Math.max(a, Math.min(b, x));
  const isNum = (x) => typeof x === 'number' && isFinite(x);

  // 🟜 reject, 🟫 tend, ⬛ affirm (color semantics can be mapped downstream)
  const FLAGS = {
    '-1': { emoji: '🟜', color: '#7f1d1d', label: 'reject' },
     '0': { emoji: '🟫', color: '#7c6f64', label: 'tend'   },
     '1': { emoji: '⬛', color: '#0f172a', label: 'affirm' }
  };

  // Normalize any input into {v, w}
  function norm(x, wDefault = 1) {
    if (isNum(x)) return { v: CLAMP(x, -1, 1), w: wDefault };
    if (x && isNum(x.v)) return { v: CLAMP(x.v, -1, 1), w: isNum(x.w) ? x.w : wDefault };
    return { v: 0, w: 0 };
  }

  /**
   * score: weighted ternary aggregation (a ⊕ b ⊕ c …) → scalar in [-1,1]
   * Default operator is a weighted mean with soft‑nonlinearity to emphasize extremal consensus.
   */
  function score(inputs, weights) {
    if (!Array.isArray(inputs) || inputs.length === 0) return 0;
    const items = inputs.map((x, i) => norm(weights ? { v: x, w: weights[i] } : x));
    let wsum = 0, acc = 0;
    for (const { v, w } of items) { wsum += w; acc += w * v; }
    if (wsum === 0) return 0;
    const m = acc / wsum; // mean in [-1,1]
    // Soft nonlinearity: push consensus toward corners, keep neutrality near 0 gentle
    const k = 1.25; // curvature
    return CLAMP(Math.tanh(k * m), -1, 1);
  }

  /**
   * decide: snap a scalar to {-1,0,+1} with asymmetric thresholds.
   */
  function decide(inputs, weights, thresholds) {
    const s = isNum(inputs) ? CLAMP(inputs, -1, 1) : score(inputs, weights);
    const th = Object.assign({ neg: -0.25, pos: 0.25 }, thresholds);
    if (s <= th.neg) return -1;
    if (s >= th.pos) return +1;
    return 0;
  }

  /**
   * flag: map scalar/decision to UI signal (emoji/color/label).
   */
  function flag(value) {
    const v = isNum(value) ? (value < -0.5 ? -1 : value > 0.5 ? 1 : 0) : 0;
    const key = String(v);
    return FLAGS[key];
  }

  /**
   * reduce: temporal exponent t̂ — rolling aggregation with momentum + hysteresis.
   * opts: { alpha (0..1), inertia (0..1), neg, pos }
   */
  function reduce() {
    let state = { s: 0, d: 0 }; // scalar, discrete decision
    return function next(input, opts = {}) {
      const { alpha = 0.25, inertia = 0.6, neg = -0.25, pos = 0.25 } = opts;
      const x = isNum(input) ? CLAMP(input, -1, 1) : score([].concat(input));
      // EWMA toward new signal (alpha), plus inertia on previous scalar
      const s = CLAMP((1 - alpha) * state.s + alpha * x, -1, 1);
      // hysteresis: require margin beyond thresholds to flip
      let d = state.d;
      if (d === 0) d = s <= neg ? -1 : s >= pos ? +1 : 0;
      else if (d === -1) d = s >= neg * (1 - inertia) ? 0 : -1;
      else if (d === +1) d = s <= pos * (1 - inertia) ? 0 : +1;
      state = { s, d };
      return state;
    };
  }

  /** Attach a small badge to any DOM node to visualize ternary state. */
  function badge(el, value, opts = {}) {
    const f = flag(value);
    const text = opts.text ?? f.emoji;
    const bg = opts.bg ?? f.color;
    const color = opts.color ?? '#e5e7eb';
    const style = Object.assign({
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      padding: '2px 6px', borderRadius: '9999px', font: '600 12px/1 Inter, system-ui',
      background: bg, color, marginLeft: '6px'
    }, opts.style || {});
    const span = document.createElement('span');
    Object.assign(span.style, style);
    span.textContent = text;
    el.appendChild(span);
    return span;
  }

  /** explain: return a transparent rationale payload for logs/LLMs. */
  function explain(inputs, weights, thresholds) {
    const items = (Array.isArray(inputs) ? inputs : [inputs]).map((x, i) => norm(weights ? { v: x, w: weights[i] } : x));
    const s = score(items);
    const d = decide(s, undefined, thresholds);
    return {
      inputs: items, scalar: s, decision: d, flag: flag(d), thresholds: Object.assign({ neg: -0.25, pos: 0.25 }, thresholds)
    };
  }

  // Minimal web component for drop‑in use: <tern-flag value="-1|0|1|scalar"></tern-flag>
  class TernFlag extends HTMLElement {
    static get observedAttributes() { return ['value']; }
    attributeChangedCallback() { this.render(); }
    connectedCallback() { this.render(); }
    render(){
      const v = parseFloat(this.getAttribute('value'));
      const f = flag(isFinite(v) ? v : 0);
      this.innerHTML = '';
      const pill = document.createElement('span');
      pill.textContent = f.emoji;
      Object.assign(pill.style, { display:'inline-flex', padding:'2px 6px', borderRadius:'9999px', background:f.color, color:'#e5e7eb', font:'600 12px/1 Inter, system-ui' });
      this.appendChild(pill);
    }
  }
  if (typeof customElements !== 'undefined' && !customElements.get('tern-flag')) {
    customElements.define('tern-flag', TernFlag);
  }

  return { score, decide, flag, reduce, badge, explain, FLAGS };
});

/*
USAGE
-----
<script src="https://eriirfos-eng.github.io/ternlang/docs/ternary-core.js"></script>
<script>
  const { score, decide, reduce, badge } = TernaryCore;
  const s = score([+1, 0, -1], [0.5, 0.2, 0.3]);
  const d = decide(s); // -1 | 0 | +1
  const next = reduce();
  console.log(next(+1)); // {s:…, d:+1}
  // attach a badge
  badge(document.body, d);
</script>
*/
