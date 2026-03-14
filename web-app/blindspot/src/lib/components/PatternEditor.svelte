<script>
  import { patterns } from '$lib/stores.js';

  let { activeIdx = 0, objectLabel = '', oncloseeditor } = $props();

  let editorSeq = $state([...$patterns[activeIdx]]);

  function addSeg(type) {
    if (editorSeq.length >= 8) return;
    editorSeq = [...editorSeq, type];
  }

  function toggleSeg(i) {
    editorSeq = editorSeq.map((s, idx) => idx === i ? (s === 'dot' ? 'dash' : 'dot') : s);
  }

  function delSeg(i) {
    editorSeq = editorSeq.filter((_, idx) => idx !== i);
  }

  function save() {
    if (editorSeq.length === 0) return;
    patterns.update(p => {
      const copy = [...p];
      copy[activeIdx] = [...editorSeq];
      return copy;
    });
    oncloseeditor();
  }
</script>

<div class="modal-overlay open" onclick={oncloseeditor}>
  <div class="modal" onclick={(e) => e.stopPropagation()}>
    <div class="modal-handle"></div>
    <div class="modal-title">Edit — <span>{objectLabel}</span></div>
    <div class="modal-sub">Tap to toggle short/long. Hover to delete.</div>

    <div class="seq-label">SEQUENCE (plays on repeat):</div>

    <div class="seq-slots">
      {#each editorSeq as seg, i}
        <div class="seq-slot">
          <div
            class="slot-btn is-{seg}"
            onclick={() => toggleSeg(i)}
            role="button"
            tabindex="0"
          >
            <div class="{seg === 'dot' ? 'si-dot' : 'si-dash'}"></div>
          </div>
          <div class="slot-lbl">{seg === 'dot' ? '•' : '—'}</div>
          <button class="slot-del" onclick={() => delSeg(i)}>×</button>
        </div>
      {/each}
    </div>

    <div class="add-row">
      <button class="add-btn add-dot" onclick={() => addSeg('dot')}>
        + Short buzz &nbsp;•
      </button>
      <button class="add-btn add-dash" onclick={() => addSeg('dash')}>
        + Long buzz &nbsp;—
      </button>
    </div>

    <div class="modal-actions">
      <button class="btn-cancel" onclick={oncloseeditor}>Cancel</button>
      <button class="btn-save" onclick={save}>Save Pattern</button>
    </div>
  </div>
</div>