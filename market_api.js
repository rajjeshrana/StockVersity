(() => {
  "use strict";

  const API_BASE =
    window.STOCKVERSITY_API_BASE ||
    "http://127.0.0.1:8787";

  const MARKET_URL = `${API_BASE}/api/market`;
  const FUTURES_URL = `${API_BASE}/api/futures`;

  const state = {
    market: null,
    futures: null,
    marketOk: false,
    futuresOk: false,
    lastSuccess: null,
    lastError: null,
    running: false
  };

  let timer = null;
  let requestInProgress = false;

  async function fetchWithTimeout(url, timeoutMs = 8000) {
    const controller = new AbortController();
    const timerId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        method: "GET",
        cache: "no-store",
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } finally {
      clearTimeout(timerId);
    }
  }

  function updateStatus() {
    const dot = document.getElementById("connection-dot");
    const txt = document.getElementById("connection-text");

    const online = state.marketOk;
    const partial = !online && state.futuresOk;

    if (dot) {
      dot.className =
        online || partial
          ? "status-dot live"
          : "status-dot offline";
    }

    if (txt) {
      txt.textContent =
        online
          ? "API ONLINE"
          : partial
            ? "API PARTIAL"
            : "API OFFLINE";
    }

    const updated = document.getElementById("last-updated");

    if (updated && state.lastSuccess) {
      updated.textContent =
        "Last update: " +
        new Date(state.lastSuccess).toLocaleTimeString("en-IN");
    }
  }

  async function refresh() {
    if (requestInProgress) {
      return getState();
    }

    requestInProgress = true;

    try {
      const results = await Promise.allSettled([
        fetchWithTimeout(MARKET_URL),
        fetchWithTimeout(FUTURES_URL)
      ]);

      if (results[0].status === "fulfilled") {
        state.market = results[0].value;
        state.marketOk = Boolean(state.market?.ok);
      }

      if (results[1].status === "fulfilled") {
        state.futures = results[1].value;
        state.futuresOk = Boolean(state.futures?.ok);
      }

      if (
        results[0].status === "fulfilled" ||
        results[1].status === "fulfilled"
      ) {
        state.lastSuccess = Date.now();
        state.lastError = null;
      } else {
        state.lastError = "API request failed";
      }

    } catch (error) {
      state.lastError = String(error);
    } finally {
      requestInProgress = false;
      updateStatus();

      window.dispatchEvent(
        new CustomEvent("stockversity:api", {
          detail: getState()
        })
      );
    }

    return getState();
  }

  function getState() {
    return {
      market: state.market,
      futures: state.futures,
      marketOk: state.marketOk,
      futuresOk: state.futuresOk,
      lastSuccess: state.lastSuccess,
      lastError: state.lastError
    };
  }

  function start() {
    if (state.running) {
      return;
    }

    state.running = true;

    refresh();

    timer = window.setInterval(
      refresh,
      3000
    );
  }

  function stop() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }

    state.running = false;
  }

  window.StockVersityAPI = Object.freeze({
    getState,
    refresh,
    start,
    stop,
    urls: Object.freeze({
      market: MARKET_URL,
      futures: FUTURES_URL
    })
  });

  start();
})();

