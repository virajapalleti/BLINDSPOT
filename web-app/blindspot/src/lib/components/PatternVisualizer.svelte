<script>
  import { onMount, onDestroy } from 'svelte';

  let { pattern = [] } = $props();

  let activeStep = $state(-1);
  let animTO = null;

  function stopAnim() {
    if (animTO) { clearTimeout(animTO); animTO = null; }
    activeStep = -1;
  }

  function startAnim() {
    stopAnim();
    let step = 0;
    const DOT = 230, DASH = 580, GAP = 170, PAUSE = 950;
    function tick() {
      if (step >= pattern.length) {
        step = 0;
        activeStep = -1;
        animTO = setTimeout(tick, PAUSE);
        return;
      }
      activeStep = step;
      const dur = pattern[step] === 'dot' ? DOT : DASH;
      animTO = setTimeout(() => {
        activeStep = -1;
        step++;
        animTO = setTimeout(tick, GAP);
      }, dur);
    }
    tick();
  }

  onMount(() => startAnim());
  onDestroy(() => stopAnim());

  $effect(() => {
    // Restart when pattern changes
    const _ = pattern.join(',');
    startAnim();
  });
</script>

<div class="big-dot-wrap">
  <div class="big-dot" class:on={activeStep >= 0}></div>

  <div class="morse-repr">
    <span class="morse-repr-label">PATTERN:</span>
    <div class="morse-syms">
      {#each pattern as seg, i}
        <div
          class="{seg === 'dot' ? 'msym-dot' : 'msym-dash'}"
          class:active={activeStep === i}
        ></div>
      {/each}
    </div>
  </div>

  <div class="morse-legend">
    <div class="leg"><div class="leg-dot"></div>short buzz</div>
    <div class="leg"><div class="leg-dash"></div>long buzz</div>
  </div>
</div>