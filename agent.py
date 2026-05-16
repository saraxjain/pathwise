from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)
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


def ask_nemotron(system_prompt, user_message, max_tokens=1400):
    print("  Nemotron reasoning...")
    response = nvidia_client.chat.completions.create(
        model="nvidia/llama-3.3-nemotron-super-49b-v1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=max_tokens,
        temperature=0.3
    )
    return response.choices[0].message.content


def parse_json_safely(raw):
    """
    Robust JSON parser — handles markdown fences, extra text before/after,
    and truncated responses. Returns (dict, error_string).
    """
    if not raw:
        return None, "Empty response from AI"

    clean = raw.strip()

    # Strip markdown code fences
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                clean = candidate
                break

    # Find outermost JSON object
    start = clean.find("{")
    if start == -1:
        return None, "No JSON object found in response"

    # Walk to find matching closing brace
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
        # Response was truncated — try parsing what we have
        candidate = clean[start:]
        # Try to close any open braces
        open_count = candidate.count("{") - candidate.count("}")
        candidate += "}" * open_count
        try:
            return json.loads(candidate), None
        except Exception:
            return None, "Response was truncated before completing. Please try again."

    try:
        return json.loads(clean[start:end]), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {str(e)}"


def ask_nemotron_json(system_prompt, user_message, max_tokens=1400, retries=2):
    """
    Call Nemotron and parse JSON. Retries on parse failure with a stricter prompt.
    """
    for attempt in range(retries + 1):
        if attempt > 0:
            print(f"  Retrying (attempt {attempt+1})...")
            # On retry, add extra emphasis on JSON-only output
            system_prompt = system_prompt + "\n\nCRITICAL: Your ENTIRE response must be a single valid JSON object. Start with { and end with }. No text before or after."

        raw = ask_nemotron(system_prompt, user_message, max_tokens)
        result, error = parse_json_safely(raw)

        if result is not None:
            return result

        print(f"  Parse failed (attempt {attempt+1}): {error}")
        print(f"  Raw response preview: {raw[:200]}")

    return {"error": f"Could not parse AI response after {retries+1} attempts. Please try again."}


# ── STRUCTURED PLAN ───────────────────────────────────────────
def run_pathwise_structured(user_input):
    print("\n=== PATHWISE PLAN ===")
    memory = load_memory()
    rates = get_live_rates()

    system = """You are Pathwise, a financial planning AI that speaks like a knowledgeable friend — clear, direct, and human.
You MUST respond with ONLY valid JSON. Start your response with { and end with }. No markdown, no explanation, no text outside the JSON."""

    prompt = f"""User situation: {user_input}

Live rates:
- HYSA: {rates['hysa'][:300]}
- S&P 500: {rates['sp500'][:300]}

Return this exact JSON with real numbers:
{{
  "monthly_income": <number>,
  "monthly_expenses": <number>,
  "debts": [
    {{"name": "Credit Card", "balance": <number>, "apr": <number>, "monthly_payment": <number>}},
    {{"name": "Student Loans", "balance": <number>, "apr": <number>, "monthly_payment": <number>}}
  ],
  "situation_summary": "2-3 sentences explaining their financial picture in plain English — what is working, what needs attention, and the single biggest lever they have right now.",
  "why_this_order": "1-2 sentences explaining WHY we prioritize the way we do. Make it feel logical, not like a rule.",
  "monthly_plan": [
    {{
      "label": "Months 1-3",
      "focus": "Emergency Fund First",
      "allocations": {{
        "Emergency Fund": <number>,
        "Credit Card": <number>,
        "Student Loans": <number>
      }},
      "guidance": "One sentence of human advice for this phase — what to watch for, or why this matters.",
      "milestone": "Emergency fund complete — you now have a real safety net." or null
    }}
  ],
  "hysa_rate": "5.10% APY",
  "hysa_tip": "Specific sentence about where to put emergency fund and why.",
  "sp500_note": "One sentence about what S&P 500 outlook means for them right now.",
  "key_insight": "The single most important thing they should understand — genuinely useful, not obvious.",
  "debt_free_month": <number 1-24>,
  "debt_free_note": "One encouraging sentence about their debt-free timeline."
}}

Rules:
- monthly_plan must have exactly 4 phases covering 12 months
- allocations must be real numbers summing to roughly (monthly_income - monthly_expenses)
- Start response with {{ and end with }}"""

    result = ask_nemotron_json(system, prompt, max_tokens=1500)

    if "error" not in result:
        memory["profile"] = {"input": user_input, "result": result}
        memory["sessions"].append({"timestamp": datetime.now().isoformat(), "input": user_input})
        memory["plans"].append({"timestamp": datetime.now().isoformat(), "input": user_input, "structured": result})
        save_memory(memory)

    return result


