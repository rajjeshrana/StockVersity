const $ = id => document.getElementById(id);
const API_BASE = window.STOCKVERSITY_API_BASE || "https://api.stockversity.in";
const MARKET_URL = `${API_BASE}/api/market`;
const FUTURES_URL = "/api/futures";

const fmt = n => Number.isFinite(Number(n))
  ? Number(n).toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2})
  : "--";
const pct = n => Number.isFinite(Number(n))
  ? `${Number(n) > 0 ? "+" : ""}${Number(n).toFixed(2)}%`
  : "--";
const setText = (id, v) => { const e = $(id); if (e) e.textContent = v; };
const num = (...xs) => { for (const x of xs) { const n = Number(x); if (Number.isFinite(n)) return n; } return NaN; };
function setPctClass(e, v) {
  if (!e) return;
  e.classList.remove("green-text", "red-text");
  if (Number(v) > 0) e.classList.add("green-text");
  else if (Number(v) < 0) e.classList.add("red-text");
}
function add(parent, html, cls) {
  if (!parent) return;
  parent.insertAdjacentHTML("beforeend", `<div class="${cls}">${html}</div>`);
}
function pctChange(x) {
  return num(x?.change_percent, x?.percent_change, x?.change, x?.average_change_percent);
}
function priceOf(x) { return num(x?.ltp, x?.last_price, x?.price, x?.close); }

function updateQuotes(payload) {
  const rows = Array.isArray(payload?.results) ? payload.results : [];

  const norm = v =>
    String(v ?? "")
      .toUpperCase()
      .replace(/[^A-Z0-9]+/g, "");

  const fields = x => [
    x?.instrument_key,
    x?.trading_symbol,
    x?.symbol,
    x?.name,
    x?.display_name,
    x?.exchange_token
  ].map(norm);

  const findQuote = aliases => {
    const wanted = aliases.map(norm);

    return rows.find(x => {
      const f = fields(x);
      return f.some(v =>
        wanted.some(a => a && (v === a || v.includes(a) || a.includes(v)))
      );
    }) || {};
  };

  const specs = [
    [["NSE_INDEX|Nifty 50", "NIFTY 50", "NIFTY50"], "nifty"],
    [["NSE_INDEX|Nifty Bank", "NIFTY BANK", "BANKNIFTY"], "banknifty"],
    [["NSE_INDEX|India VIX", "INDIA VIX", "INDIAVIX"], "vix"],
    [["GLOBAL_INDEX|SGX NIFTY", "GIFT NIFTY", "GIFTNIFTY", "SGX NIFTY"], "gift"],
    [["BTC/USD", "BTCUSD", "BTC-USD", "BITCOIN"], "btc"],
    [["GOLD/USD", "GOLDUSD", "GOLD-USD", "GOLD"], "gold"]
  ];

  specs.forEach(([aliases, id]) => {
    const x = findQuote(aliases);
    const price = priceOf(x);
    const previous = num(x.previous_close, x.close);

    const change =
      Number.isFinite(price) &&
      Number.isFinite(previous) &&
      previous > 0
        ? ((price - previous) / previous) * 100
        : NaN;

    const prefix = id === "btc" || id === "gold" ? "$" : "";

    setText(
      `${id}-price`,
      Number.isFinite(price)
        ? prefix + fmt(price)
        : "--"
    );

    setText(`${id}-change`, pct(change));
    setPctClass($(`${id}-change`), change);
  });
}

function normalizeFutures(payload) {
  const rows = Array.isArray(payload?.results) ? payload.results : [];
  return rows.map(x => ({
    ...x,
    symbol: x.symbol || x.trading_symbol || x.name || x.instrument_key || "--",
    price: priceOf(x),
    change: pctChange(x),
    signal: String(x.signal || x.action || x.side || "").toUpperCase(),
    score: num(x.score, x.confidence, x.opportunity_score),
    pattern: x.pattern || x.trigger || x.reason || "Scanner Match",
    sector: x.sector || x.sector_name || x.industry || "",
  }));
}

function renderSectors(items) {
  const bull = $("bullish-sectors"), bear = $("bearish-sectors");
  if (!bull || !bear) return;
  bull.innerHTML = ""; bear.innerHTML = "";
  const sectorMap = new Map();
  items.forEach(x => {
    if (!x.sector) return;
    const prev = sectorMap.get(x.sector);
    if (!prev || Math.abs(x.change || 0) > Math.abs(prev.change || 0)) sectorMap.set(x.sector, x);
  });
  const data = [...sectorMap.values()].sort((a,b) => (b.change||0)-(a.change||0));
  const b = data.filter(x => x.change > 0).slice(0,5);
  const r = data.filter(x => x.change < 0).sort((a,b)=>(a.change||0)-(b.change||0)).slice(0,5);
  [[bull,b,"bull"],[bear,r,"bear"]].forEach(([root, arr, side]) => {
    arr.forEach(x => {
      const strength = Math.min(100, Math.max(2, Math.abs(x.change) * 20));
      add(root, `<span>${x.sector}</span><div class="bar"><i style="width:${strength}%"></i></div><span class="${side === "bull" ? "change-pos" : "change-neg"}">${pct(x.change)}</span>`, "sector-row");
    });
  });
}

function renderBreadth(items) {
  const a = items.filter(x => (x.change || 0) > 0).length;
  const d = items.filter(x => (x.change || 0) < 0).length;
  const u = Math.max(0, items.length - a - d);
  const total = a+d+u;
  const p = total ? Math.round(a / total * 100) : 0;
  const ring = $("breadth-ring");
  if (ring) ring.style.setProperty("--pct", `${p * 3.6}deg`);
  setText("breadth-value", `${p}%`);
  setText("advances", a ? a.toLocaleString("en-IN") : "--");
  setText("declines", d ? d.toLocaleString("en-IN") : "--");
  setText("unchanged", u ? u.toLocaleString("en-IN") : "--");
  setText("pulse-breadth", p >= 60 ? "Healthy" : p >= 45 ? "Balanced" : "Weak");
}

function renderHeatmap(items) {
  const e = $("heatmap"); if (!e) return;
  e.innerHTML = "";
  const rows = [...items].filter(x => Number.isFinite(x.change)).sort((a,b) => Math.abs(b.change)-Math.abs(a.change)).slice(0,25);
  rows.forEach(x => {
    const c = x.change || 0;
    const bg = c > 0 ? "rgba(32,215,122,.24)" : c < 0 ? "rgba(255,79,98,.24)" : "rgba(49,130,255,.14)";
    add(e, `<span>${x.symbol}</span><small>${pct(c)}</small>`, "heat");
    if (e.lastElementChild) e.lastElementChild.style.background = bg;
  });
}

function renderOpportunities(items) {
  const e = $("opportunities"); if (!e) return;
  e.innerHTML = "";
  items.slice().sort((a,b) => (b.score||0)-(a.score||0)).slice(0,5).forEach(x => {
    add(e, `<span>${x.symbol}</span><span class="${x.signal === "SELL" ? "signal-sell" : "signal-buy"}">${x.signal || "--"}</span><span>${Number.isFinite(x.score) ? Math.round(x.score) : "--"}</span><span>${fmt(x.price)}</span>`, "table-row");
  });
  const buys = items.filter(x => x.signal === "BUY").length;
  const sells = items.filter(x => x.signal === "SELL").length;
  const scores = items.map(x => x.score).filter(Number.isFinite);
  const avg = scores.length ? Math.round(scores.reduce((a,b)=>a+b,0)/scores.length) : 0;
  setText("donut-total", items.length);
  setText("summary-buy", buys);
  setText("summary-sell", sells);
  setText("summary-avg", avg);
  const total = Math.max(items.length,1);
  const donut = $("donut"); if (donut) donut.style.setProperty("--buy", `${Math.round(buys/total*360)}deg`);
}

function renderMovers(parentId, items, positive) {
  const e = $(parentId); if (!e) return;
  e.innerHTML = "";
  items.slice().sort((a,b)=>(positive ? b.change-a.change : a.change-b.change)).slice(0,6).forEach(x => {
    add(e, `<span>${x.symbol}</span><span>${fmt(x.price)}</span><span class="${positive ? "green-text" : "red-text"}">${pct(x.change)}</span>`, "mover-row");
  });
}

