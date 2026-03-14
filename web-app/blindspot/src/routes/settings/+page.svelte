<script>
  import { detectionRange } from '$lib/stores.js';
  import { pushRange } from '$lib/api.js';
  import MotorDiagram from '$lib/components/MotorDiagram.svelte';

  function handleRange(e) {
    const v = parseFloat(e.target.value);
    detectionRange.set(v);
    pushRange(v).catch(() => {});
  }

  function pct(v)       { return ((v - 0.5) / 3.5 * 100).toFixed(1); }
  function sliderBg(v)  { return `linear-gradient(to right, #6367FF 0%, #6367FF ${pct(v)}%, #32326e ${pct(v)}%, #32326e 100%)`; }
  function nearZone(v)  { return `≤${(v * 0.25).toFixed(1)}m`; }
  function warnZone(v)  { return `${(v * 0.25).toFixed(1)}–${v.toFixed(1)}m`; }
  function safeZone(v)  { return `>${v.toFixed(1)}m`; }
</script>

<div class="navbar">
  <div class="nav-title">Settings</div>
  <a href="/" class="back-btn">← Back</a>
</div>

<div class="page-content">
  <div class="screen-title">General <span>Settings</span></div>

  <div class="card">
    <div class="slider-header">
      <div class="card-label">📏 Detection Range</div>
      <div class="value-badge">{$detectionRange.toFixed(1)}m</div>
    </div>
    <div class="slider-labels">
      <span>0.5m</span><span>1.5m</span><span>2.5m</span>
      <span>3.5m</span><span>4.0m</span>
    </div>
    <input
      type="range" min="0.5" max="4.0" step="0.1"
      value={$detectionRange}
      style="background: {sliderBg($detectionRange)}"
      on:input={handleRange}
    />
    <div class="zone-chips">
      <div class="zone-chip">
        <div class="zl">NEAR</div>
        <div class="zv" style="color:var(--blush)">{nearZone($detectionRange)}</div>
      </div>
      <div class="zone-chip">
        <div class="zl">WARN</div>
        <div class="zv" style="color:var(--lavender)">{warnZone($detectionRange)}</div>
      </div>
      <div class="zone-chip">
        <div class="zl">SAFE</div>
        <div class="zv" style="color:var(--periwinkle)">{safeZone($detectionRange)}</div>
      </div>
    </div>
  </div>

  <MotorDiagram />
</div>

<style>
  :global(a.back-btn) { text-decoration: none; }
</style>