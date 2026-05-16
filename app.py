from flask import Flask, request, jsonify, Response
from agent import run_pathwise_structured, run_whatif_structured, generate_tab_content
import json

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<title>Pathwise</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root {
  --bg: #f5f5f7; --card: #fff; --border: #e5e5ea; --text: #1d1d1f; --muted: #86868b;
  --blue: #007aff; --green: #34c759; --orange: #ff9500; --red: #ff3b30; --purple: #5856d6;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

/* HEADER */
.header { background: rgba(255,255,255,0.94); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding: 0 40px; position: sticky; top: 0; z-index: 200; }
.header-inner { max-width: 960px; margin: 0 auto; height: 52px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 1.05rem; font-weight: 700; letter-spacing: -0.02em; }
.badge { font-size: 0.68rem; color: var(--muted); background: var(--bg); border: 1px solid var(--border); border-radius: 20px; padding: 3px 10px; }

/* HERO */
.hero { background: #1d1d1f; padding: 60px 40px 52px; text-align: center; }
.hero h1 { font-size: 2.6rem; font-weight: 800; color: #f5f5f7; letter-spacing: -0.04em; line-height: 1.06; margin-bottom: 12px; }
.hero p { font-size: 1rem; color: rgba(255,255,255,0.45); max-width: 420px; margin: 0 auto 22px; line-height: 1.65; }
.pills { display: flex; gap: 7px; justify-content: center; flex-wrap: wrap; }
.pill { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 980px; padding: 4px 12px; font-size: 0.72rem; color: rgba(255,255,255,0.45); }

/* LAYOUT */
.main { max-width: 960px; margin: 0 auto; padding: 36px 20px 80px; }
.tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 32px; overflow-x: auto; }
.tabs::-webkit-scrollbar { display: none; }
.tab-btn { background: none; border: none; border-bottom: 2px solid transparent; padding: 10px 16px; font-size: 0.84rem; font-weight: 500; color: var(--muted); cursor: pointer; white-space: nowrap; margin-bottom: -1px; font-family: inherit; transition: color 0.15s; }
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--text); border-bottom-color: var(--text); font-weight: 600; }
.panel { display: none; }
.panel.active { display: block; }

/* CARDS */
.card { background: var(--card); border-radius: 14px; padding: 22px 24px; margin-bottom: 12px; }
.card-flat { background: var(--bg); border-radius: 12px; padding: 16px 18px; margin-bottom: 10px; }

/* TYPE */
.section-title { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 4px; }
.section-sub { font-size: 0.86rem; color: var(--muted); margin-bottom: 22px; line-height: 1.55; }
.eyebrow { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-bottom: 8px; display: block; }
.body-text { font-size: 0.88rem; line-height: 1.7; color: var(--text); }
.muted-text { font-size: 0.82rem; color: var(--muted); line-height: 1.6; }

