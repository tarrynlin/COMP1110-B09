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
                if key not in rule_groups:
                    rule_groups[key] = []
                rule_groups[key].append(rule)
            
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
                
                 # Sort rules by threshold (ascending) to check warning before critical
                sorted_rules = sorted(group_rules, key=lambda r: r.threshold)
                
                # Track the highest threshold exceeded
                highest_alert = None
                highest_usage = 0
                
                for rule in sorted_rules:
                    if rule.threshold > 0:
                        usage = total / rule.threshold
                        
                        # Check if this rule's threshold is exceeded
                        if usage >= 1.0:
                            alert_type = rule.alert.value
                            alert_msg = f"{alert_type}! [{period}] {category.value} spending has reached ${total:.2f}, ${(total - rule.threshold):.2f} over limit!"
                            
                            
                            # Track the most severe alert (Critical > Warning)
                            if highest_alert is None:
                                highest_alert = (alert_msg, alert_type, usage)
                            elif alert_type == "Critical" and highest_alert[1] == "Warning":
                                # Replace warning with critical if critical threshold is higher
                                if rule.threshold > sorted_rules[0].threshold:
                                    highest_alert = (alert_msg, alert_type, usage)
                        elif usage >= 0.95:
                            alert_msg = f"{rule.alert.value}! [{period}] {category.value} is at {usage*100:.1f}% of your limit! (Only {int((1-usage)*100)}% left)"
                            alert_type = rule.alert.value
                            
                            if highest_alert is None:
                                highest_alert = (alert_msg, alert_type, usage)
                            elif alert_type == "Critical" and highest_alert[1] == "Warning":
                                highest_alert = (alert_msg, alert_type, usage)
                        elif usage >= 0.85:
                            alert_msg = f"{rule.alert.value}! [{period}] {category.value} is at {usage*100:.1f}%! of your limit!"
                            alert_type = rule.alert.value
                            
                            if highest_alert is None:
                                highest_alert = (alert_msg, alert_type, usage)
                            elif alert_type == "Critical" and highest_alert[1] == "Warning":
                                highest_alert = (alert_msg, alert_type, usage)
                        
                
                # Add the most severe alert for this category-period combination
                if highest_alert:
                    alerts.append(highest_alert[0])
                
                    
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
                if percentage > 0 and cat_totals[cat] > (income_value * percentage):
                    alerts.append(f"Warning: \"{label}\" spending is over {int(percentage*100)}% of your budget")

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
