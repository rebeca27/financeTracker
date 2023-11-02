import pickle
import json
from datetime import datetime


# Base Transaction Class
class Transaction:
    def __init__(self, category, amount, date, receipt = None):
        self.category = category
        self.amount = amount
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.receipt = Receipt(receipt) if receipt else None


    def display(self):
        return f"{self.date.strftime('%Y-%m-%d')} | {self.category} | ${self.amount}"


class Income(Transaction):
    def display(self):
        return f"{self.date.strftime('%Y-%m-%d')} | Income | {self.category} | +${self.amount}"


class Expense(Transaction):
    def display(self):
        return f"{self.date.strftime('%Y-%m-%d')} | Expense | {self.category} | -${self.amount}"


class Budget:
    def __init__(self, monthly_budget):
        self.monthly_budget = monthly_budget

    def remaining_budget(self, transactions):
        total_expense = sum([t.amount for t in transactions if isinstance(t, Expense)])
        return self.monthly_budget - total_expense


class SavingGoal:
    def __init__(self, goal_name, goal_amount, deadline_date):
        self.goal_name = goal_name
        self.goal_amount = goal_amount
        self.deadline_date = datetime.strptime(deadline_date, '%Y-%m-%d')
        self.saved_amount = 0

    def add_savings(self, amount):
        self.saved_amount += amount

    def amount_remaining(self):
        return self.goal_amount - self.saved_amount

    def display(self):
        return f"{self.goal_name} - Goal: ${self.goal_amount}, Saved: ${self.saved_amount}, Remaining: ${self.amount_remaining()}, Deadline: {self.deadline_date.strftime('%Y-%m-%d')}"

class Receipt:
    def __init__(self, image_path):
        with open(image_path, "rb") as file:
            self.image_data = bytearray(file.read())
    def save_image(self, output_path):
        with open(output_path, "wb") as file:
            file.write(self.image_data)

class FinanceTracker:
    def __init__(self, monthly_budget):
        self.transactions = []
        self.budget = Budget(monthly_budget)
        self.saving_goals = []  # new attribute for saving goals


    @classmethod
    def restore_from_binary(cls, filename="backup.bin"):
        with open(filename, "rb") as file:
            restored = pickle.load(file)
            return restored
    def backup_to_binary(self, filename = "backup.bin"):
        with open(filename, "wb") as file:
            pickle.dump(self,file)


    def backup_to_txt(self, filename="backup.txt"):
        with open(filename, "w") as file:
            # Write monthly budget
            file.write(f"{self.budget.monthly_budget}\n")
            file.write("---\n")

            # Write transactions
            for t in self.transactions:
                type_str = 'Income' if isinstance(t, Income) else 'Expense'
                file.write(f"{type_str} | {t.category} | {t.amount} | {t.date.strftime('%Y-%m-%d')}\n")

            file.write("---\n")

            # Write saving goals
            for goal in self.saving_goals:
                file.write(f"{goal.goal_name} | {goal.goal_amount} | {goal.deadline_date.strftime('%Y-%m-%d')} | {goal.saved_amount}\n")

    @classmethod
    def restore_from_txt(cls, filename="backup.txt"):
         with open(filename, "r") as file:
            lines = file.readlines()

            monthly_budget = float(lines[0].strip())
            restored_finance = cls(monthly_budget)
            for line in lines[2:-2]: 
                parts = line.strip().split(" | ")
                if len(parts) == 4:  
                    type_str, category, amount, date = parts
                    restored_finance.add_transaction(type_str, category, float(amount), date)
                else:
                    break  
                
            for line in lines[lines.index("---\n") + 1:]:
                goal_name, goal_amount, deadline_date, saved_amount = line.strip().split(" | ")
                goal = SavingGoal(goal_name, float(goal_amount), deadline_date)
                goal.saved_amount = float(saved_amount)
                restored_finance.saving_goals.append(goal)

            return restored_finance


    def add_transaction(self, type, category, amount, date, receipt = None):
        transaction = Income(category, amount, date, receipt) if type == 'Income' else Expense(category, amount, date, receipt)
        self.transactions.append(transaction)

    def view_transactions(self):
        for t in self.transactions:
            print(t.display())

    def view_remaining_budget(self):
        print(f"Remaining Budget: ${self.budget.remaining_budget(self.transactions)}")

    def give_recommendations(self):
        total_income = sum([t.amount for t in self.transactions if isinstance(t, Income)])
        total_expense = sum([t.amount for t in self.transactions if isinstance(t, Expense)])

        if total_expense > total_income:
            print("Warning: Your expenses are higher than your income!")
        if self.budget.remaining_budget(self.transactions) < 0:
            print("You have exceeded your monthly budget!")

    def add_saving_goal(self, goal_name, goal_amount, deadline_date):

        goal = SavingGoal(goal_name, goal_amount, deadline_date)
        self.saving_goals.append(goal)


    def view_saving_goals(self):
        for goal in self.saving_goals:
            print(goal.display())

    def add_to_saving_goal(self, goal_name, amount):
        # Find the goal by its name
        for goal in self.saving_goals:
            if goal.goal_name == goal_name:
                goal.add_savings(amount)
                return  # Exit the method once the goal is found and updated
        print(f"Goal named '{goal_name}' not found.")  # Print a message if the goal was not found
# Example Usage
finance = FinanceTracker(5000)
finance.add_transaction('Income', 'Salary', 3000, '2023-10-10')
finance.add_transaction('Expense', 'Groceries', 150, '2023-10-11')
finance.add_transaction('Expense', 'Rent', 1000, '2023-10-01')

print("Transactions:")
finance.view_transactions()
print()

print("Financial Insights:")
finance.give_recommendations()
print()

print("Budget Information:")
finance.view_remaining_budget()
print()

# Saving goals example usage
finance.add_saving_goal("New Car", 20000, '2024-12-31')
finance.add_saving_goal("Vacation to Bali", 5000, '2023-12-15')
print("Saving Goals:")
finance.view_saving_goals()

finance.add_to_saving_goal("New Car", 500)

print("Saving Goals:")
finance.view_saving_goals()

cheltuiala_chitanta = Expense('cina', 50, '2023-12-31', receipt= "image_chitanta.jpg")
finance.transactions.append(cheltuiala_chitanta)
if hasattr(cheltuiala_chitanta, 'receipt') and cheltuiala_chitanta.receipt:
    cheltuiala_chitanta.receipt.save_image("imagine.jpg")
finance.backup_to_binary("backup_finance.bin")
finance.backup_to_txt("backup_finance.txt")
finance_restaurant_binary = FinanceTracker.restore_from_binary("backup_finance.bin")
finance_restaurant_txt = FinanceTracker.restore_from_txt("backup_finance.txt")