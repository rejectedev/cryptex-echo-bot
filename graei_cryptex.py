import random

# Initial Setup
initial_investment = 500
days_in_quarter = 90
daily_fluctuation_in_passer1 = 0.005
daily_fluctuation_in_passer2 = -0.005
daily_fluctuation_runner = 0.15
profit_boost = 0.20
creator_fee = 0.10  # 10% cut for the creator

starting_capital = {
    "runner": 200,
    "in_passer1": 150,
    "in_passer2": 150,
    "solo_coin": 500  # Added for Single-Coin Merkaba mode
}

initial_prices = {
    "in_passer1": 1800,  # Near Runner for frequent "echo"
    "in_passer2": 2200,  # Near Runner for frequent "echo"
    "runner": 2000,
    "solo_coin": 1.0  # Initial price for solo mode
}

capital = starting_capital.copy()
current_prices = initial_prices.copy()

# Tiered Profit Pools
pools = {
    "daily": 0,
    "weekly": 0,
    "bi_weekly": 0,
    "monthly": 0,
    "bi_monthly": 0,
    "quarterly": 0,
    "creator": 0  # 10% profit share pool
}

# Approval State
plan_approvals = {
    "echo_pattern": False,
    "coin_suggestion": None
}

month_profits = [0]
month = 1

# Currency Class
class Currency:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.positions = []

    def buy(self, price, units, capital):
        cost = price * units
        if capital >= cost:
            self.positions.append((price, units))
            return cost
        return 0

    def sell(self, price, units_to_sell):
        if not self.positions:
            return 0
        proceeds = 0
        sold_units = 0
        new_positions = []
        for buy_price, units in self.positions:
            if sold_units < units_to_sell:
                sell_units = min(units, units_to_sell - sold_units)
                sold_units += sell_units
                proceeds += sell_units * price
                remaining_units = units - sell_units
                if remaining_units > 0:
                    new_positions.append((buy_price, remaining_units))
            else:
                new_positions.append((buy_price, units))
        self.positions = new_positions
        return proceeds

currencies = {name: Currency(name, price) for name, price in initial_prices.items()}

# Trading Logic
def trade_overlap_zones():
    global capital, pools
    runner_price = current_prices["runner"]
    in_passer1_price = current_prices["in_passer1"]
    in_passer2_price = current_prices["in_passer2"]

    # Spectrum-based sizing logic: Buy more as price decreases within the 10% buy zone
    diff1_pct = (in_passer1_price - runner_price) / in_passer1_price
    if 0 < diff1_pct <= 0.10:
        # Increasing investment as we go deeper into the "decreasing spectrum"
        sizing_factor = diff1_pct / 0.10 
        units_to_buy = (capital["runner"] * sizing_factor) / runner_price
        cost = currencies["runner"].buy(runner_price, units_to_buy, capital["runner"])
        capital["runner"] -= cost

    # Spectrum-based sizing logic: Sell more as price increases within the 10% sell zone
    diff2_pct = (runner_price - in_passer2_price) / in_passer2_price
    if abs(diff2_pct) <= 0.10 and runner_price >= in_passer2_price * 0.5:
        # Sell proportional to the "increase of the spectrum"
        total_units = sum(units for _, units in currencies["runner"].positions)
        if total_units > 0:
            sizing_factor = max(0.1, 1 - abs(diff2_pct) / 0.10)
            units_to_sell = total_units * sizing_factor
            proceeds = currencies["runner"].sell(runner_price, units_to_sell)
            capital["runner"] += proceeds
            profit = proceeds - (runner_price * units_to_sell * 0.9)
            if profit > 0:
                # Deduct creator fee (10% of profit)
                fee = profit * creator_fee
                pools["creator"] += fee
                profit -= fee
                
                # Initial daily profit capture
                pools["daily"] += profit * 0.5
                capital["runner"] += profit * 0.5

# Merkaba Pattern: Intersecting Buy/Sell Zones
def merkaba_trade_logic(asset_name, low_bound, high_bound):
    global capital, pools
    price = current_prices[asset_name]
    
    # Buy at decreasing spectrum (Merkaba Lower Tetrahedron)
    diff_low = (low_bound - price) / low_bound
    if 0 < diff_low <= 0.10:
        sizing = diff_low / 0.10
        units = (capital[asset_name] * sizing) / price
        cost = currencies[asset_name].buy(price, units, capital[asset_name])
        capital[asset_name] -= cost
        
    # Sell at increasing spectrum (Merkaba Upper Tetrahedron)
    diff_high = (price - high_bound) / high_bound
    if abs(diff_high) <= 0.10:
        total_units = sum(u for _, u in currencies[asset_name].positions)
        if total_units > 0:
            sizing = max(0.1, 1 - (abs(diff_high) / 0.10))
            units_to_sell = total_units * sizing
            proceeds = currencies[asset_name].sell(price, units_to_sell)
            capital[asset_name] += proceeds
            profit = proceeds - (price * units_to_sell * 0.9)
            if profit > 0:
                # Deduct creator fee (10% of profit)
                fee = profit * creator_fee
                pools["creator"] += fee
                profit -= fee
                
                pools["daily"] += profit * 0.5
                capital[asset_name] += profit * 0.5

def suggest_best_coin(historical_averages):
    """
    Determine the most valuable coin based on past 90-day period
    for its time differential scheme.
    """
    # Simple selection based on highest historical volatility/returns
    best_coin = max(historical_averages, key=historical_averages.get)
    return best_coin

