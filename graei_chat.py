from graei_cryptex import run_simulation
from graei_strategy import GraeiStrategy
from typing import Dict, Any

def get_current_state() -> Dict[str, Any]:
    """Get current state by running a simulation."""
    sim = run_simulation()
    return {
        "capital": sim["capital"],
        "current_prices": {
            "runner": 2000,  # Default prices
            "in_passer1": 1000,
            "in_passer2": 30000
        },
        "currencies": {}  # We'll populate this as needed
    }

def analyze_market_conditions() -> str:
    """Analyze current market conditions and provide insights"""
    state = get_current_state()
    current_prices = state["current_prices"]
    
    runner_price = current_prices["runner"]
    passer1_price = current_prices["in_passer1"]
    passer2_price = current_prices["in_passer2"]
    
    # Calculate price differences
    diff1 = abs(runner_price - passer1_price)
    diff2 = abs(runner_price - passer2_price)
    
    conditions = []
    if diff1 < diff2:
        conditions.append("🔍 Runner is closer to Low-Passer, potential buy zone")
    else:
        conditions.append("🔍 Runner is closer to High-Passer, watching for sell signals")
        
    if runner_price < passer1_price:
        conditions.append("📉 Runner price below Low-Passer, accumulation possible")
    elif runner_price > passer2_price:
        conditions.append("📈 Runner price above High-Passer, consider taking profits")
    
    return "\n".join(conditions)

def get_performance_metrics():
    """Calculate and return performance metrics"""
    sim = run_simulation()
    total_capital = sum(sim["capital"].values())
    total_in_pools = sum(sim["pools"].values())
    initial_total = 500  # Based on graei_cryptex.initial_investment
    roi = (((total_capital + total_in_pools) / initial_total) - 1) * 100
    
    pool_stats = "\n    ".join([f"{name.replace('_', ' ').capitalize()}: ${amount:,.2f}" for name, amount in sim["pools"].items()])
    
    return f"""[STATS] Performance Metrics:
    Total Value: ${(total_capital + total_in_pools):,.2f}
    ROI: {roi:,.2f}%
    Capital: ${total_capital:,.2f}
    Pools Breakdown:
    {pool_stats}"""

def sanitize_emojis(text: str) -> str:
    """Replace emojis with text equivalents"""
    emoji_map = {
        "🔍": "[SCAN]",
        "📉": "[DOWN]",
        "📈": "[UP]",
        "📊": "[STATS]",
        "🤖": "[BOT]",
        "🎯": "[TARGET]",
        "⚙️": "[CONFIG]",
        "🧿": "[ECHO]"
    }
    for emoji, text_version in emoji_map.items():
        text = text.replace(emoji, text_version)
    return text

def process_chat_message(message: str) -> str:
    """Process chat messages and return appropriate responses"""
    message = message.lower()
    
    # Analysis commands
    if any(word in message for word in ['analyze', 'analysis', 'condition']):
        return sanitize_emojis(analyze_market_conditions())
    
    # Status and performance queries
    if any(word in message for word in ['status', 'balance', 'capital', 'performance']):
        state = get_current_state()
        metrics = sanitize_emojis(get_performance_metrics())
        return f"{metrics}\n\nCurrent Prices:\n" + \
               "\n".join(f"{name}: ${price:,.2f}" for name, price in state["current_prices"].items())
    
    # Trading commands
    if 'trade' in message:
        if 'auto' in message or 'run' in message:
            sim = run_simulation()
            return "🤖 Trade executed automatically based on Echo Zones. Check the pearl log for details."
        else:
            analysis = analyze_market_conditions()
            return f"Current Market Analysis:\n{analysis}\n\nSay 'run trade' to execute based on these conditions."
    
    # Position queries
    if any(word in message for word in ['position', 'holding']):
        # Simulated response since we're not tracking real positions
        return "No active positions at the moment. (Simulation mode)"
    
    # Price queries
    if any(word in message for word in ['price', 'value', 'worth']):
        state = get_current_state()
        if 'runner' in message:
            return f"Runner Price: ${state['current_prices']['runner']:,.2f}"
        elif 'high' in message or 'upper' in message:
            return f"High-Passer Price: ${state['current_prices']['in_passer2']:,.2f}"
        elif 'low' in message or 'lower' in message:
            return f"Low-Passer Price: ${state['current_prices']['in_passer1']:,.2f}"
        else:
            return "\n".join(f"{name}: ${price:,.2f}" for name, price in state["current_prices"].items())
    
    # Strategy explanation
    if any(word in message for word in ['strategy', 'how', 'work']):
        return """🎯 Echo Cascading Strategy:
        1. Multi-Tiered Profit Sharing:
           - Daily -> Weekly -> Bi-weekly -> Monthly -> Bi-monthly -> Quarterly
           - Profits cascade through time increments at specific percentages.
        2. Price Spectrum Exploitation:
           - Buys in proportionally as price enters the "decreasing spectrum."
           - Sells in opposite amounts on the "increase of the spectrum."
        3. Dynamic Reinvestment:
           - Monthly pools provide a structured boost to initial capital.
        
        Current Parameters:
        - Fluctuation: +/- 10% daily
        - Buy Zone: Proxies Low-Passer (e.g. TSLA vs F)
        - Sell Zone: Proxies High-Passer (e.g. TSLA vs RIVN)"""
    
    # Configuration queries
    if any(word in message for word in ['config', 'setup', 'settings']):
        state = get_current_state()
        sim = run_simulation()
        return f"""⚙️ Current Configuration:
        Initial Investment: ${sum(sim["capital"].values()):,.2f}
        Runner: TSLA
        Low-Passer: F
        High-Passer: RIVN
        
        Active Positions: 0 (Simulation mode)"""
    
    # Approval commands
    if any(word in message for word in ['approve', 'accept', 'confirm', 'agree']):
        # Simulate approval of the suggested coin (e.g., TSLA or a Crypto coin)
        sim = run_simulation(mode="tri", approved_plan="TSLA")
        return "✅ Plan Approved. The system has locked in the suggested buy/sell pattern based on 90-day historical averages. (Liability acknowledged by user approval)"

    if any(word in message for word in ['suggest', 'recommend', 'plan']):
        historical_averages = {"TSLA": 0.12, "BTC": 0.15, "ETH": 0.11}
        from graei_cryptex import suggest_best_coin
        best = suggest_best_coin(historical_averages)
        return f"📊 90-Day Evaluation: Based on historical data standards, the most valuable asset for your current time differential is **{best}**. \n\nDo you want to 'approve plan' for {best} utilizing the Merkaba Buy/Sell system?"

    # Help command
    if 'help' in message:
        return """[BOT] Graei Assistant Commands:
        
        Market Analysis:
        - 'analyze market' - Get current market conditions
        - 'suggest plan' - Get 90-day asset recommendation
        - 'approve plan' - Accept the suggested buy/sell outlook
        - 'show prices' - View all asset prices
        - 'check runner price' - Get Runner price
        
        Trading:
        - 'run trade' - Execute automatic trade
        - 'show positions' - View current holdings
        - 'check performance' - Get ROI and metrics
        
        Information:
        - 'explain strategy' - Learn how Echo trading works
        - 'show config' - View current settings
        - 'show status' - Get complete overview
        
        You can also ask questions in natural language!"""
    
    # Default response with context
    analysis = analyze_market_conditions()
    return f"""I'm here to help you trade! Here's the current market situation:

{analysis}

Ask for 'help' to see all available commands."""