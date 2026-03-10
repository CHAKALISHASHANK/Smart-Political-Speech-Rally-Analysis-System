/* ══════════════════════════════════════════════════════════════════════════
   PolAnalytica — Dashboard JavaScript
   Fetches API data and renders all charts & interactive UI
══════════════════════════════════════════════════════════════════════════ */

const API = "";  // Same-origin Flask server

// ── Shared chart defaults ──────────────────────────────────────────────────
Chart.defaults.color = "#94a3b8";
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size   = 12;

const COLORS = {
  gold:    "#f59e0b", goldL: "#fcd34d",
  blue:    "#3b82f6", blueL: "#60a5fa",
  purple:  "#8b5cf6", purpleL:"#a78bfa",
  green:   "#10b981", greenL: "#34d399",
  red:     "#ef4444", redL:   "#f87171",
  cyan:    "#06b6d4",
  text:    "#94a3b8", textP: "#f8fafc",
  border:  "rgba(255,255,255,0.07)"
};

const CHART_BG = "rgba(0,0,0,0)";

function chartGrid() {
  return {
    color: COLORS.border,
    drawBorder: false
  };
}

function makeGradient(ctx, c1, c2) {
  const grad = ctx.createLinearGradient(0, 0, 0, 300);
  grad.addColorStop(0, c1 + "cc");
  grad.addColorStop(1, c1 + "08");
  return grad;
}

// ── Utility ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

function formatNum(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1) + "M";
  if (n >= 1e3) return (n/1e3).toFixed(1) + "K";
  return n.toString();
}

function showToast(msg, dur = 3000) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), dur);
}

function getLevelClass(level) {
  const l = level.toLowerCase();
  if (l.includes("game")) return "level-game-changing";
  if (l.includes("high")) return "level-high";
  if (l.includes("moderate")) return "level-moderate";
  return "level-low";
}

// Sentiment color helper
function sentColor(polarity) {
  if (polarity > 0.05) return COLORS.green;
  if (polarity < -0.05) return COLORS.red;
  return COLORS.gold;
}

// ── Cached data ────────────────────────────────────────────────────────────
let _rallies   = null;
let _crowd     = null;
let _sentiment = null;
let _impact    = null;
let _timeline  = null;
let _forecast  = null;
let _featImp   = null;

async function fetchJSON(path) {
  const res = await fetch(API + path);
  return res.json();
}

// ── Chart registry for destroy-on-update ─────────────────────────────────
const _charts = {};
function getOrDestroyChart(id, config) {
  if (_charts[id]) { _charts[id].destroy(); }
  const ctx = $(id);
  if (!ctx) return null;
  _charts[id] = new Chart(ctx, config);
  return _charts[id];
}