def run_simulation(mode="tri", approved_plan=None):
    global capital, current_prices, pools, month_profits, month, plan_approvals
    
    # Check for customer approval before proceeding with recommended plan
    if approved_plan:
        plan_approvals["echo_pattern"] = True
        plan_approvals["coin_suggestion"] = approved_plan
    
    # Reset state
    capital = starting_capital.copy()
    current_prices = initial_prices.copy()
    for p in pools: pools[p] = 0
    month_profits = [0]
    month = 1
    
    # Asset roles for dynamic selection
    roles = {
        "runner": "runner",
        "low_passer": "in_passer1",
        "high_passer": "in_passer2"
    }
    
    # Main Loop
    for day in range(1, days_in_quarter + 1):
        # --- Dynamic Selection (Anti-Stagnation) ---
        # Every 10 days, re-evaluate which asset should be the "Runner"
        if mode == "tri" and day % 10 == 0:
            potential_runners = ["runner", "in_passer1", "in_passer2"]
            # Simulate historical data evaluation: swap based on "volatility echo"
            random.shuffle(potential_runners)
            roles["runner"] = potential_runners[0]
            roles["low_passer"] = potential_runners[1]
            roles["high_passer"] = potential_runners[2]

        # Price Generation (Tri-Similar & Solo)
        if mode == "tri":
            current_prices["in_passer1"] *= (1 + daily_fluctuation_in_passer1)
            current_prices["in_passer2"] *= (1 + daily_fluctuation_in_passer2)
            direction = random.choice([-1, 1])
            current_prices["runner"] *= (1 + daily_fluctuation_runner * direction)
        else:
            # Solo mode uses internal volatility echo
            direction = random.choice([-1, 1])
            current_prices["solo_coin"] *= (1 + 0.05 * direction)

        # Trade 3 times per day using Merkaba logic
        for _ in range(3):
            if mode == "tri":
                # Utilize the best coin in their respected time differential
                merkaba_trade_logic(roles["runner"], current_prices[roles["low_passer"]], current_prices[roles["high_passer"]])
            else:
                # Solo Merkaba logic using self-adjusting bounds
                low_bound = current_prices["solo_coin"] * 0.9
                high_bound = current_prices["solo_coin"] * 1.1
                merkaba_trade_logic("solo_coin", low_bound, high_bound)

        # --- Cascading Profit Share Logic ---
        
        # 1. Weekly Cascade (Every 7 days)
        if day % 7 == 0:
            pools["weekly"] += pools["daily"] * 0.7  # 70% of daily flows to weekly
            pools["daily"] *= 0.3                   # 30% retained at daily level
            
        # 2. Bi-weekly Cascade (Every 14 days)
        if day % 14 == 0:
            pools["bi_weekly"] += pools["weekly"] * 0.6
            pools["weekly"] *= 0.4
            
        # 3. Monthly Cascade (Every 30 days)
        if day % 30 == 0:
            # Monthly reinvestment and pool movement
            pools["monthly"] += pools["bi_weekly"] * 0.5
            pools["bi_weekly"] *= 0.5
            
            # Simulated "Monthly Boost" from pooled profits
            monthly_boost = pools["monthly"] * 0.2
            for curr_name in starting_capital:
                capital[curr_name] += monthly_boost * (starting_capital[curr_name] / initial_investment)
            
            # Passer automated buys
            for passer in ["in_passer1", "in_passer2"]:
                if capital[passer] > 0 and random.random() > 0.5:
                    units_to_buy = capital[passer] / current_prices[passer]
                    cost = currencies[passer].buy(current_prices[passer], units_to_buy, capital[passer])
                    capital[passer] -= cost

        # 4. Bi-monthly Cascade (Every 60 days)
        if day % 60 == 0:
            pools["bi_monthly"] += pools["monthly"] * 0.4
            pools["monthly"] *= 0.6

        # 5. Quarterly Cascade (Day 90)
        if day == 90:
            pools["quarterly"] += pools["bi_monthly"]

        # 6. Structured Capital Boost (Efficiency representation)
        assets_to_boost = ["runner", "in_passer1", "in_passer2"] if mode == "tri" else ["solo_coin"]
        for curr_name in assets_to_boost:
            initial = starting_capital[curr_name]
            profit = capital[curr_name] - initial
            if profit > 0:
                capital[curr_name] *= (1 + profit_boost)

        # Track Monthly Profits for reporting
        if day % 30 == 0:
            month_profit = sum(capital[curr] - starting_capital[curr] for curr in starting_capital)
            month_profits.append(month_profit)

    # Calculate Final Results
    total_in_pools = sum(pools.values())
    total = sum(capital.values()) + total_in_pools
    quarterly_roi = (total / initial_investment - 1) * 100
    
    return {
        "capital": capital,
        "pools": pools,
        "total": total,
        "quarterly_roi": quarterly_roi
    }

if __name__ == "__main__":
    mode_to_run = "tri" # or "solo"
    results = run_simulation(mode=mode_to_run)
    print(f"Mode: {mode_to_run}")
    print(f"Capital Breakdown: {results['capital']}")
    print(f"Pools Breakdown: {results['pools']}")
    print(f"Total: ${results['total']:.2f}")
    print(f"Quarterly ROI: {results['quarterly_roi']:.2f}%")