# ── STRUCTURED WHAT-IF ────────────────────────────────────────
def run_whatif_structured(scenario):
    print("\n=== WHAT-IF ===")
    memory = load_memory()

    if not memory.get("plans"):
        return {"error": "No existing plan found. Build your plan first."}

    last_plan = memory["plans"][-1]
    plan_ctx = json.dumps(last_plan.get("structured", {}))[:1200]

    system = """You are Pathwise, a financial planning AI that speaks like a knowledgeable friend.
You MUST respond with ONLY valid JSON. Start with { and end with }. No text outside the JSON."""

    prompt = f"""Existing plan: {plan_ctx}

Scenario: {scenario}

Return this exact JSON focused on what changes and WHY it matters:
{{
  "scenario_title": "Short label, e.g. 'Full-Time Job at $5,000/month'",
  "what_changes": "2-3 sentences in plain English: what this scenario actually changes. Be specific with dollars and months.",
  "why_it_matters": "2-3 sentences on the deeper impact — does this change their timeline meaningfully? Does it unlock something they could not do before? What does this mean for their life?",
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
    {{"icon": "🎯", "title": "Debt Freedom", "body": "Specific detail about how debt payoff changes — months saved, interest avoided, and what becoming debt free unlocks for them next.", "type": "good"}},
    {{"icon": "📈", "title": "Investment Unlock", "body": "When they can now start investing, how much per month, and what that amount compounds to over 10 years at 7%.", "type": "good"}},
    {{"icon": "🛡️", "title": "Financial Breathing Room", "body": "How their monthly buffer improves and why that buffer matters — what it protects them from.", "type": "info"}},
    {{"icon": "💡", "title": "The Bigger Picture", "body": "What this scenario change means for their financial trajectory over the next 5 years — not just the next 12 months.", "type": "info"}}
  ],
  "what_to_do_now": "If this scenario happened today, the first concrete action they should take — specific, with a dollar amount and a reason."
}}

Rules:
- comparisons must have exactly 4 rows with real numbers from the plan
- monthly_surplus_chart must have exactly 6 months with realistic numbers
- impacts must have exactly 4 items with genuine reasoning, not generic filler
- Start with {{ and end with }}"""

    return ask_nemotron_json(system, prompt, max_tokens=1300)