function renderInstitutional(d) {
  const inst = d?.institutional || d || {};
  const fii = inst?.fii || {};
  const dii = inst?.dii || {};
  const pro = inst?.pro || inst?.participant_pro || inst?.participants?.pro || {};
  const agg = inst?.aggregate || {};

  const n = v => Number.isFinite(Number(v)) ? Number(v) : null;
  const cr = v => {
    const x = n(v);
    return x === null ? "--" : x.toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2});
  };
  const cnt = v => {
    const x = n(v);
    return x === null ? "--" : x.toLocaleString("en-IN");
  };
  const set = (id,v) => {
    const e=$(id);
    if(e)e.textContent=v;
  };
  const net = (id,v) => {
    const e=$(id),x=n(v);
    if(!e)return;
    e.textContent=x===null?"--":`${x>=0?"+":"-"}â‚¹${cr(Math.abs(x))} Cr`;
    setPctClass(e,x);
  };
  const bars = (prefix,buy,sell) => {
    const b=n(buy),s=n(sell),t=(b||0)+(s||0);
    const a=$(prefix+"-buy-bar"),z=$(prefix+"-sell-bar");
    if(a&&z&&t>0){
      a.style.width=(b/t*100)+"%";
      z.style.width=(s/t*100)+"%";
    }
  };

  set("institutional-date",inst?.date?"("+String(inst.date).split("-").reverse().join("-")+")":"--");

  /* HTML already contains BUY / SELL labels */
  set("fii-buy",fii.buy==null?"--":`â‚¹${cr(fii.buy)} Cr`);
  set("fii-sell",fii.sell==null?"--":`â‚¹${cr(fii.sell)} Cr`);
  net("fii-net",fii.net);
  bars("fii",fii.buy,fii.sell);

  set("dii-buy",dii.buy==null?"--":`â‚¹${cr(dii.buy)} Cr`);
  set("dii-sell",dii.sell==null?"--":`â‚¹${cr(dii.sell)} Cr`);
  net("dii-net",dii.net);
  bars("dii",dii.buy,dii.sell);

  set("pro-long",cnt(pro.total_long));
  set("pro-short",cnt(pro.total_short));
  net("pro-net",pro.net_oi);
  bars("pro",pro.total_long,pro.total_short);

  const buy = n(agg.buy)!=null ? agg.buy : (n(inst.buy)!=null ? inst.buy : null);
  const sell = n(agg.sell)!=null ? agg.sell : (n(inst.sell)!=null ? inst.sell : null);
  const turnover = n(agg.turnover)!=null ? agg.turnover : (n(inst.turnover)!=null ? inst.turnover : null);
  const totalNet = n(agg.net)!=null ? agg.net : (n(inst.net)!=null ? inst.net : null);

  set("institutional-turnover",turnover===null?"--":`â‚¹${cr(turnover)} Cr`);
  set("institutional-buy-total",buy===null?"--":`â‚¹${cr(buy)} Cr`);
  set("institutional-sell-total",sell===null?"--":`â‚¹${cr(sell)} Cr`);
  net("institutional-net",totalNet);
  set("institutional-bias",totalNet===null?"--":(totalNet>=0?"NET BUYERS":"NET SELLERS"));

  /* Live PRO fallback: use the production market response when the current payload lacks PRO */
  if(pro.total_long==null && typeof MARKET_URL!=="undefined"){
    fetch(MARKET_URL+"?sv="+Date.now(),{cache:"no-store"})
      .then(x=>x.json())
      .then(x=>{
        const live=x?.institutional;
        if(live?.pro){
          renderInstitutional(live);
        }
      })
      .catch(()=>{});
  }
}
async function fetchDashboardData() {
  const api = window.StockVersityAPI;

  if (!api) {
    return;
  }

  const snapshot = api.getState();

  let marketData = snapshot.market;
  let futuresData = snapshot.futures;

  /* ===== LIVE MARKET FALLBACK ===== */
  if (!marketData || !Array.isArray(marketData.results) || marketData.results.length === 0) {
    try {
      const response = await fetch(
        `${MARKET_URL}?sv=${Date.now()}`,
        { cache: "no-store" }
      );

      if (response.ok) {
        marketData = await response.json();
      }
    } catch (e) {
      console.error("Live market fetch failed:", e);
    }
  }

  if (marketData) {
    const byKey = new Map(
      (marketData.results || []).map(
        x => [x.instrument_key, x]
      )
    );

    const q = key => byKey.get(key) || {};

    const nq = q("NSE_INDEX|Nifty 50");
    const bq = q("NSE_INDEX|Nifty Bank");

    /* ===== HEADER QUOTES - EXTEND EXISTING MARKET RESPONSE ===== */
    const norm = v =>
      String(v ?? "")
        .toUpperCase()
        .replace(/[^A-Z0-9]+/g,"");

    const headerFind = aliases => {
      const wanted = aliases.map(norm);

      for (const item of (marketData.results || [])) {
        const fields = [
          item.instrument_key,
          item.trading_symbol,
          item.exchange_token,
          item.name,
          item.display_name,
          item.symbol
        ].map(norm);

        if (fields.some(v => v && wanted.some(a => a && (v === a || v.includes(a) || a.includes(v))))) {
          return item;
        }
      }

      return {};
    };

    const hVix  = q("NSE_INDEX|India VIX");
    const hGift = headerFind(["GIFT NIFTY","GIFTNIFTY"]);
    const hBtc  = headerFind(["BTC/USD","BTCUSD","BITCOIN"]);
    const hGold = headerFind(["GOLD/USD","GOLDUSD","GOLD"]);

    const headerChange = item => {
      const p = priceOf(item);
      const pc = num(item.previous_close);
      return Number.isFinite(p) && Number.isFinite(pc) && pc > 0
        ? ((p-pc)/pc)*100
        : NaN;
    };

    const paintHeader = (priceId,changeId,item,prefix="") => {
      const p = priceOf(item);
      const c = headerChange(item);

      const pe=document.getElementById(priceId);
      const ce=document.getElementById(changeId);

      if(pe && Number.isFinite(p)){
        pe.textContent=prefix+p.toLocaleString("en-IN",{
          minimumFractionDigits:2,
          maximumFractionDigits:2
        });
      }

      if(ce && Number.isFinite(c)){
        ce.textContent=(c>=0?"+":"")+c.toFixed(2)+"%";
        ce.style.color=c>=0?"#00e69a":"#ff5065";
      }
    };

    paintHeader("nifty-price","nifty-change",nq);
    paintHeader("banknifty-price","banknifty-change",bq);
    paintHeader("vix-price","vix-change",hVix);
    const localHeader = marketData.header || {};

    const finalGift = localHeader.gift || hGift;
    const finalBtc  = localHeader.btc  || hBtc;
    const finalGold = localHeader.gold || hGold;

    paintHeader("gift-price","gift-change",finalGift);
    paintHeader("btc-price","btc-change",finalBtc,"$");
    paintHeader("gold-price","gold-change",finalGold,"$");

    window.__MARKET_STATE = {
      nifty_change:
        Number.isFinite(priceOf(nq)) &&
        Number.isFinite(num(nq.previous_close)) &&
        num(nq.previous_close) > 0
          ? ((priceOf(nq) - num(nq.previous_close)) /
             num(nq.previous_close)) * 100
          : NaN,

      bank_change:
        Number.isFinite(priceOf(bq)) &&
        Number.isFinite(num(bq.previous_close)) &&
        num(bq.previous_close) > 0
          ? ((priceOf(bq) - num(bq.previous_close)) /
             num(bq.previous_close)) * 100
          : NaN
    };

    try {
      updateQuotes(marketData);
      renderInstitutional(marketData.institutional);
    } catch (e) {
      console.error("Quote render failed:", e);
    }

    try {

    } catch (e) {
      console.error("Institutional Flow render failed:", e);
    }
  }

  const futuresRows =
    futuresData
      ? normalizeFutures(futuresData)
      : [];

  try {
    renderDerivedCards(futuresRows);
  } catch (e) {
    console.error("Derived card render failed:", e);
  }
}
function clock() { setText("clock", new Date().toLocaleTimeString("en-IN", {hour12:false})); }
function init() {
  clock(); setInterval(clock,1000);
  fetchDashboardData();
  const refresh = $("refresh-btn"); if (refresh) refresh.onclick = fetchDashboardData;
}
init();
setInterval(() => {
  const t = new Date().toLocaleTimeString("en-IN", {hour12:false, timeZone:"Asia/Kolkata"});
  setText("header-time", `${t} IST`);
}, 1000);

 
// ============================================================
// Institutional Flow - direct live API binding
// ============================================================
async function refreshInstitutionalFlow() {
  try {
    const response = await fetch(
      "https://api.stockversity.in/api/market?institutional_refresh=1",
      { cache: "no-store" }
    );

    if (!response.ok) {
      console.error("Institutional Flow API:", response.status);
      return;
    }

    const market = await response.json();
    const d = market?.institutional;

    if (!d || d.available === false) {
      console.warn("Institutional Flow data unavailable.");
      return;
    }

    const fii = d.fii || {};
    const dii = d.dii || {};

    const number = value => {
      const n = Number(value);
      return Number.isFinite(n) ? n : 0;
    };

    const money = value =>
      number(value).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });

    const set = (id, value) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    };

    const setNet = (id, value) => {
      const element = document.getElementById(id);
      if (!element) return;

      const n = number(value);

      element.textContent =
        (n >= 0 ? "+" : "-") +
        "?" +
        money(Math.abs(n)) +
        " Cr";

      element.classList.remove("green-text", "red-text");

      if (n > 0) {
        element.classList.add("green-text");
      } else if (n < 0) {
        element.classList.add("red-text");
      }
    };

    set("institutional-date", d.date?"("+String(d.date).split("-").reverse().join("-")+")":"--");

    set("fii-buy", "BUY ?" + money(fii.buy) + " Cr");
    set("fii-sell", "SELL ?" + money(fii.sell) + " Cr");

    set("dii-buy", "BUY ?" + money(dii.buy) + " Cr");
    set("dii-sell", "SELL ?" + money(dii.sell) + " Cr");

    setNet("fii-net", fii.net);
    setNet("dii-net", dii.net);
    setNet(
      "institutional-net",
      d.net !== undefined
        ? d.net
        : number(fii.net) + number(dii.net)
    );

    console.log("Institutional Flow updated:", d);

  } catch (error) {
    console.error("Institutional Flow error:", error);
  }
}

refreshInstitutionalFlow();
setInterval(refreshInstitutionalFlow, 60000);


/* ============================================================
   INSTITUTIONAL FLOW RUNTIME LOCK
   Keeps this frozen card independent of future CSS changes.
   ============================================================ */
(function lockInstitutionalFlowCard() {
  function applyInstitutionalLock() {
    const card = document.querySelector(".institutional-flow-card");
    if (!card) return;

    card.style.cssText +=
      ";grid-column:9 / 13 !important;" +
      "grid-row:3 !important;" +
      "width:100% !important;" +
      "min-width:400px !important;" +
      "max-width:none !important;" +
      "justify-self:stretch !important;" +
      "align-self:stretch !important;" +
      "box-sizing:border-box !important;";

    const values = card.querySelectorAll(".flow-values");
    values.forEach(el => {
      el.style.cssText +=
        ";display:grid !important;" +
        "grid-template-columns:1fr 1fr !important;" +
        "gap:24px !important;" +
        "width:100% !important;" +
        "box-sizing:border-box !important;";
    });

    const buySell = card.querySelectorAll(".flow-values span");
    buySell.forEach(el => {
      el.style.cssText +=
        ";min-width:0 !important;" +
        "white-space:nowrap !important;";
    });

    // Rebuild Institutional Flow values with a runtime-generated â‚¹.
    const rupee = String.fromCharCode(8377);

    const netNodes = [
      ["fii-net", window.__SV_LAST_FII_NET],
      ["dii-net", window.__SV_LAST_DII_NET],
      ["institutional-net", window.__SV_LAST_INST_NET]
    ];

    netNodes.forEach(([id, value]) => {
      if (!Number.isFinite(Number(value))) return;
      const n = Number(value);
      const el = document.getElementById(id);
      if (!el) return;

      el.textContent =
        (n >= 0 ? "+" : "-") +
        rupee +
        Math.abs(n).toLocaleString("en-IN", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }) +
        " Cr";
    });
  }

  applyInstitutionalLock();

  const observer = new MutationObserver(applyInstitutionalLock);
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  window.addEventListener(
    "resize",
    applyInstitutionalLock
  );
})();
/* SV AUTHORITATIVE INSTITUTIONAL FLOW */
(function(){
  const INR=String.fromCharCode(8377);
  const root=()=>document.querySelector(".sv-institutional-card");
  const n=v=>{const x=Number(v);return Number.isFinite(x)?x:null};
  const money=v=>{const x=n(v);return x===null?"--":INR+x.toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2})+" Cr"};
  const count=v=>{const x=n(v);return x===null?"--":x.toLocaleString("en-IN")};
  const put=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v};
  const setnet=(id,v)=>{const e=document.getElementById(id),x=n(v);if(!e)return;e.textContent=x===null?"--":(x>=0?"+":"-")+INR+Math.abs(x).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2})+" Cr";if(typeof setPctClass==="function")setPctClass(e,x)};
  const bars=(p,b,s)=>{const x=n(b)||0,y=n(s)||0,t=x+y;if(!t)return;const bp=(x/t*100),sp=(y/t*100);const a=document.getElementById(p+"-buy-bar"),z=document.getElementById(p+"-sell-bar");if(a){a.style.width=bp+"%";a.innerHTML="<span>"+bp.toFixed(0)+"%</span>";}if(z){z.style.width=sp+"%";z.innerHTML="<span>"+sp.toFixed(0)+"%</span>";}};

  async function render(){
    try{
      const r=await fetch("https://api.stockversity.in/api/market?sv="+Date.now(),{cache:"no-store"});
      const payload=await r.json();
      const i=payload&&payload.institutional;
      if(!i)return;

      const f=i.fii||{},d=i.dii||{},p=i.pro||i.participant_pro||{};
      const a=i.aggregate||i.aggregates||i.totals||{};

      const sub=document.querySelector(".sv-institutional-card .sv-if-subtitle");
      if(sub)sub.textContent="FII â€¢ DII â€¢ PRO";

      { const fx=Number(f.net); const fp=document.getElementById("fii-net-pct"); if(fp){fp.textContent=Number.isFinite(fx)?((fx>=0?"â–² +":"â–¼ -")+Math.abs(fx/(Number(f.buy)+Number(f.sell))*100).toFixed(1)+"%"):"--"; fp.className="sv-if-net-pct "+(fx>=0?"positive":"negative");} }
      { const dx=Number(d.net); const dp=document.getElementById("dii-net-pct"); if(dp){dp.textContent=Number.isFinite(dx)?((dx>=0?"â–² +":"â–¼ -")+Math.abs(dx/(Number(d.buy)+Number(d.sell))*100).toFixed(1)+"%"):"--"; dp.className="sv-if-net-pct "+(dx>=0?"positive":"negative");} }
      { const px=Number(p.net_oi); const pp=document.getElementById("pro-net-pct"); if(pp){pp.textContent=Number.isFinite(px)?((px>=0?"â–² +":"â–¼ -")+Math.abs(px/(Number(p.total_long)+Number(p.total_short))*100).toFixed(1)+"%"):"--"; pp.className="sv-if-net-pct "+(px>=0?"positive":"negative"); pp.style.setProperty("color",px>=0?"#00e69a":"#ff5065","important");} }
      put("fii-buy",money(f.buy));
      put("fii-sell",money(f.sell));
      setnet("fii-net",f.net);
      bars("fii",f.buy,f.sell);
      { const t=(n(f.buy)||0)+(n(f.sell)||0); put("fii-buy-pct",t?(n(f.buy)/t*100).toFixed(1)+"%":"--"); put("fii-sell-pct",t?(n(f.sell)/t*100).toFixed(1)+"%":"--"); put("fii-net-bottom",f.net==null?"--":((n(f.net)>=0?"+":"-")+INR+Math.abs(n(f.net)).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2})+" Cr")); }
      { const t=(n(d.buy)||0)+(n(d.sell)||0); put("dii-buy-pct",t?(n(d.buy)/t*100).toFixed(1)+"%":"--"); put("dii-sell-pct",t?(n(d.sell)/t*100).toFixed(1)+"%":"--"); put("dii-net-bottom",d.net==null?"--":((n(d.net)>=0?"+":"-")+INR+Math.abs(n(d.net)).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2})+" Cr")); }
      { const t=(n(p.total_long)||0)+(n(p.total_short)||0); put("pro-buy-pct",t?(n(p.total_long)/t*100).toFixed(1)+"%":"--"); put("pro-sell-pct",t?(n(p.total_short)/t*100).toFixed(1)+"%":"--"); put("pro-net-bottom",n(p.net_oi)==null?"--":((n(p.net_oi)>=0?"+":"")+count(Math.abs(n(p.net_oi))))); { const e=document.getElementById("pro-net-bottom"),x=n(p.net_oi); if(e){e.style.setProperty("color",x>=0?"#00e69a":"#ff5065","important");} } }

      put("dii-buy",money(d.buy));
      put("dii-sell",money(d.sell));
      setnet("dii-net",d.net);
      bars("dii",d.buy,d.sell);

      put("pro-long",count(p.total_long));
      put("pro-short",count(p.total_short));
      put("pro-net",n(p.net_oi)===null?"--":(n(p.net_oi)>=0?"+":"")+count(Math.abs(n(p.net_oi))));
      bars("pro",p.total_long,p.total_short);

      const fiiNote=document.querySelector(".sv-if-note-fii div"); if(fiiNote) fiiNote.innerHTML=(n(f.net)||0)>=0?"FII turned net buyers today<br><small>with higher cash inflows.</small>":"FII turned net sellers today<br><small>with slightly higher selling.</small>";
      const diiNote=document.querySelector(".sv-if-note-dii div"); if(diiNote) diiNote.innerHTML=(n(d.net)||0)>=0?"DII remained net buyers<br><small>for the session.</small>":"DII turned net sellers<br><small>for the session.</small>";
      const proNote=document.querySelector(".sv-if-note-pro div"); if(proNote) proNote.innerHTML=(n(p.net_oi)||0)>=0?"Proprietary traders<br><small>show a bullish OI bias.</small>":"Proprietary traders<br><small>show a bearish OI bias.</small>";
      const biasText=document.getElementById("institutional-bias");
      if(biasText) biasText.textContent=((n(f.net)||0)+(n(d.net)||0))>=0?"Overall, institutions are net buyers today (FII + DII).":"Overall, institutions are net sellers today (FII + DII).";
            const buy=n(a.buy)!==null?a.buy:(n(f.buy)||0)+(n(d.buy)||0);
      const sell=n(a.sell)!==null?a.sell:(n(f.sell)||0)+(n(d.sell)||0);
      const turnover=n(a.turnover)!==null?a.turnover:buy+sell;
      const totalNet=n(a.net)!==null?a.net:(n(f.net)||0)+(n(d.net)||0);

      put("institutional-turnover",money(turnover));
      put("institutional-buy-total",money(buy));
      put("institutional-sell-total",money(sell));
      setnet("institutional-net",totalNet);

