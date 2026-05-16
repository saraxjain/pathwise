from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

# ── clients ──────────────────────────────────────────────────────────────────
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MEMORY_FILE = "memory.json"

# ── persistent memory ─────────────────────────────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {"profile": {}, "plans": [], "sessions": []}

def save_memory(memory):
    json.dump(memory, open(MEMORY_FILE, "w"), indent=2)
    print("💾 Memory saved.")

# ── live tools ────────────────────────────────────────────────────────────────
def search_rates(query):
    print(f"🔍 Searching: {query}")
    result = tavily.search(query=query, max_results=3)
    snippets = [r["content"] for r in result["results"]]
    return " ".join(snippets)[:1500]

def get_live_rates():
    print("📡 Fetching live financial rates...")
    rates = {}
    rates["hysa"] = search_rates("best high yield savings account interest rate 2026")
    rates["mortgage_30yr"] = search_rates("current 30 year fixed mortgage rate 2026")
    rates["sp500"] = search_rates("S&P 500 average annual return 2026 forecast")
    return rates

# ── nemotron reasoning ────────────────────────────────────────────────────────
def ask_nemotron(system_prompt, user_message):
    print("🧠 Nemotron is reasoning...")
    response = nvidia_client.chat.completions.create(
        model="nvidia/llama-3.3-nemotron-super-49b-v1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return response.choices[0].message.content

# ── core agent ────────────────────────────────────────────────────────────────
def run_pathwise(user_input):
    print("\n" + "="*60)
    print("💰 PATHWISE — Personal Financial Planning Agent")
    print("="*60 + "\n")

    # Step 1: Load memory
    memory = load_memory()
    print("📂 Memory loaded.")

    # Step 2: Fetch live rates
    rates = get_live_rates()

    # Step 3: Extract financial profile
    print("📋 Extracting your financial profile...")
    profile_prompt = """You are a financial data extractor. 
Extract the following from the user's message as JSON:
- monthly_income (number)
- debts (list of {name, amount, apr})
- goals (list of strings)
- timeframe (string)
- monthly_expenses (number, estimate if not given)

Return ONLY valid JSON, nothing else."""

    profile_json = ask_nemotron(profile_prompt, user_input)

    try:
        # clean up response in case of markdown fences
        clean = profile_json.strip().replace("```json", "").replace("```", "").strip()
        profile = json.loads(clean)
    except:
        profile = {"raw_input": user_input}

    memory["profile"] = profile
    memory["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "input": user_input
    })

    # Step 4: Generate the financial roadmap
    print("🗺️  Building your personalized roadmap...")
    plan_prompt = f"""You are Pathwise, an expert autonomous financial planning agent.

You have access to these LIVE rates fetched right now:
- HYSA rates: {rates['hysa'][:500]}
- 30yr Mortgage rates: {rates['mortgage_30yr'][:500]}
- S&P 500 outlook: {rates['sp500'][:500]}

The user's financial profile:
{json.dumps(profile, indent=2)}

Your job:
1. Analyze their situation honestly
2. Prioritize their financial steps in the right order (emergency fund → high interest debt → investing → goals)
3. Generate a clear month-by-month roadmap for the next 12 months
4. Give specific dollar amounts for each month
5. Reference the live rates you found when relevant
6. End with a "What-If" section showing how a 10% raise would change the plan

Be specific, actionable, and encouraging. Format with clear sections and months."""

    roadmap = ask_nemotron(plan_prompt, f"Build my financial roadmap. My situation: {user_input}")

    # Step 5: Save plan to memory
    memory["plans"].append({
        "timestamp": datetime.now().isoformat(),
        "input": user_input,
        "roadmap": roadmap
    })
    save_memory(memory)

    # Step 6: Print the roadmap
    print("\n" + "="*60)
    print("📊 YOUR PERSONALIZED FINANCIAL ROADMAP")
    print("="*60)
    print(roadmap)
    print("\n" + "="*60)
    print("✅ Plan saved to memory. Run again to update your profile.")
    print("="*60 + "\n")

    return roadmap

# ── what-if scenario ──────────────────────────────────────────────────────────
def run_whatif(scenario):
    print(f"\n🔄 Running what-if: {scenario}")
    memory = load_memory()

    if not memory["plans"]:
        print("No existing plan found. Run the main agent first.")
        return

    last_plan = memory["plans"][-1]["roadmap"]

    whatif_prompt = f"""You are Pathwise, a financial planning agent.
The user has an existing financial plan:
{last_plan[:1000]}

They want to know: {scenario}

Explain specifically how this change affects their roadmap.
Give updated month-by-month numbers where relevant.
Be concise but specific."""

    result = ask_nemotron(whatif_prompt, scenario)
    print("\n" + "="*60)
    print("🔄 WHAT-IF ANALYSIS")
    print("="*60)
    print(result)
    print("="*60 + "\n")

# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nWelcome to Pathwise 💰")
    print("1. Build my financial plan")
    print("2. What-if scenario")
    choice = input("\nChoose (1 or 2): ").strip()

    if choice == "1":
        print("\nDescribe your financial situation in plain English.")
        print("Example: I make $3,000/month, have $5,000 in credit card debt at 22% APR, and want to buy a car in 2 years.\n")
        user_input = input("Your situation: ").strip()
        run_pathwise(user_input)
    elif choice == "2":
        scenario = input("What scenario do you want to explore? ").strip()
        run_whatif(scenario)
    else:
        print("Invalid choice.")