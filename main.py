import customtkinter as ctk
from datetime import datetime
from data_model import Category, Transaction, CurrentState, AlertType, BudgetRules, TotalIncome
from file_handling import FileHandler
from summaries import SummaryEngine
from alerts import AlertEngine
from test_data_generator import TestDataGenerator
from tkinter import filedialog


class main_GUI:
    """
    This is the main GUI application for the budgeting tool
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Budgeting Tool")
        self.root.geometry("1100x600")
        self.state: CurrentState        #for loading and saving total income, transactions and budget rules from and into CurrentState      

        self.state, load_errors = FileHandler.load_state()

        #display any errors that arise from loading in total income, transactions and budget rules from their respective json files into CurrentState
        if load_errors:
            self.show_error("Errors loading data:\n\n" + "\n".join(load_errors))

        self.setup()

    
    def setup(self):
        """
        This function sets up UIs
        """

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        #tabs
        self.tab_income = self.tabview.add("Set Income")
        self.tab_transactions = self.tabview.add("Transactions")
        self.tab_budgets = self.tabview.add("Budget Rules")
        self.tab_summary = self.tabview.add("Summary")
        self.tab_alerts = self.tabview.add("Alerts")
        self.tab_test = self.tabview.add("Test Data")
    
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.income_tab()
        self.transactions_tab()
        self.budget_rules_tab()
        self.summaries_tab()
        self.alerts_tab()
        self.test_tab()

        ctk.CTkButton(bottom_frame, text="Save Data", command=self.save_all).pack(side="left", padx=5)
        ctk.CTkButton(bottom_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)
        ctk.CTkButton(bottom_frame, text="Delete All Data", command=self.clear_all).pack(side="right", padx=5)

    
    def income_tab(self):
        """
        This function sets up the tab for entering total income
        """

        input_frame = ctk.CTkFrame(self.tab_income, height=400)
        input_frame.pack(fill="x")

        ctk.CTkLabel(input_frame, text="Please enter your net total income to begin budgeting:", font=("Arial", 15)).place(relx=0.35, rely=0.2)
        self.income_entry = ctk.CTkEntry(input_frame, width=150)
        self.income_entry.place(relx=0.44, rely=0.3)

        ctk.CTkButton(input_frame, text="Set Total Income", command=self.add_income).place(relx=0.445, rely=0.5)


    def transactions_tab(self):
        """
        This function sets up the transactions tab
        """

        input_frame = ctk.CTkFrame(self.tab_transactions, height=400)
        input_frame.pack(fill="x")

        ctk.CTkLabel(input_frame, text="Date (YYYY-MM-DD):").place(relx=0.03, rely=0.2)
        self.date_entry = ctk.CTkEntry(input_frame, width=150)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.place(relx=0.16, rely=0.2)

        ctk.CTkLabel(input_frame, text="Amount:").place(relx=0.03, rely=0.35)
        self.amount_entry = ctk.CTkEntry(input_frame, width=100)
        self.amount_entry.place(relx=0.16, rely=0.35)

        ctk.CTkLabel(input_frame, text="Category:").place(relx=0.03, rely=0.5)
        self.category = ctk.StringVar(value=Category.UNCATEGORISED.value)       #default value is "Uncategorised"
        self.category_menu = ctk.CTkOptionMenu(input_frame, values=[c.value for c in Category], variable=self.category).place(relx=0.16, rely=0.5)

        ctk.CTkLabel(input_frame, text="Description:").place(relx=0.03, rely=0.65)
        self.description_entry = ctk.CTkEntry(input_frame, width=200)
        self.description_entry.place(relx=0.16, rely=0.65)

        ctk.CTkButton(input_frame, text="Add Transaction",command=self.add_transaction).place(relx=0.16, rely=0.85)

        self.transaction_box = ctk.CTkTextbox(input_frame, width=650, height=850)
        self.transaction_box.configure(state="disabled")
        self.transaction_box.place(relx=0.4, rely=0.2)

        self.filter = ctk.StringVar(value="All")        #default value is "All"
        self.filter_menu = ctk.CTkOptionMenu(input_frame, values=["All"]+[c.value for c in Category], variable=self.filter, command=self.display_transactions).place(relx=0.4, rely=0.1)

        self.display_transactions()


    def budget_rules_tab(self):
        """
        This function sets up the budget rules tab
        """
        
        input_frame = ctk.CTkFrame(self.tab_budgets, height=400)
        input_frame.pack(fill="x")
        ctk.CTkLabel(input_frame, text="Threshold:").place(relx=0.03, rely=0.2)
        self.budget_threshold = ctk.CTkEntry(input_frame, width=100)
        self.budget_threshold.place(relx=0.16, rely=0.2)

        ctk.CTkLabel(input_frame, text="Category:").place(relx=0.03, rely=0.35)
        self.budget_category = ctk.StringVar(value=Category.OTHER.value)
        self.budget_category_menu = ctk.CTkOptionMenu(input_frame, values=[c.value for c in Category], variable=self.budget_category).place(relx=0.16, rely=0.35)

        ctk.CTkLabel(input_frame, text="Time Period:").place(relx=0.03, rely=0.5)
        self.budget_period = ctk.StringVar(value="Monthly")
        self.budget_period_menu = ctk.CTkOptionMenu(input_frame, values=["Daily", "Weekly", "Monthly"], variable=self.budget_period).place(relx=0.16, rely=0.5)

        ctk.CTkLabel(input_frame, text="Alert Type:").place(relx=0.03, rely=0.65)
        self.budget_alert = ctk.StringVar(value=AlertType.WARNING.value)
        self.budget_alert_menu = ctk.CTkOptionMenu(input_frame, values=[a.value for a in AlertType], variable=self.budget_alert).place(relx=0.16, rely=0.65)

        ctk.CTkButton(input_frame, text="Add Budget Rule", command=self.add_budget_rules).place(relx=0.16, rely=0.85)

        self.budget_box = ctk.CTkTextbox(input_frame, width=650, height=850)
        self.budget_box.configure(state="disabled")
        self.budget_box.place(relx=0.4, rely=0.1)

        self.display_budget_rules()


    def summaries_tab(self):
        """
        This function sets up the summaries tab
        """

        summary_frame = ctk.CTkFrame(self.tab_summary)
        summary_frame.pack(fill="x", expand=True)

        self.summary_box = ctk.CTkTextbox(summary_frame, height=500)
        self.summary_box.configure(state="disabled")
        self.summary_box.pack(fill="x")

        self.display_summaries()
    

    def alerts_tab(self):
        """
        This function sets up the alerts tab
        """

        alerts_frame = ctk.CTkFrame(self.tab_alerts)
        alerts_frame.pack(fill="x", expand=True)
        
        self.alert_box = ctk.CTkTextbox(alerts_frame, height=500)
        self.alert_box.configure(state="disabled")
        self.alert_box.pack(fill="x")

        self.display_alerts()


    def test_tab(self):
        """
        This function sets up the test data generator tab
        """

        test_frame = ctk.CTkFrame(self.tab_test)
        test_frame.pack(fill="x", expand=True)


        ctk.CTkLabel(test_frame, text='Test Data Generator:', font=("Arial", 14, "bold")).pack(pady=10)

        ctk.CTkButton(test_frame, text="Scenario 1: Realistic 30 Days", command = lambda: self.load_test_scenario("realistic")).pack(pady=10)
        ctk.CTkButton(test_frame, text="Scenario 2: Overspend", command = lambda: self.load_test_scenario("overspend")).pack(pady=10)
        ctk.CTkButton(test_frame, text="Scenario 3: Empty", command = lambda: self.load_test_scenario("empty")).pack(pady=10)
        ctk.CTkButton(test_frame, text="Load Custom JSON Scenario", command = self.load_custom_json_scenario).pack(pady=10)

    
    def load_test_scenario(self, mode):
        """
        This function loads in realistic test transaction sets
        """
        
        if mode == "realistic":
            trans, rules, income = TestDataGenerator.generate_sample_data(days = 30)
        elif mode == "overspend":
            trans, rules, income = TestDataGenerator.generate_overspend_scenario()
        else:
            trans, rules , income = TestDataGenerator.generate_empty_scenario()
        
        self.state.transactions = trans
        self.state.budget_rules = rules

        total_spent = sum(t.amount for t in trans)
        remaining = income - total_spent
        self.state.total_income = TotalIncome(total=float(income), current = float(remaining))

        self.display_transactions()
        self.display_budget_rules()
        self.display_summaries()
        self.display_alerts()

        messages = {
            "realistic" : "Successfully generated 30 days of realistic data!",
            "overspend" : "Successfully generated overspending scenario!",
            "empty" : "Successfully cleared all data."
        }
        self.show_success_dialog(messages.get(mode, "Test data loaded."))
    

    def load_custom_json_scenario(self):
        """
        This function loads in custom scenarios from json files
        """
        
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            filetypes = [("JSON files", "*.json"), ("JSONL files", "*.jsonl")],
            title = "Select Scenario File"
        )

        if file:
            result, message = TestDataGenerator.load_json(file)
            if result:
                trans, rules, income = result
                self.state.transactions = trans
                self.state.budget_rules = rules

                from data_model import TotalIncome
                self.state.total_income = TotalIncome(float(income), current=float(income))
                self.display_transactions()
                self.display_budget_rules()
                self.display_summaries()
                self.display_alerts()

                self.show_success_dialog("You have successfully loaded the custom JSON scenario")
            
            else:
                self.show_error(f"Failed to load: {message}")
        
    
    def add_income(self):
        """
        This function adds total income with input validation
        """

        flag = False
        
        try:
            income_str = self.income_entry.get()

            if not income_str:
                self.show_error("Please fill in the required field")
                flag = True

            try:
                income = float(income_str)
                if income <= 0:
                    self.show_error("Invalid amount: Please enter a positive number")
                    flag = True
            except ValueError:
                self.show_error("Invalid amount: Please enter a number")
                flag = True
                
        except Exception as e:
            self.show_error(f"Error: {e}")
            flag = True

        #if no errors
        if not flag:
            self.show_success_dialog("You have successfully set your total net income")

            total = TotalIncome(income, income)
            self.state.total_income = total

            self.income_entry.delete(0, "end")   #clearing input
            self.display_budget_rules()          
            self.display_summaries()             
            

    def add_transaction(self):
        """
        This function adds a transaction with input validation
        """

        flag = False  
        
        try:
            date_str = self.date_entry.get()
            amount_str = self.amount_entry.get()
            category_str = self.category.get()
            description = self.description_entry.get()
        
            if not date_str or not amount_str or not description:
                self.show_error("Please fill in all required fields")
                flag = True
            
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                self.show_error("Invalid date format: Please use YYYY-MM-DD")
                flag = True

            try:
                amt = float(amount_str)
                if amt <= 0:
                    self.show_error("Invalid amount: Please enter a positive number")
                    flag = True
            except ValueError:
                self.show_error("Invalid amount: Please enter a number")
                flag = True

        except Exception as e:
            self.show_error(f"Error: {e}")
            flag = True

        if not flag:
            trans = Transaction(date, amt, Category(category_str), description)
            self.state.transactions.append(trans)        #adding transaction to CurrentState
            self.display_transactions(self.filter.get())
            
            #updating summaries and alerts to include new transaction
            self.display_summaries()
            self.display_alerts()
            
            self.clear_inputs()
            
        
    def show_error(self, message: str):
        """
        This function displays an error window
        """

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Error")
        dialog.geometry("400x150")

        dialog.focus()
        dialog.attributes("-topmost", True)
        ctk.CTkLabel(dialog, text=message, text_color="red", wraplength=350).pack(padx=20, pady=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

        
    def show_success_dialog(self, message:str):
        """
        This function displays a success window
        """
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Success")
        dialog.geometry("400x150")

        dialog.focus()
        dialog.attributes("-topmost", True)
        ctk.CTkLabel(dialog, text=message, wraplength=350).pack(padx=20, pady=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

    
    def clear_inputs(self):
        """
        This function clears transaction inputs
        """

        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.amount_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        self.category.set(Category.OTHER.value)


    def filter_trans(self, list, filtered_var):
        """
        This function filters the transactions based on category
        """

        filtered_list = []

        for i in list:
            if i.category.value == Category(filtered_var).value:
                filtered_list.append(i)
        
        return filtered_list
    

    def display_transactions(self, filtered_var="All"):
        """
        This function gets all transactions from CurrentState and displays them
        """

        self.transaction_box.configure(state="normal")
        self.transaction_box.delete("1.0","end")
        trans = self.state.transactions        #getting transactions from CurrentState

        if filtered_var != "All":
            trans = self.filter_trans(trans, filtered_var)

        if trans:
            for t in trans:
                text = f"[{t.date.strftime('%Y-%m-%d')}] {t.category.value}: ${t.amount:.2f} - {t.description}"
                self.transaction_box.insert("end", text + "\n")
            
        else:
            self.transaction_box.insert("0.0","No transactions found")
            
        self.transaction_box.configure(state="disabled")


    def add_budget_rules(self):
        """
        This function adds a budget rule with input validation
        """

        flag = False 
        try:
            threshold_str = self.budget_threshold.get()
            category = self.budget_category.get()
            period = self.budget_period.get()
            alert = self.budget_alert.get()

            if not threshold_str or not category or not period or not alert:
                self.show_error("Please fill in all the required fields")
                flag = True
            
            try:
                threshold = float(threshold_str)
                if threshold <= 0:
                    self.show_error("Invalid amount: Please enter a positive number")
                    flag = True

                try: 
                    #allocating total income amount to various categories for budget rules
                    current = self.state.total_income.current         #remaining income after allocation
                    if threshold > current:
                        self.show_error("Invalid amount: you do not have enough income to allocate to this rule")
                        flag = True
                    else:
                        subtract = 0

                        #ensures that if there are duplicate categories, only the largest amount in each category is subtracted from the remianing income
                        repeat_cat = [rule for rule  in self.state.budget_rules if rule .category == Category(category)]        #checking if a budget rule with the same category has been set before
                        if repeat_cat:
                            for match in repeat_cat:
                                if threshold <= match.threshold: continue
                                else:
                                    subtract += threshold - match.threshold
                        else:
                            subtract = threshold

                        self.state.total_income.current -= subtract     
                except Exception as e:
                    print(e)
                    self.show_error("Please set total net income first")
                    flag = True
            except ValueError:
                self.show_error("Invalid amount: Please enter a number")
                flag = True
        except Exception as e:
            self.show_error(f"Error: {e}")
            flag = True
        
        if not flag:

            budget = BudgetRules(threshold, Category(category), period, AlertType(alert))
            self.state.budget_rules.append(budget)
            self.display_budget_rules()
            
            #updating summaries and alerts to include new budget rule
            self.display_summaries()
            self.display_alerts()

            self.budget_threshold.delete(0, "end") #or seperate clear input function


    def display_budget_rules(self):
        """
        This function gets all budget rules from CurrentState, displays them and displays how much of the total income has not yet been allocated to the budget rules
        """

        self.budget_box.configure(state="normal")
        self.budget_box.delete("1.0","end")
        
        if self.state.total_income:
            self.budget_box.insert("end", f"Income yet to be allocated: ${self.state.total_income.current: .2f}\n")

        if self.state.budget_rules:
            for b in self.state.budget_rules:
                display = f"{b.category.value} - {b.period.upper()}: ${b.threshold: .2f} ({b.alert.value})\n"
                self.budget_box.insert("end", display)
        else:
            self.budget_box.insert("end", "No budget rules configured")
        
        self.budget_box.configure(state="disabled")

    
    def display_summaries(self):
        """
        This function gets all summaries and displays them
        """
        
        self.summary_box.configure(state = "normal")
        self.summary_box.delete("1.0", "end")

        report_lines = SummaryEngine.get_monthly_report(self.state.transactions, total_income_obj=self.state.total_income, mode="monthly")

        for line in report_lines:
            self.summary_box.insert("end", line + "\n")
        self.summary_box.configure(state = "disabled")

    
    def display_alerts(self):
        """
        This function checks for alerts and displays them
        """
        
        self.alert_box.configure(state = "normal")
        self.alert_box.delete("1.0", "end")

        income_value = 0
        if self.state.total_income:
            income_value = self.state.total_income.total

        active_alerts = AlertEngine.check_alerts(self.state.transactions, self.state.budget_rules, income_value)
        
        for alert in active_alerts:
            prefix = "⚠️" if "Warning" in alert or "Notice" in alert else "❌"
            if alert == "Safe within budget.": prefix = "✅"
            self.alert_box.insert("end", prefix + alert + "\n")
        
        self.alert_box.configure(state = "disabled")

    
    def save_all(self):
        """
        This function saves all transaction and budget rule data into json files
        """

        FileHandler.save_state(self.state)

    
    def clear_all(self):
        """
        This function clears all data from CurrentState and empties json files
        """

        FileHandler.delete_all(self.state)

        self.display_transactions()
        self.display_budget_rules()
        self.display_summaries()
        self.display_alerts()


def main():
    """
    This is the main entry point of program
    It sets the default colour scheme and initalises and calls the GUI
    """
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    main_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
