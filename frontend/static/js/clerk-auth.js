let clerkInitPromise = null;

async function initClerk() {
  if (clerkInitPromise) {
    return clerkInitPromise;
  }

  clerkInitPromise = (async () => {
    const configResponse = await fetch('/api/clerk-config');
    const config = await configResponse.json();

    if (!config.publishableKey || !config.frontendApi) {
      throw new Error('Clerk is not configured');
    }

    await loadScript(`${config.frontendApi}/npm/@clerk/ui@1/dist/ui.browser.js`);
    await loadScript(
      `${config.frontendApi}/npm/@clerk/clerk-js@6/dist/clerk.browser.js`,
      { 'data-clerk-publishable-key': config.publishableKey }
    );

    await window.Clerk.load({
      ui: { ClerkUI: window.__internal_ClerkUICtor },
    });

    return window.Clerk;
  })();

  return clerkInitPromise;
}

function loadScript(src, attributes = {}) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.defer = true;
    script.crossOrigin = 'anonymous';
    Object.entries(attributes).forEach(([key, value]) => {
      script.setAttribute(key, value);
    });
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function syncBackendSession() {
  const response = await fetch('/api/auth/sync', { method: 'POST' });
  if (!response.ok) {
    throw new Error('Failed to sync session');
  }
  return response.json();
}

async function clerkLogout() {
  try {
    await fetch('/api/logout', { method: 'POST' });
    const clerk = await initClerk();
    await clerk.signOut({ redirectUrl: '/' });
  } catch (error) {
    window.location.href = '/';
  }
}
