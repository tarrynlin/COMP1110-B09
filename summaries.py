from datetime import datetime, timedelta
from data_model import Transaction, Category

class SummaryEngine:
    @staticmethod
    def get_monthly_report(transactions, total_income_obj=None, mode = "monthly"):
        if not transactions:
            return ["No transaction data available.", "Please add a transaction or load a scenario"]
        reference_date = max(t.date for t in transactions)
        
        category_totals = {}
        daily_totals = {}
        weekly_totals = {}
        
        filtered_total = 0
        all_time_total = 0
        uncat_count_filtered = 0
        uncat_total_filtered = 0

        for t in transactions:
            all_time_total += t.amount
            is_match = False
            if mode == "monthly":
                if t.date.month == reference_date.month and t.date.year == reference_date.year:
                    is_match = True
            elif mode == "trend":
                cutoff_date = reference_date - timedelta(days = 7)
                if t.date >= cutoff_date:
                    is_match = True
                
            if is_match:
                if t.category == Category.UNCATEGORISED:
                    uncat_count_filtered += 1
                    uncat_total_filtered += t.amount

                cat_name = t.category.value
                category_totals[cat_name] = category_totals.get(cat_name, 0) + t.amount
                filtered_total += t.amount

                day_key = t.date.strftime("%Y-%m-%d")
                daily_totals[day_key] = daily_totals.get(day_key, 0) + t.amount

                week_key = t.date.strftime("Week %V")
                weekly_totals[week_key] = weekly_totals.get(week_key, 0) + t.amount
        
        valid_cats = [c for c in category_totals.items() if c[0] != "Uncategorised"]
        sorted_categories = sorted(valid_cats, key=lambda x: x[1], reverse=True)
        top3 = sorted_categories[:3]
        avg_daily = filtered_total/len(daily_totals) if daily_totals else 0
        
        report = []
        report.append(f"--- {reference_date.strftime('%B %Y')} Summary ---" if mode == "monthly" else "--- 7-Day Trend Analysis ---")

        starting_balance = total_income_obj.total
        remaining = starting_balance - all_time_total
        report.append(f"STARTING BALANCE: ${starting_balance:.2f}")
        report.append(f"REMAINING BALANCE: ${remaining:.2f}")

        report.append("-"*25)

        report.append(f"TOTAL (FILTERED): ${filtered_total:.2f}")
        report.append(f"TOTAL (ALL-TIME): ${all_time_total:.2f}")
        report.append(f"DAILY AVERAGE: ${avg_daily:.2f}")
        
        
        report.append(f"UNCATEGORIZED ITEMS ({mode.upper()}): {uncat_count_filtered} (Total: ${uncat_total_filtered:.2f})")
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
            if name == Category.UNCATEGORISED.value:
                continue
            percentage = (amount/filtered_total)*100 if filtered_total > 0 else 0
            report.append(f"{name}: ${amount:.2f} ({percentage:.1f}%)")
        
        return report
