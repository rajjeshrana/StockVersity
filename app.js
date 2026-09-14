const $ = id => document.getElementById(id);
const API_BASE = window.STOCKVERSITY_API_BASE || "";
const MARKET_URL = `${API_BASE}/api/market`;
const FUTURES_URL = `${API_BASE}/api/futures`;

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
    e.textContent=x===null?"--":`${x>=0?"+":"-"}₹${cr(Math.abs(x))} Cr`;
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
  set("fii-buy",fii.buy==null?"--":`₹${cr(fii.buy)} Cr`);
  set("fii-sell",fii.sell==null?"--":`₹${cr(fii.sell)} Cr`);
  net("fii-net",fii.net);
  bars("fii",fii.buy,fii.sell);

  set("dii-buy",dii.buy==null?"--":`₹${cr(dii.buy)} Cr`);
  set("dii-sell",dii.sell==null?"--":`₹${cr(dii.sell)} Cr`);
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

  set("institutional-turnover",turnover===null?"--":`₹${cr(turnover)} Cr`);
  set("institutional-buy-total",buy===null?"--":`₹${cr(buy)} Cr`);
  set("institutional-sell-total",sell===null?"--":`₹${cr(sell)} Cr`);
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

    // Rebuild Institutional Flow values with a runtime-generated ₹.
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
      if(sub)sub.textContent="FII • DII • PRO";

      { const fx=Number(f.net); const fp=document.getElementById("fii-net-pct"); if(fp){fp.textContent=Number.isFinite(fx)?((fx>=0?"▲ +":"▼ -")+Math.abs(fx/(Number(f.buy)+Number(f.sell))*100).toFixed(1)+"%"):"--"; fp.className="sv-if-net-pct "+(fx>=0?"positive":"negative");} }
      { const dx=Number(d.net); const dp=document.getElementById("dii-net-pct"); if(dp){dp.textContent=Number.isFinite(dx)?((dx>=0?"▲ +":"▼ -")+Math.abs(dx/(Number(d.buy)+Number(d.sell))*100).toFixed(1)+"%"):"--"; dp.className="sv-if-net-pct "+(dx>=0?"positive":"negative");} }
      { const px=Number(p.net_oi); const pp=document.getElementById("pro-net-pct"); if(pp){pp.textContent=Number.isFinite(px)?((px>=0?"▲ +":"▼ -")+Math.abs(px/(Number(p.total_long)+Number(p.total_short))*100).toFixed(1)+"%"):"--"; pp.className="sv-if-net-pct "+(px>=0?"positive":"negative"); pp.style.setProperty("color",px>=0?"#00e69a":"#ff5065","important");} }
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
        : (pct>=0 ? "▲ +" : "▼ -")+Math.abs(pct).toFixed(1)+"%";

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

