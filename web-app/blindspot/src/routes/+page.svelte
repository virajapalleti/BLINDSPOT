<script>
  import { onMount } from 'svelte';
  import { connectionStatus } from '$lib/stores.js';
  import { checkConnection } from '$lib/api.js';

  onMount(() => {
    async function poll() {
      const ok = await checkConnection();
      connectionStatus.set(ok ? 'connected' : 'disconnected');
    }
    poll();
    const interval = setInterval(poll, 10000);
    return () => clearInterval(interval);
  });

  const labels = {
    connected: 'CONNECTED',
    disconnected: 'NOT CONNECTED',
    connecting: 'CONNECTING...'
  };

  const dotColors = {
    connected: 'var(--lavender)',
    disconnected: 'var(--blush)',
    connecting: 'var(--muted)'
  };

  const borderColors = {
    connected: 'rgba(99,103,255,0.4)',
    disconnected: 'rgba(255,219,253,0.35)',
    connecting: 'rgba(201,190,255,0.2)'
  };
</script>

<div class="home-bg"></div>
<div class="grid-lines"></div>

<div class="home-content">
  <div class="intro-line">introducing</div>
  <div class="hero-name">BlindSpot</div>

  <div class="status-badge" style="border-color: {borderColors[$connectionStatus]}">
    <div class="pulse-dot" style="background: {dotColors[$connectionStatus]}"></div>
    <span>{labels[$connectionStatus]}</span>
  </div>

  <div class="nav-grid">
    <a href="/settings" class="nav-card" style="--ac: var(--lavender)">
      <div class="ci">⚙️</div>
      <div class="ct">Settings</div>
      <div class="cd">Detection range & motor info</div>
    </a>
    <a href="/haptic" class="nav-card" style="--ac: var(--indigo)">
      <div class="ci">📳</div>
      <div class="ct">Haptic Patterns</div>
      <div class="cd">Customize vibrations per object</div>
    </a>
  </div>
</div>

<style>
  :global(body) {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    overflow-x: hidden;
  }

  :global(.home-bg) {
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
      radial-gradient(ellipse 70% 55% at 50% 10%, rgba(132,148,255,0.28) 0%, transparent 65%),
      radial-gradient(ellipse 45% 45% at 85% 85%, rgba(255,219,253,0.18) 0%, transparent 60%),
      radial-gradient(ellipse 35% 40% at 10% 75%, rgba(201,190,255,0.18) 0%, transparent 55%);
  }

  :global(.grid-lines) {
    position: fixed;
    inset: 0;
    z-index: 0;
    background-image:
      linear-gradient(rgba(201,190,255,0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(201,190,255,0.08) 1px, transparent 1px);
    background-size: 44px 44px;
  }

  .home-content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    width: 100%;
    max-width: 460px;
    gap: 36px;
    padding: 52px 28px;
    margin: 0 auto;
  }

  :global(a.nav-card) {
    text-decoration: none;
    color: inherit;
  }
</style>