// ══════════════════════════════════════════════════════════════════════════
// PAGE: OVERVIEW
// ══════════════════════════════════════════════════════════════════════════
async function loadOverview() {
  const [overview, timeline, rallies, sentiment] = await Promise.all([
    fetchJSON("/api/overview"),
    fetchJSON("/api/timeline"),
    fetchJSON("/api/rallies"),
    fetchJSON("/api/sentiment")
  ]);

  _timeline = timeline;
  _rallies  = rallies;

  // KPIs
  $("kpi-rallies").textContent    = overview.total_rallies;
  $("kpi-attendance").textContent = formatNum(overview.total_attendance);
  $("kpi-sentiment").textContent  = (overview.avg_sentiment >= 0 ? "+" : "") +
                                     overview.avg_sentiment.toFixed(3);
  $("kpi-impact").textContent     = (overview.avg_impact_score * 100).toFixed(1) + "%";

  // ── Timeline Chart ───────────────────────────────────────────────────
  const tlLabels = timeline.map(t => t.city);
  getOrDestroyChart("timelineChart", {
    type: "line",
    data: {
      labels: tlLabels,
      datasets: [
        {
          label: "Impact Score",
          data: timeline.map(t => +(t.impact_score * 100).toFixed(1)),
          borderColor: COLORS.gold, borderWidth: 2.5,
          tension: 0.4, pointRadius: 5, pointHoverRadius: 8,
          pointBackgroundColor: COLORS.gold,
          fill: true,
          backgroundColor: (ctx) => makeGradient(ctx.chart.ctx, COLORS.gold, COLORS.gold)
        },
        {
          label: "Sentiment × 100",
          data: timeline.map(t => +(t.sentiment * 100).toFixed(2)),
          borderColor: COLORS.green, borderWidth: 2,
          tension: 0.4, pointRadius: 4,
          pointBackgroundColor: COLORS.green,
          fill: true,
          backgroundColor: (ctx) => makeGradient(ctx.chart.ctx, COLORS.green, COLORS.green)
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { position:"top" }, tooltip: { mode:"index", intersect:false } },
      scales: {
        x: { grid: chartGrid() },
        y: { grid: chartGrid(), min: -10, max: 100 }
      }
    }
  });

  // ── Attendance Bar ───────────────────────────────────────────────────
  getOrDestroyChart("attendanceChart", {
    type: "bar",
    data: {
      labels: rallies.map(r => r.city),
      datasets: [{
        label: "Attendance",
        data: rallies.map(r => r.attendance),
        backgroundColor: rallies.map((_, i) =>
          `hsl(${210 + i*20},80%,${55 + i*3}%)`),
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display:false } },
      scales: {
        x: { grid: chartGrid() },
        y: { grid: chartGrid(), ticks: { callback: v => formatNum(v) } }
      }
    }
  });

  // ── Swing Radar ──────────────────────────────────────────────────────
  getOrDestroyChart("swingRadarChart", {
    type: "radar",
    data: {
      labels: rallies.map(r => r.city),
      datasets: [{
        label: "Swing Probability",
        data: rallies.map(r => +(r.swing_probability * 100).toFixed(1)),
        borderColor: COLORS.purple, borderWidth: 2,
        backgroundColor: COLORS.purple + "30",
        pointBackgroundColor: COLORS.purpleL,
        pointRadius: 4
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display:false } },
      scales: { r: {
        grid: { color: COLORS.border },
        ticks: { backdropColor:"transparent", color: COLORS.text, stepSize: 20 },
        pointLabels: { color: COLORS.text, font: { size:10 } }
      }}
    }
  });

  // ── Sentiment Donut ──────────────────────────────────────────────────
  const posCount = rallies.filter(r => r.sentiment_label === "Positive").length;
  const negCount = rallies.filter(r => r.sentiment_label === "Negative").length;
  const neuCount = rallies.filter(r => r.sentiment_label === "Neutral").length;

  getOrDestroyChart("sentimentDonutChart", {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [posCount, neuCount, negCount],
        backgroundColor: [COLORS.green, COLORS.gold, COLORS.red],
        borderColor: "#111428", borderWidth: 3, hoverOffset: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      cutout: "65%",
      plugins: { legend: { position:"bottom" } }
    }
  });

  // ── Top Rallies List ────────────────────────────────────────────────
  const sorted = [...rallies].sort((a,b) => b.impact_score - a.impact_score);
  $("top-rallies-list").innerHTML = sorted.map((r, i) => {
    const rankClass = i === 0 ? "rank-1" : i === 1 ? "rank-2" : i === 2 ? "rank-3" : "rank-other";
    return `
      <div class="top-rally-item">
        <div class="rally-rank ${rankClass}">${i+1}</div>
        <div class="rally-info">
          <div class="rally-name">${r.name}</div>
          <div class="rally-city">${r.city}</div>
        </div>
        <div class="rally-score">${(r.impact_score*100).toFixed(1)}%</div>
      </div>`;
  }).join("");
}

