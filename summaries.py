from datetime import datetime, timedelta
from data_model import Transaction, Category, TotalIncome
from typing import List, Dict, Tuple
from collections import defaultdict

class SummaryEngine:
    @staticmethod
    def get_monthly_report(transactions: List[Transaction], total_income_obj: TotalIncome = None, mode: str = "monthly") -> List[str]:
        """
        Generates a comprehensive spending report with various metrics.
        """

        report = []
        now = max((t.date for t in transactions), default=datetime.today())
        
        # Filter transactions based on mode
        filtered_trans = SummaryEngine._filter_transactions(transactions, mode)
        
        if not filtered_trans:
            report.append("No transactions to summarize.")
            return report
        
        # Total spending
        total_spending_filtered = sum(t.amount for t in filtered_trans)
        report.append(f"{now.strftime("%B").upper()} SPENDING SUMMARY")
        report.append("-" * 60)
        report.append(f"Total spending (this month): ${total_spending_filtered:.2f}")
        
        # Income information
        if total_income_obj:
            report.append(f"Total monthly income: ${total_income_obj.total:.2f}")
            remaining = total_income_obj.total - total_spending_filtered
            spending_percentage = (total_spending_filtered / total_income_obj.total) * 100 if total_income_obj.total > 0 else 0
            report.append(f"Remaining: ${remaining:.2f}")
            report.append(f"Spending: {spending_percentage:.1f}%")
        
        report.append("")
        

        # Per-category totals
        report.extend(SummaryEngine._get_category_summary(filtered_trans))
        report.append("")

        
        # Top 3 spending categories
        report.extend(SummaryEngine._get_top_categories(filtered_trans, total_income_obj.total))
        report.append("")

        
        # Daily totals
        report.extend(SummaryEngine._get_daily_totals(filtered_trans))
        report.append("")
        
        # Weekly totals
        report.extend(SummaryEngine._get_weekly_totals(filtered_trans))
        report.append("")

        
        # Spending trends
        report.extend(SummaryEngine._get_spending_trends(transactions))
        report.append("")
        
        report.append("=" * 60)
        
        
        #spending summary for ALL transactions
        report.append("HISTORICAL SPENDING SUMMARY")
        report.append("-" * 60)
        total_spending = sum(t.amount for t in transactions)
        
        report.append(f"Total spending (all-time): ${total_spending:.2f}\n")

        report.extend(SummaryEngine._get_category_summary(transactions))
        report.append("")
        report.extend(SummaryEngine._get_top_categories(transactions, total_income_obj.total, "All"))
        report.append("")
        report.extend(SummaryEngine._get_weekly_totals(transactions))
        report.append("")
        report.extend(SummaryEngine._get_monthly_totals(transactions))
        report.append("")

        return report
    
    @staticmethod
    def _filter_transactions(transactions: List[Transaction], mode: str) -> List[Transaction]:
        """
        Filters transactions based on the specified mode.
        """
        if not transactions:
            return []
        
        now = max((t.date for t in transactions), default=datetime.today())
        
        if mode == "monthly":
            return [t for t in transactions if t.date.month == now.month and t.date.year == now.year]

    
    @staticmethod
    def _get_category_summary(transactions: List[Transaction]) -> List[str]:
        """
        Returns per-category spending totals.
        """
        report = []
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for t in transactions:
            category_totals[t.category] += t.amount
            category_counts[t.category] += 1
        
        report.append("SPENDING BY CATEGORY:")
        report.append("-" * 60)
        
        # Sort by spending amount (descending)
        sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        for category, total in sorted_cats:
            count = category_counts[category]
            report.append(f"  {category.value:20s} ${total:.2f}  ({count} transactions)")
        
        return report
    
    @staticmethod
    def _get_top_categories(transactions: List[Transaction], totalincome, mode="monthly") -> List[str]:
        """
        Returns the top 3 spending categories.
        """
        report = []
        category_totals = defaultdict(float)
        
        for t in transactions:
            category_totals[t.category] += t.amount
        
        # Sort by spending amount (descending)
        sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_3 = sorted_cats[:3]
        
        report.append("TOP 3 SPENDING CATEGORIES:")
        report.append("-" * 60)
        
        if not top_3:
            report.append("  No spending data available")
            return report
        
        for i, (category, total) in enumerate(top_3, 1):
            percentage_spending = (total / sum(t.amount for t in transactions)) * 100 if transactions else 0
            percentage_budget = (total / totalincome) * 100 if transactions else 0
            temp = f"  {i}. {category.value:20s} ${total:.2f}"
            if mode == "monthly":
                temp += f" ({percentage_spending:.1f}% of total spending, {percentage_budget:.1f}% of total income)"
            else:
                temp += f" ({percentage_spending:.1f}% of total spending)"
            report.append(temp)
        
        return report
    
    @staticmethod
    def _get_daily_totals(transactions: List[Transaction]) -> List[str]:
        """
        Returns daily spending totals.
        """
        report = []
        daily_totals = defaultdict(float)
        daily_counts = defaultdict(int)
        
        for t in transactions:
            day_key = t.date.strftime("%Y-%m-%d")
            daily_totals[day_key] += t.amount
            daily_counts[day_key] += 1
        
        report.append("DAILY SPENDING (last 5 days):")
        report.append("-" * 60)
        
        # Sort by date (ascending)
        sorted_days = sorted(daily_totals.items(), reverse=True)
        c = 0

        for day, total in sorted_days:
            if c == 5:
                break
            count = daily_counts[day]
            report.append(f"  {day}  ${total:.2f}  ({count} transactions)")
            c += 1
            
        
        return report
    
    @staticmethod
    def _get_weekly_totals(transactions: List[Transaction]) -> List[str]:
        """
        Returns weekly spending totals.
        """
        report = []
        weekly_totals = defaultdict(float)
        weekly_counts = defaultdict(int)
        
        for t in transactions:
            # Get the week number and year
            week_num = t.date.isocalendar()[1]
            year = t.date.isocalendar()[0]
            week_key = f"{year}-W{week_num:02d}"
            weekly_totals[week_key] += t.amount
            weekly_counts[week_key] += 1
        
        report.append("WEEKLY SPENDING:")
        report.append("-" * 60)
        
        # Sort by week
        sorted_weeks = sorted(weekly_totals.items())
        
        for week, total in sorted_weeks:
            count = weekly_counts[week]
            report.append(f"  {week}  ${total:.2f}  ({count} transactions)")
        
        return report
    
    @staticmethod
    def _get_monthly_totals(transactions: List[Transaction]) -> List[str]:
        """
        Returns monthly spending totals across all months in data.
        """
        report = []
        monthly_totals = defaultdict(float)
        monthly_counts = defaultdict(int)
        
        for t in transactions:
            month_key = t.date.strftime("%Y-%m")
            monthly_totals[month_key] += t.amount
            monthly_counts[month_key] += 1
        
        report.append("MONTHLY SPENDING:")
        report.append("-" * 60)
        
        # Sort by month (ascending)
        sorted_months = sorted(monthly_totals.items())
        
        for month, total in sorted_months:
            count = monthly_counts[month]
            report.append(f"  {month}  ${total:.2f}  ({count} transactions)")
        
        return report
    
    @staticmethod
    def _get_spending_trends(transactions: List[Transaction]) -> List[str]:
        """
        Returns spending trends for last 7 days and last 30 days.
        """
        report = []
        now = max((t.date for t in transactions), default=datetime.today())
        
        report.append("SPENDING TRENDS:")
        report.append("-" * 60)
        
        # Last 7 days
        seven_days_ago = now - timedelta(days=7)
        last_7_trans = [t for t in transactions if t.date >= seven_days_ago]
        last_7_spending = sum(t.amount for t in last_7_trans)
        last_7_avg = last_7_spending / 7 if last_7_spending > 0 else 0
        
        report.append("  Last 7 Days:")
        report.append(f"   Total: ${last_7_spending:.2f}")
        report.append(f"   Daily Average: ${last_7_avg:.2f}")
        report.append(f"   Transaction Count: {len(last_7_trans)}")
        
        # Last 30 days
        thirty_days_ago = now - timedelta(days=30)
        last_30_trans = [t for t in transactions if t.date >= thirty_days_ago]
        last_30_spending = sum(t.amount for t in last_30_trans)
        last_30_avg = last_30_spending / 30 if last_30_spending > 0 else 0
        
        report.append(f"  Last 30 Days:")
        report.append(f"   Total: ${last_30_spending:.2f}")
        report.append(f"   Daily Average: ${last_30_avg:.2f}")
        report.append(f"   Transaction Count: {len(last_30_trans)}")
        
        return report

    
    @staticmethod
    def get_top_categories_dict(transactions: List[Transaction], limit: int = 3) -> List[Tuple[str, float]]:
        """
        Returns top spending categories as a list of tuples (category_name, amount).
        """
        category_totals = defaultdict(float)
        
        for t in transactions:
            category_totals[t.category.value] += t.amount
        
        sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_cats[:limit]
