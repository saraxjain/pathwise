from flask import Flask, request, jsonify, Response
from agent import run_pathwise, run_whatif

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Pathwise</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
            background: #ffffff;
            color: #1d1d1f;
            min-height: 100vh;
        }

        /* ── HEADER ── */
        .header {
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid #e5e5ea;
            padding: 0 48px;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-inner {
            max-width: 1000px;
            margin: 0 auto;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .logo-mark {
            width: 32px;
            height: 32px;
            background: #1d1d1f;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .logo-mark svg { width: 18px; height: 18px; }
        .logo-text {
            font-size: 1.05rem;
            font-weight: 700;
            color: #1d1d1f;
            letter-spacing: -0.02em;
        }
        .badge {
            font-size: 0.72rem;
            color: #86868b;
        }

        /* ── HERO ── */
        .hero {
            position: relative;
            min-height: 540px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: #0a0a0a;
        }

        .hero-canvas {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
        }

        .hero-content {
            position: relative;
            z-index: 2;
            text-align: center;
            padding: 80px 24px;
            max-width: 680px;
        }

        .hero-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(52, 199, 89, 0.12);
            border: 1px solid rgba(52, 199, 89, 0.25);
            border-radius: 980px;
            padding: 5px 14px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #34c759;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 24px;
        }

        .hero-eyebrow-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #34c759;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        .hero h1 {
            font-size: 3.2rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.04em;
            line-height: 1.08;
            margin-bottom: 18px;
        }

        .hero h1 span {
            background: linear-gradient(135deg, #34c759, #30d158);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero p {
            font-size: 1.05rem;
            color: rgba(255,255,255,0.5);
            line-height: 1.65;
            margin-bottom: 36px;
            max-width: 480px;
            margin-left: auto;
            margin-right: auto;
        }

        .hero-pills {
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .pill {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 980px;
            padding: 6px 14px;
            font-size: 0.76rem;
            color: rgba(255,255,255,0.45);
        }

        /* ── MAIN ── */
        .main {
            max-width: 1000px;
            margin: 0 auto;
            padding: 52px 32px 80px;
        }

        /* ── TABS ── */
        .tabs {
            display: flex;
            border-bottom: 1px solid #e5e5ea;
            margin-bottom: 44px;
            overflow-x: auto;
            gap: 0;
        }
        .tabs::-webkit-scrollbar { display: none; }

        .tab-btn {
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 12px 18px;
            font-size: 0.86rem;
            font-weight: 500;
            color: #86868b;
            cursor: pointer;
            white-space: nowrap;
            margin-bottom: -1px;
            font-family: inherit;
            transition: color 0.15s;
        }
        .tab-btn:hover { color: #1d1d1f; }
        .tab-btn.active {
            color: #1d1d1f;
            border-bottom-color: #1d1d1f;
            font-weight: 600;
        }

        /* ── PANELS ── */
        .panel { display: none; }
        .panel.active { display: block; }

        /* ── SECTION ── */
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            margin-bottom: 6px;
            color: #1d1d1f;
        }
        .section-sub {
            font-size: 0.9rem;
            color: #86868b;
            margin-bottom: 32px;
            line-height: 1.6;
            max-width: 520px;
        }

        /* ── FORM ── */
        .field { margin-bottom: 18px; }
        .field label {
            display: block;
            font-size: 0.75rem;
            font-weight: 600;
            color: #86868b;
            margin-bottom: 7px;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        textarea, input[type="number"] {
            width: 100%;
            background: #f5f5f7;
            border: 1.5px solid transparent;
            border-radius: 12px;
            color: #1d1d1f;
            font-size: 0.93rem;
            padding: 13px 15px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.15s, background 0.15s;
            line-height: 1.55;
        }
        textarea { resize: vertical; min-height: 110px; }
        textarea:focus, input:focus {
            border-color: #34c759;
            background: #ffffff;
        }

        /* ── BUTTON ── */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #1d1d1f;
            color: #ffffff;
            border: none;
            border-radius: 980px;
            padding: 13px 26px;
            font-size: 0.88rem;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            margin-top: 6px;
            transition: background 0.15s, transform 0.1s;
        }
        .btn:hover { background: #3a3a3c; transform: translateY(-1px); }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
        .btn-full { width: 100%; justify-content: center; }

        /* ── STEPS ── */
        .steps {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 22px;
            padding: 20px 22px;
            background: #f9f9f9;
            border-radius: 14px;
        }
        .step {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.84rem;
            color: #c7c7cc;
            transition: color 0.3s;
        }
        .step.active { color: #1d1d1f; font-weight: 500; }
        .step.done { color: #34c759; }
        .step-dot {
            width: 7px; height: 7px;
            border-radius: 50%;
            background: #e5e5ea;
            flex-shrink: 0;
            transition: background 0.3s;
        }
        .step.active .step-dot { background: #34c759; }
        .step.done .step-dot { background: #34c759; }

        /* ── RESULT ── */
        .result-wrap {
            margin-top: 24px;
            display: none;
        }
        .result-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #86868b;
            margin-bottom: 10px;
        }
        .result {
            background: #f9f9f9;
            border-radius: 16px;
            padding: 28px 32px;
            white-space: pre-wrap;
            font-size: 0.88rem;
            line-height: 1.85;
            color: #1d1d1f;
            max-height: 560px;
            overflow-y: auto;
            border: 1px solid #f0f0f0;
        }
        .result::-webkit-scrollbar { width: 4px; }
        .result::-webkit-scrollbar-track { background: transparent; }
        .result::-webkit-scrollbar-thumb { background: #e5e5ea; border-radius: 2px; }

        /* ── TWO COL ── */
        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }

        /* ── STAT CARDS ── */
        .stat-row {
            display: flex;
            gap: 12px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }
        .stat-card {
            flex: 1;
            min-width: 120px;
            background: #f5f5f7;
            border-radius: 14px;
            padding: 18px 20px;
        }
        .stat-label {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #86868b;
            margin-bottom: 6px;
            display: block;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            display: block;
        }

        /* ── BARS ── */
        .bar-row {
            display: grid;
            grid-template-columns: 148px 1fr 68px 46px;
            align-items: center;
            gap: 12px;
            margin-bottom: 11px;
            font-size: 0.85rem;
        }
        .bar-track {
            background: #f0f0f0;
            border-radius: 99px;
            height: 5px;
            overflow: hidden;
        }
        .bar-fill { height: 100%; border-radius: 99px; transition: width 0.6s ease; }

        /* ── TIP ── */
        .tip {
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.84rem;
            margin: 16px 0;
            font-weight: 500;
        }
        .tip-warn { background: #fff2f2; color: #ff3b30; }
        .tip-good { background: #f0fff4; color: #248a3d; }
        .tip-neutral { background: #f5f5f7; color: #86868b; }

        /* ── BENCH ── */
        .bench-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        .bench-card {
            background: #f5f5f7;
            border-radius: 10px;
            padding: 14px 16px;
        }
        .bench-label {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #86868b;
            margin-bottom: 4px;
            display: block;
        }
        .bench-value {
            font-size: 0.9rem;
            font-weight: 600;
            color: #1d1d1f;
        }

        /* ── EYEBROW ── */
        .eyebrow {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #86868b;
            margin-bottom: 12px;
            display: block;
            margin-top: 28px;
        }

        /* ── MILESTONE ── */
        .milestone-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }
        .milestone-card {
            background: #f9f9f9;
            border-radius: 16px;
            padding: 24px 26px;
            border: 1px solid #f0f0f0;
        }
        .milestone-stage {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 16px;
            display: block;
        }
        .milestone-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 11px;
            font-size: 0.85rem;
            color: #3a3a3c;
            line-height: 1.5;
        }
        .mdot {
            width: 6px; height: 6px;
            border-radius: 50%;
            flex-shrink: 0;
            margin-top: 6px;
        }

        /* ── INVESTING ── */
        .inv-hero {
            background: #1d1d1f;
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 22px;
        }
        .inv-hero-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
            letter-spacing: -0.02em;
        }
        .inv-hero-sub {
            font-size: 0.88rem;
            color: rgba(255,255,255,0.45);
            line-height: 1.55;
        }
        .inv-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
            margin-bottom: 28px;
        }
        .inv-card {
            background: #f9f9f9;
            border-radius: 14px;
            padding: 20px;
            border: 1px solid #f0f0f0;
        }
        .inv-title {
            font-size: 0.88rem;
            font-weight: 700;
            color: #1d1d1f;
            margin-bottom: 8px;
        }
        .inv-desc {
            font-size: 0.81rem;
            color: #86868b;
            line-height: 1.6;
        }
        .step-list { margin-bottom: 6px; }
        .step-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 0;
            border-bottom: 1px solid #f5f5f7;
            font-size: 0.87rem;
            color: #1d1d1f;
        }
        .step-num {
            width: 24px; height: 24px;
            border-radius: 50%;
            background: #1d1d1f;
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .avoid-item {
            padding: 10px 14px;
            background: #fff5f5;
            border-radius: 8px;
            font-size: 0.83rem;
            color: #ff3b30;
            margin-bottom: 7px;
        }

        /* ── FUTURE ── */
        .future-card {
            background: #f9f9f9;
            border-radius: 18px;
            padding: 30px 32px;
            border: 1px solid #f0f0f0;
        }
        .future-age {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
            display: block;
        }
        .future-title {
            font-size: 1.55rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            margin-bottom: 6px;
        }
        .future-sub {
            font-size: 0.9rem;
            color: #86868b;
            margin-bottom: 20px;
            line-height: 1.55;
        }
        .future-bullet {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 0.87rem;
            line-height: 1.5;
        }
        .future-insight {
            background: white;
            border-radius: 10px;
            padding: 14px 16px;
            margin-top: 20px;
            font-size: 0.85rem;
            line-height: 1.6;
            color: #3a3a3c;
        }

        /* ── SLIDER ── */
        input[type="range"] {
            width: 100%;
            accent-color: #34c759;
            margin: 10px 0 28px;
            background: transparent;
            padding: 0;
            border: none;
            box-shadow: none;
        }
        input[type="range"]:focus { box-shadow: none; }

        /* ── FOOTER ── */
        .footer {
            text-align: center;
            padding: 32px;
            border-top: 1px solid #f0f0f0;
            font-size: 0.78rem;
            color: #c7c7cc;
            margin-top: 60px;
        }

        @media (max-width: 700px) {
            .hero h1 { font-size: 2.2rem; }
            .header { padding: 0 20px; }
            .main { padding: 36px 20px 60px; }
            .two-col, .milestone-grid, .inv-grid { grid-template-columns: 1fr; }
            .bar-row { grid-template-columns: 100px 1fr 58px 40px; }
        }
    </style>
</head>
<body>

<!-- HEADER -->
<div class="header">
    <div class="header-inner">
        <div class="logo">
            <div class="logo-mark">
                <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 13L7 8L10 11L13 6L15 8" stroke="#34c759" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="15" cy="8" r="1.2" fill="#34c759"/>
                </svg>
            </div>
            <span class="logo-text">Pathwise</span>
        </div>
        <span class="badge">Powered by NVIDIA Nemotron</span>
    </div>
</div>

<!-- HERO -->
<div class="hero">
    <canvas class="hero-canvas" id="heroCanvas"></canvas>
    <div class="hero-content">
        <div class="hero-eyebrow">
            <div class="hero-eyebrow-dot"></div>
            AI-Powered Financial Planning
        </div>
        <h1>Your money,<br><span>working smarter.</span></h1>
        <p>Describe your situation in plain English. Pathwise fetches live rates, reasons through your priorities, and builds your personalized roadmap.</p>
        <div class="hero-pills">
            <span class="pill">Live rate data</span>
            <span class="pill">Persistent memory</span>
            <span class="pill">Multi-step reasoning</span>
            <span class="pill">What-if scenarios</span>
        </div>
    </div>
</div>

<!-- MAIN -->
<div class="main">
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('plan', this)">Build My Plan</button>
        <button class="tab-btn" onclick="switchTab('whatif', this)">What-If</button>
        <button class="tab-btn" onclick="switchTab('paycheck', this)">Paycheck</button>
        <button class="tab-btn" onclick="switchTab('milestones', this)">Milestones</button>
        <button class="tab-btn" onclick="switchTab('investing', this)">Investing</button>
        <button class="tab-btn" onclick="switchTab('future', this)">Future You</button>
    </div>

    <!-- BUILD MY PLAN -->
    <div id="tab-plan" class="panel active">
        <div class="section-title">Build My Roadmap</div>
        <div class="section-sub">Tell Pathwise about your income, debts, and goals. It will fetch live rates and build a month-by-month plan tailored to you.</div>
        <div class="field">
            <label>Your financial situation</label>
            <textarea id="situation" placeholder="e.g. I'm a UCSC student, I make $1,200/month from part-time work, I have $4,500 in credit card debt at 24% APR, and I want to graduate debt-free in 2 years."></textarea>
        </div>
        <button class="btn btn-full" id="plan-btn" onclick="buildPlan()">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M7.5 1L9.5 5.5L14 6.5L10.5 10L11.5 14.5L7.5 12L3.5 14.5L4.5 10L1 6.5L5.5 5.5L7.5 1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>
            Generate My Roadmap
        </button>
        <div class="steps" id="plan-steps" style="display:none">
            <div class="step" id="s1"><div class="step-dot"></div>Loading memory</div>
            <div class="step" id="s2"><div class="step-dot"></div>Fetching live HYSA, mortgage & market rates</div>
            <div class="step" id="s3"><div class="step-dot"></div>Extracting your financial profile</div>
            <div class="step" id="s4"><div class="step-dot"></div>Nemotron building your roadmap</div>
            <div class="step" id="s5"><div class="step-dot"></div>Saving to memory</div>
        </div>
        <div class="result-wrap" id="plan-result-wrap">
            <div class="result-label">Your Roadmap</div>
            <div class="result" id="plan-result"></div>
        </div>
    </div>

    <!-- WHAT-IF -->
    <div id="tab-whatif" class="panel">
        <div class="section-title">What-If Scenarios</div>
        <div class="section-sub">Explore how a change affects your plan. Build your plan first, then ask anything.</div>
        <div class="field">
            <label>Describe a scenario</label>
            <textarea id="scenario" placeholder="e.g. What if I get a raise to $1,500/month? What if I pay $200 extra toward debt each month?"></textarea>
        </div>
        <button class="btn btn-full" id="whatif-btn" onclick="runWhatIf()">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M1 7.5C1 4 4 1 7.5 1S14 4 14 7.5 11 14 7.5 14 1 11 1 7.5Z" stroke="currentColor" stroke-width="1.3"/><path d="M7.5 5V7.5L9 9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
            Run Scenario
        </button>
        <div class="result-wrap" id="whatif-result-wrap">
            <div class="result-label">Analysis</div>
            <div class="result" id="whatif-result"></div>
        </div>
    </div>

    <!-- PAYCHECK -->
    <div id="tab-paycheck" class="panel">
        <div class="section-title">Paycheck Breakdown</div>
        <div class="section-sub">See exactly where your money goes and where you can make the biggest impact.</div>
        <div class="field">
            <label>Monthly take-home income</label>
            <input type="number" id="pay-income" placeholder="e.g. 2800">
        </div>
        <div class="two-col">
            <div class="field"><label>Rent / Housing</label><input type="number" id="pay-rent" value="0"></div>
            <div class="field"><label>Groceries</label><input type="number" id="pay-groceries" value="0"></div>
            <div class="field"><label>Subscriptions</label><input type="number" id="pay-subscriptions" value="0"></div>
            <div class="field"><label>Transport</label><input type="number" id="pay-transport" value="0"></div>
            <div class="field"><label>Dining Out</label><input type="number" id="pay-dining" value="0"></div>
            <div class="field"><label>Savings</label><input type="number" id="pay-savings" value="0"></div>
            <div class="field"><label>Other</label><input type="number" id="pay-other" value="0"></div>
        </div>
        <button class="btn btn-full" onclick="calcPaycheck()">Calculate Breakdown</button>
        <div id="paycheck-result" style="margin-top:28px"></div>
    </div>

    <!-- MILESTONES -->
    <div id="tab-milestones" class="panel">
        <div class="section-title">Financial Milestones</div>
        <div class="section-sub">Four stages, in order. Each one builds the foundation for the next.</div>
        <div class="milestone-grid">
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#007aff">Foundation</span>
                <div class="milestone-item"><div class="mdot" style="background:#007aff"></div>Open a checking account</div>
                <div class="milestone-item"><div class="mdot" style="background:#007aff"></div>Open a high-yield savings account</div>
                <div class="milestone-item"><div class="mdot" style="background:#007aff"></div>Save your first $500</div>
                <div class="milestone-item"><div class="mdot" style="background:#007aff"></div>Get a beginner credit card, pay it off monthly</div>
            </div>
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#34c759">Security</span>
                <div class="milestone-item"><div class="mdot" style="background:#34c759"></div>Build a $1,000 emergency fund</div>
                <div class="milestone-item"><div class="mdot" style="background:#34c759"></div>Grow to 3 months of expenses</div>
                <div class="milestone-item"><div class="mdot" style="background:#34c759"></div>Understand your credit score</div>
            </div>
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#ff9500">Growth</span>
                <div class="milestone-item"><div class="mdot" style="background:#ff9500"></div>Start investing in index funds</div>
                <div class="milestone-item"><div class="mdot" style="background:#ff9500"></div>Open a Roth IRA if eligible</div>
                <div class="milestone-item"><div class="mdot" style="background:#ff9500"></div>Automate savings transfers</div>
            </div>
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#5856d6">Optimization</span>
                <div class="milestone-item"><div class="mdot" style="background:#5856d6"></div>Increase income or reduce fixed costs</div>
                <div class="milestone-item"><div class="mdot" style="background:#5856d6"></div>Learn about 401k and HSA</div>
                <div class="milestone-item"><div class="mdot" style="background:#5856d6"></div>Track net worth quarterly</div>
            </div>
        </div>
        <p style="font-size:0.82rem;color:#c7c7cc;text-align:center;margin-top:20px;font-style:italic">Work through these in order — each stage enables the next.</p>
    </div>

    <!-- INVESTING -->
    <div id="tab-investing" class="panel">
        <div class="inv-hero">
            <div class="inv-hero-title">Investing Basics</div>
            <div class="inv-hero-sub">Invest consistently, over a long period, into diversified low-cost funds. That's mostly it.</div>
        </div>
        <div class="inv-grid">
            <div class="inv-card">
                <div class="inv-title" style="color:#007aff">Index Funds</div>
                <div class="inv-desc">Track the whole market. Low fees, automatic diversification, strong long-term returns.</div>
            </div>
            <div class="inv-card">
                <div class="inv-title" style="color:#34c759">Roth IRA</div>
                <div class="inv-desc">Contribute after-tax, withdraw tax-free. $7,000/year limit. Open one early.</div>
            </div>
            <div class="inv-card">
                <div class="inv-title" style="color:#ff9500">401(k)</div>
                <div class="inv-desc">Always get the full employer match — that money is part of your compensation.</div>
            </div>
        </div>
        <span class="eyebrow" style="margin-top:0">The Starting Order</span>
        <div class="step-list">
            <div class="step-item"><div class="step-num">1</div>Build a 3–6 month emergency fund first</div>
            <div class="step-item"><div class="step-num">2</div>Contribute to 401k up to the employer match</div>
            <div class="step-item"><div class="step-num">3</div>Open a Roth IRA and fund it monthly</div>
            <div class="step-item"><div class="step-num">4</div>Invest the rest in a total market index fund</div>
        </div>
        <span class="eyebrow">What to Avoid</span>
        <div class="avoid-item">✕ &nbsp;Day trading — most retail traders lose money</div>
        <div class="avoid-item">✕ &nbsp;Individual stock picking without deep research</div>
        <div class="avoid-item">✕ &nbsp;Crypto as a primary investment strategy</div>
        <div class="avoid-item">✕ &nbsp;Anything promising unusually high guaranteed returns</div>
        <p style="text-align:center;font-style:italic;font-size:0.83rem;color:#c7c7cc;padding-top:24px;border-top:1px solid #f0f0f0;margin-top:24px">Wealth is built through consistency and time, not timing or complexity.</p>
    </div>

    <!-- FUTURE YOU -->
    <div id="tab-future" class="panel">
        <div class="section-title">Future You</div>
        <div class="section-sub">Slide to your age to see the right priorities for your life stage.</div>
        <label style="font-size:0.75rem;font-weight:600;color:#86868b;text-transform:uppercase;letter-spacing:0.03em">Age: <span id="age-display">20</span></label>
        <input type="range" min="18" max="40" value="20" oninput="updateFuture(this.value)">
        <div id="future-content"></div>
    </div>
</div>

<div class="footer">
    Built at Hack-a-Claw 2026 &nbsp;·&nbsp; NVIDIA × UCSC Baskin Engineering
</div>

<script>
// ── ANIMATED CANVAS BACKGROUND ────────────────────────────────────────────────
(function() {
    const canvas = document.getElementById('heroCanvas');
    const ctx = canvas.getContext('2d');
    let W, H, particles = [], lines = [];
    const COUNT = 55;

    function resize() {
        W = canvas.width = canvas.offsetWidth;
        H = canvas.height = canvas.offsetHeight;
    }

    function rand(a, b) { return a + Math.random() * (b - a); }

    function init() {
        resize();
        particles = [];
        for (let i = 0; i < COUNT; i++) {
            particles.push({
                x: rand(0, W), y: rand(0, H),
                vx: rand(-0.3, 0.3), vy: rand(-0.2, 0.2),
                r: rand(1, 2.2),
                alpha: rand(0.2, 0.7),
            });
        }
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);

        // subtle gradient overlay
        const grad = ctx.createRadialGradient(W*0.5, H*0.5, 0, W*0.5, H*0.5, W*0.7);
        grad.addColorStop(0, 'rgba(52,199,89,0.04)');
        grad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // draw lines between close particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(52,199,89,${0.08 * (1 - dist/120)})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        // draw particles
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(52,199,89,${p.alpha})`;
            ctx.fill();

            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > W) p.vx *= -1;
            if (p.y < 0 || p.y > H) p.vy *= -1;
        });

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', () => { resize(); });
    init();
    draw();
})();

// ── TAB SWITCHING ─────────────────────────────────────────────────────────────
function switchTab(name, el) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    el.classList.add('active');
    if (name === 'future') updateFuture(20);
}

// ── STEPS ─────────────────────────────────────────────────────────────────────
function setStep(n) {
    for (let i = 1; i <= 5; i++) {
        const el = document.getElementById('s' + i);
        el.className = 'step' + (i < n ? ' done' : i === n ? ' active' : '');
    }
}

// ── BUILD PLAN ────────────────────────────────────────────────────────────────
async function buildPlan() {
    const situation = document.getElementById('situation').value.trim();
    if (!situation) return alert('Please describe your situation first.');
    const btn = document.getElementById('plan-btn');
    const stepsEl = document.getElementById('plan-steps');
    const resultWrap = document.getElementById('plan-result-wrap');
    const resultEl = document.getElementById('plan-result');
    btn.disabled = true;
    btn.textContent = 'Building...';
    stepsEl.style.display = 'flex';
    resultWrap.style.display = 'none';
    setStep(1); await sleep(400);
    setStep(2); await sleep(400);
    setStep(3);
    try {
        const res = await fetch('/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ situation })
        });
        setStep(4); await sleep(300);
        const data = await res.json();
        setStep(5); await sleep(200);
        resultEl.textContent = data.roadmap || data.error;
        resultWrap.style.display = 'block';
    } catch(e) {
        resultEl.textContent = 'Error: ' + e.message;
        resultWrap.style.display = 'block';
    }
    btn.disabled = false;
    btn.innerHTML = '<svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M7.5 1L9.5 5.5L14 6.5L10.5 10L11.5 14.5L7.5 12L3.5 14.5L4.5 10L1 6.5L5.5 5.5L7.5 1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg> Generate My Roadmap';
}

// ── WHAT-IF ───────────────────────────────────────────────────────────────────
async function runWhatIf() {
    const scenario = document.getElementById('scenario').value.trim();
    if (!scenario) return alert('Please describe a scenario.');
    const btn = document.getElementById('whatif-btn');
    const resultWrap = document.getElementById('whatif-result-wrap');
    const resultEl = document.getElementById('whatif-result');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    try {
        const res = await fetch('/whatif', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario })
        });
        const data = await res.json();
        resultEl.textContent = data.result || data.error;
        resultWrap.style.display = 'block';
    } catch(e) {
        resultEl.textContent = 'Error: ' + e.message;
        resultWrap.style.display = 'block';
    }
    btn.disabled = false;
    btn.innerHTML = '<svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M1 7.5C1 4 4 1 7.5 1S14 4 14 7.5 11 14 7.5 14 1 11 1 7.5Z" stroke="currentColor" stroke-width="1.3"/><path d="M7.5 5V7.5L9 9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg> Run Scenario';
}

// ── PAYCHECK ──────────────────────────────────────────────────────────────────
function calcPaycheck() {
    const income = parseFloat(document.getElementById('pay-income').value) || 0;
    if (!income) { document.getElementById('paycheck-result').innerHTML = '<p style="color:#86868b;font-size:0.88rem;padding:8px 0">Enter your monthly income first.</p>'; return; }
    const fields = ['rent','groceries','subscriptions','transport','dining','savings','other'];
    const labels = ['Rent / Housing','Groceries','Subscriptions','Transport','Dining Out','Savings','Other'];
    let total = 0;
    const vals = fields.map(f => { const v = parseFloat(document.getElementById('pay-'+f).value)||0; total+=v; return v; });
    const remaining = income - total;
    const rc = remaining >= 0 ? '#34c759' : '#ff3b30';
    const rl = remaining >= 0 ? 'Remaining' : 'Over Budget';
    let bars = '';
    fields.forEach((f,i) => {
        if (vals[i] > 0) {
            const pct = (vals[i]/income)*100;
            let c = '#007aff';
            if (f === 'savings') c = '#34c759';
            if (pct > 35 && f !== 'savings' && f !== 'rent') c = '#ff3b30';
            bars += `<div class="bar-row">
                <span style="color:#3a3a3c;font-size:0.85rem">${labels[i]}</span>
                <div class="bar-track"><div class="bar-fill" style="width:${Math.min(pct,100).toFixed(1)}%;background:${c}"></div></div>
                <span style="text-align:right;color:#1d1d1f;font-weight:600;font-size:0.85rem">$${vals[i].toLocaleString()}</span>
                <span style="text-align:right;color:#86868b;font-size:0.76rem">${pct.toFixed(1)}%</span>
            </div>`;
        }
    });
    let tip = '';
    if (remaining < 0) tip = '<div class="tip tip-warn">Your expenses exceed your income. Review subscriptions and dining first.</div>';
    else if (remaining/income > 0.2) tip = `<div class="tip tip-good">You have ${((remaining/income)*100).toFixed(0)}% unallocated — consider moving this to savings.</div>`;
    else tip = '<div class="tip tip-neutral">Budget is tight. Small cuts in dining and subscriptions can free up real savings.</div>';
    const benchmarks = [['Housing','under 30%'],['Savings','10–20%+'],['Subscriptions','audit quarterly'],['Dining','under 10%']];
    const benchHtml = benchmarks.map(b => `<div class="bench-card"><span class="bench-label">${b[0]}</span><span class="bench-value">${b[1]}</span></div>`).join('');
    document.getElementById('paycheck-result').innerHTML = `
        <div class="stat-row">
            <div class="stat-card"><span class="stat-label">Income</span><span class="stat-value" style="color:#34c759">$${income.toLocaleString()}</span></div>
            <div class="stat-card"><span class="stat-label">Expenses</span><span class="stat-value">$${total.toLocaleString()}</span></div>
            <div class="stat-card"><span class="stat-label">${rl}</span><span class="stat-value" style="color:${rc}">$${Math.abs(remaining).toLocaleString()}</span></div>
        </div>
        ${bars}${tip}
        <span class="eyebrow" style="margin-top:24px">Benchmarks</span>
        <div class="bench-grid">${benchHtml}</div>`;
}

// ── FUTURE YOU ────────────────────────────────────────────────────────────────
const stages = [
    { max:22, color:'#34c759', range:'18–21', title:'Build the Base', sub:'Your biggest asset right now is time — not money.', points:['Focus on saving habits, not just amounts','Build credit with responsible use','$50/month at 20 grows more than $200/month at 30'], insight:'Starting early is your single biggest financial advantage.' },
    { max:27, color:'#007aff', range:'22–26', title:'Build Momentum', sub:'More income now. Habits become systems.', points:['Always get the full 401k employer match','Pay off high-interest debt aggressively','Start investing in index funds regularly'], insight:'This decade is when the gap between investors and non-investors widens.' },
    { max:32, color:'#ff9500', range:'27–31', title:'Optimize and Grow', sub:'Real earning potential. Widen the income-spending gap.', points:['Max out Roth IRA ($7,000/year)','Increase 401k beyond the match','Evaluate whether buying property fits your goals'], insight:'Decisions in your late 20s shape your trajectory for decades.' },
    { max:41, color:'#5856d6', range:'32–40', title:'Wealth Building', sub:"Compounding is doing the heavy lifting. Don't interrupt it.", points:['Review investment portfolio annually','Consider a fee-only financial advisor','Protect wealth with adequate insurance'], insight:'Focus shifts from learning to optimizing. Systems matter more than tactics.' },
];

function updateFuture(age) {
    age = parseInt(age);
    document.getElementById('age-display').textContent = age;
    const s = stages.find(s => age < s.max) || stages[stages.length-1];
    const bullets = s.points.map(p => `<div class="future-bullet"><span style="color:${s.color};font-weight:700;flex-shrink:0">→</span><span>${p}</span></div>`).join('');
    document.getElementById('future-content').innerHTML = `
    <div class="future-card" style="border-top:3px solid ${s.color}">
        <span class="future-age" style="color:${s.color}">Ages ${s.range}</span>
        <div class="future-title">${s.title}</div>
        <div class="future-sub">${s.sub}</div>
        ${bullets}
        <div class="future-insight" style="border-left:3px solid ${s.color}">
            <strong>Why it matters:</strong> ${s.insight}
        </div>
    </div>`;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
updateFuture(20);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(HTML, mimetype='text/html')

@app.route("/plan", methods=["POST"])
def plan():
    data = request.json
    try:
        roadmap = run_pathwise(data.get("situation", ""))
        return jsonify({"roadmap": roadmap})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/whatif", methods=["POST"])
def whatif():
    data = request.json
    try:
        result = run_whatif(data.get("scenario", ""))
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)