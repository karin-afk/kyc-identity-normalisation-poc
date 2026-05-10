(() => {
  const eventMeta = document.querySelector('meta[name="telemetry-event-url"]');
  const endMeta = document.querySelector('meta[name="telemetry-session-end-url"]');

  if (!eventMeta || !eventMeta.content) {
    return;
  }

  const eventUrl = eventMeta.content;
  const sessionEndUrl = endMeta ? endMeta.content : eventUrl;

  const sendEvent = (eventName, details = {}, preferBeacon = false) => {
    const payload = {
      event_name: eventName,
      client_ts: new Date().toISOString(),
      details,
    };

    if (preferBeacon && navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
      navigator.sendBeacon(eventName === 'session_ended' ? sessionEndUrl : eventUrl, blob);
      return;
    }

    fetch(eventName === 'session_ended' ? sessionEndUrl : eventUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(() => {
      // Telemetry should never block user actions.
    });
  };

  document.addEventListener('DOMContentLoaded', () => {
    sendEvent('page_loaded', {
      path: window.location.pathname,
      title: document.title,
    });

    document.querySelectorAll('.tabs .tab').forEach((tab) => {
      tab.addEventListener('click', () => {
        sendEvent('tab_clicked', {
          label: (tab.textContent || '').trim(),
          href: tab.getAttribute('href') || '',
        });
      });
    });

    document.addEventListener('submit', (evt) => {
      const form = evt.target;
      if (!(form instanceof HTMLFormElement)) {
        return;
      }

      sendEvent('form_submitted', {
        action: form.getAttribute('action') || form.getAttribute('hx-post') || '',
        method: (form.getAttribute('method') || 'post').toLowerCase(),
      });
    }, true);

    const trackClipboard = (type) => (evt) => {
      const target = evt.target;
      const descriptor = target && target.id ? `#${target.id}` : target && target.tagName ? target.tagName : 'unknown';
      sendEvent(type, { target: descriptor });
    };

    document.addEventListener('paste', trackClipboard('input_paste'), true);
    document.addEventListener('copy', trackClipboard('input_copy'), true);
    document.addEventListener('cut', trackClipboard('input_cut'), true);
  });

  document.addEventListener('visibilitychange', () => {
    sendEvent('visibility_changed', { state: document.visibilityState });
  });

  document.body.addEventListener('htmx:beforeRequest', (evt) => {
    const path = evt && evt.detail && evt.detail.pathInfo ? evt.detail.pathInfo.requestPath : '';
    sendEvent('htmx_before_request', { path });
  });

  document.body.addEventListener('htmx:afterRequest', (evt) => {
    const status = evt && evt.detail && evt.detail.xhr ? evt.detail.xhr.status : null;
    const path = evt && evt.detail && evt.detail.pathInfo ? evt.detail.pathInfo.requestPath : '';
    sendEvent('htmx_after_request', { path, status });
  });

  window.addEventListener('beforeunload', () => {
    sendEvent('session_ended', { path: window.location.pathname }, true);
  });
})();
