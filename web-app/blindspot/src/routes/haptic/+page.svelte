<script>
  import { patterns, objects } from '$lib/stores.js';
  import { applyPattern } from '$lib/api.js';
  import PatternVisualizer from '$lib/components/PatternVisualizer.svelte';
  import PatternEditor from '$lib/components/PatternEditor.svelte';

  let activeIdx = $state(0);
  let editorOpen = $state(false);
  let applying = $state(false);
  let applied = $state(false);
  let toast = $state('');
  let toastTO = null;

  function getCurrentPattern() { return $patterns[activeIdx]; }
  function getCurrentObject()  { return objects[activeIdx]; }

  function showToast(msg) {
    toast = msg;
    if (toastTO) clearTimeout(toastTO);
    toastTO = setTimeout(() => toast = '', 2600);
  }

  async function handleApply() {
    applying = true;
    try {
      await applyPattern(getCurrentObject().label.toLowerCase(), getCurrentPattern());
      applied = true;
      applying = false;
      setTimeout(() => applied = false, 2000);
    } catch {
      applying = false;
      showToast('Saved locally — apply when connected');
    }
  }
</script>

<div class="navbar">
  <div class="nav-title">Haptic Patterns</div>
  <a href="/" class="back-btn">← Back</a>
</div>

<div class="page-content">
  <div class="screen-title">Haptic <span>Patterns</span></div>

  <div class="island-nav">
    {#each objects as obj, i}
      <button
        class="island-btn"
        class:active={i === activeIdx}
        onclick={() => { activeIdx = i; editorOpen = false; }}
      >
        {obj.emoji} {obj.label}
      </button>
    {/each}
  </div>

  <div class="object-card">
    <div class="object-hero">
      <div class="obj-emoji-el">{getCurrentObject().emoji}</div>
    </div>
    <div class="obj-meta">
      <div class="obj-name">{getCurrentObject().label}</div>
      <div class="obj-desc">{getCurrentObject().desc}</div>
    </div>

    <div class="viz-section">
      <div class="viz-header">
        <div class="viz-title">Vibration Pattern</div>
        <div class="live-badge">
          <div class="live-dot"></div>LIVE
        </div>
      </div>
      <PatternVisualizer pattern={getCurrentPattern()} />
    </div>

    <div class="action-row">
      <button class="btn-customize" onclick={() => editorOpen = true}>
        ✏️ Customize
      </button>
      <button
        class="btn-apply"
        onclick={handleApply}
        disabled={applying}
      >
        {#if applying}Sending...{:else if applied}✓ Applied{:else}↑ Apply{/if}
      </button>
    </div>
  </div>
</div>

{#if editorOpen}
  <PatternEditor
    {activeIdx}
    objectLabel={getCurrentObject().label}
    oncloseeditor={() => editorOpen = false}
  />
{/if}

{#if toast}
  <div class="toast show">{toast}</div>
{/if}

<style>
  :global(a.back-btn) { text-decoration: none; }
</style>