import subprocess
import json
import os
from datetime import datetime
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            return json.load(open(MEMORY_FILE))
        except Exception:
            pass
    return {"profile": {}, "plans": [], "sessions": []}


def save_memory(memory):
    json.dump(memory, open(MEMORY_FILE, "w"), indent=2)


def search_rates(query):
    print(f"  Searching: {query}")
    try:
        result = tavily.search(query=query, max_results=3)
        snippets = [r["content"] for r in result["results"]]
        return " ".join(snippets)[:1200]
    except Exception as e:
        return f"(unavailable: {e})"


def get_live_rates():
    print("Fetching live rates...")
    return {
        "hysa": search_rates("best high yield savings account interest rate 2026"),
        "mortgage_30yr": search_rates("current 30 year fixed mortgage rate 2026"),
        "sp500": search_rates("S&P 500 average annual return 2026 forecast")
    }


def ask_openclaw(message, max_retries=2):
    """Send a message through OpenClaw gateway and return the response."""
    print("  OpenClaw + Nemotron reasoning...")
    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                ["openclaw", "agent", "--local", "--message", message, "--json", "--agent", "main"],
                capture_output=True,
                text=True,
                timeout=300
        )
            if result.returncode != 0:
                print(f"  OpenClaw error: {result.stderr[:200]}")
                continue
            output = result.stdout.strip()
            if not output:
                print("  Empty response from OpenClaw")
                continue
            # Try to parse as JSON first
            try:
                data = json.loads(output)
                if "payloads" in data and data["payloads"]:
                    return data["payloads"][0].get("text", "")
                if "reply" in data:
                    return data["reply"]
                if "content" in data:
                    return data["content"]
                return output
            except json.JSONDecodeError:
                return output
        except subprocess.TimeoutExpired:
            print(f"  Timeout on attempt {attempt + 1}")
            continue
        except Exception as e:
            print(f"  Error: {e}")
            continue
    return None


