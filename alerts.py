import math
from datetime import datetime, timedelta
from data_model import Transaction, BudgetRules, Category

class AlertEngine:
    @staticmethod
    def check_alerts(transactions, rules, income_value):
        alerts = []
        now = max((t.date for t in transactions), default=datetime.today())

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
            # Group rules by category and period to handle multiple alert types
            rule_groups = {}
            for rule in rules:
                key = (rule.category, rule.period)
                rule_groups.setdefault(key, []).append(rule)
                
            # Process each category-period combination
            for (category, period), group_rules in rule_groups.items():
                matches = []
                for t in transactions:
                    if t.category == category:
                        if period == "Daily":
                            if t.date.date() == now.date():
                                matches.append(t)
                        elif period == "Weekly":
                            time_diff = now - t.date
                            if time_diff.days < 7:
                                matches.append(t)
                        elif period == "Monthly":
                            if t.date.month == now.month and t.date.year == now.year:
                                matches.append(t)
                    
                total = 0
                for m in matches:
                    total += m.amount
                
                severity_map = {"Critical": 2, "Warning": 1, "Notice": 0}
                highest_alert = None
                severity_score = -1

                
                for rule in group_rules:
                    usage = total/rule.threshold
                    current_score = severity_map.get(rule.alert.value, 0)
                    msg = None

                    # Check if this rule's threshold is exceeded
                    if usage >= 1.0:
                        msg = f"{rule.alert.value}! [{period}] {category.value} spending has reached ${total:.2f}, ${(total - rule.threshold):.2f} over limit!"
                    elif usage >= 0.85:
                        msg = f"{rule.alert.value}! [{period}] {category.value} spending is at {usage*100:.1f}% of limit!"
                    
                    #Replace existing alert if more severe
                    if msg and current_score > severity_score:
                            highest_alert = msg
                            severity_score = current_score
                if highest_alert: 
                    alerts.append(highest_alert)
        
             
        if income_value > 0:
            default = {
                Category.TRANSPORT: (0.15, "Transport"),
                Category.MEALS: (0.35, "Meals"),
                Category.ENTERTAINMENT: (0.10, "Entertainment"),
                Category.SHOPPING: (0.20, "Shopping"),
                Category.UTILITIES: (0.10, "Utilities"),
                Category.OTHER: (0.10, "Other"),
                Category.UNCATEGORISED: (0.0, "Uncategorised")
            }
            for cat, (percentage, label) in default.items():
                limit = income_value * percentage
                usage = cat_totals[cat] / limit if limit > 0 else 0
                if usage >= 1.0:
                    alerts.append(f"Critical: {cat.value} spending (${cat_totals[cat]:.2f}) has exceeded {percentage*100}% of your total income!")
                elif usage >= 0.90:
                    alerts.append(f"Warning: {cat.value} spending has reached almost {percentage*100}% of your total income")

        amounts = list(daily_totals.values())
        if len(amounts) >= 2:
            avg = sum(amounts)/len(amounts)
            variance = sum((x - avg)** 2 for x in amounts)/len(amounts)
            std_dev = math.sqrt(variance)

            today_str = now.strftime("%Y-%m-%d")
            today_total = daily_totals.get(today_str, 0)
            if today_total > 0 and today_total > (avg + 2*std_dev):
                alerts.append(f"Spending spike today! ${today_total:.2f} is unusually high.")
            
            sorted_days = sorted(daily_totals.keys(), reverse=True)
            streak = 0
            for day in sorted_days:
                if daily_totals[day] > avg:
                    streak += 1
                else:
                    break
            if streak >= 3:
                alerts.append(f"Warning: {streak}-day overspending streak detected!")
  
        if uncat_count > 0:
            alerts.append(f"Warning: {uncat_count} transactions are not categorized.")

        return alerts if alerts else ["Safe within budget."]