/* NET INSTITUTIONAL FLOW percentage */
{
  const netPctEl=document.getElementById("institutional-net-pct");
  if(netPctEl){
    let pct=null;

    if(n(a.net_pct)!=null) pct=n(a.net_pct);
    else if(n(a.net_percentage)!=null) pct=n(a.net_percentage);
    else if(n(a.net_change_pct)!=null) pct=n(a.net_change_pct);
    else if(n(a.change_pct)!=null) pct=n(a.change_pct);
    else if(n(a.netPercent)!=null) pct=n(a.netPercent);


    netPctEl.textContent=
      pct==null
        ? "--"
        : (pct>=0 ? "â–² +" : "â–¼ -")+Math.abs(pct).toFixed(1)+"%";

    netPctEl.style.setProperty(
      "color",
      pct==null ? "#82a8c7" : (pct>=0 ? "#00e69a" : "#ff5065"),
      "important"
    );
  }
}

      const bias=document.getElementById("institutional-bias");
      if(bias)bias.textContent=n(totalNet)===null?"--":(n(totalNet)>=0?"NET BUYERS":"NET SELLERS");

      const bp=document.getElementById("institutional-buy-pct");
      const sp=document.getElementById("institutional-sell-pct");
      const bn=n(buy)||0,sn=n(sell)||0,tt=bn+sn;
      if(bp)bp.textContent=tt?(bn/tt*100).toFixed(1)+"%":"--";
      if(sp)sp.textContent=tt?(sn/tt*100).toFixed(1)+"%":"--";
    }catch(e){
      console.error("SV AUTHORITATIVE INSTITUTIONAL FLOW",e);
    }
  }

  render();
  setInterval(render,1000);
  window.addEventListener("load",render);
})();
/* SV FINAL PRO FORMAT + BUY SELL TOTALS */
(function(){
  if(window.__SV_FINAL_IF_FIX)return;
  window.__SV_FINAL_IF_FIX=true;

  const INR=String.fromCharCode(8377);
  const n=v=>{const x=Number(v);return Number.isFinite(x)?x:null};
  const cr=v=>{const x=n(v);return x===null?"--":x.toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2})};
  const cnt=v=>{const x=n(v);return x===null?"--":x.toLocaleString("en-IN")};
  const put=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v};
  const proNet=v=>{
    const e=document.getElementById("pro-net"),x=n(v);
    if(e){
      e.textContent=x===null?"--":(x>=0?"+":"-")+cnt(Math.abs(x));
      e.style.setProperty("color",x===null?"":(x>=0?"#00e69a":"#ff5065"),"important");
    }
  };

  async function fix(){
    try{
      const r=await fetch("https://api.stockversity.in/api/market?sv="+Date.now(),{cache:"no-store"});
      const j=await r.json();
      const i=j?.institutional||{};
      const f=i?.fii||{};
      const d=i?.dii||{};
      const p=i?.pro||i?.participant_pro||{};

      const fb=n(f.buy),fs=n(f.sell),db=n(d.buy),ds=n(d.sell);

      /* PRO is OI/contracts, NOT Cr */
      put("pro-long",cnt(p.total_long));
      put("pro-short",cnt(p.total_short));
      proNet(p.net_oi);

      /* Existing HTML labels already say BUY / SELL */
      put("fii-buy",fb===null?"--":INR+cr(fb)+" Cr");
      put("fii-sell",fs===null?"--":INR+cr(fs)+" Cr");
      put("dii-buy",db===null?"--":INR+cr(db)+" Cr");
      put("dii-sell",ds===null?"--":INR+cr(ds)+" Cr");

      /* FII + DII cash totals */
      if(fb!==null && db!==null){
        const totalBuy=fb+db;
        put("institutional-buy-total",INR+cr(totalBuy)+" Cr");
      }
      if(fs!==null && ds!==null){
        const totalSell=fs+ds;
        put("institutional-sell-total",INR+cr(totalSell)+" Cr");
      }
      if(fb!==null && fs!==null && db!==null && ds!==null){
        const totalBuy=fb+db;
        const totalSell=fs+ds;
        put("institutional-turnover",INR+cr(totalBuy+totalSell)+" Cr");

        const bp=document.getElementById("institutional-buy-pct");
        const sp=document.getElementById("institutional-sell-pct");
        const total=totalBuy+totalSell;
        if(bp)bp.textContent=(totalBuy/total*100).toFixed(1)+"%";
        if(sp)sp.textContent=(totalSell/total*100).toFixed(1)+"%";
      }

      const sub=document.querySelector(".sv-institutional-card .sv-if-subtitle");
      if(sub)sub.innerHTML="FII &bull; DII &bull; PRO";
    }catch(e){
      console.error("SV FINAL PRO FORMAT",e);
    }
  }

  fix();
  setInterval(fix,1000);
})();



/* =========================================================
   LOCAL MARKET DIRECT BIND
   Uses the confirmed desktop live-market bridge.
   ========================================================= */

