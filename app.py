from flask import Flask, request, jsonify, Response
from agent import run_pathwise_structured, run_whatif_structured, generate_tab_content
import json

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<title>Pathwise</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bebas+Neue&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root {
  --primary: #0084C7;
  --black: #0a0a0a;
  --white: #f5f0e8;
  --yellow: #FFE500;
  --red: #FF2D00;
  --green: #00C853;
  --border: 3px solid #0a0a0a;
  --border-thin: 2px solid #0a0a0a;
  --shadow: 5px 5px 0px #0a0a0a;
  --shadow-sm: 3px 3px 0px #0a0a0a;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'DM Sans', sans-serif;
  background: var(--white);
  color: var(--black);
  min-height: 100vh;
}

/* HEADER */
.header {
  background: var(--black);
  border-bottom: var(--border);
  padding: 0 40px;
  position: sticky;
  top: 0;
  z-index: 200;
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem;
  color: var(--white);
  letter-spacing: 0.05em;
}
.logo span { color: var(--primary); }
.badge {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  color: var(--black);
  background: var(--yellow);
  border: var(--border-thin);
  padding: 4px 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* HERO */
.hero {
  background: var(--primary);
  border-bottom: var(--border);
  padding: 60px 40px 52px;
}
.hero-inner { max-width: 1100px; margin: 0 auto; }
.hero h1 {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(3.5rem, 8vw, 7rem);
  color: var(--white);
  letter-spacing: 0.02em;
  line-height: 0.95;
  margin-bottom: 20px;
}
.hero h1 span { color: var(--yellow); }
.hero-sub {
  font-family: 'Space Mono', monospace;
  font-size: 0.82rem;
  color: var(--white);
  opacity: 0.8;
  max-width: 560px;
  line-height: 1.8;
  margin-bottom: 24px;
}
.hero-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.hero-tag {
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: var(--black);
  color: var(--white);
  padding: 5px 12px;
  border: var(--border-thin);
}

/* MAIN */
.main { max-width: 1100px; margin: 0 auto; padding: 40px 20px 80px; }

/* TABS */
.tabs {
  display: flex;
  border: var(--border);
  margin-bottom: 36px;
  background: var(--black);
  overflow-x: auto;
}
.tabs::-webkit-scrollbar { display: none; }
.tab-btn {
  background: var(--black);
  border: none;
  border-right: var(--border);
  padding: 14px 20px;
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  color: rgba(245,240,232,0.4);
  cursor: pointer;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  transition: background 0.1s, color 0.1s;
}
.tab-btn:last-child { border-right: none; }
.tab-btn:hover { background: #1a1a1a; color: var(--white); }
.tab-btn.active {
  background: var(--primary);
  color: var(--white);
}
.panel { display: none; }
.panel.active { display: block; }

/* SECTION HEADER */
.section-header { margin-bottom: 28px; }
.section-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.8rem;
  letter-spacing: 0.02em;
  line-height: 1;
  margin-bottom: 6px;
}
.section-sub {
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  color: #555;
  line-height: 1.7;
}

/* CARDS */
.card {
  background: var(--white);
  border: var(--border);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
}
.card-dark {
  background: var(--black);
  border: var(--border);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
  color: var(--white);
}
.card-accent {
  background: var(--primary);
  border: var(--border);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
  color: var(--white);
}

/* EYEBROW */
.eyebrow {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #888;
  margin-bottom: 10px;
  display: block;
}
.eyebrow-light {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(245,240,232,0.5);
  margin-bottom: 10px;
  display: block;
}

/* FORM */
label {
  display: block;
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #555;
  margin-bottom: 8px;
}
textarea, input[type="number"] {
  width: 100%;
  background: var(--white);
  border: var(--border);
  color: var(--black);
  font-family: 'Space Mono', monospace;
  font-size: 0.85rem;
  padding: 12px 14px;
  outline: none;
  transition: box-shadow 0.1s;
  resize: vertical;
}
textarea { min-height: 100px; }
textarea:focus, input:focus {
  box-shadow: var(--shadow);
  border-color: var(--primary);
}

/* BUTTON */
.btn {
  display: inline-block;
  background: var(--black);
  color: var(--white);
  border: var(--border);
  padding: 14px 28px;
  font-family: 'Space Mono', monospace;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
  box-shadow: var(--shadow);
  transition: transform 0.1s, box-shadow 0.1s;
  margin-top: 14px;
  width: 100%;
  text-align: center;
}
.btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 7px 7px 0px var(--black);
}
.btn:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px var(--black);
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow);
}
.btn-primary {
  background: var(--primary);
  color: var(--white);
}
.btn-yellow {
  background: var(--yellow);
  color: var(--black);
}

/* STEPS */
.steps-card {
  background: var(--black);
  border: var(--border);
  padding: 20px 24px;
  margin-bottom: 16px;
  display: none;
}
.steps-title {
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(245,240,232,0.5);
  margin-bottom: 16px;
}
.steps { display: flex; flex-direction: column; gap: 10px; }
.step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  color: rgba(245,240,232,0.3);
  transition: color 0.2s;
}
.step.active { color: var(--white); }
.step.done { color: var(--green); }
.step-icon {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(245,240,232,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 700;
  flex-shrink: 0;
  color: rgba(245,240,232,0.3);
  transition: all 0.2s;
  font-family: 'Space Mono', monospace;
}
.step.active .step-icon { border-color: var(--primary); color: var(--primary); background: rgba(0,132,199,0.15); }
.step.done .step-icon { border-color: var(--green); background: var(--green); color: var(--black); }
.step-body { flex: 1; }
.step-label { font-weight: 700; line-height: 1.4; }
.step-detail { font-size: 0.68rem; color: rgba(245,240,232,0.4); margin-top: 2px; display: none; }
.step.active .step-detail { display: block; }
.step-spin {
  width: 14px; height: 14px;
  border: 2px solid rgba(0,132,199,0.2);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
  margin-top: 3px;
  display: none;
}
.step.active .step-spin { display: block; }
.step.done .step-spin { display: none; }
@keyframes spin { to { transform: rotate(360deg); } }

/* STATS */
.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
.stat {
  background: var(--white);
  border: var(--border);
  padding: 16px;
  box-shadow: var(--shadow-sm);
}
.stat-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #888;
  display: block;
  margin-bottom: 6px;
}
.stat-value {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem;
  line-height: 1;
  display: block;
  letter-spacing: 0.02em;
}
.stat-note {
  font-family: 'Space Mono', monospace;
  font-size: 0.62rem;
  color: #888;
  margin-top: 4px;
  display: block;
}

