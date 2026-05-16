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
            background: #f5f5f7;
            color: #1d1d1f;
            min-height: 100vh;
        }

        /* ── HEADER ── */
        .header {
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid #d2d2d7;
            padding: 0 48px;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-inner {
            max-width: 960px;
            margin: 0 auto;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1d1d1f;
            letter-spacing: -0.01em;
        }
        .badge {
            font-size: 0.72rem;
            color: #86868b;
            font-weight: 400;
        }

        /* ── HERO ── */
        .hero {
            background: #1d1d1f;
            padding: 72px 48px 64px;
            text-align: center;
        }
        .hero h1 {
            font-size: 3rem;
            font-weight: 700;
            color: #f5f5f7;
            letter-spacing: -0.04em;
            line-height: 1.05;
            margin-bottom: 16px;
        }
        .hero p {
            font-size: 1.1rem;
            color: rgba(255,255,255,0.55);
            font-weight: 400;
            max-width: 500px;
            margin: 0 auto 28px;
            line-height: 1.6;
        }
        .hero-pills {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .pill {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 980px;
            padding: 6px 16px;
            font-size: 0.78rem;
            color: rgba(255,255,255,0.55);
        }

        /* ── MAIN CONTENT ── */
        .main {
            max-width: 960px;
            margin: 0 auto;
            padding: 48px 24px 80px;
        }

        /* ── TABS ── */
        .tabs {
            display: flex;
            gap: 0;
            border-bottom: 1px solid #d2d2d7;
            margin-bottom: 40px;
            overflow-x: auto;
        }
        .tabs::-webkit-scrollbar { display: none; }
        .tab-btn {
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 12px 20px;
            font-size: 0.88rem;
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

        /* ── SECTION HEADER ── */
        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1d1d1f;
            letter-spacing: -0.02em;
            margin-bottom: 6px;
        }
        .section-sub {
            font-size: 0.9rem;
            color: #86868b;
            margin-bottom: 28px;
            line-height: 1.55;
        }

        /* ── CARDS ── */
        .card {
            background: #ffffff;
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 16px;
        }

        /* ── FORM ELEMENTS ── */
        label {
            display: block;
            font-size: 0.78rem;
            font-weight: 500;
            color: #86868b;
            margin-bottom: 6px;
            letter-spacing: 0.01em;
        }
        textarea, input[type="text"], input[type="number"] {
            width: 100%;
            background: #f5f5f7;
            border: none;
            border-radius: 10px;
            color: #1d1d1f;
            font-size: 0.95rem;
            padding: 12px 14px;
            font-family: inherit;
            outline: none;
            transition: box-shadow 0.15s;
            -webkit-appearance: none;
        }
        textarea { resize: vertical; min-height: 100px; }
        textarea:focus, input:focus {
            box-shadow: 0 0 0 3px rgba(0,125,250,0.25);
        }

        /* ── BUTTON ── */
        .btn {
            display: inline-block;
            background: #1d1d1f;
            color: #ffffff;
            border: none;
            border-radius: 980px;
            padding: 13px 28px;
            font-size: 0.9rem;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            margin-top: 16px;
            transition: background 0.15s, transform 0.1s;
            width: 100%;
        }
        .btn:hover { background: #3a3a3c; transform: translateY(-1px); }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

        /* ── STEPS ── */
        .steps {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 20px;
        }
        .step {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.85rem;
            color: #d2d2d7;
            transition: color 0.3s;
        }
        .step.active { color: #1d1d1f; }
        .step.done { color: #34c759; }
        .step-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #d2d2d7;
            flex-shrink: 0;
            transition: background 0.3s;
        }
        .step.active .step-dot { background: #007aff; }
        .step.done .step-dot { background: #34c759; }

        /* ── RESULT ── */
        .result {
            background: #f5f5f7;
            border-radius: 14px;
            padding: 24px 28px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-size: 0.88rem;
            line-height: 1.75;
            color: #1d1d1f;
            display: none;
            max-height: 520px;
            overflow-y: auto;
        }

        /* ── PAYCHECK ── */
        .stat-grid {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        .stat-card {
            flex: 1;
            min-width: 130px;
            background: #f5f5f7;
            border-radius: 12px;
            padding: 16px 18px;
        }
        .stat-label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #86868b;
            margin-bottom: 6px;
            display: block;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1d1d1f;
            display: block;
        }
        .bar-row {
            display: grid;
            grid-template-columns: 150px 1fr 68px 46px;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }
        .bar-label { font-size: 0.86rem; color: #1d1d1f; }
        .bar-track {
            background: #f5f5f7;
            border-radius: 99px;
            height: 6px;
            overflow: hidden;
        }
        .bar-fill { height: 100%; border-radius: 99px; }
        .bar-amount { font-size: 0.86rem; font-weight: 600; text-align: right; color: #1d1d1f; }
        .bar-pct { font-size: 0.76rem; color: #86868b; text-align: right; }
        .tip-box {
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.85rem;
            margin: 16px 0;
        }
        .tip-warn { background: #fff2f2; color: #ff3b30; }
        .tip-good { background: #f0fff4; color: #248a3d; }
        .tip-neutral { background: #f5f5f7; color: #86868b; }
        .benchmark-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
            margin-top: 16px;
        }
        .benchmark-card {
            background: #f5f5f7;
            border-radius: 10px;
            padding: 14px 16px;
        }
        .benchmark-label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #86868b;
            margin-bottom: 4px;
            display: block;
        }
        .benchmark-value {
            font-size: 0.92rem;
            font-weight: 600;
            color: #1d1d1f;
            display: block;
        }
        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        @media (max-width: 600px) {
            .two-col { grid-template-columns: 1fr; }
            .hero h1 { font-size: 2rem; }
            .header { padding: 0 20px; }
            .main { padding: 32px 16px 60px; }
            .bar-row { grid-template-columns: 110px 1fr 58px 40px; }
        }

        /* ── MILESTONES ── */
        .milestone-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
        }
        .milestone-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 22px 24px;
        }
        .milestone-stage {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 14px;
            display: block;
        }
        .milestone-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 0.86rem;
            color: #1d1d1f;
            line-height: 1.5;
        }
        .milestone-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            flex-shrink: 0;
            margin-top: 5px;
        }

        /* ── FUTURE YOU ── */
        .future-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 32px;
        }
        .future-age {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
            display: block;
        }
        .future-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1d1d1f;
            letter-spacing: -0.02em;
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
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 0.88rem;
            color: #1d1d1f;
            line-height: 1.5;
        }
        .future-insight {
            border-radius: 10px;
            padding: 14px 16px;
            margin-top: 16px;
            font-size: 0.86rem;
            color: #1d1d1f;
            line-height: 1.6;
            background: #f5f5f7;
        }

        /* ── INVESTING ── */
        .investing-hero {
            background: #1d1d1f;
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 22px;
        }
        .investing-hero-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
        }
        .investing-hero-sub {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.55);
            line-height: 1.5;
        }
        .investing-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }
        .investing-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 20px;
        }
        .investing-card-title {
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .investing-card-desc {
            font-size: 0.82rem;
            color: #86868b;
            line-height: 1.6;
        }
        .step-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 22px;
        }
        .step-item {
            display: flex;
            align-items: center;
            gap: 14px;
            background: #ffffff;
            border-radius: 10px;
            padding: 13px 16px;
            font-size: 0.88rem;
            color: #1d1d1f;
        }
        .step-num {
            background: #1d1d1f;
            color: #ffffff;
            font-weight: 700;
            font-size: 0.75rem;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .avoid-item {
            background: #fff2f2;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 0.84rem;
            color: #ff3b30;
            margin-bottom: 8px;
        }

        .section-eyebrow {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #86868b;
            margin-bottom: 10px;
            display: block;
        }

        /* ── FOOTER ── */
        .footer {
            text-align: center;
            padding: 32px;
            border-top: 1px solid #d2d2d7;
            font-size: 0.8rem;
            color: #86868b;
        }

        /* ── AGE SLIDER ── */
        input[type="range"] {
            width: 100%;
            accent-color: #1d1d1f;
            background: transparent;
            padding: 0;
            margin: 8px 0 24px;
            box-shadow: none;
        }
        input[type="range"]:focus { box-shadow: none; }
    </style>
</head>
<body>

<!-- HEADER -->
<div class="header">
    <div class="header-inner">
        <span class="logo">Pathwise</span>
        <span class="badge">Powered by NVIDIA Nemotron</span>
    </div>
</div>

<!-- HERO -->
<div class="hero">
    <h1>Your financial plan,<br>built by AI.</h1>
    <p>Describe your situation in plain English. Pathwise fetches live rates and builds your personalized roadmap.</p>
    <div class="hero-pills">
        <span class="pill">Live data</span>
        <span class="pill">Persistent memory</span>
        <span class="pill">Multi-step reasoning</span>
        <span class="pill">What-if scenarios</span>
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

    <!-- TAB: BUILD MY PLAN -->
    <div id="tab-plan" class="panel active">
        <div class="section-title">Build My Roadmap</div>
        <div class="section-sub">Nemotron will fetch live rates and reason through your priorities to build a month-by-month plan.</div>
        <div class="card">
            <label>Describe your financial situation</label>
            <textarea id="situation" placeholder="e.g. I'm a UCSC student, I make $1,200/month from part-time work, I have $4,500 in credit card debt at 24% APR, and I want to graduate debt-free in 2 years."></textarea>
            <button class="btn" id="plan-btn" onclick="buildPlan()">Build My Roadmap</button>
            <div class="steps" id="plan-steps" style="display:none">
                <div class="step" id="s1"><div class="step-dot"></div>Loading memory</div>
                <div class="step" id="s2"><div class="step-dot"></div>Fetching live rates (HYSA, mortgage, S&P 500)</div>
                <div class="step" id="s3"><div class="step-dot"></div>Extracting your financial profile</div>
                <div class="step" id="s4"><div class="step-dot"></div>Nemotron is building your roadmap</div>
                <div class="step" id="s5"><div class="step-dot"></div>Saving to memory</div>
            </div>
        </div>
        <div class="result" id="plan-result"></div>
    </div>

    <!-- TAB: WHAT-IF -->
    <div id="tab-whatif" class="panel">
        <div class="section-title">What-If Scenarios</div>
        <div class="section-sub">Explore how changes to your situation affect your plan. Build your plan first.</div>
        <div class="card">
            <label>Describe a scenario</label>
            <textarea id="scenario" placeholder="e.g. What if I get a raise to $1,500/month? What if I pay an extra $200 toward debt?"></textarea>
            <button class="btn" id="whatif-btn" onclick="runWhatIf()">Run Scenario</button>
        </div>
        <div class="result" id="whatif-result"></div>
    </div>

    <!-- TAB: PAYCHECK -->
    <div id="tab-paycheck" class="panel">
        <div class="section-title">Paycheck Breakdown</div>
        <div class="section-sub">See exactly where your money goes and where you can cut.</div>
        <div class="card">
            <div style="margin-bottom:20px">
                <label>Monthly Take-Home Income</label>
                <input type="number" id="pay-income" placeholder="e.g. 2800">
            </div>
            <div class="two-col">
                <div><label>Rent / Housing</label><input type="number" id="pay-rent" placeholder="0" value="0"></div>
                <div><label>Groceries</label><input type="number" id="pay-groceries" placeholder="0" value="0"></div>
                <div><label>Subscriptions</label><input type="number" id="pay-subscriptions" placeholder="0" value="0"></div>
                <div><label>Transport</label><input type="number" id="pay-transport" placeholder="0" value="0"></div>
                <div><label>Dining Out</label><input type="number" id="pay-dining" placeholder="0" value="0"></div>
                <div><label>Savings</label><input type="number" id="pay-savings" placeholder="0" value="0"></div>
                <div><label>Other</label><input type="number" id="pay-other" placeholder="0" value="0"></div>
            </div>
            <button class="btn" onclick="calcPaycheck()">Calculate Breakdown</button>
        </div>
        <div id="paycheck-result"></div>
    </div>

    <!-- TAB: MILESTONES -->
    <div id="tab-milestones" class="panel">
        <div class="section-title">Financial Milestones</div>
        <div class="section-sub">Four stages, in order. Each builds the foundation for the next.</div>
        <div class="milestone-grid">
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#007aff">Foundation</span>
                <div class="milestone-item"><div class="milestone-dot" style="background:#007aff"></div>Open a checking account</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#007aff"></div>Open a high-yield savings account</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#007aff"></div>Save your first $500</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#007aff"></div>Get a beginner credit card, pay it off monthly</div>
            </div>
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#34c759">Security</span>
                <div class="milestone-item"><div class="milestone-dot" style="background:#34c759"></div>Build a $1,000 emergency fund</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#34c759"></div>Grow to 3 months of expenses</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#34c759"></div>Understand your credit score</div>
            </div>
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#ff9500">Growth</span>
                <div class="milestone-item"><div class="milestone-dot" style="background:#ff9500"></div>Start investing in index funds</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#ff9500"></div>Open a Roth IRA if eligible</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#ff9500"></div>Automate savings transfers</div>
            </div>
            <div class="milestone-card">
                <span class="milestone-stage" style="color:#5856d6">Optimization</span>
                <div class="milestone-item"><div class="milestone-dot" style="background:#5856d6"></div>Increase income or reduce fixed costs</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#5856d6"></div>Learn about 401k and HSA</div>
                <div class="milestone-item"><div class="milestone-dot" style="background:#5856d6"></div>Track net worth quarterly</div>
            </div>
        </div>
        <p style="font-size:0.82rem;color:#86868b;text-align:center;margin-top:20px;font-style:italic">Work through these in order — each stage enables the next.</p>
    </div>

    <!-- TAB: INVESTING -->
    <div id="tab-investing" class="panel">
        <div class="investing-hero">
            <div class="investing-hero-title">Investing Basics</div>
            <div class="investing-hero-sub">Invest consistently, over a long period, into diversified low-cost funds. That's mostly it.</div>
        </div>
        <div class="investing-cards">
            <div class="investing-card">
                <div class="investing-card-title" style="color:#007aff">Index Funds</div>
                <div class="investing-card-desc">Track the whole market. Low fees, automatic diversification, historically strong long-term returns.</div>
            </div>
            <div class="investing-card">
                <div class="investing-card-title" style="color:#34c759">Roth IRA</div>
                <div class="investing-card-desc">Contribute after-tax dollars, pay zero taxes at withdrawal. $7,000/year limit. Open one early.</div>
            </div>
            <div class="investing-card">
                <div class="investing-card-title" style="color:#ff9500">401(k)</div>
                <div class="investing-card-desc">Always contribute enough to get the full employer match — that money is part of your compensation.</div>
            </div>
        </div>
        <span class="section-eyebrow">The Starting Order</span>
        <div class="step-list">
            <div class="step-item"><div class="step-num">1</div>Build a 3–6 month emergency fund first</div>
            <div class="step-item"><div class="step-num">2</div>Contribute to 401k up to your employer match</div>
            <div class="step-item"><div class="step-num">3</div>Open and fund a Roth IRA ($25–$100/month to start)</div>
            <div class="step-item"><div class="step-num">4</div>Invest remaining in a total market index fund</div>
        </div>
        <span class="section-eyebrow">What to Avoid Early On</span>
        <div class="avoid-item">✕ &nbsp;Day trading — most retail traders lose money</div>
        <div class="avoid-item">✕ &nbsp;Individual stock picking without deep research</div>
        <div class="avoid-item">✕ &nbsp;Crypto as a primary investment strategy</div>
        <div class="avoid-item">✕ &nbsp;Anything promising unusually high guaranteed returns</div>
        <p style="text-align:center;font-style:italic;font-size:0.84rem;color:#86868b;padding-top:20px;border-top:1px solid #d2d2d7;margin-top:20px">Wealth is built through consistency and time, not timing or complexity.</p>
    </div>

    <!-- TAB: FUTURE YOU -->
    <div id="tab-future" class="panel">
        <div class="section-title">Future You</div>
        <div class="section-sub">Slide to your age to see the right priorities for your life stage.</div>
        <label>Your Age: <span id="age-display">20</span></label>
        <input type="range" min="18" max="40" value="20" oninput="updateFuture(this.value)">
        <div id="future-content"></div>
    </div>
</div>

<div class="footer">
    Built at Hack-a-Claw 2026 · NVIDIA × UCSC Baskin Engineering
</div>

<script>
    // ── TAB SWITCHING ─────────────────────────────────────────────
    function switchTab(name, el) {
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('tab-' + name).classList.add('active');
        el.classList.add('active');
        if (name === 'future') updateFuture(20);
    }

    // ── BUILD PLAN ────────────────────────────────────────────────
    async function buildPlan() {
        const situation = document.getElementById('situation').value.trim();
        if (!situation) return alert('Please describe your situation first.');
        const btn = document.getElementById('plan-btn');
        const stepsEl = document.getElementById('plan-steps');
        const resultEl = document.getElementById('plan-result');
        btn.disabled = true;
        btn.textContent = 'Building your plan...';
        stepsEl.style.display = 'flex';
        resultEl.style.display = 'none';
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
            setStep(5);
            resultEl.textContent = data.roadmap || data.error;
            resultEl.style.display = 'block';
        } catch(e) {
            resultEl.textContent = 'Error: ' + e.message;
            resultEl.style.display = 'block';
        }
        btn.disabled = false;
        btn.textContent = 'Build My Roadmap';
    }

    function setStep(n) {
        for (let i = 1; i <= 5; i++) {
            const el = document.getElementById('s' + i);
            el.className = 'step' + (i < n ? ' done' : i === n ? ' active' : '');
        }
    }

    // ── WHAT-IF ───────────────────────────────────────────────────
    async function runWhatIf() {
        const scenario = document.getElementById('scenario').value.trim();
        if (!scenario) return alert('Please describe a scenario.');
        const btn = document.getElementById('whatif-btn');
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
            resultEl.style.display = 'block';
        } catch(e) {
            resultEl.textContent = 'Error: ' + e.message;
            resultEl.style.display = 'block';
        }
        btn.disabled = false;
        btn.textContent = 'Run Scenario';
    }

    // ── PAYCHECK ──────────────────────────────────────────────────
    function calcPaycheck() {
        const income = parseFloat(document.getElementById('pay-income').value) || 0;
        const fields = ['rent','groceries','subscriptions','transport','dining','savings','other'];
        const labels = ['Rent / Housing','Groceries','Subscriptions','Transport','Dining Out','Savings','Other'];
        const colors = ['#007aff','#007aff','#ff9500','#007aff','#ff9500','#34c759','#007aff'];
        if (!income) { document.getElementById('paycheck-result').innerHTML = '<p style="color:#86868b;padding:16px 0;font-size:0.88rem">Enter your monthly income first.</p>'; return; }
        let total = 0;
        const vals = fields.map(f => { const v = parseFloat(document.getElementById('pay-'+f).value)||0; total+=v; return v; });
        const remaining = income - total;
        const remainColor = remaining >= 0 ? '#34c759' : '#ff3b30';
        const remainLabel = remaining >= 0 ? 'Remaining' : 'Over Budget';
        let bars = '';
        fields.forEach((f,i) => {
            if (vals[i] > 0) {
                const pct = (vals[i]/income)*100;
                let c = colors[i];
                if (pct > 35 && f !== 'savings' && f !== 'rent') c = '#ff3b30';
                bars += `<div class="bar-row">
                    <span class="bar-label">${labels[i]}</span>
                    <div class="bar-track"><div class="bar-fill" style="width:${Math.min(pct,100).toFixed(1)}%;background:${c}"></div></div>
                    <span class="bar-amount">$${vals[i].toLocaleString()}</span>
                    <span class="bar-pct">${pct.toFixed(1)}%</span>
                </div>`;
            }
        });
        let tip = '';
        if (remaining < 0) tip = '<div class="tip-box tip-warn">Your expenses exceed your income. Review subscriptions and dining first.</div>';
        else if (remaining/income > 0.2) tip = `<div class="tip-box tip-good">You have ${((remaining/income)*100).toFixed(0)}% unallocated — consider moving this to savings or investments.</div>`;
        else tip = '<div class="tip-box tip-neutral">Budget is tight. Small cuts in dining and subscriptions can free up real savings.</div>';
        document.getElementById('paycheck-result').innerHTML = `
        <div class="card">
            <div class="stat-grid">
                <div class="stat-card"><span class="stat-label">Monthly Income</span><span class="stat-value" style="color:#007aff">$${income.toLocaleString()}</span></div>
                <div class="stat-card"><span class="stat-label">Total Expenses</span><span class="stat-value">$${total.toLocaleString()}</span></div>
                <div class="stat-card"><span class="stat-label">${remainLabel}</span><span class="stat-value" style="color:${remainColor}">$${Math.abs(remaining).toLocaleString()}</span></div>
            </div>
            ${bars}
            ${tip}
            <span class="section-eyebrow" style="margin-top:20px">Healthy Benchmarks</span>
            <div class="benchmark-grid">
                <div class="benchmark-card"><span class="benchmark-label">Housing</span><span class="benchmark-value">under 30%</span></div>
                <div class="benchmark-card"><span class="benchmark-label">Savings</span><span class="benchmark-value">10–20%+</span></div>
                <div class="benchmark-card"><span class="benchmark-label">Subscriptions</span><span class="benchmark-value">audit quarterly</span></div>
                <div class="benchmark-card"><span class="benchmark-label">Dining Out</span><span class="benchmark-value">under 10%</span></div>
            </div>
        </div>`;
    }

    // ── FUTURE YOU ────────────────────────────────────────────────
    const futureStages = [
        { max: 22, color: '#007aff', range: '18–21', title: 'Build the Base', sub: 'Your biggest asset right now is time — not money.', points: ['Focus on saving habits, not just amounts','Build credit with responsible use','$50/month invested at 20 grows more than $200/month invested at 30'], insight: 'Starting early is your single biggest financial advantage.' },
        { max: 27, color: '#34c759', range: '22–26', title: 'Build Momentum', sub: 'More income now. This is when habits become systems.', points: ['Always get the full 401k employer match','Pay off high-interest debt aggressively','Start investing in index funds regularly'], insight: 'This decade is when the gap between investors and non-investors starts to widen.' },
        { max: 32, color: '#ff9500', range: '27–31', title: 'Optimize and Grow', sub: 'Real earning potential. Focus on widening the income-spending gap.', points: ['Max out Roth IRA ($7,000/year)','Increase 401k beyond the match','Evaluate whether buying property fits your goals'], insight: 'Decisions in your late 20s shape your trajectory for decades.' },
        { max: 41, color: '#5856d6', range: '32–40', title: 'Wealth Building', sub: 'Compounding is doing the heavy lifting. Don&#39;t interrupt it.', points: ['Review investment portfolio annually','Consider a fee-only financial advisor','Protect wealth with adequate insurance'], insight: 'Focus shifts from learning to optimizing. Systems matter more than tactics.' },
    ];

    function updateFuture(age) {
        age = parseInt(age);
        document.getElementById('age-display').textContent = age;
        const stage = futureStages.find(s => age < s.max) || futureStages[futureStages.length-1];
        const bullets = stage.points.map(p => `<div class="future-bullet"><span style="color:${stage.color};font-weight:700;flex-shrink:0">→</span><span>${p}</span></div>`).join('');
        document.getElementById('future-content').innerHTML = `
        <div class="future-card" style="border-top:3px solid ${stage.color}">
            <span class="future-age" style="color:${stage.color}">Ages ${stage.range}</span>
            <div class="future-title">${stage.title}</div>
            <div class="future-sub">${stage.sub}</div>
            ${bullets}
            <div class="future-insight" style="border-left:3px solid ${stage.color}">
                <strong>Why it matters:</strong> ${stage.insight}
            </div>
        </div>`;
    }

    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    // init future tab
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