(function(){
  const LOCAL_MARKET_URL = "/api/market";

  function n(v){
    const x = Number(v);
    return Number.isFinite(x) ? x : NaN;
  }

  function put(id, value, prefix=""){
    const el = document.getElementById(id);
    if(!el || !Number.isFinite(value)) return;

    el.textContent = prefix + value.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function change(price, previous){
    price = n(price);
    previous = n(previous);

    if(!Number.isFinite(price) || !Number.isFinite(previous) || previous <= 0){
      return NaN;
    }

    return ((price - previous) / previous) * 100;
  }

  function putChange(id, absolute, percent){
    const el = document.getElementById(id);
    if(!el) return;

    absolute = n(absolute);
    percent = n(percent);

    if(!Number.isFinite(absolute) && !Number.isFinite(percent)) return;

    const absoluteText = Number.isFinite(absolute)
      ? (absolute >= 0 ? "+" : "") + absolute.toFixed(2)
      : "";

    const percentText = Number.isFinite(percent)
      ? (percent >= 0 ? "+" : "") + percent.toFixed(2) + "%"
      : "";

    el.textContent = percentText
      ? absoluteText + "(" + percentText + ")"
      : absoluteText;

    const positive = Number.isFinite(percent)
      ? percent >= 0
      : absolute >= 0;

    el.style.color = positive ? "#00e69a" : "#ff5065";
  }
async function refreshLocalMarket(){
    try{
      const response = await fetch(
        LOCAL_MARKET_URL + "?sv=" + Date.now(),
        {cache:"no-store"}
      );

      if(!response.ok) return;

      const payload = await response.json();

      const rows = Array.isArray(payload?.results)
        ? payload.results
        : [];

      const normalize = value =>
        String(value || "")
          .trim()
          .toUpperCase()
          .replace(/:/g, "|");

      const find = key =>
        rows.find(x =>
          normalize(x?.instrument_key) === normalize(key)
        ) || {};

      const valueOf = row =>
        n(row?.ltp ?? row?.last_price ?? row?.price ?? row?.value);

      const absoluteChangeOf = row => {
        const direct = n(row?.change);
        if(Number.isFinite(direct)) return direct;

        const price = valueOf(row);
        const previous = n(row?.previous_close);

        if(
          Number.isFinite(price) &&
          Number.isFinite(previous)
        ){
          return price - previous;
        }

        return NaN;
      };

      const installHeaderMarketStyle = () => {
        if(document.getElementById("sv-header-market-style")) return;

        const style = document.createElement("style");
        style.id = "sv-header-market-style";

        style.textContent = `
          #nifty-price,
          #banknifty-price,
          #vix-price,
          #gift-price,
          #btc-price,
          #gold-price {
            font-size: 18px !important;
            line-height: 1.08 !important;
            font-weight: 800 !important;
          }

          #nifty-change,
          #banknifty-change,
          #vix-change,
          #gift-change,
          #btc-change,
          #gold-change {
            font-size: 14px !important;
            line-height: 1.15 !important;
            font-weight: 800 !important;
            white-space: nowrap !important;
          }

          .quote-card.sv-market-closed {
            opacity: 0.45 !important;
            filter: saturate(0.55) !important;
          }

          .quote-card.sv-market-closed .quote-name,
          .quote-card.sv-market-closed .quote-price,
          .quote-card.sv-market-closed .quote-change {
            opacity: 0.75 !important;
          }
        `;

        document.head.appendChild(style);
      };

      const setMarketClosed = (id, closed) => {
        const el = document.getElementById(id);
        const card = el?.closest(".quote-card");

        if(card){
          card.classList.toggle("sv-market-closed", Boolean(closed));
        }
      };

      const NSE_HOLIDAYS_2026 = new Set([
        "2026-01-26",
        "2026-03-03",
        "2026-03-26",
        "2026-03-31",
        "2026-04-03",
        "2026-04-14",
        "2026-05-01",
        "2026-05-28",
        "2026-06-26",
        "2026-08-26",
        "2026-09-14",
        "2026-10-02",
        "2026-10-20",
        "2026-11-10",
        "2026-11-24",
        "2026-12-25"
      ]);

      const indiaDateKey = () => {
        const parts = new Intl.DateTimeFormat("en-CA", {
          timeZone: "Asia/Kolkata",
          year: "numeric",
          month: "2-digit",
          day: "2-digit"
        }).formatToParts(new Date());

        const y = parts.find(x => x.type === "year")?.value;
        const m = parts.find(x => x.type === "month")?.value;
        const d = parts.find(x => x.type === "day")?.value;

        return `${y}-${m}-${d}`;
      };

      const indiaWeekday = () => {
        const parts = new Intl.DateTimeFormat("en-IN", {
          timeZone: "Asia/Kolkata",
          weekday: "short"
        }).formatToParts(new Date());

        return parts.find(x => x.type === "weekday")?.value;
      };

      const isNseCashClosed = () => {
        const dateKey = indiaDateKey();
        const weekday = indiaWeekday();

        if(
          weekday === "Sat" ||
          weekday === "Sun"
        ){
          return true;
        }

        if(NSE_HOLIDAYS_2026.has(dateKey)){
          return true;
        }

        const parts = new Intl.DateTimeFormat("en-IN", {
          timeZone: "Asia/Kolkata",
          hour: "2-digit",
          minute: "2-digit",
          hourCycle: "h23"
        }).formatToParts(new Date());

        const hour = Number(
          parts.find(x => x.type === "hour")?.value
        );

        const minute = Number(
          parts.find(x => x.type === "minute")?.value
        );

        const total = hour * 60 + minute;

        return total < 555 || total > 930;
      };

      const isGoldClosed = () => {
        const weekday = indiaWeekday();

        return (
          weekday === "Sat" ||
          weekday === "Sun"
        );
      };

      installHeaderMarketStyle();
      const changeOf = row => {
        const direct = n(row?.change_percent);
        if(Number.isFinite(direct)) return direct;

        return change(
          valueOf(row),
          row?.previous_close
        );
      };

      const nifty = find("NSE_INDEX|NIFTY 50");
      const bank = find("NSE_INDEX|NIFTY BANK");
      const vix = find("NSE_INDEX|INDIA VIX");
      const gift = find("GLOBAL_INDEX|SGX NIFTY");
      const btc = rows.find(x =>
        String(x?.key || "").toUpperCase() === "BTC"
      ) || {};
      const gold = rows.find(x =>
        String(x?.key || "").toUpperCase() === "GOLD"
      ) || {};

      put("nifty-price", valueOf(nifty));
      putChange("nifty-change", absoluteChangeOf(nifty), changeOf(nifty));

      put("banknifty-price", valueOf(bank));
      putChange("banknifty-change", absoluteChangeOf(bank), changeOf(bank));

      put("vix-price", valueOf(vix));
      putChange("vix-change", absoluteChangeOf(vix), changeOf(vix));

      put("gift-price", valueOf(gift));
      putChange("gift-change", absoluteChangeOf(gift), changeOf(gift));

      const btcPrice = valueOf(btc);
      const goldPrice = valueOf(gold);

      put("btc-price", btcPrice, "");
      putChange("btc-change", absoluteChangeOf(btc), changeOf(btc));

      put("gold-price", goldPrice, "");
      putChange("gold-change", absoluteChangeOf(gold), changeOf(gold));

      const nseOpen = isNseCashOpen();

      setMarketClosed("nifty-price", !nseOpen);
      setMarketClosed("banknifty-price", !nseOpen);
      setMarketClosed("vix-price", !nseOpen);
      const nseClosed = isNseCashClosed();
      const goldClosed = isGoldClosed();

      setMarketClosed("nifty-price", nseClosed);
      setMarketClosed("banknifty-price", nseClosed);
      setMarketClosed("vix-price", nseClosed);
      setMarketClosed("gold-price", goldClosed);
      console.log(
        "[LOCAL MARKET DIRECT BIND]",
        "NIFTY=", valueOf(nifty),
        "BANKNIFTY=", valueOf(bank),
        "VIX=", valueOf(vix),
        "GIFT=", valueOf(gift),
        "BTC=", btcPrice,
        "GOLD=", goldPrice
      );

    }catch(error){
      console.error("[LOCAL MARKET DIRECT BIND]", error);
    }
  }
  refreshLocalMarket();
  window.setInterval(refreshLocalMarket, 3000);
})();

// ============================================================
// STOCKVERSITY DAILY MARKET FOCUS
// Mirrors the frozen desktop Daily Message Engine.
// One deterministic message for the entire India calendar day.
// ============================================================
(function(){
  const dailyMessages = [
    ["Trade the setup,<br>not the emotion.","Stay disciplined. Protect capital and wait for high-quality opportunities."],
    ["Patience is a<br>trading edge.","Wait for confirmation. Let the market come to your setup."],
    ["Protect capital<br>before chasing profit.","Small losses are acceptable. Large uncontrolled losses are not."],
    ["Follow your plan,<br>not the noise.","Avoid emotional trades and focus only on high-quality setups."],
    ["Quality trades<br>beat more trades.","Trade selectively. One excellent setup is better than many mediocre ones."],
    ["Let winners run,<br>cut losers early.","Respect your stop-loss and give strong trades room to develop."],
    ["Risk first.<br>Reward second.","Know your risk before entering and demand a worthwhile reward."],
    ["No setup?<br>No trade.","Cash is a position. Wait patiently until the market offers an edge."],
    ["Trade with<br>confidence, not urgency.","A missed trade is better than a forced trade."],
    ["Consistency creates<br>the edge.","Follow the process every day and let disciplined execution compound."],
    ["Wait for the<br>high-quality breakout.","Volume, structure and confirmation should support the move."],
    ["The market rewards<br>patience.","Do not chase candles. Let price come to your planned entry."],
    ["Control risk.<br>Control emotions.","Your first job is to protect trading capital."],
    ["Plan the trade.<br>Trade the plan.","Define entry, stop-loss and target before taking the position."]
  ];
  function updateDailyMarketFocus(){
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Kolkata",
      year: "numeric",
      month: "2-digit",
      day: "2-digit"
    }).formatToParts(new Date());
    const year = Number(parts.find(x => x.type === "year")?.value);
    const month = Number(parts.find(x => x.type === "month")?.value);
    const day = Number(parts.find(x => x.type === "day")?.value);
    const indiaDate = new Date(Date.UTC(year, month - 1, day));
    const ordinal = Math.floor(indiaDate.getTime() / 86400000) + 719163;
    const index = ordinal % dailyMessages.length;
    const message = dailyMessages[index];
    if(!message) return;
    const quote = document.querySelector(".focus-quote");
    const copy = document.querySelector(".focus-copy");
    if(quote){
      quote.innerHTML =
        '<span class="quote-mark">&#8220;</span><div>' +
        message[0] +
        '</div>';
    }
    if(copy){
      copy.textContent = message[1];
    }
  }
  updateDailyMarketFocus();
})();


/* ============================================================
   STOCKVERSITY
   INTRADAY SCANNER > FUTURES & OPTIONS
   SINGLE AUTHORITATIVE IMPLEMENTATION

   Columns:
   TIME | STOCK | LTP | SCORE | ENTRY | SL | TARGET | RR | ACTION
   ============================================================ */