/* BARS */
.bar-row { display: grid; grid-template-columns: 140px 1fr 72px 44px; align-items: center; gap: 10px; margin-bottom: 10px; }
.bar-label { font-family: 'Space Mono', monospace; font-size: 0.72rem; }
.bar-track { background: #ddd; border: var(--border-thin); height: 18px; overflow: hidden; }
.bar-fill { height: 100%; transition: width 0.5s ease; }
.bar-amt { font-family: 'Space Mono', monospace; font-size: 0.72rem; font-weight: 700; text-align: right; }
.bar-pct { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #888; text-align: right; }

/* ALERTS */
.alert {
  border: var(--border);
  padding: 12px 16px;
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  line-height: 1.6;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
}
.alert-good { background: #e6fff0; border-left: 6px solid var(--green); }
.alert-warn { background: #fff0ee; border-left: 6px solid var(--red); }
.alert-info { background: #e6f4ff; border-left: 6px solid var(--primary); }
.alert-neutral { background: #f5f0e8; border-left: 6px solid #888; }

/* PLACEHOLDER */
.placeholder {
  background: var(--white);
  border: var(--border);
  padding: 60px 28px;
  text-align: center;
  box-shadow: var(--shadow);
}
.placeholder-icon { font-size: 2.4rem; margin-bottom: 12px; }
.placeholder-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.8rem;
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}
.placeholder-sub {
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  color: #888;
  line-height: 1.7;
  max-width: 340px;
  margin: 0 auto;
}

/* TIMELINE */
.timeline { display: flex; flex-direction: column; }
.tl-item { display: flex; gap: 16px; padding-bottom: 24px; }
.tl-item:last-child { padding-bottom: 0; }
.tl-left { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; }
.tl-dot {
  width: 32px; height: 32px;
  border: var(--border);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1rem;
  color: var(--white);
  flex-shrink: 0;
}
.tl-line { width: 3px; flex: 1; background: var(--black); margin-top: 4px; min-height: 16px; }
.tl-right { flex: 1; padding-top: 4px; }
.tl-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #888;
  margin-bottom: 4px;
}
.tl-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.3rem;
  letter-spacing: 0.02em;
  margin-bottom: 10px;
}
.tl-alloc { display: flex; flex-direction: column; gap: 5px; margin-bottom: 10px; }
.tl-alloc-row { display: flex; justify-content: space-between; font-family: 'Space Mono', monospace; font-size: 0.72rem; }
.tl-alloc-key { color: #666; }
.tl-alloc-val { font-weight: 700; }
.tl-guidance { font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #666; line-height: 1.6; }

/* DEBT ITEMS */
.debt-item {
  background: var(--white);
  border: var(--border);
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
}
.debt-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.debt-name { font-family: 'Space Mono', monospace; font-size: 0.82rem; font-weight: 700; }
.debt-badge {
  font-family: 'Space Mono', monospace;
  font-size: 0.62rem;
  font-weight: 700;
  padding: 3px 8px;
  border: var(--border-thin);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.badge-hi { background: var(--red); color: var(--white); border-color: var(--red); }
.badge-lo { background: var(--primary); color: var(--white); border-color: var(--primary); }
.debt-meta { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #666; display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }
.debt-bar { background: #ddd; border: var(--border-thin); height: 8px; overflow: hidden; }
.debt-bar-fill { height: 100%; }

/* MILESTONES */
.ms-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.ms-card {
  background: var(--white);
  border: var(--border);
  padding: 20px;
  border-top: 6px solid var(--black);
  box-shadow: var(--shadow);
}
.ms-stage-label {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.2rem;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  display: block;
}
.ms-stage-desc { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #666; margin-bottom: 14px; line-height: 1.6; }
.ms-item { display: flex; gap: 10px; margin-bottom: 12px; }
.ms-dot { width: 8px; height: 8px; border: 2px solid var(--black); flex-shrink: 0; margin-top: 5px; }
.ms-item-body { flex: 1; }
.ms-item-label { font-family: 'Space Mono', monospace; font-size: 0.75rem; font-weight: 700; margin-bottom: 2px; }
.ms-item-target { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #888; }
.ms-item-why { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #666; margin-top: 3px; line-height: 1.5; }

/* INVESTING */
.inv-header {
  background: var(--black);
  border: var(--border);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
}
.inv-header-title { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: var(--white); margin-bottom: 6px; letter-spacing: 0.02em; }
.inv-header-body { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: rgba(245,240,232,0.5); line-height: 1.7; }
.acc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px; }
.acc-card { background: var(--white); border: var(--border); padding: 18px; box-shadow: var(--shadow-sm); }
.acc-priority { font-family: 'Space Mono', monospace; font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; display: block; }
.acc-amount { font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; margin-bottom: 2px; letter-spacing: 0.02em; }
.acc-status { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #888; margin-bottom: 10px; }
.acc-what { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #666; line-height: 1.6; margin-bottom: 8px; }
.acc-why { font-family: 'Space Mono', monospace; font-size: 0.7rem; line-height: 1.6; padding: 10px 12px; background: #f0ebe0; border: var(--border-thin); }
.acc-where { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #888; margin-top: 8px; }
.avoid-row { display: flex; gap: 12px; background: #fff0ee; border: var(--border); padding: 12px 14px; margin-bottom: 10px; box-shadow: var(--shadow-sm); }
.avoid-thing { font-family: 'Space Mono', monospace; font-size: 0.75rem; font-weight: 700; color: var(--red); margin-bottom: 4px; }
.avoid-reason { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #666; line-height: 1.6; }

/* COMPARE */
.compare-wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.compare-col { border: var(--border); padding: 18px; box-shadow: var(--shadow-sm); }
.compare-orig { background: var(--white); }
.compare-new { background: #e6f4ff; }
.compare-col-label { font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 0.03em; margin-bottom: 12px; display: block; }
.compare-row { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 2px solid #0a0a0a22; font-family: 'Space Mono', monospace; font-size: 0.72rem; }
.compare-row:last-child { border-bottom: none; }
.compare-key { color: #666; }
.compare-val { font-weight: 700; }
.compare-val.up { color: var(--green); }

/* FUTURE */
.future-slider-card { background: var(--white); border: var(--border); padding: 24px; margin-bottom: 16px; box-shadow: var(--shadow); }
.age-big { font-family: 'Bebas Neue', sans-serif; font-size: 5rem; letter-spacing: -0.02em; line-height: 1; }
.age-sub { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #888; margin-top: 4px; margin-bottom: 20px; }
input[type="range"] { width: 100%; accent-color: var(--primary); background: transparent; padding: 0; margin: 0; }
input[type="range"]:focus { box-shadow: none; }
.future-scenario-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.future-sc { border: var(--border); padding: 16px; box-shadow: var(--shadow-sm); }
.future-sc-best { background: #e6fff0; }
.future-sc-real { background: #fff8e6; }
.future-sc-label { font-family: 'Space Mono', monospace; font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; display: block; }
.future-sc-val { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; margin-bottom: 6px; letter-spacing: 0.02em; }
.future-sc-desc { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #666; line-height: 1.6; }
.milestone-check { display: flex; gap: 12px; align-items: flex-start; padding: 12px 0; border-bottom: 2px solid #0a0a0a22; }
.milestone-check:last-child { border-bottom: none; }
.check-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.check-body { flex: 1; }
.check-label { font-family: 'Space Mono', monospace; font-size: 0.78rem; font-weight: 700; margin-bottom: 3px; }
.check-detail { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #666; line-height: 1.6; }

/* CHART */
.chart-wrap { position: relative; height: 220px; margin: 14px 0; border: var(--border); padding: 8px; background: var(--white); }
.chart-wrap-sm { position: relative; height: 180px; margin: 14px 0; border: var(--border); padding: 8px; background: var(--white); }

/* TWO COL */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.three-col { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; }

/* BODY TEXT */
.body-text { font-size: 0.88rem; line-height: 1.7; }
.muted-text { font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #666; line-height: 1.7; }
.card-flat { background: #f0ebe0; border: var(--border-thin); padding: 16px 18px; margin-bottom: 12px; }

/* FOOTER */
.footer {
  text-align: center;
  padding: 28px;
  border-top: var(--border);
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  color: #888;
  background: var(--black);
  color: rgba(245,240,232,0.4);
}

@media (max-width: 640px) {
  .two-col, .three-col, .compare-wrap, .future-scenario-row { grid-template-columns: 1fr; }
  .hero h1 { font-size: 3rem; }
  .header { padding: 0 20px; }
  .main { padding: 24px 16px 60px; }
  .bar-row { grid-template-columns: 100px 1fr 56px 36px; }
  .age-big { font-size: 3.5rem; }
  .tabs { flex-wrap: wrap; }
}
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <span class="logo">PATH<span>WISE</span></span>
    <span class="badge">NVIDIA Nemotron</span>
  </div>
</div>

<div class="hero">
  <div class="hero-inner">
    <h1>YOUR MONEY.<br><span>YOUR PLAN.</span></h1>
    <p class="hero-sub">Describe your finances in plain English. Pathwise fetches live rates and builds your personalized roadmap — powered by NVIDIA Nemotron via OpenClaw.</p>
    <div class="hero-tags">
      <span class="hero-tag">Live Market Data</span>
      <span class="hero-tag">OpenClaw Agent</span>
      <span class="hero-tag">What-If Scenarios</span>
      <span class="hero-tag">Persistent Memory</span>
    </div>
  </div>
</div>

<div class="main">
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('plan',this)">Build My Plan</button>
    <button class="tab-btn" onclick="switchTab('whatif',this)">What-If</button>
    <button class="tab-btn" onclick="switchTab('paycheck',this)">Paycheck</button>
    <button class="tab-btn" onclick="switchTab('milestones',this)">Milestones</button>
    <button class="tab-btn" onclick="switchTab('investing',this)">Investing</button>
    <button class="tab-btn" onclick="switchTab('future',this)">Future You</button>
  </div>

  <!-- BUILD MY PLAN -->
  <div id="tab-plan" class="panel active">
    <div class="section-header">
      <div class="section-title">BUILD MY ROADMAP</div>
      <div class="section-sub">Describe your situation and Nemotron will build a month-by-month plan using live market data.</div>
    </div>
    <div class="card">
      <label>Your financial situation</label>
      <textarea id="situation" placeholder="e.g. I am 22, make $2,500/month as a software intern, have $5,000 in student loans at 5% and $1,500 in credit card debt at 19% APR. Monthly expenses are $1,200. I want to be debt free in 2 years and start a Roth IRA."></textarea>
      <button class="btn btn-primary" id="plan-btn" onclick="buildPlan()">Generate My Roadmap</button>
    </div>
    <div class="steps-card" id="plan-sc">
      <div class="steps-title">// Nemotron is working on your plan</div>
      <div class="steps">
        <div class="step" id="ps1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Loading your memory</div><div class="step-detail">Checking for past sessions and saved profile data</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Fetching live market rates</div><div class="step-detail">Searching current HYSA, mortgage, and S&P 500 data</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Extracting your financial profile</div><div class="step-detail">Parsing income, debts, expenses, and goals</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Nemotron building your roadmap</div><div class="step-detail">Reasoning through priorities and generating month-by-month allocations</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Saving to memory</div><div class="step-detail">Storing your plan for What-If and other tabs</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps6"><div class="step-icon">6</div><div class="step-body"><div class="step-label">Rendering your dashboard</div><div class="step-detail">Building charts, timelines, and visualizations</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="plan-result"></div>
  </div>

  <!-- WHAT-IF -->
  <div id="tab-whatif" class="panel">
    <div class="section-header">
      <div class="section-title">WHAT-IF SCENARIOS</div>
      <div class="section-sub">Explore how a change affects your entire plan — with a clear breakdown of what changes and why.</div>
    </div>
    <div class="card">
      <label>Describe a scenario</label>
      <textarea id="scenario" placeholder="e.g. What if I get a raise to $5,000/month? What if I put an extra $200 toward my credit card?"></textarea>
      <button class="btn btn-primary" id="wi-btn" onclick="runWhatIf()">Run Scenario</button>
    </div>
    <div class="steps-card" id="wi-sc">
      <div class="steps-title">// Nemotron is analyzing your scenario</div>
      <div class="steps">
        <div class="step" id="ws1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Loading your existing plan</div><div class="step-detail">Reading your saved financial roadmap from memory</div></div><div class="step-spin"></div></div>
        <div class="step" id="ws2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Understanding the scenario</div><div class="step-detail">Identifying what changes and what stays the same</div></div><div class="step-spin"></div></div>
        <div class="step" id="ws3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is recalculating</div><div class="step-detail">Rerunning debt timelines, surplus, and investment capacity</div></div><div class="step-spin"></div></div>
        <div class="step" id="ws4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Building the comparison</div><div class="step-detail">Generating side-by-side metrics and chart data</div></div><div class="step-spin"></div></div>
        <div class="step" id="ws5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your results</div><div class="step-detail">Drawing comparison cards and surplus chart</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="wi-result"></div>
  </div>

  <!-- PAYCHECK -->
  <div id="tab-paycheck" class="panel">
    <div class="section-header">
      <div class="section-title">PAYCHECK BREAKDOWN</div>
      <div class="section-sub">See where every dollar goes and where you can find more money for your goals.</div>
    </div>
    <div class="card">
      <div style="margin-bottom:18px"><label>Monthly Take-Home Income</label><input type="number" id="pay-income" placeholder="e.g. 2500"></div>
      <div class="two-col">
        <div><label>Rent / Housing</label><input type="number" id="pay-rent" value="0"></div>
        <div><label>Groceries</label><input type="number" id="pay-groceries" value="0"></div>
        <div><label>Subscriptions</label><input type="number" id="pay-subscriptions" value="0"></div>
        <div><label>Transport</label><input type="number" id="pay-transport" value="0"></div>
        <div><label>Dining Out</label><input type="number" id="pay-dining" value="0"></div>
        <div><label>Savings</label><input type="number" id="pay-savings" value="0"></div>
        <div><label>Debt Payments</label><input type="number" id="pay-debt" value="0"></div>
        <div><label>Other</label><input type="number" id="pay-other" value="0"></div>
      </div>
      <button class="btn btn-primary" onclick="calcPaycheck()">Analyze My Paycheck</button>
    </div>
    <div class="steps-card" id="pc-sc">
      <div class="steps-title">// Analyzing your paycheck</div>
      <div class="steps">
        <div class="step" id="pcs1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Calculating totals and surplus</div></div><div class="step-spin"></div></div>
        <div class="step" id="pcs2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Benchmarking your spending</div></div><div class="step-spin"></div></div>
        <div class="step" id="pcs3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Finding optimization opportunities</div></div><div class="step-spin"></div></div>
        <div class="step" id="pcs4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Rendering your dashboard</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="pc-result"></div>
  </div>

  <!-- MILESTONES -->
  <div id="tab-milestones" class="panel">
    <div class="section-header">
      <div class="section-title">FINANCIAL MILESTONES</div>
      <div class="section-sub">Your personalized roadmap — real targets and timelines based on your actual situation.</div>
    </div>
    <div id="ms-placeholder" class="placeholder">
      <div class="placeholder-icon">[ ]</div>
      <div class="placeholder-title">Build your plan first</div>
      <div class="placeholder-sub">Pathwise will generate personalized milestones with real dollar targets and the reasoning behind each one.</div>
    </div>
    <div class="steps-card" id="ms-sc">
      <div class="steps-title">// Nemotron is generating your milestones</div>
      <div class="steps">
        <div class="step" id="mss1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Reading your financial plan</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Assessing your current stage</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is setting your targets</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Calculating your progress</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your milestone board</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="ms-result"></div>
  </div>

  <!-- INVESTING -->
  <div id="tab-investing" class="panel">
    <div class="section-header">
      <div class="section-title">INVESTING STRATEGY</div>
      <div class="section-sub">A personalized plan explaining what to open, when to start, and how much to contribute.</div>
    </div>
    <div id="inv-placeholder" class="placeholder">
      <div class="placeholder-icon">[ ]</div>
      <div class="placeholder-title">Build your plan first</div>
      <div class="placeholder-sub">Pathwise will generate a personalized investing strategy based on your income, debts, and goals.</div>
    </div>
    <div class="steps-card" id="inv-sc">
      <div class="steps-title">// Nemotron is building your investing strategy</div>
      <div class="steps">
        <div class="step" id="invs1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Evaluating your investing readiness</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Calculating your contribution capacity</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is selecting your accounts</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Projecting your portfolio growth</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your strategy</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="inv-result"></div>
  </div>

  <!-- FUTURE YOU -->
  <div id="tab-future" class="panel">
    <div class="section-header">
      <div class="section-title">FUTURE YOU</div>
      <div class="section-sub">Slide to any age and see a realistic projection of your net worth and what the numbers mean for your life.</div>
    </div>
    <div id="fut-placeholder" class="placeholder">
      <div class="placeholder-icon">[ ]</div>
      <div class="placeholder-title">Build your plan first</div>
      <div class="placeholder-sub">Pathwise will project your financial future at any age based on your real numbers.</div>
    </div>
    <div id="fut-slider-card" class="future-slider-card" style="display:none">
      <div class="age-big" id="fut-age-display">25</div>
      <div class="age-sub">// years old</div>
      <input type="range" min="18" max="65" value="25" id="fut-slider" oninput="onFutureSlide(this.value)">
    </div>
    <div class="steps-card" id="fut-sc">
      <div class="steps-title">// Nemotron is projecting your future</div>
      <div class="steps">
        <div class="step" id="futs1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Reading your financial plan</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Calculating your debt-free timeline</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is modeling your net worth</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Generating best and realistic scenarios</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your future dashboard</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="fut-result"></div>
  </div>
</div>

<div class="footer">HACK-A-CLAW 2026 &nbsp;·&nbsp; NVIDIA × UCSC BASKIN ENGINEERING &nbsp;·&nbsp; BUILT WITH OPENCLAW + NEMOTRON</div>

<script>
const S = {
  plan: null, situation: null, whatif: null, paycheck: null,
  msGenerated: false, invGenerated: false, futCache: {}, futAge: 25,
  charts: {}
};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const fmt = n => '$' + Math.round(n || 0).toLocaleString();
const C = { blue:'#0084C7', green:'#00C853', orange:'#FF9500', red:'#FF2D00', purple:'#7C3AED', yellow:'#FFE500' };
const destroyChart = k => { if (S.charts[k]) { S.charts[k].destroy(); delete S.charts[k]; } };

function showSC(id) { document.getElementById(id).style.display = 'block'; }
function hideSC(id) { document.getElementById(id).style.display = 'none'; }
function resetSteps(prefix, total) {
  for (let i = 1; i <= total; i++) {
    const el = document.getElementById(prefix + i);
    if (!el) continue;
    el.className = 'step';
    el.querySelector('.step-icon').textContent = i;
  }
}
function setStep(prefix, n, total) {
  for (let i = 1; i <= total; i++) {
    const el = document.getElementById(prefix + i);
    if (!el) continue;
    if (i < n) { el.className = 'step done'; el.querySelector('.step-icon').textContent = '✓'; }
    else if (i === n) el.className = 'step active';
    else { el.className = 'step'; el.querySelector('.step-icon').textContent = i; }
  }
}

function switchTab(name, el) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  el.classList.add('active');
  if (name === 'milestones' && S.plan && !S.msGenerated) generateMilestones();
  if (name === 'investing' && S.plan && !S.invGenerated) generateInvesting();
  if (name === 'future' && S.plan) {
    document.getElementById('fut-placeholder').style.display = 'none';
    document.getElementById('fut-slider-card').style.display = 'block';
    if (!S.futCache[S.futAge]) generateFuture(S.futAge);
  }
}

async function buildPlan() {
  const situation = document.getElementById('situation').value.trim();
  if (!situation) return alert('Please describe your situation first.');
  const btn = document.getElementById('plan-btn');
  btn.disabled = true; btn.textContent = 'Building your plan...';
  document.getElementById('plan-result').innerHTML = '';
  showSC('plan-sc'); resetSteps('ps', 6);
  setStep('ps', 1, 6); await sleep(600);
  setStep('ps', 2, 6); await sleep(500);
  setStep('ps', 3, 6);
  try {
    const res = await fetch('/plan', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({situation}) });
    setStep('ps', 4, 6); await sleep(400);
    const data = await res.json();
    setStep('ps', 5, 6); await sleep(300);
    setStep('ps', 6, 6); await sleep(300);
    hideSC('plan-sc');
    if (data.error) { document.getElementById('plan-result').innerHTML = `<div class="alert alert-warn">${data.error}</div>`; }
    else { S.plan = data; S.situation = situation; S.msGenerated = false; S.invGenerated = false; S.futCache = {}; renderPlan(data); }
  } catch(e) { hideSC('plan-sc'); document.getElementById('plan-result').innerHTML = `<div class="alert alert-warn">Error: ${e.message}</div>`; }
  btn.disabled = false; btn.textContent = 'Rebuild My Roadmap';
}

function renderPlan(d) {
  const el = document.getElementById('plan-result');
  const surplus = (d.monthly_income||0) - (d.monthly_expenses||0);
  const totalDebt = (d.debts||[]).reduce((s,x) => s+(x.balance||0), 0);
  const dotC = [C.blue, C.orange, C.green, C.purple, C.red, C.yellow];

  const statsHTML = `<div class="stat-row">
    <div class="stat"><span class="stat-label">Monthly Income</span><span class="stat-value" style="color:${C.blue}">${fmt(d.monthly_income)}</span><span class="stat-note">take-home</span></div>
    <div class="stat"><span class="stat-label">Monthly Expenses</span><span class="stat-value">${fmt(d.monthly_expenses)}</span><span class="stat-note">fixed costs</span></div>
    <div class="stat"><span class="stat-label">Monthly Surplus</span><span class="stat-value" style="color:${surplus>=0?C.green:C.red}">${fmt(Math.abs(surplus))}</span><span class="stat-note">${surplus>=0?'to allocate':'over budget'}</span></div>
    <div class="stat"><span class="stat-label">Total Debt</span><span class="stat-value" style="color:${C.red}">${fmt(totalDebt)}</span><span class="stat-note">${(d.debts||[]).length} account(s)</span></div>
  </div>`;

  const summaryHTML = d.situation_summary ? `
    <div class="card-flat" style="margin-bottom:16px">
      <span class="eyebrow">Your Situation</span>
      <p class="body-text" style="margin-bottom:${d.why_this_order?'10px':'0'}">${d.situation_summary}</p>
      ${d.why_this_order ? `<p class="muted-text" style="margin-top:8px;padding-top:10px;border-top:2px solid #0a0a0a22">${d.why_this_order}</p>` : ''}
    </div>` : '';

  const debtsHTML = (d.debts||[]).map(debt => {
    const isHigh = (debt.apr||0) >= 10;
    const pmt = debt.monthly_payment || Math.ceil((debt.balance||0)/24);
    const months = pmt > 0 ? Math.ceil((debt.balance||0)/pmt) : '?';
    return `<div class="debt-item">
      <div class="debt-header">
        <span class="debt-name">${debt.name}</span>
        <span class="debt-badge ${isHigh?'badge-hi':'badge-lo'}">${debt.apr}% APR${isHigh?' · PAY FIRST':''}</span>
      </div>
      <div class="debt-meta">
        <span>${fmt(debt.balance)} remaining</span>
        <span>~${months} months at current rate</span>
        <span>${fmt(pmt)}/mo</span>
      </div>
      <div class="debt-bar"><div class="debt-bar-fill" style="width:10%;background:${isHigh?C.red:C.blue}"></div></div>
    </div>`;
  }).join('');

  const tlHTML = (d.monthly_plan||[]).map((m,i) => {
    const allocs = Object.entries(m.allocations||{}).filter(([,v])=>v>0);
    return `<div class="tl-item">
      <div class="tl-left">
        <div class="tl-dot" style="background:${dotC[i%dotC.length]}">${i+1}</div>
        ${i<(d.monthly_plan.length-1)?'<div class="tl-line"></div>':''}
      </div>
      <div class="tl-right">
        <div class="tl-label">${m.label||'Phase '+(i+1)}</div>
        <div class="tl-title">${m.focus||''}</div>
        <div class="tl-alloc">
          ${allocs.map(([k,v])=>`<div class="tl-alloc-row"><span class="tl-alloc-key">${k}</span><span class="tl-alloc-val">${fmt(v)}</span></div>`).join('')}
        </div>
        ${m.guidance?`<p class="tl-guidance">${m.guidance}</p>`:''}
        ${m.milestone?`<div class="alert alert-good" style="margin-top:10px;margin-bottom:0">// ${m.milestone}</div>`:''}
      </div>
    </div>`;
  }).join('');

  const allKeys = [...new Set((d.monthly_plan||[]).flatMap(m=>Object.keys(m.allocations||{})))];
  const chartColors = [C.red, C.blue, C.green, C.orange, C.purple, C.yellow];
  const datasets = allKeys.map((k,i)=>({
    label: k,
    data: (d.monthly_plan||[]).map(m=>(m.allocations||{})[k]||0),
    backgroundColor: chartColors[i%chartColors.length],
    borderRadius: 0, borderSkipped: false,
    borderWidth: 2, borderColor: '#0a0a0a'
  }));

  const ratesHTML = d.hysa_rate ? `<div class="card">
    <span class="eyebrow">Live Rates</span>
    <div class="three-col" style="margin-top:12px;margin-bottom:14px">
      <div class="stat"><span class="stat-label">Best HYSA</span><span class="stat-value" style="font-size:1.4rem;color:${C.green}">${d.hysa_rate}</span></div>
      <div class="stat"><span class="stat-label">S&P 500</span><span class="stat-value" style="font-size:1.4rem;color:${C.blue}">${d.sp500_note?'See below':'—'}</span></div>
      <div class="stat"><span class="stat-label">Debt Free</span><span class="stat-value" style="font-size:1.4rem;color:${C.orange}">Month ${d.debt_free_month||'?'}</span></div>
    </div>
    ${d.hysa_tip?`<div class="alert alert-good" style="margin-bottom:10px">${d.hysa_tip}</div>`:''}
    ${d.sp500_note?`<div class="alert alert-info" style="margin-bottom:10px">${d.sp500_note}</div>`:''}
    ${d.debt_free_note?`<div class="alert alert-neutral">${d.debt_free_note}</div>`:''}
  </div>` : '';

  el.innerHTML = `
    <div class="card">${statsHTML}${summaryHTML}<span class="eyebrow">Your Debts</span><div style="margin-top:10px">${debtsHTML||'<p class="muted-text">No debts detected.</p>'}</div></div>
    <div class="card">
      <span class="eyebrow">Where Your Surplus Goes Each Phase</span>
      <div class="chart-wrap"><canvas id="planChart"></canvas></div>
    </div>
    <div class="card"><span class="eyebrow">Month-by-Month Plan</span><div class="timeline" style="margin-top:16px">${tlHTML}</div></div>
    ${ratesHTML}
    ${d.key_insight?`<div class="alert alert-info"><strong>// Key insight:</strong> ${d.key_insight}</div>`:''}
  `;

  destroyChart('plan');
  const ctx = document.getElementById('planChart').getContext('2d');
  S.charts['plan'] = new Chart(ctx, {
    type: 'bar',
    data: { labels: (d.monthly_plan||[]).map(m=>m.label||''), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font:{size:10, family:'Space Mono'}, padding:10, boxWidth:12 } } },
      scales: {
        x: { stacked:true, grid:{display:false}, ticks:{font:{size:9, family:'Space Mono'}} },
        y: { stacked:true, grid:{color:'#0a0a0a22'}, ticks:{font:{size:9, family:'Space Mono'}, callback: v=>'$'+v.toLocaleString()} }
      }
    }
  });
}

async function runWhatIf() {
  const scenario = document.getElementById('scenario').value.trim();
  if (!scenario) return alert('Please describe a scenario.');
  const btn = document.getElementById('wi-btn');
  btn.disabled = true; btn.textContent = 'Analyzing...';
  document.getElementById('wi-result').innerHTML = '';
  showSC('wi-sc'); resetSteps('ws', 5);
  setStep('ws', 1, 5); await sleep(500);
  setStep('ws', 2, 5); await sleep(400);
  setStep('ws', 3, 5);
  try {
    const res = await fetch('/whatif', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({scenario}) });
    setStep('ws', 4, 5); await sleep(400);
    const data = await res.json();
    setStep('ws', 5, 5); await sleep(300);
    hideSC('wi-sc');
    if (data.error) { document.getElementById('wi-result').innerHTML = `<div class="alert alert-warn">${data.error}</div>`; }
    else { S.whatif = data; renderWhatIf(data); }
  } catch(e) { hideSC('wi-sc'); document.getElementById('wi-result').innerHTML = `<div class="alert alert-warn">Error: ${e.message}</div>`; }
  btn.disabled = false; btn.textContent = 'Run Scenario';
}

function renderWhatIf(d) {
  const el = document.getElementById('wi-result');
  const origRows = (d.comparisons||[]).map(c=>`<div class="compare-row"><span class="compare-key">${c.metric}</span><span class="compare-val">${c.original}</span></div>`).join('');
  const newRows = (d.comparisons||[]).map(c=>`<div class="compare-row"><span class="compare-key">${c.metric}</span><span class="compare-val ${c.better?'up':''}">${c.new_value}</span></div>`).join('');
  const impacts = (d.impacts||[]).map(i=>`<div class="alert alert-${i.type||'info'}"><strong>${i.icon||''} ${i.title}:</strong> ${i.body}</div>`).join('');
  const chartLabels = (d.monthly_surplus_chart||[]).map(m=>m.month);
  const orig = (d.monthly_surplus_chart||[]).map(m=>m.original||0);
  const newv = (d.monthly_surplus_chart||[]).map(m=>m.new||0);

  el.innerHTML = `
    <div class="card">
      <span class="eyebrow">${d.scenario_title||'Scenario Analysis'}</span>
      <p class="body-text" style="margin:8px 0 8px">${d.what_changes||''}</p>
      ${d.why_it_matters?`<p class="muted-text" style="padding-top:10px;border-top:2px solid #0a0a0a22;margin-top:10px">${d.why_it_matters}</p>`:''}
    </div>
    <div class="compare-wrap">
      <div class="compare-col compare-orig"><span class="compare-col-label">Original Plan</span>${origRows}</div>
      <div class="compare-col compare-new"><span class="compare-col-label" style="color:${C.blue}">With Scenario</span>${newRows}</div>
    </div>
    <div class="card">
      <span class="eyebrow">Monthly Surplus — Before vs After</span>
      <div class="chart-wrap-sm"><canvas id="wiChart"></canvas></div>
    </div>
    <div class="card"><span class="eyebrow">What Changes and Why</span><div style="margin-top:10px">${impacts}</div></div>
    ${d.what_to_do_now?`<div class="alert alert-good"><strong>// If this happened today:</strong> ${d.what_to_do_now}</div>`:''}
  `;

  destroyChart('whatif');
  const ctx = document.getElementById('wiChart').getContext('2d');
  S.charts['whatif'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartLabels,
      datasets: [
        { label: 'Original', data: orig, backgroundColor: 'rgba(0,132,199,0.3)', borderColor: C.blue, borderWidth: 2, borderRadius: 0 },
        { label: 'With Scenario', data: newv, backgroundColor: 'rgba(0,200,83,0.3)', borderColor: C.green, borderWidth: 2, borderRadius: 0 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font:{size:10, family:'Space Mono'}, padding:10, boxWidth:12 } } },
      scales: {
        x: { grid:{display:false}, ticks:{font:{size:9, family:'Space Mono'}} },
        y: { grid:{color:'#0a0a0a22'}, ticks:{font:{size:9, family:'Space Mono'}, callback: v=>'$'+v.toLocaleString()} }
      }
    }
  });
}

async function calcPaycheck() {
  const income = parseFloat(document.getElementById('pay-income').value)||0;
  if (!income) { document.getElementById('pc-result').innerHTML = '<div class="alert alert-warn">Enter your monthly income first.</div>'; return; }

  const fields = ['rent','groceries','subscriptions','transport','dining','savings','debt','other'];
  const labels = ['Rent / Housing','Groceries','Subscriptions','Transport','Dining Out','Savings','Debt Payments','Other'];
  const fillColors = [C.blue, C.green, C.orange, C.blue, C.orange, C.green, C.red, C.blue];
  const benchmarks = [30, 15, 5, 10, 10, 20, null, null];

  showSC('pc-sc'); resetSteps('pcs', 4);
  setStep('pcs', 1, 4); await sleep(350);

  let total = 0;
  const vals = fields.map(f => { const v = parseFloat(document.getElementById('pay-'+f).value)||0; total+=v; return v; });
  const remaining = income - total;
  const savingsRate = income > 0 ? (vals[5]/income)*100 : 0;
  const housingPct = income > 0 ? (vals[0]/income)*100 : 0;
  const diningPct = income > 0 ? (vals[4]/income)*100 : 0;

  S.paycheck = { income, rent:vals[0], groceries:vals[1], subscriptions:vals[2], transport:vals[3], dining:vals[4], savings:vals[5], debt:vals[6], other:vals[7], total, remaining, savingsRate };

  setStep('pcs', 2, 4); await sleep(450);

  const bars = fields.map((f,i) => {
    if (vals[i]<=0) return '';
    const p = (vals[i]/income)*100;
    const over = benchmarks[i] && p > benchmarks[i];
    const fill = f==='savings'?C.green : f==='debt'?C.red : over?C.red : fillColors[i];
    return `<div class="bar-row">
      <span class="bar-label">${labels[i]}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.min(p,100).toFixed(1)}%;background:${fill}"></div></div>
      <span class="bar-amt">${fmt(vals[i])}</span>
      <span class="bar-pct">${p.toFixed(0)}%</span>
    </div>`;
  }).join('');

  setStep('pcs', 3, 4); await sleep(350);

  let alerts = '';
  if (remaining < 0) alerts += `<div class="alert alert-warn"><strong>Over budget by ${fmt(Math.abs(remaining))}.</strong> Start with subscriptions and dining — easiest cuts with least lifestyle impact.</div>`;
  if (housingPct > 30) alerts += `<div class="alert alert-warn"><strong>Housing is ${housingPct.toFixed(0)}% of income</strong> — above the 30% guideline.</div>`;
  if (diningPct > 10) alerts += `<div class="alert alert-info"><strong>Dining out is ${diningPct.toFixed(0)}% of income.</strong> Cutting in half frees up ${fmt(vals[4]*0.5)}/month.</div>`;
  if (savingsRate >= 20) alerts += `<div class="alert alert-good"><strong>${savingsRate.toFixed(0)}% savings rate — excellent.</strong> Keep it automated.</div>`;
  else if (savingsRate >= 10) alerts += `<div class="alert alert-info"><strong>${savingsRate.toFixed(0)}% savings rate — solid.</strong> Push toward 20% for real momentum.</div>`;
  else alerts += `<div class="alert alert-warn"><strong>${savingsRate.toFixed(0)}% savings rate — below minimum 10%.</strong> Need ${fmt((income*0.1)-vals[5])} more per month.</div>`;
  if (remaining > 0 && remaining/income > 0.15) alerts += `<div class="alert alert-good"><strong>${fmt(remaining)} unallocated.</strong> Give it a job — debt or emergency fund.</div>`;

  setStep('pcs', 4, 4); await sleep(300);
  hideSC('pc-sc');

  const donutVals = vals.filter(v=>v>0);
  const donutLabels = fields.filter((f,i)=>vals[i]>0).map((f,i)=>labels[fields.indexOf(f)]);
  const donutColors = fields.filter((f,i)=>vals[i]>0).map((f,i)=>fillColors[fields.indexOf(f)]);

  document.getElementById('pc-result').innerHTML = `
    <div class="card">
      <div class="stat-row">
        <div class="stat"><span class="stat-label">Income</span><span class="stat-value" style="color:${C.blue}">${fmt(income)}</span></div>
        <div class="stat"><span class="stat-label">Expenses</span><span class="stat-value">${fmt(total)}</span></div>
        <div class="stat"><span class="stat-label">${remaining>=0?'Remaining':'Over Budget'}</span><span class="stat-value" style="color:${remaining>=0?C.green:C.red}">${fmt(Math.abs(remaining))}</span></div>
        <div class="stat"><span class="stat-label">Savings Rate</span><span class="stat-value" style="color:${savingsRate>=10?C.green:C.red}">${savingsRate.toFixed(0)}%</span></div>
      </div>
      <div style="margin-top:6px">${alerts}</div>
    </div>
    <div class="two-col">
      <div class="card"><span class="eyebrow">Spending Breakdown</span><div style="margin-top:12px">${bars}</div></div>
      <div class="card"><span class="eyebrow">Allocation Overview</span><div class="chart-wrap-sm"><canvas id="pcDonut"></canvas></div></div>
    </div>
    <div class="card">
      <span class="eyebrow">Benchmarks</span>
      <div class="three-col" style="margin-top:12px">
        <div class="stat"><span class="stat-label">Housing</span><span class="stat-value" style="font-size:1.2rem;color:${housingPct>30?C.red:C.green}">${housingPct.toFixed(0)}%<span style="font-size:0.6rem;color:#888"> / 30% max</span></span></div>
        <div class="stat"><span class="stat-label">Savings</span><span class="stat-value" style="font-size:1.2rem;color:${savingsRate>=10?C.green:C.red}">${savingsRate.toFixed(0)}%<span style="font-size:0.6rem;color:#888"> / 10-20% goal</span></span></div>
        <div class="stat"><span class="stat-label">Dining</span><span class="stat-value" style="font-size:1.2rem;color:${diningPct>10?C.red:C.green}">${diningPct.toFixed(0)}%<span style="font-size:0.6rem;color:#888"> / 10% max</span></span></div>
      </div>
    </div>
  `;

  destroyChart('paycheck');
  const ctx = document.getElementById('pcDonut').getContext('2d');
  S.charts['paycheck'] = new Chart(ctx, {
    type: 'doughnut',
    data: { labels: donutLabels, datasets: [{ data: donutVals, backgroundColor: donutColors, borderWidth: 3, borderColor: '#0a0a0a' }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: { legend: { position: 'bottom', labels: { font:{size:10, family:'Space Mono'}, padding:8, boxWidth:10 } } } }
  });
}

function ctx() {
  const c = {};
  if (S.situation) c.situation = S.situation;
  if (S.plan) c.plan = S.plan;
  if (S.whatif) c.whatif = S.whatif;
  if (S.paycheck) c.paycheck = S.paycheck;
  return c;
}

async function generateMilestones() {
  S.msGenerated = true;
  document.getElementById('ms-placeholder').style.display = 'none';
  document.getElementById('ms-result').innerHTML = '';
  showSC('ms-sc'); resetSteps('mss', 5);
  setStep('mss', 1, 5); await sleep(500);
  setStep('mss', 2, 5); await sleep(400);
  setStep('mss', 3, 5);
  try {
    const res = await fetch('/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({type:'milestones', context:ctx()}) });
    setStep('mss', 4, 5); await sleep(400);
    const data = await res.json();
    setStep('mss', 5, 5); await sleep(300);
    hideSC('ms-sc');
    if (data.error) { document.getElementById('ms-result').innerHTML = `<div class="alert alert-warn">${data.error}</div>`; return; }
    renderMilestones(data);
  } catch(e) { hideSC('ms-sc'); document.getElementById('ms-result').innerHTML = `<div class="alert alert-warn">Error: ${e.message}</div>`; }
}

function renderMilestones(d) {
  const el = document.getElementById('ms-result');
  const progress = d.overall_progress || 0;
  const stageColors = [C.blue, C.green, C.orange, C.purple];

  const stagesHTML = (d.stages||[]).map((stage,i) => {
    const items = (stage.milestones||[]).map(m => `
      <div class="ms-item">
        <div class="ms-dot" style="background:${stageColors[i]};border-color:${stageColors[i]}"></div>
        <div class="ms-item-body">
          <div class="ms-item-label">${m.label}</div>
          <div class="ms-item-target">${m.target||''}${m.timeline?' · '+m.timeline:''}</div>
          ${m.why?`<div class="ms-item-why">${m.why}</div>`:''}
        </div>
      </div>`).join('');
    return `<div class="ms-card" style="border-top-color:${stageColors[i]}">
      <span class="ms-stage-label" style="color:${stageColors[i]}">${stage.name}</span>
      ${stage.description?`<p class="ms-stage-desc">${stage.description}</p>`:''}
      ${items}
    </div>`;
  }).join('');

  el.innerHTML = `
    <div class="card">
      <span class="eyebrow">Where You Are</span>
      <p class="body-text" style="margin:8px 0 14px">${d.where_you_are||''}</p>
      <div style="display:flex;justify-content:space-between;font-family:'Space Mono',monospace;font-size:0.72rem;margin-bottom:6px">
        <span style="color:#888">${d.progress_label||''}</span>
        <span style="font-weight:700">${progress}%</span>
      </div>
      <div class="bar-track" style="height:20px"><div class="bar-fill" style="width:${progress}%;background:${C.green}"></div></div>
    </div>
    <div class="ms-grid">${stagesHTML}</div>
    ${d.next_action?`<div class="alert alert-info" style="margin-top:12px"><strong>// Do this first:</strong> ${d.next_action}</div>`:''}
    ${d.encouragement?`<div class="alert alert-neutral" style="margin-top:10px">${d.encouragement}</div>`:''}
  `;
}

async function generateInvesting() {
  S.invGenerated = true;
  document.getElementById('inv-placeholder').style.display = 'none';
  document.getElementById('inv-result').innerHTML = '';
  showSC('inv-sc'); resetSteps('invs', 5);
  setStep('invs', 1, 5); await sleep(500);
  setStep('invs', 2, 5); await sleep(400);
  setStep('invs', 3, 5);
  try {
    const res = await fetch('/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({type:'investing', context:ctx()}) });
    setStep('invs', 4, 5); await sleep(400);
    const data = await res.json();
    setStep('invs', 5, 5); await sleep(300);
    hideSC('inv-sc');
    if (data.error) { document.getElementById('inv-result').innerHTML = `<div class="alert alert-warn">${data.error}</div>`; return; }
    renderInvesting(data);
  } catch(e) { hideSC('inv-sc'); document.getElementById('inv-result').innerHTML = `<div class="alert alert-warn">Error: ${e.message}</div>`; }
}

function renderInvesting(d) {
  const el = document.getElementById('inv-result');
  const accCards = (d.accounts||[]).map(a => `
    <div class="acc-card">
      <span class="acc-priority" style="color:${a.color||C.blue}">Priority ${a.priority||''} — ${a.name}</span>
      <div class="acc-amount">${a.monthly_amount ? fmt(a.monthly_amount)+'/mo' : (a.status_label||'—')}</div>
      <div class="acc-status">${a.status_label||''}</div>
      <p class="acc-what">${a.what_it_is||''}</p>
      ${a.why_first?`<div class="acc-why">${a.why_first}</div>`:''}
      ${a.where_to_open?`<p class="acc-where">${a.where_to_open}</p>`:''}
    </div>`).join('');

  const chartLabels = (d.growth_projection||[]).map(p=>p.year);
  const chartData = (d.growth_projection||[]).map(p=>p.value);

  const avoids = (d.avoid||[]).map(a => `
    <div class="avoid-row">
      <div style="flex:1">
        <div class="avoid-thing">✕ ${a.thing||a}</div>
        ${a.reason?`<div class="avoid-reason">${a.reason}</div>`:''}
      </div>
    </div>`).join('');

  el.innerHTML = `
    <div class="inv-header">
      <div class="inv-header-title">${d.readiness_title||'Your Investing Readiness'}</div>
      <div class="inv-header-body">${d.readiness_explanation||''}</div>
    </div>
    <div class="acc-grid">${accCards}</div>
    ${d.the_math?`<div class="alert alert-info" style="margin-bottom:14px"><strong>// The math:</strong> ${d.the_math}</div>`:''}
    <div class="card">
      <span class="eyebrow">Projected Portfolio Growth</span>
      <p class="muted-text" style="margin-bottom:6px">Consistent investing at your capacity — at 7% average annual return.</p>
      <div class="chart-wrap"><canvas id="invChart"></canvas></div>
    </div>
    <div class="card">
      <span class="eyebrow">What to Avoid</span>
      <p class="muted-text" style="margin-bottom:12px">Most common mistakes for someone in your situation.</p>
      ${avoids}
    </div>
    ${d.biggest_mistake?`<div class="alert alert-warn"><strong>// Biggest mistake to avoid:</strong> ${d.biggest_mistake}</div>`:''}
  `;

  destroyChart('investing');
  const ctx2 = document.getElementById('invChart').getContext('2d');
  S.charts['investing'] = new Chart(ctx2, {
    type: 'line',
    data: { labels: chartLabels, datasets: [{ label: 'Portfolio Value', data: chartData, borderColor: C.green, backgroundColor: 'rgba(0,200,83,0.08)', fill:true, tension:0, pointRadius:5, pointBackgroundColor: C.green, borderWidth:3, pointBorderWidth:2, pointBorderColor:'#0a0a0a' }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false}, tooltip:{callbacks:{label: c=>' $'+c.raw.toLocaleString()}} },
      scales: {
        x: { grid:{display:false}, ticks:{font:{size:9, family:'Space Mono'}} },
        y: { grid:{color:'#0a0a0a22'}, ticks:{font:{size:9, family:'Space Mono'}, callback: v=>'$'+(v>=1000?(v/1000).toFixed(0)+'k':v)} }
      }
    }
  });
}

let futDebounce = null;
function onFutureSlide(age) {
  age = parseInt(age);
  S.futAge = age;
  document.getElementById('fut-age-display').textContent = age;
  clearTimeout(futDebounce);
  futDebounce = setTimeout(() => generateFuture(age), 700);
}

async function generateFuture(age) {
  document.getElementById('fut-result').innerHTML = '';
  showSC('fut-sc'); resetSteps('futs', 5);
  setStep('futs', 1, 5); await sleep(400);
  setStep('futs', 2, 5); await sleep(400);
  setStep('futs', 3, 5);
  try {
    const res = await fetch('/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({type:'future', age, context:ctx()}) });
    setStep('futs', 4, 5); await sleep(400);
    const data = await res.json();
    setStep('futs', 5, 5); await sleep(300);
    hideSC('fut-sc');
    if (data.error) { document.getElementById('fut-result').innerHTML = `<div class="alert alert-warn">${data.error}</div>`; return; }
    S.futCache[age] = data;
    renderFuture(data, age);
  } catch(e) { hideSC('fut-sc'); document.getElementById('fut-result').innerHTML = `<div class="alert alert-warn">Error: ${e.message}</div>`; }
}

function renderFuture(d, age) {
  const el = document.getElementById('fut-result');
  const statCards = (d.key_metrics||[]).map(m=>`
    <div class="stat">
      <span class="stat-label">${m.label}</span>
      <span class="stat-value" style="color:${m.color||'var(--black)'};font-size:1.2rem">${m.value}</span>
      <span class="stat-note">${m.note||''}</span>
    </div>`).join('');

  const chartLabels = (d.net_worth_projection||[]).map(p=>'Age '+p.age);
  const chartData = (d.net_worth_projection||[]).map(p=>p.net_worth);

  const milestones = (d.milestones_by_then||[]).map(m=>`
    <div class="milestone-check">
      <div class="check-icon">${m.achieved?'[x]':'[ ]'}</div>
      <div class="check-body">
        <div class="check-label">${m.label}${m.age_achieved?' — Age '+m.age_achieved:''}</div>
        <div class="check-detail">${m.detail||''}</div>
      </div>
    </div>`).join('');

  el.innerHTML = `
    ${d.headline?`<div class="card"><p class="body-text" style="font-size:0.95rem;font-weight:600">${d.headline}</p></div>`:''}
    <div class="card">
      <span class="eyebrow">At Age ${age} — Key Metrics</span>
      <div class="stat-row" style="margin-top:12px">${statCards}</div>
    </div>
    <div class="card">
      <span class="eyebrow">Net Worth Trajectory</span>
      <p class="muted-text" style="margin-bottom:6px">Starts negative (debt), crosses zero, then grows through investing.</p>
      <div class="chart-wrap"><canvas id="futChart"></canvas></div>
    </div>
    ${d.what_the_numbers_mean?`<div class="card"><span class="eyebrow">What This Actually Means</span><p class="body-text" style="margin-top:8px">${d.what_the_numbers_mean}</p></div>`:''}
    <div class="future-scenario-row">
      <div class="future-sc future-sc-best">
        <span class="future-sc-label" style="color:${C.green}">Best Case</span>
        <div class="future-sc-val" style="color:${C.green}">${(d.best_case||{}).net_worth||'N/A'}</div>
        <div class="future-sc-desc">${(d.best_case||{}).description||''}</div>
      </div>
      <div class="future-sc future-sc-real">
        <span class="future-sc-label" style="color:${C.orange}">Realistic Case</span>
        <div class="future-sc-val" style="color:${C.orange}">${(d.realistic_case||{}).net_worth||'N/A'}</div>
        <div class="future-sc-desc">${(d.realistic_case||{}).description||''}</div>
      </div>
    </div>
    <div class="card"><span class="eyebrow">Milestones by Age ${age}</span><div style="margin-top:8px">${milestones}</div></div>
    ${d.the_decision_that_matters_most?`<div class="alert alert-info"><strong>// The decision that matters most:</strong> ${d.the_decision_that_matters_most}</div>`:''}
  `;

  destroyChart('future');
  const ctx3 = document.getElementById('futChart').getContext('2d');
  S.charts['future'] = new Chart(ctx3, {
    type: 'line',
    data: { labels: chartLabels, datasets: [{
      label: 'Net Worth', data: chartData,
      borderColor: C.blue, backgroundColor: 'rgba(0,132,199,0.08)',
      fill: true, tension: 0, pointRadius: 5, borderWidth: 3,
      pointBackgroundColor: C.blue, pointBorderWidth: 2, pointBorderColor: '#0a0a0a'
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false}, tooltip:{callbacks:{label: c=>' $'+c.raw.toLocaleString()}} },
      scales: {
        x: { grid:{display:false}, ticks:{font:{size:9, family:'Space Mono'}} },
        y: { grid:{color:'#0a0a0a22'}, ticks:{font:{size:9, family:'Space Mono'}, callback: v=>'$'+(Math.abs(v)>=1000?((v/1000).toFixed(0))+'k':v)} }
      }
    }
  });
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return Response(HTML, mimetype='text/html')


@app.route("/plan", methods=["POST"])
def plan():
    data = request.json
    try:
        return jsonify(run_pathwise_structured(data.get("situation", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/whatif", methods=["POST"])
def whatif():
    data = request.json
    try:
        return jsonify(run_whatif_structured(data.get("scenario", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    try:
        return jsonify(generate_tab_content(
            gen_type=data.get("type"),
            context=data.get("context", {}),
            age=data.get("age", 25)
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)