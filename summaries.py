from datetime import datetime, timedelta
from data_model import Transaction, Category

class SummaryEngine:
    @staticmethod
    def get_monthly_report(transactions, mode = "monthly"):
        category_totals = {}
        daily_totals = {}
        weekly_totals = {}
        
        filtered_total = 0
        all_time_total = 0
        uncat_count = 0

        now = datetime.now()
        for t in transactions:
            all_time_total += t.amount
            if t.category == Category.UNCATEGORIZED:
                uncat_count += 1

            is_match = False
            if mode == "monthly":
                if t.date.month == now.month and t.date.year == now.year:
                    is_match = True
            elif mode == "trend":
                cutoff_date = now - timedelta(days = 7)
                if t.date >= cutoff_date:
                    is_match = True
                
            if is_match:
                cat_name = t.category.value
                if cat_name not in category_totals:
                    category_totals[cat_name]=0
                category_totals[cat_name] += t.amount
                filtered_total += t.amount

                day_key = t.date.strftime("%Y-%m-%d")
                daily_totals[day_key] = daily_totals.get(day_key, 0) + t.amount

                week_key = t.date.strftime("Week %V")
                weekly_totals[week_key] = weekly_totals.get(week_key, 0) + t.amount
        
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top3 = sorted_categories[:3]
        avg_daily = filtered_total/len(daily_totals) if daily_totals else 0
        
        today_str = now.strftime("%Y-%m-%d")
        today_spend = daily_totals.get(today_str, 0)

        report = []
        report.append(f"--- {now.strftime('%B %Y')} Summary ---" if mode == "monthly" else "--- 7-Day Trend Analysis ---")
        report.append(f"TOTAL (FILTERED): ${filtered_total:.2f}")
        report.append(f"TOTAL (ALL-TIME): ${all_time_total:.2f}")
        report.append(f"DAILY AVERAGE: ${avg_daily:.2f}")
        report.append(f"UNCATEGORIZED ITEMS: {uncat_count}")
        report.append("\nDAILY HISTORY (Last 5 Days):")
        sorted_days = sorted(daily_totals.items(), reverse = True)[:5]
        for day, amt in sorted_days:
            report.append(f"{day}: ${amt:.2f}")

        report.append("\nWEEKLY BREAKDOWN:")
        for week, amt in sorted(weekly_totals.items()):
            report.append(f"{week}: ${amt:.2f}")

        report.append("\nTOP 3 EXPENSES:")
        for i, (name, amount) in enumerate(top3, 1):
            report.append(f" {i}. {name}: ${amount:.2f}")

        report.append("-"*25)

        for name, amount in category_totals.items():
            percentage = (amount/filtered_total)*100
            report.append(f"{name}: ${amount:.2f} ({percentage:.1f}%)")
        
        return report#enter code for summaries here
