# Simple Budgeting Tool - B09

## Description
This application is a simple budgeting tool that utilises envelope budgeting. By allowing users to allocate their income to specific categories, this tool provides a clear, managable way for users to track their expenses and monitor their financial health through automated summaries and alerts. Moreover, this tool incorporates flexibility in budgeting periods (Daily/Weekly/Monthly) which ensures the tool adapts to individual financial habits.

## Installation Instructions
To run this application, you need Python 3.7+

1. In your terminal (Command Prompt, Terminal, Git Bash) clone the repository
   
   ```git clone https://github.com/tarrynlin/Budget1110-B09```
   
   ```cd Budget1110-B09```

   Alternatively, you can select **Download ZIP** in GitHub or download from moodle.
3. In your terminal install dependencies
   
   The application uses customtkinter
   
   ```pip install customtkinter```

## Execution Instructions
Once the dependencies are installed, you can launch the application by running the main.py script:

```python main.py```

Alternatively, you can run it in your IDE

### How to Use
1. Set Income: Start by navigating to the "Set Income" tab to define your monthly budget.
2. Define Rules: Create "Envelopes" in the Budgeting Rules tab (e.g., $500 for "Meals" Monthly).
3. Log Transactions: Add your daily expenses in the Transaction tab.
4. Monitor: Check the Dashboard for a generated summary and any active alerts or spending spikes.
5. Loading Test Scenarios: Navigate to the **Test Data** tab and select **Load Custom JSON Scenario**. Select one of the pre-made JSON scenario files within this repository.

## Project Structure
```main.py```: The entry point and GUI controller.

```data_model.py```: Core data structures (Transactions, Rules, Categories).

```summaries.py```: Logic for calculating spending reports and averages.

```alerts.py```: Detection engine for budget breaches and spending anomalies.

```file_handling.py```: Manages saving/loading to JSON files.

```test_data_generator.py```: Tool for generating sample data for testing purposes.

## Troubleshooting
ModuleNotFoundError: If you see an error regarding customtkinter, ensure you ran ```pip install customtkinter``` in the correct Python environment. 

ModuleNotFoundError: if you see an error regarding tkinter, you may need to reinstall Python from Python.org and ensure "tcl/tk and IDLE" is checked during the custom installation

If using an IDE, ensure you have selected the correct interpreter where you ran your ```pip install``` command

If using a virtual environment, ensure that the environment is active while you install customtkinter



