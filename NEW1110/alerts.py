import math
from datetime import datetime, timedelta
from data_model import Transaction, BudgetRules, Category

class AlertEngine:
    @staticmethod
    def check_alerts(transactions, rules, income_value):
        alerts = []
        now = datetime.now()

        cat_totals = {cat: 0 for cat in Category}
        daily_totals = {}
        uncat_count = 0

        for t in transactions:
            cat_totals[t.category] += t.amount
            if t.category == Category.UNCATEGORISED:
                uncat_count += 1
            
            day_key = t.date.strftime("%Y-%m-%d")
            daily_totals[day_key] = daily_totals.get(day_key, 0) + t.amount
        
        if len(rules) > 0:
            for rule in rules:
                matches = []
                for t in transactions:
                    if t.category == rule.category:
                        if rule.period == "Daily":
                            if t.date.date() == now.date():
                                matches.append(t)
                        elif rule.period == "Weekly":
                            time_diff = now - t.date
                            if time_diff.days <= 7:
                                matches.append(t)
                        elif rule.period == "Monthly":
                            if t.date.month == now.month and t.date.year == now.year:
                                matches.append(t)
                    
                total = 0
                for m in matches:
                    total += m.amount
                
                if rule.threshold > 0:
                    usage = total/rule.threshold
                    if usage >=1.0:
                        alerts.append(f"OVER LIMIT! [{rule.period}] {rule.category.value} limit exceeded - ${total:.2f}")
                    elif usage >= 0.95:
                        alerts.append(f"[CRITICAL] {rule.category.value} is at {usage*100:.1f}%! (Only 5% left)")
                    elif usage >= 0.85:
                        alerts.append(f"[WARNING] {rule.category.value} is at {usage*100:.1f}%! of your limit.")
                    
        elif income_value > 0:
            default = {
                Category.TRANSPORT: (0.15, "Transport"),
                Category.MEALS: (0.35, "Meals"),
                Category.ENTERTAINMENT: (0.10, "Entertainment"),
                Category.SHOPPING: (0.20, "Shopping"),
                Category.UTILITIES: (0.10, "Utilities"),
                Category.OTHER: (0.10, "Others")
            }
            for cat, (percentage, label) in default.items():
                if cat_totals[cat] > (income_value * percentage):
                    alerts.append(f"Warning: \"{label}\" is over {int(percentage*100)}%")

        amounts = list(daily_totals.values())
        if len(amounts)>= 2:
            avg = sum(amounts)/len(amounts)
            variance = sum((x - avg)** 2 for x in amounts)/len(amounts)
            std_dev = math.sqrt(variance)

            today_str = now.strftime("%Y-%m-%d")
            today_total = daily_totals.get(today_str, 0)
            if today_total > (avg + 2*std_dev):
                alerts.append(f"Spending spike today! ${today_total:.2f} is unusually high.")
            
            sorted_days = sorted(daily_totals.keys(), reverse = True)
            streak = 0
            for day in sorted_days:
                if daily_totals[day]>avg:
                    streak += 1
                else:
                    break
            if streak >= 3:
                alerts.append(f"Warning: {streak}-day overspending streak detected!")
  
        if uncat_count >0:
            alerts.append(f"Notice: {uncat_count} transactions need to be categorized.")

        return alerts if alerts else ["Safe within budget."]
