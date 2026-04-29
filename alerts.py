import math
from datetime import datetime, timedelta
from data_model import Transaction, BudgetRules, Category

class AlertEngine:
    @staticmethod
    def check_alerts(transactions, rules):
        alerts = []
        now = datetime.now()

        all_spent = sum(t.amount for t in transactions)
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
                
                if total > rule.threshold:
                    alerts.append(f"OVER LIMIT! [{rule.period}] \"{rule.category.value}\" limit exceeded - ${total:.2f}")
                elif total > (rule.threshold*0.8):
                    alerts.append(f"Warning: \"{rule.category.value}\" is approaching your ${rule.threshold:.2f} limit.")
        
                all_spent = 0
                transport_spent = 0
                meals_spent = 0
                entertainment_spent = 0
                shopping_spent = 0
                utilities_spent = 0
                other_spent = 0
                for t in transactions:
                    all_spent += t.amount
                    if t.category == Category.TRANSPORT:
                        transport_spent += t.amount
                    if t.category == Category.MEALS:
                        meals_spent += t.amount
                    if t.category == Category.ENTERTAINMENT:
                        entertainment_spent+= t.amount
                    if t.category == Category.SHOPPING:
                        shopping_spent += t.amount
                    if t.category == Category.UTILITIES:
                        utilities_spent += t.amount
                    if t.category == Category.OTHER:
                        other_spent += t.amount
        
        elif all_spent > 0:
            if (transport_spent/all_spent) > 0.15:
                alerts.append("Warning: Transport is over 15% of total budget.")
            if (meals_spent/all_spent)>0.35:
                alerts.append("Warning: Meals is over 35% of total budget.")
            if (entertainment_spent/all_spent)>0.10:
                alerts.append("Warning: Entertainment is over 10% of total budget.")
            if (shopping_spent/all_spent) > 0.20:
                alerts.append("Warning: Shopping is over 20% of total budget.")
            if(utilities_spent/all_spent) > 0.10:
                alerts.append("Warning: Utilities is over 10% of total budget.")
            if (other_spent/all_spent)>0.10:
                alerts.append("Warning: Others is over 10% of total budget.")

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