def parse_json_safely(raw):
    if not raw:
        return None, "Empty response"
    clean = raw.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                clean = candidate
                break
    start = clean.find("{")
    if start == -1:
        return None, "No JSON found"
    depth = 0
    end = -1
    in_string = False
    escape_next = False
    for i, ch in enumerate(clean[start:], start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end == -1:
        candidate = clean[start:]
        open_count = candidate.count("{") - candidate.count("}")
        candidate += "}" * open_count
        try:
            return json.loads(candidate), None
        except Exception:
            return None, "Truncated response"
    try:
        return json.loads(clean[start:end]), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"


def ask_openclaw_json(prompt, max_retries=2):
    for attempt in range(max_retries + 1):
        if attempt > 0:
            print(f"  Retrying (attempt {attempt + 1})...")
            prompt = prompt + "\n\nCRITICAL: Respond with ONLY a valid JSON object. Start with { and end with }. No text before or after."
        raw = ask_openclaw(prompt)
        result, error = parse_json_safely(raw)
        if result is not None:
            return result
        print(f"  Parse failed: {error}")
    return {"error": "Could not parse response. Please try again."}


# ── STRUCTURED PLAN ───────────────────────────────────────────
def run_pathwise_structured(user_input):
    print("\n=== PATHWISE PLAN (via OpenClaw) ===")
    memory = load_memory()
    rates = get_live_rates()

    prompt = f"""You are Pathwise, a financial planning AI. Respond with ONLY valid JSON — start with {{ and end with }}.

User situation: {user_input}

Live rates:
- HYSA: {rates['hysa'][:300]}
- S&P 500: {rates['sp500'][:300]}

Return this exact JSON:
{{
  "monthly_income": <number>,
  "monthly_expenses": <number>,
  "debts": [
    {{"name": "Credit Card", "balance": <number>, "apr": <number>, "monthly_payment": <number>}},
    {{"name": "Student Loans", "balance": <number>, "apr": <number>, "monthly_payment": <number>}}
  ],
  "situation_summary": "2-3 sentences explaining their financial picture in plain English.",
  "why_this_order": "1-2 sentences explaining WHY we prioritize the way we do.",
  "monthly_plan": [
    {{
      "label": "Months 1-3",
      "focus": "Emergency Fund First",
      "allocations": {{"Emergency Fund": <number>, "Credit Card": <number>, "Student Loans": <number>}},
      "guidance": "One sentence of human advice for this phase.",
      "milestone": "Milestone description or null"
    }},
    {{
      "label": "Months 4-6",
      "focus": "Attack Credit Card Debt",
      "allocations": {{"Emergency Fund": <number>, "Credit Card": <number>, "Student Loans": <number>}},
      "guidance": "One sentence of human advice for this phase.",
      "milestone": "Milestone description or null"
    }},
    {{
      "label": "Months 7-9",
      "focus": "Accelerate Debt Payoff",
      "allocations": {{"Emergency Fund": <number>, "Credit Card": <number>, "Student Loans": <number>}},
      "guidance": "One sentence of human advice for this phase.",
      "milestone": "Milestone description or null"
    }},
    {{
      "label": "Months 10-12",
      "focus": "Build Momentum",
      "allocations": {{"Emergency Fund": <number>, "Credit Card": <number>, "Student Loans": <number>}},
      "guidance": "One sentence of human advice for this phase.",
      "milestone": "Milestone description or null"
    }}
  ],
  "hysa_rate": "5.10% APY",
  "hysa_tip": "Specific sentence about where to put emergency fund.",
  "sp500_note": "One sentence about S&P 500 outlook.",
  "key_insight": "The single most important thing they should understand.",
  "debt_free_month": <number 1-24>,
  "debt_free_note": "One encouraging sentence about their debt-free timeline."
}}

Start with {{ and end with }}. No other text."""

    result = ask_openclaw_json(prompt)

    if "error" not in result:
        memory["profile"] = {"input": user_input, "result": result}
        memory["sessions"].append({"timestamp": datetime.now().isoformat(), "input": user_input})
        memory["plans"].append({"timestamp": datetime.now().isoformat(), "input": user_input, "structured": result})
        save_memory(memory)

    return result


# ── STRUCTURED WHAT-IF ────────────────────────────────────────
def run_whatif_structured(scenario):
    print("\n=== WHAT-IF (via OpenClaw) ===")
    memory = load_memory()

    if not memory.get("plans"):
        return {"error": "No existing plan found. Build your plan first."}

    last_plan = memory["plans"][-1]
    plan_ctx = json.dumps(last_plan.get("structured", {}))[:1200]

    prompt = f"""You are Pathwise, a financial planning AI. Respond with ONLY valid JSON — start with {{ and end with }}.

Existing plan: {plan_ctx}
Scenario: {scenario}

Return this exact JSON:
{{
  "scenario_title": "Short label for the scenario",
  "what_changes": "2-3 sentences on what this scenario changes with specific dollars.",
  "why_it_matters": "2-3 sentences on the deeper impact.",
  "comparisons": [
    {{"metric": "Debt Free By", "original": "Month 14", "new_value": "Month 7", "better": true}},
    {{"metric": "Monthly Surplus", "original": "$1,300", "new_value": "$2,800", "better": true}},
    {{"metric": "Roth IRA Start", "original": "Month 15", "new_value": "Month 8", "better": true}},
    {{"metric": "Interest Saved", "original": "$0", "new_value": "$480", "better": true}}
  ],
  "monthly_surplus_chart": [
    {{"month": "Jan", "original": 1300, "new": 2800}},
    {{"month": "Feb", "original": 1300, "new": 2800}},
    {{"month": "Mar", "original": 1300, "new": 2800}},
    {{"month": "Apr", "original": 1300, "new": 2800}},
    {{"month": "May", "original": 1300, "new": 2800}},
    {{"month": "Jun", "original": 1300, "new": 2800}}
  ],
  "impacts": [
    {{"icon": "🎯", "title": "Debt Freedom", "body": "Specific detail about debt payoff changes.", "type": "good"}},
    {{"icon": "📈", "title": "Investment Unlock", "body": "When they can start investing and what it compounds to.", "type": "good"}},
    {{"icon": "🛡️", "title": "Financial Breathing Room", "body": "How monthly buffer improves.", "type": "info"}},
    {{"icon": "💡", "title": "The Bigger Picture", "body": "5-year trajectory impact.", "type": "info"}}
  ],
  "what_to_do_now": "First concrete action with a dollar amount."
}}

Start with {{ and end with }}. No other text."""

    return ask_openclaw_json(prompt)


# ── GENERATE TAB CONTENT ──────────────────────────────────────
def generate_tab_content(gen_type, context, age=25):
    print(f"\n=== GENERATE: {gen_type} (via OpenClaw) ===")

    situation = context.get("situation", "")
    plan = context.get("plan", {})
    paycheck = context.get("paycheck", {})

    income = plan.get("monthly_income", paycheck.get("income", 2500)) if isinstance(plan, dict) else 2500
    expenses = plan.get("monthly_expenses", paycheck.get("total", 1200)) if isinstance(plan, dict) else 1200
    surplus = income - expenses
    debts = plan.get("debts", []) if isinstance(plan, dict) else []
    total_debt = sum(d.get("balance", 0) for d in debts)
    has_high_apr = any(d.get("apr", 0) >= 10 for d in debts)

    ctx_str = f"Situation: {situation}\nIncome: ${income}, Expenses: ${expenses}, Surplus: ${surplus}, Total debt: ${total_debt}"

    if gen_type == "milestones":
        prompt = f"""You are Pathwise, a financial planning AI. Respond with ONLY valid JSON.

User data: {ctx_str}

Return this JSON:
{{
  "overall_progress": <0-100>,
  "progress_label": "Just getting started",
  "where_you_are": "2-3 sentences describing their position honestly.",
  "stages": [
    {{
      "name": "Foundation",
      "color": "#007aff",
      "description": "What this stage means for them.",
      "milestones": [
        {{"label": "Build $1,000 emergency fund", "target": "$1,000", "timeline": "Month 1-2", "priority": "high", "why": "Your safety net so one bad month does not set you back."}},
        {{"label": "Pay minimums on all debts", "target": "Every month", "timeline": "Ongoing", "priority": "high", "why": "Protects your credit score while you build momentum."}}
      ]
    }},
    {{
      "name": "Security",
      "color": "#34c759",
      "description": "What unlocks in this stage.",
      "milestones": [
        {{"label": "Eliminate credit card debt", "target": "$<balance>", "timeline": "<realistic>", "priority": "high", "why": "Highest guaranteed return — eliminate the 19% APR cost."}},
        {{"label": "3-month emergency fund", "target": "$<3x expenses>", "timeline": "<realistic>", "priority": "medium", "why": "The line between surviving a job loss and going back into debt."}}
      ]
    }},
    {{
      "name": "Growth",
      "color": "#ff9500",
      "description": "What becomes possible once debt is cleared.",
      "milestones": [
        {{"label": "Open and fund Roth IRA", "target": "$200/mo", "timeline": "<after debt>", "priority": "high", "why": "Tax-free growth — every year delayed is compounding missed."}},
        {{"label": "Pay off student loans", "target": "$<balance>", "timeline": "<realistic>", "priority": "medium", "why": "Frees up serious monthly cash flow."}}
      ]
    }},
    {{
      "name": "Optimization",
      "color": "#5856d6",
      "description": "What financial life looks like at this stage.",
      "milestones": [
        {{"label": "Max out Roth IRA", "target": "$7,000/year", "timeline": "<realistic>", "priority": "high", "why": "Full tax-free compounding."}},
        {{"label": "Reach positive net worth", "target": "Assets exceed debts", "timeline": "<realistic>", "priority": "medium", "why": "Your trajectory becomes self-reinforcing."}}
      ]
    }}
  ],
  "next_action": "One specific thing to do this week with a dollar amount.",
  "encouragement": "One genuine encouraging sentence."
}}

Start with {{ and end with }}."""

    elif gen_type == "investing":
        monthly_invest = max(50, int(surplus * 0.25)) if not has_high_apr else 0

        def compound(monthly, years):
            if monthly <= 0:
                return 0
            return int(monthly * 12 * ((1.07**years - 1) / 0.07))

        y1 = compound(monthly_invest, 1)
        y5 = compound(monthly_invest, 5)
        y10 = compound(monthly_invest, 10)
        y20 = compound(monthly_invest, 20)
        y30 = compound(monthly_invest, 30)

        prompt = f"""You are Pathwise. Respond with ONLY valid JSON.

User data: {ctx_str}
Monthly invest capacity: ${monthly_invest}
Has high APR debt: {has_high_apr}

Return this JSON:
{{
  "readiness_title": "Clear your credit card first — then invest",
  "readiness_explanation": "2-3 sentences explaining why with their actual APR and math.",
  "monthly_capacity": {monthly_invest},
  "accounts": [
    {{
      "name": "High-Yield Savings Account",
      "priority": 1,
      "monthly_amount": {int(surplus * 0.3)},
      "status_label": "Open now — before anything else",
      "color": "#34c759",
      "what_it_is": "A savings account earning 4.5-5%+ APY with zero risk.",
      "why_first": "Your emergency fund goes here. Without it one bad month wipes out your debt progress.",
      "where_to_open": "Marcus by Goldman Sachs, Ally, or SoFi — all 4.5%+ APY, no fees."
    }},
    {{
      "name": "Roth IRA",
      "priority": 2,
      "monthly_amount": {monthly_invest},
      "status_label": "Start after credit card is paid",
      "color": "#007aff",
      "what_it_is": "Retirement account where growth is completely tax-free.",
      "why_first": "At your income level, paying tax now on contributions beats paying tax on withdrawals later.",
      "where_to_open": "Fidelity — zero minimums, invest in FSKAX (total market index fund)."
    }},
    {{
      "name": "401(k)",
      "priority": 3,
      "monthly_amount": null,
      "status_label": "When you go full-time",
      "color": "#ff9500",
      "what_it_is": "Employer retirement account, often with matching.",
      "why_first": "Always contribute enough to get the full employer match — it is free money.",
      "where_to_open": "Through your employer — ask HR on day one."
    }}
  ],
  "growth_projection": [
    {{"year": "Year 1", "value": {y1}}},
    {{"year": "Year 5", "value": {y5}}},
    {{"year": "Year 10", "value": {y10}}},
    {{"year": "Year 20", "value": {y20}}},
    {{"year": "Year 30", "value": {y30}}}
  ],
  "the_math": "${monthly_invest}/month at 7% grows to ${y10:,} in 10 years and ${y30:,} in 30 years.",
  "biggest_mistake": "The most common investing mistake for someone in their situation.",
  "avoid": [
    {{"thing": "Individual stocks before index funds", "reason": "Fund managers underperform index funds 80%+ of the time over 10 years."}},
    {{"thing": "Waiting until all debt is gone", "reason": "Once high-interest debt is cleared, delaying investing costs real compounding."}},
    {{"thing": "Crypto as a core strategy", "reason": "Too volatile to be the foundation of wealth building."}}
  ]
}}

Start with {{ and end with }}."""

    elif gen_type == "future":
        current_age = 22
        years = max(1, age - current_age)
        start_nw = -total_debt
        monthly_debt_payment = surplus * 0.7
        months_to_debt_free = int(total_debt / monthly_debt_payment) if monthly_debt_payment > 0 else 24
        monthly_invest_post_debt = surplus * 0.4

        def nw_at_year(y):
            months = y * 12
            if months <= months_to_debt_free:
                return int(start_nw + (monthly_debt_payment * months))
            else:
                invest_months = months - months_to_debt_free
                invest_growth = monthly_invest_post_debt * 12 * ((1.07**(invest_months/12) - 1) / 0.07) if invest_months > 0 else 0
                return int(invest_growth)

        age_points = sorted(set([current_age, min(current_age+2, age), min(current_age+5, age), min(current_age+10, age), age]))
        proj_data = [{"age": a, "net_worth": nw_at_year(a - current_age)} for a in age_points]
        final_nw = proj_data[-1]["net_worth"]
        best_nw = int(final_nw * 1.35)

        prompt = f"""You are Pathwise. Respond with ONLY valid JSON.

User data: {ctx_str}
Current age: {current_age}, Target age: {age}
Net worth now: ${start_nw}
Months to debt free: ~{months_to_debt_free}
Projected net worth at age {age}: ${final_nw}
Net worth projection data: {json.dumps(proj_data)}

Return this JSON:
{{
  "headline": "One specific sentence about what age {age} could look like financially.",
  "key_metrics": [
    {{"label": "Estimated Net Worth", "value": "${final_nw:,}", "note": "following their plan", "color": "#007aff"}},
    {{"label": "Investment Portfolio", "value": "<realistic amount>", "note": "Roth IRA + index funds", "color": "#34c759"}},
    {{"label": "Est. Monthly Income", "value": "<with career growth>", "note": "typical progression", "color": "#ff9500"}},
    {{"label": "Debt Status", "value": "Debt Free", "note": "age {current_age + int(months_to_debt_free/12)}", "color": "#5856d6"}}
  ],
  "net_worth_projection": {json.dumps(proj_data)},
  "what_the_numbers_mean": "2-3 sentences on what this net worth actually means for their life.",
  "milestones_by_then": [
    {{"label": "Debt Free", "achieved": true, "age_achieved": {current_age + int(months_to_debt_free/12)}, "detail": "All debt eliminated."}},
    {{"label": "Emergency Fund", "achieved": true, "age_achieved": {current_age + 1}, "detail": "3 months expenses saved."}},
    {{"label": "Roth IRA Started", "achieved": true, "age_achieved": {current_age + int(months_to_debt_free/12) + 1}, "detail": "Investing monthly after debt payoff."}},
    {{"label": "$25k Net Worth", "achieved": {str(final_nw >= 25000).lower()}, "age_achieved": <estimate>, "detail": "First major net worth milestone."}}
  ],
  "best_case": {{
    "net_worth": "${best_nw:,}",
    "description": "If you max Roth IRA and get a raise within 2 years."
  }},
  "realistic_case": {{
    "net_worth": "${final_nw:,}",
    "description": "Following your current plan consistently."
  }},
  "the_decision_that_matters_most": "The single most impactful decision they can make right now."
}}

Start with {{ and end with }}."""

    else:
        return {"error": f"Unknown type: {gen_type}"}

    return ask_openclaw_json(prompt)


def run_pathwise(user_input):
    return json.dumps(run_pathwise_structured(user_input), indent=2)


def run_whatif(scenario):
    return json.dumps(run_whatif_structured(scenario), indent=2)


if __name__ == "__main__":
    print("\nWelcome to Pathwise (powered by OpenClaw + Nemotron)")
    print("1. Build my financial plan")
    print("2. What-if scenario")
    choice = input("\nChoose (1 or 2): ").strip()
    if choice == "1":
        user_input = input("Your situation: ").strip()
        print(json.dumps(run_pathwise_structured(user_input), indent=2))
    elif choice == "2":
        scenario = input("What scenario? ").strip()
        print(json.dumps(run_whatif_structured(scenario), indent=2))
    else:
        print("Invalid choice.")