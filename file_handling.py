import json
import os
from typing import List, Tuple
from datetime import datetime
from data_model import Transaction, BudgetRules, CurrentState, TotalIncome

class FileHandler:
    """
    This class handles all file I/O
    """
    
    TRANSACTIONS = "transactions.json"
    BUDGET_RULES = "budget_rules.json"
    TOTAL = "total_income.json"

    @staticmethod
    def load_trans() -> Tuple[List[Transaction], List[str]]:
        """
        This method reads transactions.json and returns a list of Transaction objects and error messages
        """
        errors = []
        try:
            if not os.path.isfile(FileHandler.TRANSACTIONS):
                return [], []
            
            with open(FileHandler.TRANSACTIONS, 'r') as f:
                content = f.read().strip()
                if not content:
                    return [], [] 
                
                data = json.loads(content)
                trans = []
                for index, i in enumerate(data):
                    try:
                        #validate data that does not automatically raise error
                        amt_flag = i["amount"] <= 0
                        dsc_flag = i["description"] == ""
                        
                        if amt_flag or dsc_flag:
                            if amt_flag:
                                errors.append(f"Transaction {index+1}: Amount is not a positive number")
                            if dsc_flag:
                                errors.append(f"Transaction {index+1}: Description is empty")
                        else:
                            trans.append(Transaction.fromDict(i))
                            
                    except Exception as e:
                        errors.append(f"Transaction {index+1}: {str(e)}")
                        continue
                return trans, errors
                
        except json.JSONDecodeError as e:
            errors.append(f"Malformed transactions file: {str(e)}")
            return [], errors
        except Exception as e:
            errors.append(f"Error loading transactions: {str(e)}")
            return [], errors

    @staticmethod    
    def save_trans(trans: List[Transaction]) -> bool:
        """
        This method saves transactions to transactions.json
        """
        
        try:
            data = [t.toDict() for t in trans]
            with open(FileHandler.TRANSACTIONS, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False
        
    @staticmethod    
    def load_budget_rules(totalincome: TotalIncome) -> Tuple[List[BudgetRules], List[str], int]:
        """
        This method reads budget_rules.json and returns a list of BudgetRules objects, error messages and income not allocated to budget rules as an integer
        This method will manually calculate the remaining income using the total income and budget rule thresholds
        """

        errors = []

        
        try:
            if not os.path.isfile(FileHandler.BUDGET_RULES):
                return [], [], 0
            
            with open(FileHandler.BUDGET_RULES, 'r') as f:
                content = f.read().strip()
                if not content:
                    return [], [], 0
                
                data = json.loads(content) 
                if not data:
                    return [], [], 0
                
                if totalincome:
                    current = totalincome.total     #get total income 
                else:
                    errors.append("Error loading budget rule: Total income not yet set")
                    return [], errors, 0
                
                data = json.loads(content)
                budget = []
                for index, i in enumerate(data):
                    try:
                        #validate data that does not automatically raise error
                        period_str = ["Daily", "Weekly", "Monthly"]
                        thr_flag = i["threshold"] <= 0
                        period_flag = i["period"] not in period_str
                        
                        
                        total_flag = i["threshold"] > current        #check if threshold exceeds remaining income

                        if thr_flag or period_flag or total_flag:
                            if thr_flag:
                                errors.append(f"Budget rule {index+1}: Threshold is not a positive number")
                            if period_flag:
                                errors.append(f"Budget rule {index+1}: Period is not valid")
                            if total_flag:
                                errors.append(f"Budget rules threshold exceeds total income. Budget rules after {index+1} will be ignored")
                        else:
                            subtract = 0
                            
                            # Ensures that if there are duplicate categories, only the largest amount in each category is subtracted from the remaining income
                            from data_model import Category
                            repeat_cat = [rule for rule in budget if rule.category == Category(i['category'])]
                            if repeat_cat:
                                for match in repeat_cat:
                                    if i["threshold"] <= match.threshold:
                                        continue
                                    else:
                                        subtract += i["threshold"] - match.threshold
                            else:
                                subtract = i["threshold"]
                            
                            current -= subtract
                            budget.append(BudgetRules.fromDict(i))
        
                    except Exception as e:
                        errors.append(f"Budget rule {index+1}: {str(e)}")
                        continue
                return budget, errors, current
                
        except json.JSONDecodeError as e:
            errors.append(f"Malformed budget rules file: {str(e)}")
            return [], errors, current
        except Exception as e:
            errors.append(f"Error loading budget rules: {str(e)}")
            return [], errors, current

    @staticmethod    
    def save_budget_rules(rules: List[BudgetRules]) -> bool:
        """
        This method saves budget rules to budget_rules.json
        """
        
        try:
            data = [r.toDict() for r in rules]
            with open(FileHandler.BUDGET_RULES, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    @staticmethod   
    def load_total() -> Tuple[TotalIncome, List[str]]:
        """
        This method reads total.json and a TotalIncome object and error messages
        Income not allocated to budget rule thresholds is manually calculated in load_budget_rules, therefore the value of data["current"] is unimportant
        """
        
        errors = []
        try:
            if not os.path.isfile(FileHandler.TOTAL):
                return None, []
            
            with open(FileHandler.TOTAL, 'r') as f:
                content = f.read().strip()
                if not content:
                    return None, []
                
                data = json.loads(content) 
                if not data:
                    return None, []
                
                try:
                    total = TotalIncome(data["total"], data["current"])
                    if total.total <= 0 or total.current <= 0:
                        errors.append("Total income is not a positive number")
                    return total, []
                except Exception as e:
                    errors.append(f"Error loading total income: {e}")

        except json.JSONDecodeError as e:
            errors.append(f"Malformed total income file: {str(e)}")

        except Exception as e:
            errors.append(f"Error loading total income: {str(e)}")
            
        return None, errors

    
    @staticmethod   
    def save_total(total: TotalIncome) -> bool:
        """
        This method saves total income and income not yet allocated to budget rules to total.json
        """
        
        try:
            data = total.toDict()
            with open(FileHandler.TOTAL, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(e)
            return False


    @staticmethod    
    def load_state() -> Tuple[CurrentState, List[str]]:
        """
        This method returns all errors and a CurrentState object with all transactions, budget rules and income
        """
        
        total, to_errors = FileHandler.load_total()
        trans, tr_errors = FileHandler.load_trans()
        rules, r_errors, current = FileHandler.load_budget_rules(total)

        if total:
            total = TotalIncome(total.total, current)   #creating a new TotalIncome object with total extracted in load_total and current calculated in load_budget_rules 

        return CurrentState(
            total_income = total,   
            transactions = trans, 
            budget_rules = rules
        ), to_errors+tr_errors+r_errors
    

    @staticmethod
    def save_state(state: CurrentState) -> Tuple[bool, str]:
        """
        This method saves all transactions, budget rules and income to their respective json files
        """
        
        total_save = FileHandler.save_total(state.total_income)
        trans_save = FileHandler.save_trans(state.transactions)
        budget_save = FileHandler.save_budget_rules(state.budget_rules)

        if total_save and trans_save and budget_save:
            return True, "Data saved succesfully"
        else:
            return False, "Error: data not saved"
        
    
    @staticmethod
    def delete_all(state: CurrentState):
        """
        This method clears CurrentState and empties json files
        """
        
        state.transactions.clear()
        state.budget_rules.clear()
        state.total_income = None

        with open(FileHandler.TOTAL, 'w') as f:
            json.dump({}, f)

        with open(FileHandler.TRANSACTIONS, 'w') as f:
            json.dump([], f)

        with open(FileHandler.BUDGET_RULES, 'w') as f:
            json.dump([], f)
        
