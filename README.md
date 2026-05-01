# Simple Budgeting Tool - B09

## Description

## Installation Instructions
To run this application, you need Python 3.7+

1. Clone the repository
   git clone https://github.com/your-username/budgeting-tool.git
   cd budgeting-tool
2. Install Dependencies
   The application uses customtkinter
   pip install customtkinter

## Execution Instructions
Once the dependencies are installed, you can launch the application by running the main.py script:
python main.py

### How to Use
1. Set Income: Start by navigating to the "Set Income" tab to define your monthly budget.
2. Define Rules: Create "Envelopes" in the Budgeting Rules tab (e.g., $500 for "Meals" Monthly).
3. Log Transactions: Add your daily expenses in the Transaction tab.
4. Monitor: Check the Dashboard for a generated summary and any active alerts or spending spikes.

## Project Structure
main.py: The entry point and GUI controller.

data_model.py: Core data structures (Transactions, Rules, Categories).

summaries.py: Logic for calculating spending reports and averages.

alerts.py: Detection engine for budget breaches and spending anomalies.

file_handling.py: Manages saving/loading to JSON files.

test_data_generator.py: Tool for generating sample data for testing purposes.

## Troubleshooting
ModuleNotFoundError: If you see an error regarding customtkinter, ensure you ran pip install customtkinter in the correct Python environment.