(() => {
  "use strict";

  const FO_PAGE_ID = "sv-futures-page";

  const get = id => document.getElementById(id);

  const number = (...values) => {
    for (const value of values) {
      const n = Number(value);
      if (Number.isFinite(n)) return n;
    }
    return NaN;
  };

  const money = value => {
    const n = Number(value);
    if (!Number.isFinite(n)) return "--";

    return n.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const score = value => {
    const n = Number(value);
    return Number.isFinite(n) ? n.toFixed(0) : "--";
  };

  const rr = value => {
    const n = Number(value);
    return Number.isFinite(n) ? n.toFixed(2) : "--";
  };

  function buildFuturesPage() {
    let page = get(FO_PAGE_ID);

    if (page) return page;

    page = document.createElement("section");
    page.id = FO_PAGE_ID;

    page.innerHTML = `
      <div class="sv-fo-page-header">
        <div>
          <h1>Futures &amp; Options</h1>
          <p>Intraday Scanner · NSE Stock Futures · Elite A1 Setups</p>
        </div>

        <div class="sv-fo-page-status">
          <span class="sv-fo-status-dot"></span>
          <span id="sv-fo-status">READY</span>
          <button id="sv-fo-refresh" type="button">REFRESH</button>
        </div>
      </div>

      <div class="sv-fo-rules">
        <span>SCORE ≥ 90</span>
        <span>5 MIN</span>
        <span>VWAP</span>
        <span>ATR RISK</span>
        <span>ELITE A1 ONLY</span>
        <span>MAX 10 SETUPS</span>
      </div>

      <div class="sv-fo-card">
        <div class="sv-fo-card-head">
          <div>
            <strong>Intraday Futures A1 Setups</strong>
            <small id="sv-fo-count">0 setups</small>
          </div>
          <span id="sv-fo-date"></span>
        </div>

        <div class="sv-fo-table-wrap">
          <table class="sv-fo-table">
            <thead>
              <tr>
                <th>TIME</th>
                <th>STOCK</th>
                <th>LTP</th>
                <th>SCORE</th>
                <th>ENTRY</th>
                <th>SL</th>
                <th>TARGET</th>
                <th>RR</th>
                <th>ACTION</th>
              </tr>
            </thead>

            <tbody id="sv-fo-body">
              <tr>
                <td colspan="9" class="sv-fo-empty">
                  Loading A1 futures setups...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    const main = document.querySelector(".main-area");

    if (!main) return null;

    main.appendChild(page);

    get("sv-fo-refresh")?.addEventListener(
      "click",
      loadFuturesPage
    );

    return page;
  }

  function hideDashboard() {
    document
      .querySelectorAll(".main-area > *")
      .forEach(element => {
        if (
          !element.classList.contains("main-header") &&
          element.id !== FO_PAGE_ID
        ) {
          element.style.display = "none";
        }
      });
  }

  function showFuturesPage() {
    const page = buildFuturesPage();

    if (!page) return;

    hideDashboard();

    page.style.display = "block";

    loadFuturesPage();
  }

  function renderFuturesPage(rows) {
    const body = get("sv-fo-body");
    const status = get("sv-fo-status");
    const count = get("sv-fo-count");

    if (!body) return;

    if (!rows.length) {
      body.innerHTML = `
        <tr>
          <td colspan="9" class="sv-fo-empty">
            NO A1 FUTURES SETUPS
          </td>
        </tr>
      `;

      if (count) count.textContent = "0 setups";
      if (status) status.textContent = "LIVE";

      return;
    }

    body.innerHTML = rows
      .slice()
      .sort(
        (a, b) =>
          (Number(b.score) || 0) -
          (Number(a.score) || 0)
      )
      .slice(0, 10)
      .map(row => {
        const action = String(
          row.action ||
          row.signal ||
          row.side ||
          ""
        ).toUpperCase();

        const actionClass =
          action.includes("BUY")
            ? "sv-fo-buy"
            : action.includes("SELL")
              ? "sv-fo-sell"
              : "";

        return `
          <tr>
            <td>${row.time || "--"}</td>

            <td class="sv-fo-stock">
              ${row.symbol ||
                row.trading_symbol ||
                row.name ||
                "--"}
            </td>

            <td>${money(
              row.ltp ??
              row.price ??
              row.last_price ??
              row.last_traded_price
            )}</td>

            <td class="sv-fo-score">
              ${score(
                row.score ??
                row.confidence ??
                row.opportunity_score
              )}
            </td>

            <td>${money(
              row.entry ??
              row.entry_price ??
              row.entryPrice
            )}</td>

            <td>${money(
              row.sl ??
              row.stop_loss ??
              row.stopLoss ??
              row.stop_loss_price
            )}</td>

            <td>${money(
              row.target ??
              row.target_price ??
              row.targetPrice
            )}</td>

            <td>${rr(
              row.rr ??
              row.risk_reward ??
              row.risk_reward_ratio
            )}</td>

            <td>
              <span class="sv-fo-action ${actionClass}">
                ${action || "--"}
              </span>
            </td>
          </tr>
        `;
      })
      .join("");

    if (count) {
      count.textContent =
        `${Math.min(rows.length, 10)} setup${Math.min(rows.length, 10) === 1 ? "" : "s"}`;
    }

    if (status) status.textContent = "LIVE";
  }

  async function loadFuturesPage() {
    const page = buildFuturesPage();

    if (!page) return;

    const status = get("sv-fo-status");

    if (status) status.textContent = "SCANNING...";

    try {
      const response = await fetch(
        `${FUTURES_URL}?sv=${Date.now()}`,
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error(
          `Futures API HTTP ${response.status}`
        );
      }

      const payload = await response.json();

      const rows =
        Array.isArray(payload?.results)
          ? payload.results
          : [];

      renderFuturesPage(rows);

      const date = get("sv-fo-date");

      if (date) {
        date.textContent =
          new Date().toLocaleDateString(
            "en-IN",
            {
              day: "2-digit",
              month: "short",
              year: "numeric"
            }
          );
      }

    } catch (error) {
      console.error(
        "StockVersity Futures & Options:",
        error
      );

      const body = get("sv-fo-body");

      if (body) {
        body.innerHTML = `
          <tr>
            <td colspan="9" class="sv-fo-empty">
              FUTURES DATA TEMPORARILY UNAVAILABLE
            </td>
          </tr>
        `;
      }

      if (status) status.textContent = "OFFLINE";
    }
  }

  /*
   * Intraday Scanner parent:
   * only expands/collapses its child.
   */
  get("sv-intraday-scanner")?.addEventListener(
    "click",
    event => {
      event.preventDefault();

      const children = get("sv-intraday-children");
      const plus = get("sv-intraday-plus");

      if (!children) return;

      const open =
        children.classList.toggle("open");

      if (plus) {
        plus.textContent = open ? "âˆ’" : "+";
      }
    }
  );

  /*
   * Actual child page.
   */
  get("sv-intraday-futures")?.addEventListener(
    "click",
    event => {
      event.preventDefault();
      event.stopPropagation();

      document
        .querySelectorAll(".frozen-nav-item")
        .forEach(item =>
          item.classList.remove("active")
        );

      get("sv-intraday-scanner")
        ?.classList.add("active");

      get("sv-intraday-futures")
        ?.classList.add("active");

      showFuturesPage();
    }
  );

  const style = document.createElement("style");

  style.textContent = `
    #${FO_PAGE_ID}{
      display:none;
      width:100%;
      min-height:calc(100vh - 109px);
      box-sizing:border-box;
      padding:14px;
      overflow:auto;
      color:var(--text);
    }

    #${FO_PAGE_ID} .sv-fo-page-header{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:20px;
      margin-bottom:12px;
    }

    #${FO_PAGE_ID} h1{
      margin:0;
      font-size:24px;
      font-weight:800;
    }

    #${FO_PAGE_ID} p{
      margin:4px 0 0;
      color:var(--muted);
      font-size:11px;
    }

    #${FO_PAGE_ID} .sv-fo-page-status{
      display:flex;
      align-items:center;
      gap:8px;
      font-size:9px;
      font-weight:800;
    }

    #${FO_PAGE_ID} .sv-fo-status-dot{
      width:8px;
      height:8px;
      border-radius:50%;
      background:var(--green);
      box-shadow:0 0 8px rgba(32,215,122,.55);
    }

    #${FO_PAGE_ID} #sv-fo-refresh{
      border:1px solid var(--border);
      border-radius:6px;
      background:#0a1726;
      color:var(--text);
      padding:6px 10px;
      font-size:9px;
      font-weight:800;
      cursor:pointer;
    }

    #${FO_PAGE_ID} .sv-fo-rules{
      display:flex;
      gap:7px;
      flex-wrap:wrap;
      margin-bottom:10px;
    }

    #${FO_PAGE_ID} .sv-fo-rules span{
      background:var(--row);
      border:1px solid var(--border-soft);
      border-radius:5px;
      padding:6px 9px;
      color:var(--muted);
      font-size:9px;
      font-weight:800;
    }

    #${FO_PAGE_ID} .sv-fo-card{
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:9px;
      overflow:hidden;
    }

    #${FO_PAGE_ID} .sv-fo-card-head{
      display:flex;
      align-items:center;
      justify-content:space-between;
      padding:12px 14px;
      border-bottom:1px solid var(--border);
    }

    #${FO_PAGE_ID} .sv-fo-card-head strong{
      font-size:14px;
      font-weight:800;
    }

    #${FO_PAGE_ID} .sv-fo-card-head small{
      display:block;
      margin-top:3px;
      color:var(--muted);
      font-size:9px;
    }

    #${FO_PAGE_ID} .sv-fo-table-wrap{
      width:100%;
      overflow:auto;
    }

    #${FO_PAGE_ID} .sv-fo-table{
      width:100%;
      min-width:900px;
      border-collapse:collapse;
      font-size:11px;
    }

    #${FO_PAGE_ID} .sv-fo-table th{
      padding:10px 9px;
      background:#0d1f32;
      color:#bfd0e3;
      border-bottom:1px solid var(--border);
      text-align:center;
      font-size:9px;
      font-weight:800;
      white-space:nowrap;
    }

    #${FO_PAGE_ID} .sv-fo-table td{
      padding:11px 9px;
      border-bottom:1px solid var(--border-soft);
      white-space:nowrap;
      text-align:center;
    }

    #${FO_PAGE_ID} .sv-fo-table tbody tr:hover{
      background:#0d2034;
    }

    #${FO_PAGE_ID} .sv-fo-stock{
      font-weight:800;
      text-align:left !important;
    }

    #${FO_PAGE_ID} .sv-fo-score{
      font-weight:900;
    }

    #${FO_PAGE_ID} .sv-fo-action{
      display:inline-block;
      min-width:65px;
      padding:4px 7px;
      border-radius:5px;
      font-size:9px;
      font-weight:900;
    }

    #${FO_PAGE_ID} .sv-fo-buy{
      color:var(--green);
      background:rgba(32,215,122,.09);
    }

    #${FO_PAGE_ID} .sv-fo-sell{
      color:var(--red);
      background:rgba(255,79,98,.09);
    }

    #${FO_PAGE_ID} .sv-fo-empty{
      padding:32px !important;
      color:var(--muted);
      font-weight:700;
      text-align:center !important;
    }
  `;

  document.head.appendChild(style);

})();

/* ============================================================
   STOCKVERSITY â€” FINAL F&O MENU STRUCTURE
   MAIN Future & Options = separate main page
   Intraday Scanner > Futures & Options = separate intraday page
   ============================================================ */
(() => {
  "use strict";

  const MAIN_TEXT = "future & options";
  const SCANNER_TEXT = "intraday scanner";
  const CHILD_ID = "sv-final-intraday-fo-child";
  const PAGE_ID = "sv-final-intraday-fo-page";

  const text = el =>
    (el?.textContent || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();

  const nav = () =>
    document.querySelector(".frozen-nav");

  const getScanner = () =>
    [...document.querySelectorAll(".frozen-nav-item")]
      .find(el => text(el) === SCANNER_TEXT);

  /* ------------------------------------------------------------
     REMOVE OLD INCORRECT DYNAMIC CHILD
     ------------------------------------------------------------ */
  function removeOldChildren() {
    [
      "sv-real-intraday-fo-child",
      "sv-intraday-futures",
      "sv-final-intraday-fo-child"
    ].forEach(id => {
      const el = document.getElementById(id);
      if (el && id !== CHILD_ID) el.remove();
    });

    document
      .querySelectorAll(
        ".sv-fo-real-child, .sv-intraday-child"
      )
      .forEach(el => {
        if (el.id !== CHILD_ID) el.remove();
      });

    document
      .querySelectorAll(".sv-fo-child-short")
      .forEach(el => {
        el.closest(".frozen-nav-item")?.remove();
      });
  }

  /* ------------------------------------------------------------
     RESTORE ORIGINAL MAIN-MENU Future & Options
     ------------------------------------------------------------ */
  function restoreMainFO() {
    const n = nav();
    if (!n) return null;

    const existing = [...n.children]
      .find(el =>
        el.classList?.contains("frozen-nav-item") &&
        text(el) === MAIN_TEXT
      );

    if (existing) return existing;

    const mainFO = document.createElement("button");

    mainFO.type = "button";
    mainFO.className = "frozen-nav-item frozen-expand";

    mainFO.innerHTML = `
      <span class="frozen-nav-icon">â–¥</span>
      <span>Future &amp; Options</span>
      <b>+</b>
    `;

    const stocks = [...n.children]
      .find(el =>
        el.classList?.contains("frozen-nav-item") &&
        text(el) === "stocks"
      );

    if (stocks) {
      stocks.insertAdjacentElement("afterend", mainFO);
    } else {
      n.appendChild(mainFO);
    }

    return mainFO;
  }

  /* ------------------------------------------------------------
     CREATE NEW Intraday Scanner > Futures & Options
     ------------------------------------------------------------ */
  function createChild() {
    const scanner = getScanner();
    if (!scanner) return null;

    let child = document.getElementById(CHILD_ID);

    if (child) return child;

    child = document.createElement("button");

    child.type = "button";
    child.id = CHILD_ID;
    child.className = "frozen-nav-item";

    child.innerHTML = `
      <span class="frozen-nav-icon">â–¥</span>
      <span>Futures &amp; Options</span>
    `;

    child.style.cssText += `
      padding-left:42px !important;
      min-height:33px !important;
      gap:7px !important;
      border-radius:8px !important;
      font-size:12px !important;
      font-weight:700 !important;
    `;

    scanner.insertAdjacentElement("afterend", child);

    return child;
  }

  /* ------------------------------------------------------------
     INTRADAY F&O PAGE
     ------------------------------------------------------------ */
  function buildPage() {
    let page = document.getElementById(PAGE_ID);

    if (page) return page;

    const main =
      document.querySelector(".main-area") ||
      document.querySelector("main");

    if (!main) return null;

    page = document.createElement("section");
    page.id = PAGE_ID;

    page.style.cssText = `
      display:none;
      padding:24px;
      min-height:calc(100vh - 90px);
      box-sizing:border-box;
    `;

    page.innerHTML = `
      <div style="
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:16px;
      ">
        <div>
          <div style="
            color:#F0F4FB;
            font-size:24px;
            font-weight:800;
          ">
            Futures &amp; Options
          </div>

          <div style="
            color:#8CA0BA;
            font-size:12px;
            margin-top:4px;
          ">
            Intraday Scanner · NSE Stock Futures · A1 Setups
          </div>
        </div>

        <button id="sv-final-fo-refresh" type="button" style="
          height:34px;
          padding:0 16px;
          border:1px solid #29415E;
          border-radius:7px;
          background:#0D1F32;
          color:#DCE8F5;
          font-weight:700;
          cursor:pointer;
        ">
          REFRESH
        </button>
      </div>

      <div style="
        display:flex;
        gap:22px;
        align-items:center;
        padding:10px 12px;
        margin-bottom:10px;
        background:#081522;
        border:1px solid #1A2B40;
        border-radius:8px;
        color:#A8B7C9;
        font-size:11px;
        font-weight:700;
      ">
        <span>SCORE ≥ 90</span>
        <span>5 MIN</span>
        <span>VWAP</span>
        <span>RVOL</span>
        <span>OI</span>
        <span>ATR RISK</span>
        <span>ELITE A1 ONLY</span>

        <span id="sv-final-fo-status"
          style="margin-left:auto;color:#7E91AA;">
          READY
        </span>
      </div>

      <div style="
        background:#081522;
        border:1px solid #1A2B40;
        border-radius:10px;
        overflow:auto;
      ">
        <table style="
          width:100%;
          border-collapse:collapse;
          color:#E7EEF7;
          font-size:12px;
        ">
          <thead>
            <tr style="background:#0D1F32;">
              <th style="padding:12px 9px;">TIME</th>
              <th style="padding:12px 9px;">STOCK</th>
              <th style="padding:12px 9px;">LTP</th>
              <th style="padding:12px 9px;">SCORE</th>
              <th style="padding:12px 9px;">ENTRY</th>
              <th style="padding:12px 9px;">SL</th>
              <th style="padding:12px 9px;">TARGET</th>
              <th style="padding:12px 9px;">RR</th>
              <th style="padding:12px 9px;">ACTION</th>
            </tr>
          </thead>

          <tbody id="sv-final-fo-body">
            <tr>
              <td colspan="9" style="
                padding:30px;
                text-align:center;
                color:#7E91AA;
                font-weight:700;
              ">
                READY
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    `;

    main.appendChild(page);

    document
      .getElementById("sv-final-fo-refresh")
      ?.addEventListener("click", loadPage);

    return page;
  }

  function num(v, digits = 2) {
    const n = Number(v);
    return Number.isFinite(n)
      ? n.toFixed(digits)
      : "--";
  }

  function getRows(payload) {
    const source =
      Array.isArray(payload?.results)
        ? payload.results
        : [];

    return source
      .map(x => ({
        time:
          x.time ||
          x.scan_time ||
          x.detected_at ||
          "--",

        stock:
          x.symbol ||
          x.trading_symbol ||
          x.name ||
          x.instrument_key ||
          "--",

        ltp:
          x.ltp ??
          x.price ??
          x.last_price ??
          x.last_traded_price,

        score:
          x.score ??
          x.confidence ??
          x.opportunity_score,

        entry:
          x.entry ??
          x.entry_price ??
          x.entryPrice,

        sl:
          x.sl ??
          x.stop_loss ??
          x.stopLoss ??
          x.stop_loss_price,

        target:
          x.target ??
          x.target_price ??
          x.targetPrice,

        rr:
          x.rr ??
          x.risk_reward ??
          x.risk_reward_ratio,

        action: String(
          x.action ||
          x.signal ||
          x.side ||
          ""
        ).toUpperCase()
      }))
      .filter(x =>
        Number(x.score) >= 90 &&
        [
          "BUY",
          "SELL",
          "STRONG BUY",
          "STRONG SELL"
        ].includes(x.action)
      )
      .sort((a,b) =>
        (Number(b.score) || 0) -
        (Number(a.score) || 0)
      )
      .slice(0,10);
  }

  function render(rows, failed = false) {
    const body =
      document.getElementById("sv-final-fo-body");

    const status =
      document.getElementById("sv-final-fo-status");

    if (!body) return;

    if (failed) {
      body.innerHTML = `
        <tr>
          <td colspan="9" style="
            padding:30px;
            text-align:center;
            color:#FF5C70;
            font-weight:800;
          ">
            FUTURES DATA TEMPORARILY UNAVAILABLE
          </td>
        </tr>
      `;

      if (status) status.textContent = "OFFLINE";
      return;
    }

    if (!rows.length) {
      body.innerHTML = `
        <tr>
          <td colspan="9" style="
            padding:30px;
            text-align:center;
            color:#7E91AA;
            font-weight:800;
          ">
            NO A1 FUTURES SETUPS
          </td>
        </tr>
      `;

      if (status) status.textContent = "LIVE · 0 SETUPS";
      return;
    }

    body.innerHTML = rows.map(x => {
      const isBuy = x.action.includes("BUY");
      const isSell = x.action.includes("SELL");

      const color =
        isBuy ? "#21DD7A" :
        isSell ? "#FF5C70" :
        "#A8B7C9";

      return `
        <tr>
          <td style="padding:11px 9px;text-align:center;border-bottom:1px solid #1E344B;">
            ${x.time}
          </td>

          <td style="padding:11px 9px;font-weight:800;border-bottom:1px solid #1E344B;">
            ${x.stock}
          </td>

          <td style="padding:11px 9px;text-align:right;border-bottom:1px solid #1E344B;">
            ${num(x.ltp)}
          </td>

          <td style="padding:11px 9px;text-align:center;font-weight:900;border-bottom:1px solid #1E344B;">
            ${num(x.score,0)}
          </td>

          <td style="padding:11px 9px;text-align:right;border-bottom:1px solid #1E344B;">
            ${num(x.entry)}
          </td>

          <td style="padding:11px 9px;text-align:right;border-bottom:1px solid #1E344B;">
            ${num(x.sl)}
          </td>

          <td style="padding:11px 9px;text-align:right;border-bottom:1px solid #1E344B;">
            ${num(x.target)}
          </td>

          <td style="padding:11px 9px;text-align:center;border-bottom:1px solid #1E344B;">
            ${num(x.rr)}
          </td>

          <td style="
            padding:11px 9px;
            text-align:center;
            color:${color};
            font-weight:900;
            border-bottom:1px solid #1E344B;
          ">
            ${x.action || "--"}
          </td>
        </tr>
      `;
    }).join("");

    if (status) {
      status.textContent =
        `LIVE · ${rows.length} A1 SETUP${rows.length === 1 ? "" : "S"}`;
    }
  }

  async function loadPage() {
    buildPage();

    const status =
      document.getElementById("sv-final-fo-status");

    if (status) status.textContent = "SCANNING...";

    try {
      const url =
        typeof FUTURES_URL !== "undefined"
          ? FUTURES_URL
          : `${API_BASE}/api/futures`;

      const response = await fetch(
        `${url}${url.includes("?") ? "&" : "?"}sv=${Date.now()}`,
        { cache:"no-store" }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const payload = await response.json();

      render(getRows(payload), false);

    } catch (e) {
      console.error(
        "Intraday Scanner > Futures & Options:",
        e
      );

      render([], true);
    }
  }

  function showPage() {
    const page = buildPage();
    if (!page) return;

    document
      .querySelectorAll(".main-area > *")
      .forEach(el => {
        if (
          el !== page &&
          !el.classList.contains("main-header")
        ) {
          el.style.display = "none";
        }
      });

    page.style.display = "block";

    const scanner = getScanner();
    const child = document.getElementById(CHILD_ID);

    document
      .querySelectorAll(".frozen-nav-item")
      .forEach(x => x.classList.remove("active"));

    scanner?.classList.add("active");
    child?.classList.add("active");

    loadPage();
  }

  /* ------------------------------------------------------------
     CAPTURE-PHASE CLICK
     Prevents the OLD global F&O handler from hijacking
     the NEW Intraday Scanner child.
     ------------------------------------------------------------ */
  document.addEventListener("click", event => {
    const child =
      event.target.closest("#" + CHILD_ID);

    if (!child) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    showPage();
  }, true);

  /* ------------------------------------------------------------
     INSTALL
     ------------------------------------------------------------ */
  function install() {
    const scanner = getScanner();

    if (!scanner) return;

    removeOldChildren();
    restoreMainFO();
    createChild();

    const plus = scanner.querySelector("b");

    if (plus) {
      plus.textContent = "âˆ’";
    }
  }

  install();

  const observer = new MutationObserver(() => {
    install();
  });

  observer.observe(document.body, {
    childList:true,
    subtree:true
  });

})();





/* STOCKVERSITY_FUTURES_FINAL_UI_20260916 */
(() => {
  "use strict";

  const PAGE_ID = "sv-intraday-futures-page";
  const LIVE_TABLE = ".sv-fo-real-table";
  const HISTORY_ID = "sv-fo-history-final";

  const escapeHtml = value =>
    String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");

  const num = value => {
    const n = Number(value);
    return Number.isFinite(n) ? n : NaN;
  };

  const money = value => {
    const n = num(value);
    return Number.isFinite(n)
      ? n.toLocaleString("en-IN", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })
      : "--";
  };

  const score = value => {
    const n = num(value);
    return Number.isFinite(n) ? n.toFixed(0) : "--";
  };

  const rr = value => {
    const n = num(value);
    return Number.isFinite(n) ? n.toFixed(2) : "--";
  };

  const rvol = value => {
    const n = num(value);
    return Number.isFinite(n) ? `${n.toFixed(2)}x` : "--";
  };

  const actionClass = action => {
    const a = String(action || "").toUpperCase();
    if (a.includes("BUY")) return "sv-fo-real-buy";
    if (a.includes("SELL")) return "sv-fo-real-sell";
    return "";
  };

  const normalizeTime = value => {
    const s = String(value ?? "").trim();
    if (!s) return "--";

    const m12 = s.match(/^(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)$/i);
    if (m12) {
      let h = Number(m12[1]);
      const min = m12[2];
      const sec = m12[3];
      const ap = m12[4].toUpperCase();
      if (ap === "PM" && h < 12) h += 12;
      if (ap === "AM" && h === 12) h = 0;
      return `${String(h).padStart(2, "0")}:${min}:${sec}`;
    }

    const m24 = s.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);
    if (m24) {
      return `${String(Number(m24[1])).padStart(2, "0")}:${m24[2]}:${m24[3] || "00"}`;
    }

    return s;
  };

  const formatDate = value => {
    const s = String(value ?? "").trim();
    const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return s || "--";

    const d = new Date(`${s}T00:00:00+05:30`);
    if (Number.isNaN(d.getTime())) return s;

    return d.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      timeZone: "Asia/Kolkata"
    });
  };

  const weekday = value => {
    const s = String(value ?? "").trim();
    const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return "";
    const d = new Date(`${s}T00:00:00+05:30`);
    if (Number.isNaN(d.getTime())) return "";
    return d.toLocaleDateString("en-IN", {
      weekday: "long",
      timeZone: "Asia/Kolkata"
    }).toUpperCase();
  };

  const repairedText = value => {
    let s = String(value ?? "");

    const replacements = [
      ["ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢", "â€¢"],
      ["Ã¢â‚¬Â¢", "â€¢"],
      ["Ã‚Â·", "Â·"],
      ["Ãƒâ€šÂ·", "Â·"],
      ["Ã¢â€°Â¥", "â‰¥"],
      ["Ã‚â‰¥", "â‰¥"],
      ["Ã¢Ë†â€™", "âˆ’"],
      ["Ã¢â‚¬â€œ", "â€“"],
      ["Ã¢â‚¬â€", "â€”"],
      ["Ã¢â€ â€™", "â†’"],
      ["Ã¢â€ Â", "â†"],
      ["Ã¢Å“â€œ", "âœ“"],
      ["Ã¢Å“â€”", "âœ•"],
      ["Ã¢Ëœâ€¦", "â˜…"],
      ["Ã°Å¸â€˜â€¹", "ðŸ‘‹"],
      ["Ã°Å¸Å½Â¯", "ðŸŽ¯"]
    ];

    for (const [bad, good] of replacements) {
      s = s.split(bad).join(good);
    }

    if (/[ÃƒÃ‚Ã¢Ã°]/.test(s)) {
      try {
        const allByteChars = Array.from(s)
          .every(ch => ch.charCodeAt(0) >= 0 && ch.charCodeAt(0) <= 255);

        if (allByteChars) {
          const encoded = Array.from(s)
            .map(ch => `%${ch.charCodeAt(0).toString(16).padStart(2, "0")}`)
            .join("");
          const fixed = decodeURIComponent(encoded);
          if (fixed && !fixed.includes("ï¿½")) s = fixed;
        }
      } catch (_) {}
    }

    return s;
  };

  const repairDomEncoding = root => {
    if (!root) return;

    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT
    );

    const nodes = [];
    let node;

    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (!parent) continue;

      const tag = parent.tagName.toLowerCase();
      if (tag === "script" || tag === "style") continue;

      if (/[ÃƒÃ‚Ã¢Ã°]/.test(node.nodeValue || "")) {
        nodes.push(node);
      }
    }

    for (const textNode of nodes) {
      const fixed = repairedText(textNode.nodeValue);
      if (fixed !== textNode.nodeValue) {
        textNode.nodeValue = fixed;
      }
    }
  };

  const renderHeader = table => {
    if (!table) return;
    const head = table.querySelector("thead");
    if (!head) return;

    head.innerHTML = `
      <tr>
        <th>TIME</th>
        <th>STOCK</th>
        <th>LTP</th>
        <th>SCORE</th>
        <th>TREND STRENGTH</th>
        <th>OI SETUP</th>
        <th>RVOL</th>
        <th>ENTRY</th>
        <th>SL</th>
        <th>TARGET</th>
        <th>RR</th>
        <th>ACTION</th>
      </tr>
    `;
  };

  const renderRows = (body, rows, emptyText) => {
    if (!body) return;

    if (!rows.length) {
      body.innerHTML = `
        <tr>
          <td colspan="12" class="sv-fo-real-empty">
            ${escapeHtml(emptyText)}
          </td>
        </tr>
      `;
      return;
    }

    body.innerHTML = rows.map(x => {
      const action = String(
        x.action || x.signal || x.side || ""
      ).toUpperCase();

      const trend = String(
        x.trend_strength || x.trend || "--"
      ).trim();

      const oi = String(
        x.oi_setup || x.oi || "--"
      ).trim();

      return `
        <tr>
          <td class="sv-fo-time">${escapeHtml(normalizeTime(x.time || x.generated))}</td>
          <td class="sv-fo-real-stock">${escapeHtml(x.symbol || x.stock || x.trading_symbol || "--")}</td>
          <td>${money(x.ltp ?? x.price)}</td>
          <td class="sv-fo-real-score">${score(x.score)}</td>
          <td>${escapeHtml(trend)}</td>
          <td>${escapeHtml(oi)}</td>
          <td class="sv-fo-rvol">${escapeHtml(rvol(x.rvol))}</td>
          <td>${money(x.entry)}</td>
          <td class="sv-fo-sl">${money(x.sl)}</td>
          <td class="sv-fo-target">${money(x.target)}</td>
          <td>${rr(x.rr)}</td>
          <td>
            <span class="sv-fo-real-action ${actionClass(action)}">
              ${escapeHtml(action || "--")}
            </span>
          </td>
        </tr>
      `;
    }).join("");
  };

  const ensureLiveTable = page => {
    const table = page?.querySelector(LIVE_TABLE);
    if (!table) return null;
    renderHeader(table);
    table.style.minWidth = "1180px";
    return table;
  };

  const ensureHistory = page => {
    if (!page) return null;

    let history = page.querySelector(`#${HISTORY_ID}`);

    if (!history) {
      history = document.createElement("section");
      history.id = HISTORY_ID;
      history.className = "sv-fo-history-final";

      const card = page.querySelector(".sv-fo-real-card");
      if (card) {
        card.insertAdjacentElement("afterend", history);
      } else {
        page.appendChild(history);
      }
    }

    return history;
  };

  const renderHistory = (historyRoot, sections) => {
    if (!historyRoot) return;

    if (!Array.isArray(sections) || !sections.length) {
      historyRoot.innerHTML = `
        <div class="sv-fo-history-head">
          <div>
            <strong>Last 3 Trading Days</strong>
            <small>Real 5-minute historical A1 setups</small>
          </div>
        </div>
        <div class="sv-fo-history-empty">
          Historical A1 setups are not available yet.
        </div>
      `;
      return;
    }

    const blocks = sections.map(section => {
      const dateText = formatDate(section.date);
      const dayText = weekday(section.date);
      const rows = Array.isArray(section.rows) ? section.rows : [];

      return `
        <article class="sv-fo-history-block">
          <div class="sv-fo-history-block-head">
            <div>
              <strong>${escapeHtml(dateText)}${dayText ? ` (${escapeHtml(dayText)})` : ""}</strong>
              <small>${rows.length} A1 SETUP${rows.length === 1 ? "" : "S"}</small>
            </div>
            <span class="sv-fo-history-badge">HISTORICAL</span>
          </div>

          <div class="sv-fo-history-scroll">
            <table class="sv-fo-real-table sv-fo-history-table">
              <thead>
                <tr>
                  <th>TIME</th>
                  <th>STOCK</th>
                  <th>LTP</th>
                  <th>SCORE</th>
                  <th>TREND STRENGTH</th>
                  <th>OI SETUP</th>
                  <th>RVOL</th>
                  <th>ENTRY</th>
                  <th>SL</th>
                  <th>TARGET</th>
                  <th>RR</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                ${
                  rows.length
                    ? rows.map(x => {
                        const action = String(
                          x.action || x.signal || x.side || ""
                        ).toUpperCase();

                        return `
                          <tr>
                            <td class="sv-fo-time">${escapeHtml(normalizeTime(x.time || x.generated))}</td>
                            <td class="sv-fo-real-stock">${escapeHtml(x.symbol || x.stock || x.trading_symbol || "--")}</td>
                            <td>${money(x.ltp ?? x.price)}</td>
                            <td class="sv-fo-real-score">${score(x.score)}</td>
                            <td>${escapeHtml(x.trend_strength || x.trend || "--")}</td>
                            <td>${escapeHtml(x.oi_setup || x.oi || "--")}</td>
                            <td class="sv-fo-rvol">${escapeHtml(rvol(x.rvol))}</td>
                            <td>${money(x.entry)}</td>
                            <td class="sv-fo-sl">${money(x.sl)}</td>
                            <td class="sv-fo-target">${money(x.target)}</td>
                            <td>${rr(x.rr)}</td>
                            <td>
                              <span class="sv-fo-real-action ${actionClass(action)}">
                                ${escapeHtml(action || "--")}
                              </span>
                            </td>
                          </tr>
                        `;
                      }).join("")
                    : `
                      <tr>
                        <td colspan="12" class="sv-fo-real-empty">
                          No qualifying A1 setups for this trading day.
                        </td>
                      </tr>
                    `
                }
              </tbody>
            </table>
          </div>
        </article>
      `;
    }).join("");

    historyRoot.innerHTML = `
      <div class="sv-fo-history-head">
        <div>
          <strong>Last 3 Trading Days</strong>
          <small>Historical A1 setups Â· Today + previous 3 NSE sessions</small>
        </div>
      </div>
      ${blocks}
      <div class="sv-fo-history-footer">
        A1 Criteria: Score â‰¥ 90 Â· Trend = Very Strong Â· RR â‰¥ 1.50 Â· RVOL â‰¥ 1.50 Â· Valid Directional OI Â· OI N/A Excluded Â· Max 10 Setups
      </div>
    `;
  };

  const paint = async () => {
    const page = document.getElementById(PAGE_ID);
    if (!page) return;

    const table = ensureLiveTable(page);
    const historyRoot = ensureHistory(page);
    if (!table) return;

    const body = table.querySelector("tbody");
    const count = page.querySelector("#sv-fo-real-count");
    const status = page.querySelector("#sv-fo-real-status");
    const date = page.querySelector("#sv-fo-real-date");

    try {
      const response = await fetch("/api/futures?sv=" + Date.now(), {
        cache: "no-store"
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const payload = await response.json();
      const rows = Array.isArray(payload?.results)
        ? payload.results
        : [];

      renderRows(
        body,
        rows.slice(0, 10),
        "No A1 setups found for this session."
      );

      if (count) {
        const visible = Math.min(rows.length, 10);
        count.textContent =
          `${visible} setup${visible === 1 ? "" : "s"}`;
      }

      if (status) status.textContent = "LIVE";

      if (date) {
        date.textContent =
          formatDate(payload.session_date || payload.date);
      }

      renderHistory(
        historyRoot,
        payload.history
      );

      repairDomEncoding(page);
      repairDomEncoding(document.body);
    } catch (error) {
      console.error("StockVersity F&O final page:", error);

      if (status) status.textContent = "OFFLINE";

      renderRows(
        body,
        [],
        "Futures data temporarily unavailable."
      );

      renderHistory(historyRoot, []);
      repairDomEncoding(document.body);
    }
  };

  const install = () => {
    const page = document.getElementById(PAGE_ID);
    if (!page) return;

    ensureLiveTable(page);
    ensureHistory(page);
    paint();
  };

  const observer = new MutationObserver(() => {
    const page = document.getElementById(PAGE_ID);
    if (page) {
      ensureLiveTable(page);
      ensureHistory(page);
    }
    repairDomEncoding(document.body);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  if (!document.getElementById("stockversity-futures-final-ui-style")) {
    const style = document.createElement("style");
    style.id = "stockversity-futures-final-ui-style";
    style.textContent = `
      #${PAGE_ID} .sv-fo-real-table {
        min-width: 1180px !important;
        font-size: 13px !important;
      }

      #${PAGE_ID} .sv-fo-real-table th {
        font-size: 10px !important;
        padding: 12px 11px !important;
        letter-spacing: .055em !important;
      }

      #${PAGE_ID} .sv-fo-real-table td {
        font-size: 13px !important;
        padding: 14px 11px !important;
      }

      #${PAGE_ID} .sv-fo-real-stock,
      #${PAGE_ID} .sv-fo-real-score {
        font-size: 13.5px !important;
        font-weight: 800 !important;
      }

      #${PAGE_ID} .sv-fo-real-action {
        min-width: 74px !important;
        padding: 6px 9px !important;
        font-size: 10px !important;
      }

      #${PAGE_ID} .sv-fo-rvol {
        font-weight: 700 !important;
      }

      #${PAGE_ID} .sv-fo-history-final {
        margin-top: 20px;
        border: 1px solid rgba(90,130,190,.2);
        border-radius: 10px;
        overflow: hidden;
        background: rgba(9,17,31,.72);
      }

      #${PAGE_ID} .sv-fo-history-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 18px;
        border-bottom: 1px solid rgba(90,130,190,.15);
      }

      #${PAGE_ID} .sv-fo-history-head strong {
        display: block;
        font-size: 16px !important;
      }

      #${PAGE_ID} .sv-fo-history-head small {
        display: block;
        margin-top: 4px;
        font-size: 11px !important;
        opacity: .65;
      }

      #${PAGE_ID} .sv-fo-history-block {
        border-bottom: 1px solid rgba(90,130,190,.13);
      }

      #${PAGE_ID} .sv-fo-history-block-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 13px 18px;
        background: rgba(20,35,60,.32);
      }

      #${PAGE_ID} .sv-fo-history-block-head strong {
        font-size: 14px !important;
      }

      #${PAGE_ID} .sv-fo-history-block-head small {
        display: block;
        margin-top: 3px;
        font-size: 10px !important;
        opacity: .65;
      }

      #${PAGE_ID} .sv-fo-history-badge {
        font-size: 9px !important;
        font-weight: 800;
        padding: 5px 8px;
        border: 1px solid rgba(100,150,220,.2);
        border-radius: 5px;
        opacity: .72;
      }

      #${PAGE_ID} .sv-fo-history-scroll {
        overflow-x: auto;
      }

      #${PAGE_ID} .sv-fo-history-table {
        margin: 0;
      }

      #${PAGE_ID} .sv-fo-history-empty {
        padding: 30px 18px;
        text-align: center;
        font-size: 13px;
        opacity: .6;
      }

      #${PAGE_ID} .sv-fo-history-footer {
        padding: 13px 18px;
        font-size: 10px;
        line-height: 1.5;
        opacity: .62;
      }
    `;
    document.head.appendChild(style);
  }

  install();
  repairDomEncoding(document.body);

  setTimeout(install, 250);
  setTimeout(install, 1000);

  setInterval(() => {
    if (document.getElementById(PAGE_ID)) paint();
    repairDomEncoding(document.body);
  }, 30000);
})();



/* SV_FO_FRONTEND_V7 */
(() => {
  "use strict";

  const PAGE_ID = "sv-intraday-futures-page";
  const amp = String.fromCharCode(38);

  function apiUrl() {
    return typeof FUTURES_URL !== "undefined"
      ? FUTURES_URL
      : ((typeof API_BASE !== "undefined" ? API_BASE : "") + "/api/futures");
  }

  function esc(v) {
    return String(v == null ? "--" : v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function num(v, d) {
    const n = Number(v);
    return Number.isFinite(n) ? n.toFixed(d == null ? 2 : d) : "--";
  }

  function money(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return "--";
    return n.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function actionOf(x) {
    return String(x && (x.action || x.signal || x.side) || "").toUpperCase();
  }

  function validA1(x) {
    const score = Number(x && x.score);
    const rr = Number(x && x.rr);
    const rvol = Number(x && x.rvol);
    const trend = String(x && (x.trend_strength || x.trend) || "").toLowerCase();
    const oi = String(x && (x.oi_setup || x.oi) || "").toLowerCase();
    const action = actionOf(x);

    return score >= 90 &&
      rr >= 1.5 &&
      rvol >= 1.5 &&
      trend.indexOf("very strong") >= 0 &&
      /(long build|short build|short cover|long unwind)/.test(oi) &&
      ["BUY","SELL","STRONG BUY","STRONG SELL"].includes(action);
  }

  function ensurePage() {
    return document.getElementById(PAGE_ID);
  }

  function repairPage() {
    const page = ensurePage();
    if (!page) return null;

    let card = page.querySelector(".sv-fo-real-card");
    if (!card) return page;

    if (!card.dataset.svV7) {
      card.dataset.svV7 = "1";
      card.innerHTML = `
        <div class="sv-fo-v7-card-head">
          <div>
            <strong>Intraday Futures A1 Setups</strong>
            <small id="sv-fo-v7-count">SCANNING...</small>
          </div>
          <span id="sv-fo-v7-date"></span>
        </div>
        <div class="sv-fo-v7-table-wrap">
          <table class="sv-fo-v7-table">
            <thead>
              <tr>
                <th>TIME</th>
                <th>STOCK</th>
                <th>LTP</th>
                <th>SCORE</th>
                <th>TREND STRENGTH</th>
                <th>OI SETUP</th>
                <th>RVOL</th>
                <th>ENTRY</th>
                <th>SL</th>
                <th>TARGET</th>
                <th>RR</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody id="sv-fo-v7-body">
              <tr><td colspan="12" class="sv-fo-v7-empty">Loading A1 futures setups...</td></tr>
            </tbody>
          </table>
        </div>
      `;
    }

    if (!page.querySelector("#sv-fo-v7-history")) {
      const host = document.createElement("div");
      host.id = "sv-fo-v7-history";
      page.appendChild(host);
    }

    return page;
  }

  function renderCurrent(page, payload) {
    const body = page.querySelector("#sv-fo-v7-body");
    const count = page.querySelector("#sv-fo-v7-count");
    const date = page.querySelector("#sv-fo-v7-date");
    if (!body) return;

    const rows = (Array.isArray(payload && payload.results) ? payload.results : [])
      .filter(validA1)
      .slice(0, 10);

    if (date && payload && payload.session_date) {
      const d = new Date(String(payload.session_date) + "T00:00:00+05:30");
      date.textContent = d.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      });
    }

    if (!rows.length) {
      body.innerHTML = `
        <tr>
          <td colspan="12" class="sv-fo-v7-empty">
            No A1 setups found for this session.
          </td>
        </tr>
      `;
      if (count) count.textContent = "0 setups";
      return;
    }

    body.innerHTML = rows.map(x => {
      const action = actionOf(x);
      const cls = action.indexOf("BUY") >= 0
        ? "sv-fo-v7-buy"
        : action.indexOf("SELL") >= 0 ? "sv-fo-v7-sell" : "";

      return `
        <tr>
          <td>${esc(x.time || "--")}</td>
          <td class="sv-fo-v7-stock">${esc(x.symbol || x.trading_symbol || "--")}</td>
          <td>${money(x.ltp == null ? x.price : x.ltp)}</td>
          <td class="sv-fo-v7-score">${num(x.score, 0)}</td>
          <td>${esc(x.trend_strength || x.trend || "--")}</td>
          <td>${esc(x.oi_setup || x.oi || "--")}</td>
          <td>${num(x.rvol, 2)}</td>
          <td>${money(x.entry)}</td>
          <td>${money(x.sl)}</td>
          <td>${money(x.target)}</td>
          <td>${num(x.rr, 2)}</td>
          <td><span class="sv-fo-v7-action ${cls}">${esc(action || "--")}</span></td>
        </tr>
      `;
    }).join("");

    if (count) count.textContent = rows.length + " setup" + (rows.length === 1 ? "" : "s");
  }

  function renderHistory(page, payload) {
    const host = page.querySelector("#sv-fo-v7-history");
    if (!host) return;

    const blocks = Array.isArray(payload && payload.history)
      ? payload.history.filter(x => Array.isArray(x && x.rows)).slice(0, 3)
      : [];

    host.innerHTML = `
      <div class="sv-fo-v7-history-card">
        <div class="sv-fo-v7-history-head">
          <strong>LAST 3 TRADING DAYS - A1 SETUPS</strong>
          <span>Previous NSE trading sessions</span>
        </div>
        ${
          blocks.length
            ? blocks.map(block => {
                const rows = Array.isArray(block.rows) ? block.rows.slice(0, 10) : [];
                return `
                  <div class="sv-fo-v7-day">
                    <div class="sv-fo-v7-day-head">
                      <strong>${esc(block.date || "--")}</strong>
                      <span>${rows.length} setup${rows.length === 1 ? "" : "s"}</span>
                    </div>
                    <div class="sv-fo-v7-table-wrap">
                      <table class="sv-fo-v7-table sv-fo-v7-history-table">
                        <thead>
                          <tr>
                            <th>TIME</th>
                            <th>STOCK</th>
                            <th>SCORE</th>
                            <th>TREND STRENGTH</th>
                            <th>OI SETUP</th>
                            <th>RVOL</th>
                            <th>ENTRY</th>
                            <th>SL</th>
                            <th>TARGET</th>
                            <th>RR</th>
                            <th>ACTION</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${
                            rows.length
                              ? rows.map(x => {
                                  const action = actionOf(x);
                                  const cls = action.indexOf("BUY") >= 0
                                    ? "sv-fo-v7-buy"
                                    : action.indexOf("SELL") >= 0 ? "sv-fo-v7-sell" : "";
                                  return `
                                    <tr>
                                      <td>${esc(x.time || "--")}</td>
                                      <td class="sv-fo-v7-stock">${esc(x.symbol || x.trading_symbol || "--")}</td>
                                      <td class="sv-fo-v7-score">${num(x.score, 0)}</td>
                                      <td>${esc(x.trend_strength || x.trend || "--")}</td>
                                      <td>${esc(x.oi_setup || x.oi || "--")}</td>
                                      <td>${num(x.rvol, 2)}</td>
                                      <td>${money(x.entry)}</td>
                                      <td>${money(x.sl)}</td>
                                      <td>${money(x.target)}</td>
                                      <td>${num(x.rr, 2)}</td>
                                      <td><span class="sv-fo-v7-action ${cls}">${esc(action || "--")}</span></td>
                                    </tr>
                                  `;
                                }).join("")
                              : '<tr><td colspan="11" class="sv-fo-v7-empty">No A1 setups recorded for this trading day.</td></tr>'
                          }
                        </tbody>
                      </table>
                    </div>
                  </div>
                `;
              }).join("")
            : '<div class="sv-fo-v7-empty">No historical A1 setup data returned by the API.</div>'
        }
      </div>
    `;
  }

  async function refresh() {
    const page = repairPage();
    if (!page) return;

    try {
      const response = await fetch(apiUrl() + "?sv=" + Date.now(), {
        cache: "no-store"
      });
      if (!response.ok) throw new Error("HTTP " + response.status);

      const payload = await response.json();
      renderCurrent(page, payload);
      renderHistory(page, payload);

      const status = page.querySelector("#sv-fo-real-status");
      if (status) status.textContent = "LIVE";
    } catch (err) {
      console.error("StockVersity F&O V7:", err);
    }
  }

  function ensureStyle() {
    if (document.getElementById("sv-fo-v7-style")) return;

    const style = document.createElement("style");
    style.id = "sv-fo-v7-style";
    style.textContent = `
      #${PAGE_ID} .sv-fo-v7-card-head,
      #${PAGE_ID} .sv-fo-v7-history-head {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:16px;
        padding:14px 16px;
        border-bottom:1px solid rgba(90,130,190,.15);
      }

      #${PAGE_ID} .sv-fo-v7-card-head strong,
      #${PAGE_ID} .sv-fo-v7-history-head strong {
        display:block;
        font-size:15px;
      }

      #${PAGE_ID} .sv-fo-v7-card-head small,
      #${PAGE_ID} .sv-fo-v7-history-head span {
        display:block;
        margin-top:3px;
        opacity:.55;
        font-size:11px;
      }

      #${PAGE_ID} .sv-fo-v7-table-wrap {
        width:100%;
        overflow-x:auto;
      }

      #${PAGE_ID} .sv-fo-v7-table {
        width:100%;
        min-width:1240px;
        border-collapse:collapse;
        font-size:12px;
      }

      #${PAGE_ID} .sv-fo-v7-table th {
        padding:12px 11px;
        text-align:left;
        font-size:10px;
        letter-spacing:.06em;
        opacity:.6;
        white-space:nowrap;
        border-bottom:1px solid rgba(90,130,190,.15);
      }

      #${PAGE_ID} .sv-fo-v7-table td {
        padding:14px 11px;
        white-space:nowrap;
        border-bottom:1px solid rgba(90,130,190,.09);
      }

      #${PAGE_ID} .sv-fo-v7-stock,
      #${PAGE_ID} .sv-fo-v7-score {
        font-weight:700;
      }

      #${PAGE_ID} .sv-fo-v7-action {
        display:inline-block;
        min-width:78px;
        padding:6px 9px;
        border-radius:5px;
        text-align:center;
        font-size:10px;
        font-weight:800;
      }

      #${PAGE_ID} .sv-fo-v7-buy {
        color:#58e0a0;
        background:rgba(55,210,140,.10);
      }

      #${PAGE_ID} .sv-fo-v7-sell {
        color:#ff7180;
        background:rgba(255,80,100,.10);
      }

      #${PAGE_ID} .sv-fo-v7-empty {
        padding:42px 15px !important;
        text-align:center;
        opacity:.6;
        font-size:12px;
      }

      #${PAGE_ID} #sv-fo-v7-history {
        margin-top:18px;
      }

      #${PAGE_ID} .sv-fo-v7-history-card {
        border:1px solid rgba(90,130,190,.2);
        border-radius:10px;
        overflow:hidden;
        background:rgba(9,17,31,.72);
      }

      #${PAGE_ID} .sv-fo-v7-day {
        border-top:1px solid rgba(90,130,190,.11);
      }

      #${PAGE_ID} .sv-fo-v7-day-head {
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:12px 16px;
        font-size:12px;
      }

      #${PAGE_ID} .sv-fo-v7-day-head span {
        opacity:.55;
      }
    `;
    document.head.appendChild(style);
  }

  ensureStyle();

  const observer = new MutationObserver(() => {
    if (ensurePage()) refresh();
  });

  observer.observe(document.body, { childList:true, subtree:true });

  setTimeout(refresh, 250);
  setTimeout(refresh, 1000);
  setTimeout(refresh, 2500);
  setInterval(refresh, 5000);
})();


