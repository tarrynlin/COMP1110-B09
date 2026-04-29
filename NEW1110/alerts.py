import math
from datetime import datetime, timedelta
from data_model import Transaction, BudgetRules, Category

class AlertEngine:
    @staticmethod
    def check_alerts(transactions, rules):
        alerts = []
        now = datetime.now()

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
                alerts.append(f"OVER LIMIT! [{rule.period}] {rule.category.value} limit exceeded ${total:.2f}")
        
        all_spent = 0
        transport_spent = 0
        meals_spent = 0
        entertainment_spent = 0
        for t in transactions:
            all_spent += t.amount
            if t.category == Category.TRANSPORT:
                transport_spent += t.amount
            if t.category == Category.MEALS:
                meals_spent += t.amount
            if t.category == Category.ENTERTAINMENT:
                entertainment_spent+= t.amount
        
        if all_spent > 0:
            if (transport_spent/all_spent) > 0.30:
                alerts.append("Warning: Transport is over 30% of total budget.")
            if (meals_spent/all_spent)>0.40:
                alerts.append("Warning: Meals is over 40% of total budget.")
            if (entertainment_spent/all_spent)>0.20:
                alerts.append("Warning: Entertainment is over 20% of total budget.")

        daily_totals = {}
        for t in transactions:
            day_key = t.date.strftime("%Y-%m-%d")
            daily_totals[day_key] = daily_totals.get(day_key, 0) + t.amount
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


        uncat_count = 0
        for t in transactions:
            if t.category == Category.UNCATEGORISED:
                uncat_count += 1
        if uncat_count >0:
            alerts.append(f"Notice: {uncat_count} transactions need to be categorized.")

        return alerts if alerts else ["Safe within budget."]