/* FORM */
label { display: block; font-size: 0.72rem; font-weight: 600; color: var(--muted); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.05em; }
textarea, input[type="number"] { width: 100%; background: var(--bg); border: 1px solid transparent; border-radius: 10px; color: var(--text); font-size: 0.92rem; padding: 10px 12px; font-family: inherit; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
textarea { resize: vertical; min-height: 88px; }
textarea:focus, input:focus { border-color: var(--blue); box-shadow: 0 0 0 3px rgba(0,122,255,0.12); }
.btn { display: block; width: 100%; background: var(--text); color: #fff; border: none; border-radius: 980px; padding: 12px; font-size: 0.88rem; font-weight: 600; font-family: inherit; cursor: pointer; margin-top: 12px; transition: opacity 0.15s, transform 0.1s; }
.btn:hover { opacity: 0.85; transform: translateY(-1px); }
.btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }

/* STEPS */
.steps-card { background: var(--card); border-radius: 14px; padding: 20px 24px; margin-bottom: 12px; display: none; }
.steps-title { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 14px; }
.steps { display: flex; flex-direction: column; gap: 11px; }
.step { display: flex; align-items: flex-start; gap: 11px; font-size: 0.83rem; color: #ccc; transition: color 0.25s; }
.step.active { color: var(--text); }
.step.done { color: var(--green); }
.step-icon { width: 20px; height: 20px; border-radius: 50%; border: 1.5px solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 700; flex-shrink: 0; margin-top: 1px; color: #ccc; transition: all 0.25s; }
.step.active .step-icon { border-color: var(--blue); color: var(--blue); background: rgba(0,122,255,0.07); }
.step.done .step-icon { border-color: var(--green); background: var(--green); color: #fff; }
.step-body { flex: 1; }
.step-label { font-weight: 500; line-height: 1.3; }
.step-detail { font-size: 0.74rem; color: var(--muted); margin-top: 2px; display: none; }
.step.active .step-detail { display: block; }
.step-spin { width: 13px; height: 13px; border: 2px solid rgba(0,122,255,0.15); border-top-color: var(--blue); border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0; margin-top: 3px; display: none; }
.step.active .step-spin { display: block; }
.step.done .step-spin { display: none; }
@keyframes spin { to { transform: rotate(360deg); } }

/* STATS */
.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 16px; }
.stat { background: var(--bg); border-radius: 10px; padding: 12px 14px; }
.stat-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); display: block; margin-bottom: 4px; }
.stat-value { font-size: 1.4rem; font-weight: 700; line-height: 1; display: block; }
.stat-note { font-size: 0.7rem; color: var(--muted); margin-top: 2px; display: block; }

/* BARS */
.bar-row { display: grid; grid-template-columns: 130px 1fr 64px 40px; align-items: center; gap: 8px; margin-bottom: 8px; }
.bar-label { font-size: 0.82rem; }
.bar-track { background: var(--bg); border-radius: 99px; height: 6px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.bar-amt { font-size: 0.82rem; font-weight: 600; text-align: right; }
.bar-pct { font-size: 0.72rem; color: var(--muted); text-align: right; }

/* ALERTS */
.alert { border-radius: 10px; padding: 12px 14px; font-size: 0.83rem; line-height: 1.55; margin-bottom: 8px; }
.alert:last-child { margin-bottom: 0; }
.alert-good { background: #f0fff4; color: #1a7a34; border-left: 3px solid var(--green); }
.alert-warn { background: #fff5f5; color: #c0392b; border-left: 3px solid var(--red); }
.alert-info { background: #f0f6ff; color: #1a4fa0; border-left: 3px solid var(--blue); }
.alert-neutral { background: var(--bg); color: var(--muted); border-left: 3px solid var(--border); }

/* PLACEHOLDER */
.placeholder { background: var(--card); border-radius: 14px; padding: 52px 28px; text-align: center; }
.placeholder-icon { font-size: 2.4rem; margin-bottom: 12px; }
.placeholder-title { font-size: 1rem; font-weight: 600; margin-bottom: 6px; }
.placeholder-sub { font-size: 0.83rem; color: var(--muted); line-height: 1.6; max-width: 340px; margin: 0 auto; }

/* TIMELINE */
.timeline { display: flex; flex-direction: column; }
.tl-item { display: flex; gap: 14px; padding-bottom: 20px; }
.tl-item:last-child { padding-bottom: 0; }
.tl-left { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; }
.tl-dot { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: #fff; flex-shrink: 0; }
.tl-line { width: 2px; flex: 1; background: var(--border); margin-top: 4px; min-height: 16px; }
.tl-right { flex: 1; padding-top: 3px; }
.tl-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 3px; }
.tl-title { font-size: 0.92rem; font-weight: 600; margin-bottom: 8px; }
.tl-alloc { display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; }
.tl-alloc-row { display: flex; justify-content: space-between; font-size: 0.8rem; }
.tl-alloc-key { color: var(--muted); }
.tl-alloc-val { font-weight: 600; }
.tl-guidance { font-size: 0.8rem; color: var(--muted); line-height: 1.55; font-style: italic; }

/* DEBT ITEMS */
.debt-item { background: var(--bg); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; }
.debt-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.debt-name { font-size: 0.86rem; font-weight: 600; }
.debt-badge { font-size: 0.66rem; font-weight: 700; padding: 2px 7px; border-radius: 20px; }
.badge-hi { background: #fff2f2; color: var(--red); }
.badge-lo { background: #f0f6ff; color: var(--blue); }
.debt-meta { font-size: 0.76rem; color: var(--muted); display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 7px; }
.debt-bar { background: var(--border); border-radius: 99px; height: 5px; overflow: hidden; }
.debt-bar-fill { height: 100%; border-radius: 99px; }

/* MILESTONES */
.ms-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
.ms-card { background: var(--card); border-radius: 12px; padding: 18px 20px; border-top: 3px solid var(--border); }
.ms-stage-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; display: block; }
.ms-stage-desc { font-size: 0.78rem; color: var(--muted); margin-bottom: 12px; line-height: 1.5; }
.ms-item { display: flex; gap: 8px; margin-bottom: 10px; }
.ms-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.ms-item-body { flex: 1; }
.ms-item-label { font-size: 0.83rem; font-weight: 500; margin-bottom: 2px; }
.ms-item-target { font-size: 0.74rem; color: var(--muted); }
.ms-item-why { font-size: 0.74rem; color: var(--muted); font-style: italic; margin-top: 2px; line-height: 1.4; }

/* INVESTING */
.inv-header { background: var(--text); border-radius: 14px; padding: 22px 24px; margin-bottom: 12px; }
.inv-header-title { font-size: 1.2rem; font-weight: 700; color: #fff; margin-bottom: 6px; }
.inv-header-body { font-size: 0.86rem; color: rgba(255,255,255,0.5); line-height: 1.6; }
.acc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 12px; }
.acc-card { background: var(--card); border-radius: 12px; padding: 16px 18px; }
.acc-priority { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; display: block; }
.acc-amount { font-size: 1.2rem; font-weight: 700; margin-bottom: 3px; }
.acc-status { font-size: 0.72rem; color: var(--muted); margin-bottom: 8px; }
.acc-what { font-size: 0.78rem; color: var(--muted); line-height: 1.5; margin-bottom: 6px; }
.acc-why { font-size: 0.78rem; line-height: 1.5; padding: 8px 10px; background: var(--bg); border-radius: 8px; }
.acc-where { font-size: 0.74rem; color: var(--muted); margin-top: 6px; font-style: italic; }
.avoid-row { display: flex; gap: 10px; background: #fff5f5; border-radius: 10px; padding: 11px 13px; margin-bottom: 8px; }
.avoid-thing { font-size: 0.83rem; font-weight: 600; color: var(--red); margin-bottom: 2px; }
.avoid-reason { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }

/* COMPARE */
.compare-wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.compare-col { border-radius: 12px; padding: 16px 18px; }
.compare-orig { background: var(--bg); border: 1px solid var(--border); }
.compare-new { background: #f0f6ff; border: 1px solid #c0d8f8; }
.compare-col-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 10px; display: block; }
.compare-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(0,0,0,0.04); font-size: 0.82rem; }
.compare-row:last-child { border-bottom: none; }
.compare-key { color: var(--muted); }
.compare-val { font-weight: 600; }
.compare-val.up { color: var(--green); }

/* FUTURE */
.future-slider-card { background: var(--card); border-radius: 14px; padding: 22px 24px; margin-bottom: 12px; }
.age-big { font-size: 3.2rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1; }
.age-sub { font-size: 0.82rem; color: var(--muted); margin-top: 3px; margin-bottom: 18px; }
input[type="range"] { width: 100%; accent-color: var(--text); background: transparent; padding: 0; margin: 0; }
input[type="range"]:focus { box-shadow: none; }
.future-scenario-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.future-sc { border-radius: 12px; padding: 14px 16px; }
.future-sc-best { background: #f0fff4; border: 1px solid #b8e8c8; }
.future-sc-real { background: #fff8f0; border: 1px solid #f5d5a8; }
.future-sc-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; display: block; }
.future-sc-val { font-size: 1.3rem; font-weight: 700; margin-bottom: 4px; }
.future-sc-desc { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }
.milestone-check { display: flex; gap: 10px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid var(--border); }
.milestone-check:last-child { border-bottom: none; }
.check-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.check-body { flex: 1; }
.check-label { font-size: 0.86rem; font-weight: 600; margin-bottom: 2px; }
.check-detail { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }

/* CHART */
.chart-wrap { position: relative; height: 220px; margin: 12px 0; }
.chart-wrap-sm { position: relative; height: 180px; margin: 12px 0; }

/* TWO COL */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.three-col { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }

/* FOOTER */
.footer { text-align: center; padding: 24px; border-top: 1px solid var(--border); font-size: 0.76rem; color: var(--muted); }

@media (max-width: 600px) {
  .two-col, .three-col, .compare-wrap, .future-scenario-row { grid-template-columns: 1fr; }
  .hero h1 { font-size: 2rem; }
  .header { padding: 0 20px; }
  .main { padding: 24px 16px 60px; }
  .bar-row { grid-template-columns: 100px 1fr 56px 36px; }
  .age-big { font-size: 2.4rem; }
}
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <span class="logo">Pathwise</span>
    <span class="badge">Powered by NVIDIA Nemotron</span>
  </div>
</div>

<div class="hero">
  <h1>Your financial plan,<br>built by AI.</h1>
  <p>Describe your situation in plain English. Pathwise fetches live rates and builds your personalized roadmap.</p>
  <div class="pills">
    <span class="pill">Live market data</span>
    <span class="pill">Interactive charts</span>
    <span class="pill">What-if scenarios</span>
    <span class="pill">Persistent memory</span>
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
    <div class="section-title">Build My Roadmap</div>
    <div class="section-sub">Describe your situation and Nemotron will build a month-by-month plan using live market data.</div>
    <div class="card">
      <label>Your financial situation</label>
      <textarea id="situation" placeholder="e.g. I am 22, make $2,500/month as a software intern, have $5,000 in student loans at 5% and $1,500 in credit card debt at 19% APR. Monthly expenses are $1,200. I want to be debt free in 2 years and start a Roth IRA."></textarea>
      <button class="btn" id="plan-btn" onclick="buildPlan()">Build My Roadmap</button>
    </div>
    <div class="steps-card" id="plan-sc">
      <div class="steps-title">Nemotron is working on your plan</div>
      <div class="steps">
        <div class="step" id="ps1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Loading your memory</div><div class="step-detail">Checking for past sessions and saved profile data</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Fetching live market rates</div><div class="step-detail">Searching current HYSA, mortgage, and S&P 500 data</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Extracting your financial profile</div><div class="step-detail">Parsing income, debts, expenses, and goals from your description</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Nemotron is building your roadmap</div><div class="step-detail">Reasoning through priorities and generating month-by-month allocations</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Saving to memory</div><div class="step-detail">Storing your plan so What-If and other tabs can reference it</div></div><div class="step-spin"></div></div>
        <div class="step" id="ps6"><div class="step-icon">6</div><div class="step-body"><div class="step-label">Rendering your dashboard</div><div class="step-detail">Building charts, timelines, and visualizations</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="plan-result"></div>
  </div>

  <!-- WHAT-IF -->
  <div id="tab-whatif" class="panel">
    <div class="section-title">What-If Scenarios</div>
    <div class="section-sub">Explore how a change to your situation affects your entire plan — with a clear explanation of what actually changes and why.</div>
    <div class="card">
      <label>Describe a scenario</label>
      <textarea id="scenario" placeholder="e.g. What if I get a raise to $5,000/month after my internship? What if I put an extra $200 toward my credit card?"></textarea>
      <button class="btn" id="wi-btn" onclick="runWhatIf()">Run Scenario</button>
    </div>
    <div class="steps-card" id="wi-sc">
      <div class="steps-title">Nemotron is analyzing your scenario</div>
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
    <div class="section-title">Paycheck Breakdown</div>
    <div class="section-sub">See where every dollar goes, how you compare to healthy benchmarks, and where you can find more money for your goals.</div>
    <div class="card">
      <div style="margin-bottom:16px"><label>Monthly Take-Home Income</label><input type="number" id="pay-income" placeholder="e.g. 2500"></div>
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
      <button class="btn" onclick="calcPaycheck()">Analyze My Paycheck</button>
    </div>
    <div class="steps-card" id="pc-sc">
      <div class="steps-title">Analyzing your paycheck</div>
      <div class="steps">
        <div class="step" id="pcs1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Calculating totals and surplus</div><div class="step-detail">Adding up all expense categories</div></div><div class="step-spin"></div></div>
        <div class="step" id="pcs2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Benchmarking your spending</div><div class="step-detail">Comparing each category against healthy financial guidelines</div></div><div class="step-spin"></div></div>
        <div class="step" id="pcs3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Finding optimization opportunities</div><div class="step-detail">Identifying where small cuts free up real money for your goals</div></div><div class="step-spin"></div></div>
        <div class="step" id="pcs4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Rendering your dashboard</div><div class="step-detail">Building breakdown bars, donut chart, and benchmark cards</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="pc-result"></div>
  </div>

  <!-- MILESTONES -->
  <div id="tab-milestones" class="panel">
    <div class="section-title">Financial Milestones</div>
    <div class="section-sub">Your personalized roadmap — real targets and timelines based on your actual situation, with the reasoning behind each step.</div>
    <div id="ms-placeholder" class="placeholder">
      <div class="placeholder-icon">🎯</div>
      <div class="placeholder-title">Build your plan first</div>
      <div class="placeholder-sub">Pathwise will generate personalized milestones with real dollar targets and the reasoning behind each one.</div>
    </div>
    <div class="steps-card" id="ms-sc">
      <div class="steps-title">Nemotron is generating your milestones</div>
      <div class="steps">
        <div class="step" id="mss1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Reading your financial plan</div><div class="step-detail">Loading your roadmap, debts, income, and goals</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Assessing your current stage</div><div class="step-detail">Determining where you are in the Foundation to Optimization journey</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is setting your targets</div><div class="step-detail">Generating specific dollar amounts, timelines, and explanations for each milestone</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Calculating your progress</div><div class="step-detail">Estimating how far along you are across all four stages</div></div><div class="step-spin"></div></div>
        <div class="step" id="mss5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your milestone board</div><div class="step-detail">Building your personalized roadmap cards</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="ms-result"></div>
  </div>

  <!-- INVESTING -->
  <div id="tab-investing" class="panel">
    <div class="section-title">Investing Strategy</div>
    <div class="section-sub">A personalized plan explaining what to open, when to start, how much to contribute — and the reasoning behind every decision.</div>
    <div id="inv-placeholder" class="placeholder">
      <div class="placeholder-icon">📈</div>
      <div class="placeholder-title">Build your plan first</div>
      <div class="placeholder-sub">Pathwise will generate a personalized investing strategy based on your income, debts, and goals.</div>
    </div>
    <div class="steps-card" id="inv-sc">
      <div class="steps-title">Nemotron is building your investing strategy</div>
      <div class="steps">
        <div class="step" id="invs1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Evaluating your investing readiness</div><div class="step-detail">Checking debt levels, emergency fund status, and monthly surplus</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Calculating your contribution capacity</div><div class="step-detail">Determining how much you can realistically invest per month</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is selecting your accounts</div><div class="step-detail">Choosing the right order: HYSA, Roth IRA, 401k, brokerage</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Projecting your portfolio growth</div><div class="step-detail">Running compound interest calculations for 1, 5, 10, and 20 years</div></div><div class="step-spin"></div></div>
        <div class="step" id="invs5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your strategy</div><div class="step-detail">Building account cards, growth chart, and action steps</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="inv-result"></div>
  </div>

  <!-- FUTURE YOU -->
  <div id="tab-future" class="panel">
    <div class="section-title">Future You</div>
    <div class="section-sub">Slide to any age and see a realistic projection of your net worth, milestones, and what the numbers actually mean for your life.</div>
    <div id="fut-placeholder" class="placeholder">
      <div class="placeholder-icon">🔮</div>
      <div class="placeholder-title">Build your plan first</div>
      <div class="placeholder-sub">Pathwise will project your financial future at any age based on your real numbers.</div>
    </div>
    <div id="fut-slider-card" class="future-slider-card" style="display:none">
      <div class="age-big" id="fut-age-display">25</div>
      <div class="age-sub">years old</div>
      <input type="range" min="18" max="65" value="25" id="fut-slider" oninput="onFutureSlide(this.value)">
    </div>
    <div class="steps-card" id="fut-sc">
      <div class="steps-title">Nemotron is projecting your future</div>
      <div class="steps">
        <div class="step" id="futs1"><div class="step-icon">1</div><div class="step-body"><div class="step-label">Reading your financial plan</div><div class="step-detail">Loading income, debts, savings rate, and goals</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs2"><div class="step-icon">2</div><div class="step-body"><div class="step-label">Calculating your debt-free timeline</div><div class="step-detail">Projecting when each debt will be paid off based on current payments</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs3"><div class="step-icon">3</div><div class="step-body"><div class="step-label">Nemotron is modeling your net worth</div><div class="step-detail">Running compound growth calculations from today to your target age</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs4"><div class="step-icon">4</div><div class="step-body"><div class="step-label">Generating best and realistic scenarios</div><div class="step-detail">Modeling outcomes based on consistent vs. variable investing behavior</div></div><div class="step-spin"></div></div>
        <div class="step" id="futs5"><div class="step-icon">5</div><div class="step-body"><div class="step-label">Rendering your future dashboard</div><div class="step-detail">Building the net worth chart, key metrics, and milestone checklist</div></div><div class="step-spin"></div></div>
      </div>
    </div>
    <div id="fut-result"></div>
  </div>
</div>

<div class="footer">Built at Hack-a-Claw 2026 · NVIDIA x UCSC Baskin Engineering</div>

<script>
const S = {
  plan: null, situation: null, whatif: null, paycheck: null,
  msGenerated: false, invGenerated: false, futCache: {}, futAge: 25,
  charts: {}
};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const fmt = n => '$' + Math.round(n || 0).toLocaleString();
const C = { blue:'#007aff', green:'#34c759', orange:'#ff9500', red:'#ff3b30', purple:'#5856d6' };
const destroyChart = k => { if (S.charts[k]) { S.charts[k].destroy(); delete S.charts[k]; } };

// ── STEPS ─────────────────────────────────────────────────────
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

// ── TABS ──────────────────────────────────────────────────────
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

// ── BUILD PLAN ────────────────────────────────────────────────
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
  const dotC = [C.blue, C.orange, C.green, C.purple, C.red, '#32ade6'];

  // Stats
  const statsHTML = `<div class="stat-row">
    <div class="stat"><span class="stat-label">Monthly Income</span><span class="stat-value" style="color:${C.blue}">${fmt(d.monthly_income)}</span><span class="stat-note">take-home</span></div>
    <div class="stat"><span class="stat-label">Monthly Expenses</span><span class="stat-value">${fmt(d.monthly_expenses)}</span><span class="stat-note">fixed costs</span></div>
    <div class="stat"><span class="stat-label">Monthly Surplus</span><span class="stat-value" style="color:${surplus>=0?C.green:C.red}">${fmt(Math.abs(surplus))}</span><span class="stat-note">${surplus>=0?'to allocate':'over budget'}</span></div>
    <div class="stat"><span class="stat-label">Total Debt</span><span class="stat-value" style="color:${C.red}">${fmt(totalDebt)}</span><span class="stat-note">${(d.debts||[]).length} account(s)</span></div>
  </div>`;

  // Situation summary — the key guidance block
  const summaryHTML = d.situation_summary ? `
    <div class="card-flat" style="margin-bottom:14px">
      <span class="eyebrow">Your Situation</span>
      <p class="body-text" style="margin-bottom:${d.why_this_order?'10px':'0'}">${d.situation_summary}</p>
      ${d.why_this_order ? `<p class="muted-text" style="margin-top:6px;padding-top:10px;border-top:1px solid var(--border)">${d.why_this_order}</p>` : ''}
    </div>` : '';

  // Debts
  const debtsHTML = (d.debts||[]).map(debt => {
    const isHigh = (debt.apr||0) >= 10;
    const pmt = debt.monthly_payment || Math.ceil((debt.balance||0)/24);
    const months = pmt > 0 ? Math.ceil((debt.balance||0)/pmt) : '?';
    return `<div class="debt-item">
      <div class="debt-header">
        <span class="debt-name">${debt.name}</span>
        <span class="debt-badge ${isHigh?'badge-hi':'badge-lo'}">${debt.apr}% APR${isHigh?' · Pay First':''}</span>
      </div>
      <div class="debt-meta">
        <span>${fmt(debt.balance)} remaining</span>
        <span>~${months} months at current rate</span>
        <span>${fmt(pmt)}/mo</span>
      </div>
      <div class="debt-bar"><div class="debt-bar-fill" style="width:10%;background:${isHigh?C.red:C.blue}"></div></div>
    </div>`;
  }).join('');

  // Timeline — now with guidance text per phase
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
        ${m.milestone?`<div class="alert alert-good" style="margin-top:8px;margin-bottom:0">🎉 ${m.milestone}</div>`:''}
      </div>
    </div>`;
  }).join('');

  // Only one chart — stacked bar of allocation by phase. This is genuinely useful.
  const allKeys = [...new Set((d.monthly_plan||[]).flatMap(m=>Object.keys(m.allocations||{})))];
  const chartColors = [C.red, C.blue, C.green, C.orange, C.purple, '#32ade6'];
  const datasets = allKeys.map((k,i)=>({
    label: k,
    data: (d.monthly_plan||[]).map(m=>(m.allocations||{})[k]||0),
    backgroundColor: chartColors[i%chartColors.length],
    borderRadius: 3, borderSkipped: false
  }));

  // Rates block — guidance focused
  const ratesHTML = d.hysa_rate ? `<div class="card">
    <span class="eyebrow">Live Rates — How They Affect Your Plan</span>
    <div class="three-col" style="margin-top:10px;margin-bottom:12px">
      <div class="stat"><span class="stat-label">Best HYSA</span><span class="stat-value" style="font-size:1.1rem;color:${C.green}">${d.hysa_rate}</span></div>
      <div class="stat"><span class="stat-label">S&P 500 Outlook</span><span class="stat-value" style="font-size:1.1rem;color:${C.blue}">${d.sp500_note?'See below':'—'}</span></div>
      <div class="stat"><span class="stat-label">Debt Free Est.</span><span class="stat-value" style="font-size:1.1rem;color:${C.orange}">Month ${d.debt_free_month||'?'}</span></div>
    </div>
    ${d.hysa_tip?`<div class="alert alert-good" style="margin-bottom:8px">${d.hysa_tip}</div>`:''}
    ${d.sp500_note?`<div class="alert alert-info" style="margin-bottom:8px">${d.sp500_note}</div>`:''}
    ${d.debt_free_note?`<div class="alert alert-neutral">${d.debt_free_note}</div>`:''}
  </div>` : '';

  el.innerHTML = `
    <div class="card">${statsHTML}${summaryHTML}<span class="eyebrow">Your Debts</span><div style="margin-top:8px">${debtsHTML||'<p class="muted-text">No debts detected.</p>'}</div></div>
    <div class="card">
      <span class="eyebrow">Where Your Surplus Goes Each Phase</span>
      <div class="chart-wrap"><canvas id="planChart"></canvas></div>
    </div>
    <div class="card"><span class="eyebrow">Month-by-Month Plan</span><div class="timeline" style="margin-top:14px">${tlHTML}</div></div>
    ${ratesHTML}
    ${d.key_insight?`<div class="alert alert-info"><strong>Key insight:</strong> ${d.key_insight}</div>`:''}
  `;

  destroyChart('plan');
  const ctx = document.getElementById('planChart').getContext('2d');
  S.charts['plan'] = new Chart(ctx, {
    type: 'bar',
    data: { labels: (d.monthly_plan||[]).map(m=>m.label||''), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font:{size:11}, padding:10, boxWidth:12 } } },
      scales: {
        x: { stacked:true, grid:{display:false}, ticks:{font:{size:10}} },
        y: { stacked:true, grid:{color:'#f0f0f0'}, ticks:{font:{size:10}, callback: v=>'$'+v.toLocaleString()} }
      }
    }
  });
}

// ── WHAT-IF ───────────────────────────────────────────────────
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
    else { S.whatif = data; S.msGenerated = false; S.invGenerated = false; S.futCache = {}; renderWhatIf(data); }
  } catch(e) { hideSC('wi-sc'); document.getElementById('wi-result').innerHTML = `<div class="alert alert-warn">Error: ${e.message}</div>`; }
  btn.disabled = false; btn.textContent = 'Run Scenario';
}

function renderWhatIf(d) {
  const el = document.getElementById('wi-result');
  // Comparison columns
  const origRows = (d.comparisons||[]).map(c=>`<div class="compare-row"><span class="compare-key">${c.metric}</span><span class="compare-val">${c.original}</span></div>`).join('');
  const newRows = (d.comparisons||[]).map(c=>`<div class="compare-row"><span class="compare-key">${c.metric}</span><span class="compare-val ${c.better?'up':''}">${c.new_value}</span></div>`).join('');
  // Impact cards
  const impacts = (d.impacts||[]).map(i=>`<div class="alert alert-${i.type||'info'}"><strong>${i.icon||''} ${i.title}:</strong> ${i.body}</div>`).join('');
  // Chart
  const chartLabels = (d.monthly_surplus_chart||[]).map(m=>m.month);
  const orig = (d.monthly_surplus_chart||[]).map(m=>m.original||0);
  const newv = (d.monthly_surplus_chart||[]).map(m=>m.new||0);

  el.innerHTML = `
    <div class="card">
      <span class="eyebrow">${d.scenario_title||'Scenario Analysis'}</span>
      <p class="body-text" style="margin:8px 0 6px">${d.what_changes||''}</p>
      ${d.why_it_matters?`<p class="muted-text" style="padding-top:8px;border-top:1px solid var(--border);margin-top:8px">${d.why_it_matters}</p>`:''}
    </div>
    <div class="compare-wrap">
      <div class="compare-col compare-orig"><span class="compare-col-label">Original Plan</span>${origRows}</div>
      <div class="compare-col compare-new"><span class="compare-col-label" style="color:${C.blue}">With Scenario</span>${newRows}</div>
    </div>
    <div class="card">
      <span class="eyebrow">Monthly Surplus — Before vs After</span>
      <p class="muted-text" style="margin-bottom:4px">This shows how much money you have left over each month to allocate toward your goals.</p>
      <div class="chart-wrap-sm"><canvas id="wiChart"></canvas></div>
    </div>
    <div class="card"><span class="eyebrow">What Changes and Why</span><div style="margin-top:8px">${impacts}</div></div>
    ${d.what_to_do_now?`<div class="alert alert-good"><strong>If this happened today:</strong> ${d.what_to_do_now}</div>`:''}
  `;

  destroyChart('whatif');
  const ctx = document.getElementById('wiChart').getContext('2d');
  S.charts['whatif'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartLabels,
      datasets: [
        { label: 'Original', data: orig, backgroundColor: 'rgba(0,122,255,0.25)', borderColor: C.blue, borderWidth: 1.5, borderRadius: 4 },
        { label: 'With Scenario', data: newv, backgroundColor: 'rgba(52,199,89,0.3)', borderColor: C.green, borderWidth: 1.5, borderRadius: 4 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font:{size:11}, padding:10, boxWidth:12 } } },
      scales: {
        x: { grid:{display:false}, ticks:{font:{size:10}} },
        y: { grid:{color:'#f0f0f0'}, ticks:{font:{size:10}, callback: v=>'$'+v.toLocaleString()} }
      }
    }
  });
}

// ── PAYCHECK ──────────────────────────────────────────────────
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
  S.msGenerated = false; S.invGenerated = false; S.futCache = {};

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

  // Guidance alerts — explain WHY, not just flag
  let alerts = '';
  if (remaining < 0) alerts += `<div class="alert alert-warn"><strong>You are spending ${fmt(Math.abs(remaining))} more than you earn.</strong> Start with subscriptions and dining — these are the easiest cuts with the least lifestyle impact.</div>`;
  if (housingPct > 30) alerts += `<div class="alert alert-warn"><strong>Housing is ${housingPct.toFixed(0)}% of your income</strong> — above the 30% guideline. This limits everything else. If you can not reduce it now, plan to as income grows.</div>`;
  if (diningPct > 10) alerts += `<div class="alert alert-info"><strong>Dining out is ${diningPct.toFixed(0)}% of income.</strong> Cutting this in half frees up ${fmt(vals[4]*0.5)}/month — enough to meaningfully accelerate debt payoff.</div>`;
  if (vals[2] > 0 && (vals[2]/income)*100 > 5) alerts += `<div class="alert alert-info"><strong>Subscriptions are ${((vals[2]/income)*100).toFixed(0)}% of income.</strong> Audit these quarterly — most people are paying for 2-3 things they forgot about.</div>`;
  if (savingsRate >= 20) alerts += `<div class="alert alert-good"><strong>Your ${savingsRate.toFixed(0)}% savings rate is excellent.</strong> You are in the top tier of savers. Keep it automated so it never feels like a choice.</div>`;
  else if (savingsRate >= 10) alerts += `<div class="alert alert-info"><strong>Your ${savingsRate.toFixed(0)}% savings rate is solid.</strong> The jump from 10% to 20% is where financial independence becomes possible. Even an extra ${fmt((income*0.2)-vals[5])}/month moves the needle.</div>`;
  else alerts += `<div class="alert alert-warn"><strong>Your ${savingsRate.toFixed(0)}% savings rate is below the minimum 10%.</strong> You need an extra ${fmt((income*0.1)-vals[5])}/month saved to hit the baseline. Find it in dining and subscriptions first.</div>`;
  if (remaining > 0 && remaining/income > 0.15) alerts += `<div class="alert alert-good"><strong>You have ${fmt(remaining)} unallocated each month.</strong> This is not extra spending money — give it a job. Put it toward your highest-interest debt or emergency fund.</div>`;

  setStep('pcs', 4, 4); await sleep(300);
  hideSC('pc-sc');

  // Donut chart only — it is genuinely useful for showing proportion at a glance
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
      <div style="margin-top:4px">${alerts}</div>
    </div>
    <div class="two-col">
      <div class="card"><span class="eyebrow">Spending Breakdown</span><div style="margin-top:10px">${bars}</div></div>
      <div class="card"><span class="eyebrow">Allocation Overview</span><div class="chart-wrap-sm"><canvas id="pcDonut"></canvas></div></div>
    </div>
    <div class="card">
      <span class="eyebrow">How You Compare to Healthy Benchmarks</span>
      <p class="muted-text" style="margin-bottom:12px">These are guidelines, not rules — but staying near them gives you the most flexibility.</p>
      <div class="three-col">
        <div class="stat"><span class="stat-label">Housing</span><span class="stat-value" style="font-size:1rem;color:${housingPct>30?C.red:C.green}">${housingPct.toFixed(0)}%<span style="font-size:0.7rem;color:var(--muted)"> / 30% max</span></span></div>
        <div class="stat"><span class="stat-label">Savings</span><span class="stat-value" style="font-size:1rem;color:${savingsRate>=10?C.green:C.red}">${savingsRate.toFixed(0)}%<span style="font-size:0.7rem;color:var(--muted)"> / 10-20% goal</span></span></div>
        <div class="stat"><span class="stat-label">Dining Out</span><span class="stat-value" style="font-size:1rem;color:${diningPct>10?C.red:C.green}">${diningPct.toFixed(0)}%<span style="font-size:0.7rem;color:var(--muted)"> / 10% max</span></span></div>
      </div>
    </div>
  `;

  destroyChart('paycheck');
  const ctx = document.getElementById('pcDonut').getContext('2d');
  S.charts['paycheck'] = new Chart(ctx, {
    type: 'doughnut',
    data: { labels: donutLabels, datasets: [{ data: donutVals, backgroundColor: donutColors, borderWidth: 2, borderColor: '#fff' }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: '62%', plugins: { legend: { position: 'bottom', labels: { font:{size:10}, padding:8, boxWidth:10 } } } }
  });
}

// ── CONTEXT ───────────────────────────────────────────────────
function ctx() {
  const c = {};
  if (S.situation) c.situation = S.situation;
  if (S.plan) c.plan = S.plan;
  if (S.whatif) c.whatif = S.whatif;
  if (S.paycheck) c.paycheck = S.paycheck;
  return c;
}

// ── MILESTONES ────────────────────────────────────────────────
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
        <div class="ms-dot" style="background:${stageColors[i]}"></div>
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
      <p class="body-text" style="margin:6px 0 12px">${d.where_you_are||''}</p>
      <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:5px">
        <span class="muted-text">${d.progress_label||''}</span>
        <span style="font-weight:600">${progress}%</span>
      </div>
      <div class="bar-track" style="height:8px"><div class="bar-fill" style="width:${progress}%;background:${C.green}"></div></div>
    </div>
    <div class="ms-grid">${stagesHTML}</div>
    ${d.next_action?`<div class="alert alert-info" style="margin-top:10px"><strong>Do this first:</strong> ${d.next_action}</div>`:''}
    ${d.encouragement?`<div class="alert alert-neutral" style="margin-top:8px">${d.encouragement}</div>`:''}
  `;
}

// ── INVESTING ─────────────────────────────────────────────────
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

  // Growth chart — genuinely useful here (shows power of compounding over time)
  const chartLabels = (d.growth_projection||[]).map(p=>p.year);
  const chartData = (d.growth_projection||[]).map(p=>p.value);

  const avoids = (d.avoid||[]).map(a => `
    <div class="avoid-row">
      <div style="flex:1">
        <div class="avoid-thing">${a.thing||a}</div>
        ${a.reason?`<div class="avoid-reason">${a.reason}</div>`:''}
      </div>
    </div>`).join('');

  el.innerHTML = `
    <div class="inv-header">
      <div class="inv-header-title">${d.readiness_title||'Your Investing Readiness'}</div>
      <div class="inv-header-body">${d.readiness_explanation||''}</div>
    </div>
    <div class="acc-grid">${accCards}</div>
    ${d.the_math?`<div class="alert alert-info" style="margin-bottom:12px"><strong>The math:</strong> ${d.the_math}</div>`:''}
    <div class="card">
      <span class="eyebrow">Projected Portfolio Growth</span>
      <p class="muted-text" style="margin-bottom:4px">What consistent investing at your capacity looks like over time — at 7% average annual return.</p>
      <div class="chart-wrap"><canvas id="invChart"></canvas></div>
    </div>
    <div class="card">
      <span class="eyebrow">What to Avoid — and Why</span>
      <p class="muted-text" style="margin-bottom:10px">These are the most common mistakes people in your situation make.</p>
      ${avoids}
    </div>
    ${d.biggest_mistake?`<div class="alert alert-warn"><strong>Biggest mistake to avoid:</strong> ${d.biggest_mistake}</div>`:''}
  `;

  destroyChart('investing');
  const ctx2 = document.getElementById('invChart').getContext('2d');
  S.charts['investing'] = new Chart(ctx2, {
    type: 'line',
    data: { labels: chartLabels, datasets: [{ label: 'Portfolio Value', data: chartData, borderColor: C.green, backgroundColor: 'rgba(52,199,89,0.07)', fill:true, tension:0.4, pointRadius:4, pointBackgroundColor: C.green }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false}, tooltip:{callbacks:{label: c=>' $'+c.raw.toLocaleString()}} },
      scales: {
        x: { grid:{display:false}, ticks:{font:{size:10}} },
        y: { grid:{color:'#f0f0f0'}, ticks:{font:{size:10}, callback: v=>'$'+(v>=1000?(v/1000).toFixed(0)+'k':v)} }
      }
    }
  });
}

// ── FUTURE YOU ────────────────────────────────────────────────
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
      <span class="stat-value" style="color:${m.color||'var(--text)'};font-size:1.05rem">${m.value}</span>
      <span class="stat-note">${m.note||''}</span>
    </div>`).join('');

  // Net worth chart — the most useful chart in the app. Shows trajectory clearly.
  const chartLabels = (d.net_worth_projection||[]).map(p=>'Age '+p.age);
  const chartData = (d.net_worth_projection||[]).map(p=>p.net_worth);

  const milestones = (d.milestones_by_then||[]).map(m=>`
    <div class="milestone-check">
      <div class="check-icon">${m.achieved?'✅':'⏳'}</div>
      <div class="check-body">
        <div class="check-label">${m.label}${m.age_achieved?' — Age '+m.age_achieved:''}</div>
        <div class="check-detail">${m.detail||''}</div>
      </div>
    </div>`).join('');

  el.innerHTML = `
    ${d.headline?`<div class="card"><p class="body-text" style="font-size:0.95rem;font-weight:500">${d.headline}</p></div>`:''}
    <div class="card">
      <span class="eyebrow">At Age ${age} — Key Metrics</span>
      <div class="stat-row" style="margin-top:10px">${statCards}</div>
    </div>
    <div class="card">
      <span class="eyebrow">Net Worth Trajectory</span>
      <p class="muted-text" style="margin-bottom:4px">Starts negative (your debt), crosses zero as debt is paid, then grows as you invest.</p>
      <div class="chart-wrap"><canvas id="futChart"></canvas></div>
    </div>
    ${d.what_the_numbers_mean?`<div class="card"><span class="eyebrow">What This Actually Means</span><p class="body-text" style="margin-top:6px">${d.what_the_numbers_mean}</p></div>`:''}
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
    <div class="card"><span class="eyebrow">Milestones by Age ${age}</span><div style="margin-top:6px">${milestones}</div></div>
    ${d.the_decision_that_matters_most?`<div class="alert alert-info"><strong>The decision that matters most right now:</strong> ${d.the_decision_that_matters_most}</div>`:''}
  `;

  destroyChart('future');
  const ctx3 = document.getElementById('futChart').getContext('2d');
  // Use two colors: red below zero, blue above
  const zeroLine = chartData.findIndex(v => v >= 0);
  S.charts['future'] = new Chart(ctx3, {
    type: 'line',
    data: { labels: chartLabels, datasets: [{
      label: 'Net Worth', data: chartData,
      borderColor: C.blue, backgroundColor: 'rgba(0,122,255,0.06)',
      fill: true, tension: 0.4, pointRadius: 3, pointHoverRadius: 5
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false}, tooltip:{callbacks:{label: c=>' $'+c.raw.toLocaleString()}} },
      scales: {
        x: { grid:{display:false}, ticks:{font:{size:10}} },
        y: { grid:{color:'#f0f0f0'}, ticks:{font:{size:10}, callback: v=>'$'+(Math.abs(v)>=1000?((v/1000).toFixed(0))+'k':v)} }
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