# ── GENERATE TAB CONTENT ──────────────────────────────────────
def generate_tab_content(gen_type, context, age=25):
    print(f"\n=== GENERATE: {gen_type} ===")

    situation = context.get("situation", "")
    plan = context.get("plan", {})
    paycheck = context.get("paycheck", {})

    income = plan.get("monthly_income", paycheck.get("income", 2500)) if isinstance(plan, dict) else 2500
    expenses = plan.get("monthly_expenses", paycheck.get("total", 1200)) if isinstance(plan, dict) else 1200
    surplus = income - expenses
    debts = plan.get("debts", []) if isinstance(plan, dict) else []
    total_debt = sum(d.get("balance", 0) for d in debts)
    has_high_apr = any(d.get("apr", 0) >= 10 for d in debts)

    ctx_str = f"Situation: {situation}\nIncome: ${income}, Expenses: ${expenses}, Surplus: ${surplus}, Debts: {json.dumps(debts)}, Total debt: ${total_debt}"

    system = """You are Pathwise, a financial planning AI that speaks like a knowledgeable friend — clear, warm, and direct.
You MUST respond with ONLY valid JSON. Start with { and end with }. No text outside the JSON."""

    if gen_type == "milestones":
        prompt = f"""User data: {ctx_str}

Return personalized milestone guidance with real numbers and genuine reasoning:
{{
  "overall_progress": <0-100, honest: 0-10 if they have debt and no savings>,
  "progress_label": "Just getting started" or "Building momentum" or similar honest label,
  "where_you_are": "2-3 sentences describing their current position honestly and encouragingly. Name their actual debts and situation.",
  "stages": [
    {{
      "name": "Foundation",
      "color": "#007aff",
      "status": "current",
      "description": "What this stage means for them specifically.",
      "milestones": [
        {{"label": "Build $1,000 emergency fund", "target": "$1,000", "timeline": "Month 1-2", "priority": "high", "why": "This is your safety net so one bad month does not wipe out your progress on debt."}},
        {{"label": "Pay minimums on all debts on time", "target": "Every month", "timeline": "Ongoing", "priority": "high", "why": "Protects your credit score while you build momentum — a good score saves you thousands in future interest."}}
      ]
    }},
    {{
      "name": "Security",
      "color": "#34c759",
      "status": "upcoming",
      "description": "What unlocks in this stage for them.",
      "milestones": [
        {{"label": "Eliminate credit card debt", "target": "<their actual CC balance>", "timeline": "<realistic month>", "priority": "high", "why": "At 19% APR, this is costing you roughly $285/year just in interest. Killing it is your highest guaranteed return."}},
        {{"label": "3-month emergency fund", "target": "<3x their monthly expenses>", "timeline": "<realistic>", "priority": "medium", "why": "This is the line between surviving a job loss and going back into debt. Do not skip it."}}
      ]
    }},
    {{
      "name": "Growth",
      "color": "#ff9500",
      "status": "future",
      "description": "What becomes possible once debt is cleared.",
      "milestones": [
        {{"label": "Open and fund Roth IRA", "target": "$<realistic>/mo", "timeline": "<when debt is clear>", "priority": "high", "why": "Tax-free growth for retirement. Every year you delay is compounding you miss — $200/month at 22 vs 30 is a $150k+ difference by retirement."}},
        {{"label": "Pay off student loans", "target": "<their balance>", "timeline": "<realistic>", "priority": "medium", "why": "At 5% APR, this can coexist with Roth IRA contributions. But finishing it frees up serious monthly cash flow."}}
      ]
    }},
    {{
      "name": "Optimization",
      "color": "#5856d6",
      "status": "future",
      "description": "What financial life looks like at this stage.",
      "milestones": [
        {{"label": "Max out Roth IRA", "target": "$7,000/year", "timeline": "<realistic year>", "priority": "high", "why": "Full tax-free compounding. At this stage your money is working harder than your debt ever cost you."}},
        {{"label": "Reach positive net worth", "target": "Assets exceed debts", "timeline": "<realistic>", "priority": "medium", "why": "The milestone where your financial trajectory becomes self-reinforcing."}}
      ]
    }}
  ],
  "next_action": "The one thing they should do this week — specific, actionable, with a dollar amount.",
  "encouragement": "One genuine, non-cheesy sentence acknowledging where they are and why the path ahead is doable."
}}

Rules:
- Use their REAL numbers — actual debt balances, actual income, actual timelines
- priority must be 'high' or 'medium' — this drives visual emphasis in the UI
- overall_progress must be honest — with $6,500 in debt and no savings that is 5-10%, not 30%
- Start with {{ and end with }}"""

    elif gen_type == "investing":
        monthly_invest = max(50, int(surplus * 0.25)) if not has_high_apr else 0

        # Calculate real compound interest for projection
        # monthly_invest * 12 * ((1.07^n - 1) / 0.07) approximately
        def compound(monthly, years):
            if monthly <= 0:
                return 0
            return int(monthly * 12 * ((1.07**years - 1) / 0.07))

        y1 = compound(monthly_invest, 1)
        y3 = compound(monthly_invest, 3)
        y5 = compound(monthly_invest, 5)
        y10 = compound(monthly_invest, 10)
        y20 = compound(monthly_invest, 20)
        y30 = compound(monthly_invest, 30)

        prompt = f"""User data: {ctx_str}
Has high-interest debt: {has_high_apr}, Monthly invest capacity: ${monthly_invest}
Compound growth at 7%: Y1=${y1}, Y3=${y3}, Y5=${y5}, Y10={y10}, Y20=${y20}, Y30=${y30}

Return investing guidance with real reasoning:
{{
  "readiness_status": "not_ready" or "almost_ready" or "ready",
  "readiness_title": "e.g. 'Clear your credit card first — then invest'",
  "readiness_explanation": "2-3 sentences explaining WHY they are or are not ready. Reference their actual APR and debt. Explain the math — 19% debt cost vs 7% market return.",
  "monthly_capacity": {monthly_invest},
  "accounts": [
    {{
      "name": "High-Yield Savings Account",
      "priority": 1,
      "monthly_amount": <number for emergency fund phase>,
      "status_label": "Open now — before anything else",
      "color": "#34c759",
      "what_it_is": "A savings account earning 4.5-5%+ APY — dramatically better than a regular bank account, with zero risk.",
      "why_first": "Before you invest a single dollar, you need 3-6 months of expenses saved here. Without this buffer, one emergency forces you back into credit card debt — undoing months of progress.",
      "where_to_open": "Marcus by Goldman Sachs, Ally, or SoFi — all offer 4.5%+ APY with no minimums or fees."
    }},
    {{
      "name": "Roth IRA",
      "priority": 2,
      "monthly_amount": <0 if not ready, else realistic amount>,
      "status_label": "<'Start Month X after credit card is paid' or 'Ready to open'>",
      "color": "#007aff",
      "what_it_is": "A retirement account where your contributions grow completely tax-free. You pay taxes on the money going in, never on the growth or withdrawals.",
      "why_first": "At 22 with a moderate income, a Roth IRA is almost certainly better than a Traditional IRA. The reason: you are in a lower tax bracket now than you will be later. Paying tax now on $200/month is cheap compared to paying tax on $200k at retirement.",
      "where_to_open": "Fidelity (zero minimums, zero fees) — invest in FSKAX or FZROX. Both track the entire US stock market."
    }},
    {{
      "name": "401(k)",
      "priority": 3,
      "monthly_amount": null,
      "status_label": "When you go full-time",
      "color": "#ff9500",
      "what_it_is": "Employer-sponsored retirement account. Often includes matching — where your employer adds free money on top of your contribution.",
      "why_first": "If your employer matches even 3%, that is an instant 100% return on that money. Always contribute enough to capture the full match before doing anything else. It is literally free compensation.",
      "where_to_open": "Through your employer — ask HR on your first day about the match and vesting schedule."
    }}
  ],
  "growth_projection": [
    {{"year": "Year 1", "value": {y1}}},
    {{"year": "Year 3", "value": {y3}}},
    {{"year": "Year 5", "value": {y5}}},
    {{"year": "Year 10", "value": {y10}}},
    {{"year": "Year 20", "value": {y20}}},
    {{"year": "Year 30", "value": {y30}}}
  ],
  "the_math": "Concrete sentence: '${monthly_invest}/month at 7% annual return grows to ${y10:,} in 10 years and ${y30:,} in 30 years — entirely from compound interest on a relatively small monthly commitment.'",
  "biggest_mistake": "The single most common investing mistake for someone in their exact situation, explained in plain terms with a reason.",
  "avoid": [
    {{"thing": "Individual stocks before index funds", "reason": "Even professional fund managers underperform broad index funds 80%+ of the time over 10 years. Start with the whole market, not a bet on one company."}},
    {{"thing": "Waiting until your debt is fully gone", "reason": "Once your high-interest debt is cleared, the cost of waiting to invest is real. Every year you delay is a year of compounding you cannot get back."}},
    {{"thing": "Crypto as a core strategy", "reason": "Crypto is speculation, not investing. It is fine as a small side bet, but it is too volatile to be the foundation of a wealth-building plan."}}
  ]
}}

Rules:
- growth_projection values are already calculated above — use those exact numbers
- The chart will use these values so they MUST show a curve, not a flat line
- Start with {{ and end with }}"""

    elif gen_type == "future":
        current_age = 22
        years = max(1, age - current_age)

        # Calculate net worth trajectory with real math
        # Start: negative (debt), pay off debt over ~20 months, then invest
        start_nw = -total_debt
        monthly_debt_payment = surplus * 0.7  # aggressive during debt phase
        months_to_debt_free = int(total_debt / monthly_debt_payment) if monthly_debt_payment > 0 else 24
        monthly_invest_post_debt = surplus * 0.4

        def nw_at_year(y):
            months = y * 12
            if months <= months_to_debt_free:
                # Still paying debt
                return int(start_nw + (monthly_debt_payment * months))
            else:
                # Debt free, now investing
                invest_months = months - months_to_debt_free
                invest_growth = monthly_invest_post_debt * 12 * ((1.07**(invest_months/12) - 1) / 0.07) if invest_months > 0 else 0
                return int(invest_growth)

        # Build projection points
        proj_ages = []
        nw_values = []
        age_points = [current_age, min(current_age+2, age), min(current_age+5, age), min(current_age+10, age), age]
        age_points = sorted(set(age_points))
        for a in age_points:
            proj_ages.append(a)
            nw_values.append(nw_at_year(a - current_age))

        proj_data = [{"age": a, "net_worth": nw} for a, nw in zip(proj_ages, nw_values)]
        final_nw = nw_values[-1]
        best_nw = int(final_nw * 1.35)
        realistic_nw = final_nw

        prompt = f"""User data: {ctx_str}
Current age: {current_age}, Target age: {age}, Years: {years}
Net worth now: ${start_nw}, Monthly surplus: ${surplus}
Months to debt free: ~{months_to_debt_free}, Monthly invest after debt: ${int(monthly_invest_post_debt)}
Pre-calculated net worth projection: {json.dumps(proj_data)}
Projected net worth at age {age}: ${final_nw}
Best case net worth: ${best_nw}

Return a financial projection for age {age}:
{{
  "headline": "One specific, grounded sentence about what age {age} could look like financially if they follow their plan.",
  "key_metrics": [
    {{"label": "Estimated Net Worth", "value": "${final_nw:,}", "note": "if they follow their plan", "color": "#007aff"}},
    {{"label": "Investment Portfolio", "value": "<portion of net worth in investments>", "note": "Roth IRA + index funds", "color": "#34c759"}},
    {{"label": "Est. Monthly Income", "value": "<projected with career growth from $2,500>", "note": "with typical career progression", "color": "#ff9500"}},
    {{"label": "Debt Status", "value": "<'Debt Free' or amount>", "note": "<age when debt free>", "color": "#5856d6"}}
  ],
  "net_worth_projection": {json.dumps(proj_data)},
  "what_the_numbers_mean": "2-3 sentences explaining what their projected net worth actually means in real life — what it enables, what options it gives them, what it feels like to have that kind of financial foundation.",
  "milestones_by_then": [
    {{"label": "Debt Free", "achieved": <true if age > current_age + months_to_debt_free/12>, "age_achieved": {current_age + int(months_to_debt_free/12)}, "detail": "All $6,500 in debt eliminated. Credit card and student loans gone."}},
    {{"label": "Emergency Fund Complete", "achieved": true, "age_achieved": {current_age + 1}, "detail": "3 months of expenses saved in a high-yield savings account."}},
    {{"label": "Roth IRA Started", "achieved": <true if age > current_age + months_to_debt_free/12>, "age_achieved": <realistic>, "detail": "Contributing $<amount>/month after debt payoff. Compound growth has already begun."}},
    {{"label": "$25k Net Worth", "achieved": <true if realistic_nw >= 25000>, "age_achieved": <estimate>, "detail": "First major net worth milestone — the point where investing starts to feel real."}}
  ],
  "best_case": {{
    "net_worth": "${best_nw:,}",
    "description": "If you max out your Roth IRA annually, get a raise within 2 years, and avoid lifestyle inflation as income grows."
  }},
  "realistic_case": {{
    "net_worth": "${realistic_nw:,}",
    "description": "Following your current plan consistently — paying off debt on schedule and investing the surplus."
  }},
  "the_decision_that_matters_most": "The single most impactful financial decision they can make right now to improve this projection — specific, with a dollar amount and a clear reason."
}}

Rules:
- net_worth_projection must use EXACTLY the pre-calculated data provided above: {json.dumps(proj_data)}
- Do not change these numbers — they are mathematically correct
- key_metrics values must be consistent with the projection data
- Start with {{ and end with }}"""

    else:
        return {"error": f"Unknown type: {gen_type}"}

    return ask_nemotron_json(system, prompt, max_tokens=1400)


def run_pathwise(user_input):
    return json.dumps(run_pathwise_structured(user_input), indent=2)


def run_whatif(scenario):
    return json.dumps(run_whatif_structured(scenario), indent=2)


if __name__ == "__main__":
    print("\nWelcome to Pathwise")
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