// ══════════════════════════════════════════════════════════════════════════
// PAGE: CROWD DETECTION
// ══════════════════════════════════════════════════════════════════════════
async function loadCrowd() {
  if (!_crowd) _crowd = await fetchJSON("/api/crowd");
  const rallies = _crowd;

  // Populate selector
  const sel = $("crowd-rally-select");
  sel.innerHTML = rallies.map((r, i) =>
    `<option value="${i}">${r.rally} — ${r.city}</option>`).join("");

  sel.addEventListener("change", () => renderCrowdData(+sel.value));
  renderCrowdData(0);
}

function renderCrowdData(idx) {
  const d = _crowd[idx];

  // KPIs
  $("crowd-kpi-attendance").textContent = formatNum(d.attendance);
  $("crowd-kpi-density").textContent    = d.density_class;
  $("crowd-kpi-auth").textContent       = (d.authenticity * 100).toFixed(1) + "%";

  // Heatmap
  renderHeatmap(d.heatmap || [], "heatmap-container");

  // Zone occupancy radar
  const zones = d.zones;
  getOrDestroyChart("zoneChart", {
    type: "bar",
    data: {
      labels: Object.keys(zones).map(k => k.replace(/_/g," ")),
      datasets: [{
        label: "Occupancy %",
        data: Object.values(zones).map(v => +(v*100).toFixed(1)),
        backgroundColor: [COLORS.gold, COLORS.blue, COLORS.purple,
                          COLORS.green, COLORS.cyan],
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ display:false } },
      scales: {
        x: { grid:chartGrid() },
        y: { grid:chartGrid(), max:100, ticks:{ callback:v=>v+"%" } }
      }
    }
  });

  // Demographic donut
  const demo = d.demographics;
  getOrDestroyChart("demographicChart", {
    type: "doughnut",
    data: {
      labels: ["Youth 18-30", "Middle-Aged 31-50", "Senior 51+"],
      datasets: [{
        data: [
          +(demo.youth_18_30*100).toFixed(1),
          +(demo.middle_aged_31_50*100).toFixed(1),
          +(demo.senior_51_plus*100).toFixed(1)
        ],
        backgroundColor: [COLORS.blue, COLORS.gold, COLORS.green],
        borderColor: "#111428", borderWidth: 3, hoverOffset: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      cutout: "60%",
      plugins: { legend:{ position:"bottom" } }
    }
  });

  // Engagement chips
  const eng = d.engagement;
  const chipsData = [
    { label: "Cheer Events",    val: eng.cheer_events_detected,        unit: "", pct: eng.cheer_events_detected/45 },
    { label: "Wave Patterns",   val: eng.wave_patterns,                unit: "", pct: eng.wave_patterns/15 },
    { label: "Movement Score",  val: (eng.crowd_movement_score*100).toFixed(0), unit: "%", pct: eng.crowd_movement_score },
    { label: "Attention Focus", val: (eng.attention_focus_score*100).toFixed(0), unit: "%", pct: eng.attention_focus_score }
  ];

  $("engagement-grid").innerHTML = chipsData.map(c => `
    <div class="metric-chip">
      <div class="metric-chip-label">${c.label}</div>
      <div class="metric-chip-value">${c.val}${c.unit}</div>
      <div class="metric-chip-bar">
        <div class="metric-chip-fill" style="width:${(c.pct*100).toFixed(0)}%"></div>
      </div>
    </div>`).join("");
}

function renderHeatmap(grid, containerId) {
  if (!grid || grid.length === 0) return;
  const ctr = $(containerId);
  ctr.innerHTML = `<div class="heatmap-grid">${grid.map(row =>
    `<div class="heatmap-row">${row.map(v => {
      const h = Math.round((1-v)*220);  // hue: 220=blue(cold)…0=red(hot)
      const s = 70, l = Math.round(25 + v * 40);
      return `<div class="heatmap-cell" style="background:hsl(${h},${s}%,${l}%)"
                   title="Density: ${(v*100).toFixed(0)}%"></div>`;
    }).join("")}</div>`
  ).join("")}</div>`;
}

// ══════════════════════════════════════════════════════════════════════════
// PAGE: SPEECH SENTIMENT
// ══════════════════════════════════════════════════════════════════════════
async function loadSentiment() {
  if (!_sentiment) _sentiment = await fetchJSON("/api/sentiment");

  const sel = $("sentiment-rally-select");
  sel.innerHTML = _sentiment.map((r, i) =>
    `<option value="${i}">${r.rally}</option>`).join("");
  sel.addEventListener("change", () => renderSentimentData(+sel.value));
  renderSentimentData(0);
}

function renderSentimentData(idx) {
  const d = _sentiment[idx];
  const s = d;

  $("sent-kpi-polarity").textContent  = (s.polarity >= 0 ? "+" : "") + s.polarity.toFixed(3);
  $("sent-kpi-tone").textContent      = s.label;
  $("sent-kpi-persuasion").textContent = (s.persuasion_score * 100).toFixed(1) + "%";
  $("sent-kpi-words").innerHTML       = "<span style='font-size:18px'>—</span>";

  // Topics bar chart
  const topicsKeys = Object.keys(s.topics);
  const topicsVals = Object.values(s.topics).map(v => +(v*100).toFixed(1));

  getOrDestroyChart("topicsChart", {
    type: "bar",
    data: {
      labels: topicsKeys.map(k => k.charAt(0).toUpperCase() + k.slice(1)),
      datasets: [{
        label: "Topic Coverage %",
        data: topicsVals,
        backgroundColor: [
          COLORS.blue, COLORS.green, COLORS.purple,
          COLORS.gold, COLORS.cyan, COLORS.red, COLORS.goldL
        ],
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ display:false } },
      scales: {
        x: { grid:chartGrid(), max:100, ticks:{ callback:v=>v+"%" } },
        y: { grid:chartGrid() }
      }
    }
  });

  // Emotional arc
  const arc = s.emotional_arc || [];
  const arcLabels = arc.map((a, i) => `${(a.position*100).toFixed(0)}%`);
  const arcData   = arc.map(a => a.avg_sentiment);

  getOrDestroyChart("emotionalArcChart", {
    type: "line",
    data: {
      labels: arcLabels,
      datasets: [{
        label: "Speech Sentiment Arc",
        data: arcData,
        borderColor: COLORS.purple, borderWidth: 2.5,
        tension: 0.5, fill: true,
        backgroundColor: (ctx) => makeGradient(ctx.chart.ctx, COLORS.purple, COLORS.purple),
        pointRadius: 3, pointHoverRadius: 6,
        pointBackgroundColor: COLORS.purpleL
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ display:false } },
      scales: {
        x: { grid:chartGrid() },
        y: { grid:chartGrid(), min:-0.5, max:0.8 }
      }
    }
  });

  // Rhetoric chart
  const rh = s.rhetorical_devices;
  getOrDestroyChart("rhetoricChart", {
    type: "polarArea",
    data: {
      labels: Object.keys(rh).map(k => k.charAt(0).toUpperCase() + k.slice(1).replace(/_/g," ")),
      datasets: [{
        data: Object.values(rh),
        backgroundColor: [COLORS.gold+"88", COLORS.blue+"88",
                          COLORS.purple+"88", COLORS.green+"88", COLORS.red+"88"]
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ position:"bottom" } },
      scales: { r: { ticks:{ backdropColor:"transparent" }, grid:{ color:COLORS.border } } }
    }
  });

  // Word cloud
  const wf = s.word_frequency || [];
  if (wf.length > 0) {
    const maxCount = wf[0].count;
    const palette = [COLORS.blue, COLORS.gold, COLORS.purple, COLORS.green,
                     COLORS.cyan, COLORS.redL, COLORS.blueL, COLORS.purpleL];
    $("wordcloud-container").innerHTML = wf.map((w, i) => {
      const size = 11 + Math.round((w.count / maxCount) * 16);
      const color = palette[i % palette.length];
      return `<span class="word-tag" style="font-size:${size}px;background:${color}18;
              color:${color};border-color:${color}30">${w.word}
              <small style="opacity:0.6;font-size:9px">${w.count}</small></span>`;
    }).join("");
  }

  // Key quotes
  const quotes = s.key_quotes || [];
  $("quotes-container").innerHTML = quotes.map(q => `
    <div class="quote-card">
      <div class="quote-text">"${q.quote}"</div>
      <div class="quote-score">Impact Score: ${(q.impact_score*100).toFixed(1)}%</div>
    </div>`).join("") || "<p style='color:var(--text-muted);padding:12px'>No quotes extracted</p>";
}

// ══════════════════════════════════════════════════════════════════════════
// PAGE: IMPACT PREDICTION
// ══════════════════════════════════════════════════════════════════════════
async function loadImpact() {
  const [impact, featImp] = await Promise.all([
    _impact ? Promise.resolve(_impact) : fetchJSON("/api/impact"),
    _featImp ? Promise.resolve(_featImp) : fetchJSON("/api/feature_importance")
  ]);
  _impact = impact; _featImp = featImp;

  const labels = impact.map(r => r.city);

  // Impact Bar
  getOrDestroyChart("impactBarChart", {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Impact Score %",
        data: impact.map(r => +(r.impact_score*100).toFixed(1)),
        backgroundColor: impact.map(r => {
          const s = r.impact_score;
          if (s > 0.75) return COLORS.gold;
          if (s > 0.55) return COLORS.blue;
          return COLORS.purple;
        }),
        borderRadius: 8, borderSkipped: false
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ display:false } },
      scales: {
        x:{ grid:chartGrid() },
        y:{ grid:chartGrid(), max:100, ticks:{ callback:v=>v+"%" } }
      }
    }
  });

  // Swing Horizontal Bar
  getOrDestroyChart("swingChart", {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Vote Swing Probability %",
        data: impact.map(r => +(r.swing_probability*100).toFixed(1)),
        backgroundColor: impact.map(r =>
          r.swing_probability > 0.5 ? COLORS.green+"cc" : COLORS.red+"cc"),
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ display:false } },
      scales: {
        x:{ grid:chartGrid(), max:100, ticks:{ callback:v=>v+"%" } },
        y:{ grid:chartGrid() }
      }
    }
  });

  // Media Reach scatter
  getOrDestroyChart("mediaReachChart", {
    type: "scatter",
    data: {
      datasets: impact.map((r, i) => ({
        label: r.city,
        data: [{ x: r.predictions.media_reach_millions,
                 y: r.predictions.social_virality_score * 100 }],
        backgroundColor: `hsl(${i*40},75%,60%)`,
        pointRadius: 10, pointHoverRadius: 14
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ position:"right", labels:{ boxWidth:10, font:{ size:10 } } } },
      scales: {
        x: { title:{ display:true, text:"Media Reach (M)", color:COLORS.text }, grid:chartGrid() },
        y: { title:{ display:true, text:"Social Virality %", color:COLORS.text }, grid:chartGrid() }
      }
    }
  });

  // Feature Importance
  getOrDestroyChart("featureImportanceChart", {
    type: "bar",
    data: {
      labels: featImp.map(f => f.feature),
      datasets: [{
        label: "Importance %",
        data: featImp.map(f => f.importance),
        backgroundColor: COLORS.purple + "cc",
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: true,
      plugins: { legend:{ display:false } },
      scales: {
        x:{ grid:chartGrid(), ticks:{ callback:v=>v+"%" } },
        y:{ grid:chartGrid() }
      }
    }
  });

  // Table
  $("impact-table-body").innerHTML = impact.map((r, i) => {
    const lc = getLevelClass(r.impact_level);
    return `<tr>
      <td>${i+1}</td>
      <td style="font-weight:600">${r.rally}</td>
      <td>${r.city}</td>
      <td style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:var(--gold-light)">
        ${(r.impact_score*100).toFixed(1)}%</td>
      <td><span class="level-badge ${lc}">${r.impact_level}</span></td>
      <td>${(r.swing_probability*100).toFixed(1)}%</td>
      <td>${r.predictions.media_reach_millions.toFixed(1)}M</td>
      <td>+${r.predictions.fundraising_lift_pct.toFixed(1)}%</td>
    </tr>`;
  }).join("");
}

// ══════════════════════════════════════════════════════════════════════════
// PAGE: ELECTION FORECAST
// ══════════════════════════════════════════════════════════════════════════
async function loadForecast() {
  if (!_forecast) _forecast = await fetchJSON("/api/forecast");
  const d = _forecast;

  // KPIs
  $("fc-kpi-winprob").textContent    = (d.projected_win_probability*100).toFixed(1) + "%";
  $("fc-kpi-reach").textContent      = d.total_media_reach_millions.toFixed(1) + "M";
  $("fc-kpi-momentum").textContent   = (d.overall_momentum*100).toFixed(1) + "%";
  $("fc-kpi-confidence").textContent = (d.forecast_confidence*100).toFixed(1) + "%";

  // Polling Chart
  const pc = d.polling_curve;
  getOrDestroyChart("pollingChart", {
    type: "line",
    data: {
      labels: pc.map(p => p.date),
      datasets: [
        {
          label: "Polling Lead (%)",
          data: pc.map(p => p.polling_lead),
          borderColor: COLORS.gold, borderWidth: 2.5,
          tension: 0.4, fill: true,
          backgroundColor: ctx => makeGradient(ctx.chart.ctx, COLORS.gold, COLORS.gold),
          pointRadius: 5, pointHoverRadius: 8,
          pointBackgroundColor: COLORS.goldL
        },
        {
          label: "Upper MoE",
          data: pc.map(p => p.polling_lead + p.margin_of_error),
          borderColor: COLORS.gold+"40", borderWidth: 1,
          borderDash: [4,4], tension: 0.4, pointRadius: 0, fill:false
        },
        {
          label: "Lower MoE",
          data: pc.map(p => p.polling_lead - p.margin_of_error),
          borderColor: COLORS.gold+"40", borderWidth: 1,
          borderDash: [4,4], tension: 0.4, pointRadius: 0, fill:false
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: {
        legend:{ labels:{ filter: item => !item.text.includes("MoE") } },
        tooltip:{ mode:"index", intersect:false }
      },
      scales: {
        x:{ grid:chartGrid() },
        y:{ grid:chartGrid(), ticks:{ callback:v=>v+"%" } }
      }
    }
  });

  // States grid
  $("states-grid").innerHTML = d.key_states.map(s => {
    const leanClass = s.lean.includes("D") ? "lean-d" :
                      s.lean.includes("R") ? "lean-r" : "lean-toss";
    return `
      <div class="state-row">
        <div class="state-name">${s.state}</div>
        <div class="state-lean ${leanClass}">${s.lean}</div>
        <div class="state-prob-bar">
          <div class="state-prob-fill" style="width:${(s.swing_prob*100).toFixed(0)}%"></div>
        </div>
        <div class="state-prob-val">${(s.swing_prob*100).toFixed(1)}%</div>
      </div>`;
  }).join("");

  // Gauge
  const momentum = d.overall_momentum;
  const angle = -90 + momentum * 180;
  $("gauge-container").innerHTML = `
    <div class="gauge-wrap">
      <div class="gauge-bg"></div>
      <div class="gauge-mask"></div>
      <div class="gauge-needle" id="gauge-needle" style="transform:rotate(${-90}deg)"></div>
    </div>
    <div class="gauge-labels">
      <span>Low</span><span>Medium</span><span>High</span>
    </div>
    <div class="gauge-value-text">${(momentum*100).toFixed(1)}%</div>
    <div class="gauge-sub">Campaign Momentum Score</div>`;

  setTimeout(() => {
    const needle = document.getElementById("gauge-needle");
    if (needle) needle.style.transform = `rotate(${angle}deg)`;
  }, 200);
}

// ══════════════════════════════════════════════════════════════════════════
// PAGE: ANALYST STUDIO
// ══════════════════════════════════════════════════════════════════════════
async function runAnalysis() {
  const btn = $("analyze-btn");
  const loading = $("analyze-loading");
  const results = $("analyst-results");

  btn.disabled = true;
  loading.style.display = "flex";

  const payload = {
    speaker:        $("an-speaker").value || "Analyst Demo",
    rally_name:     $("an-rally").value || "Custom Rally",
    speech_text:    $("an-speech").value,
    attendance:     +$("an-attendance").value || 50000,
    days_to_election: +$("an-days").value || 30,
    battleground:   +$("an-battleground").value,
    incumbent:      +$("an-incumbent").value,
  };

  try {
    const res = await fetch(API + "/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    loading.style.display = "none";
    btn.disabled = false;

    renderAnalystResults(data);
    showToast("✅ Analysis complete!");
  } catch(e) {
    loading.style.display = "none";
    btn.disabled = false;
    showToast("❌ Analysis failed. Is the server running?");
    console.error(e);
  }
}

function renderAnalystResults(d) {
  const { crowd, speech, impact } = d;
  const s = speech.overall_sentiment;

  const sentColor_str = s.overall_polarity > 0.05 ? "#10b981" :
                        s.overall_polarity < -0.05 ? "#ef4444" : "#f59e0b";

  const topicBars = Object.entries(speech.topics || {})
    .sort((a,b) => b[1]-a[1])
    .map(([k,v]) => `
      <div class="topic-bar-row">
        <div class="topic-bar-label">${k}</div>
        <div class="topic-bar-track">
          <div class="topic-bar-fill" style="width:${(v*100).toFixed(0)}%"></div>
        </div>
        <div class="topic-bar-val">${(v*100).toFixed(1)}%</div>
      </div>`).join("");

  const quotes = (speech.key_quotes || []).slice(0,3).map(q =>
    `<div class="quote-card" style="margin-bottom:8px">
       <div class="quote-text">"${q.quote}"</div>
       <div class="quote-score">Impact: ${(q.impact_score*100).toFixed(1)}%</div>
     </div>`).join("");

  $("analyst-results").innerHTML = `
    <div class="results-content">

      <div>
        <div class="result-section-title">📊 Impact Prediction</div>
        <div class="score-display">
          <div class="score-chip">
            <div class="score-chip-val" style="color:var(--gold-light)">
              ${(impact.impact_score*100).toFixed(0)}%</div>
            <div class="score-chip-lbl">Impact Score</div>
          </div>
          <div class="score-chip">
            <div class="score-chip-val" style="color:var(--blue-light)">
              ${(impact.vote_swing_probability*100).toFixed(0)}%</div>
            <div class="score-chip-lbl">Swing Prob.</div>
          </div>
          <div class="score-chip">
            <div class="score-chip-val" style="color:var(--green-light)">
              ${impact.predictions.media_reach_millions.toFixed(1)}M</div>
            <div class="score-chip-lbl">Media Reach</div>
          </div>
          <div class="score-chip">
            <div class="score-chip-val" style="color:var(--purple-light)">
              +${impact.predictions.fundraising_lift_pct.toFixed(0)}%</div>
            <div class="score-chip-lbl">Fundraising Lift</div>
          </div>
        </div>
        <div style="margin-top:12px;padding:10px 14px;background:rgba(245,158,11,0.08);
             border-radius:8px;font-size:14px;font-weight:600;color:var(--gold-light);
             border:1px solid rgba(245,158,11,0.2)">
          Impact Level: ${impact.impact_level}
        </div>
      </div>

      <div>
        <div class="result-section-title">💬 Speech Sentiment</div>
        <div class="result-metric-row">
          <span class="rm-label">Overall Polarity</span>
          <span class="rm-value" style="color:${sentColor_str}">
            ${(s.overall_polarity >= 0 ? "+" : "")}${s.overall_polarity.toFixed(3)}</span>
        </div>
        <div class="result-metric-row">
          <span class="rm-label">Tone</span>
          <span class="rm-value">${s.label}</span>
        </div>
        <div class="result-metric-row">
          <span class="rm-label">Positive Sentences</span>
          <span class="rm-value" style="color:var(--green-light)">${(s.positive_ratio*100).toFixed(0)}%</span>
        </div>
        <div class="result-metric-row">
          <span class="rm-label">Persuasion Score</span>
          <span class="rm-value" style="color:var(--blue-light)">${(speech.persuasion_score*100).toFixed(1)}%</span>
        </div>
      </div>

      <div>
        <div class="result-section-title">🏷 Topic Coverage</div>
        <div class="topic-bars">${topicBars}</div>
      </div>

      <div>
        <div class="result-section-title">👥 Crowd Metrics</div>
        <div class="result-metric-row">
          <span class="rm-label">Density Class</span>
          <span class="rm-value">${crowd.density_class}</span>
        </div>
        <div class="result-metric-row">
          <span class="rm-label">Crowd Authenticity</span>
          <span class="rm-value">${(crowd.authenticity_score*100).toFixed(1)}%</span>
        </div>
        <div class="result-metric-row">
          <span class="rm-label">Engagement Score</span>
          <span class="rm-value">${(crowd.engagement_metrics.attention_focus_score*100).toFixed(1)}%</span>
        </div>
      </div>

      <div>
        <div class="result-section-title">💬 Key Quotes Extracted</div>
        ${quotes || "<p style='color:var(--text-muted);font-size:13px'>No outstanding quotes found.</p>"}
      </div>

    </div>`;
}

// ══════════════════════════════════════════════════════════════════════════
// NAVIGATION
// ══════════════════════════════════════════════════════════════════════════
const PAGE_META = {
  overview: { title:"Overview Dashboard", subtitle:"Real-time political intelligence & analysis" },
  crowd:    { title:"Crowd Detection CNN", subtitle:"AI-powered rally attendance & density analysis" },
  sentiment:{ title:"Speech Sentiment Analyzer", subtitle:"NLP-driven political speech processing" },
  impact:   { title:"Impact Prediction Model", subtitle:"ML-based election impact forecasting" },
  forecast: { title:"Election Forecast", subtitle:"Aggregated campaign trajectory & state predictions" },
  analyst:  { title:"Analyst Studio", subtitle:"Custom speech & rally analysis tool" }
};

const PAGE_LOADERS = {
  overview: loadOverview,
  crowd:    loadCrowd,
  sentiment:loadSentiment,
  impact:   loadImpact,
  forecast: loadForecast,
  analyst:  () => {}   // no initial data fetch needed
};

let _loaded = {};

function navigate(page) {
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));

  const navEl = document.querySelector(`[data-page="${page}"]`);
  const pageEl = $(`page-${page}`);
  if (navEl) navEl.classList.add("active");
  if (pageEl) pageEl.classList.add("active");

  const meta = PAGE_META[page] || { title:page, subtitle:"" };
  $("page-title").textContent    = meta.title;
  $("page-subtitle").textContent = meta.subtitle;

  if (!_loaded[page]) {
    _loaded[page] = true;
    PAGE_LOADERS[page]().catch(err => {
      console.error(`Error loading ${page}:`, err);
      showToast(`⚠️ Failed to load ${meta.title} data`);
    });
  }
}

function toggleSidebar() {
  $("sidebar").classList.toggle("open");
}

// ── Init ──────────────────────────────────────────────────────────────────
document.querySelectorAll(".nav-item").forEach(item => {
  item.addEventListener("click", () => {
    navigate(item.dataset.page);
    if (window.innerWidth < 900) $("sidebar").classList.remove("open");
  });
});

// Auto-preload overview on startup
navigate("overview");

// Preload popular pages in background after 2s
setTimeout(() => {
  ["impact", "forecast"].forEach(p => {
    if (!_loaded[p]) {
      _loaded[p] = true;
      PAGE_LOADERS[p]().catch(() => {});
    }
  });
}, 2000);
