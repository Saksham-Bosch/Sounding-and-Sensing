import ast
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

# Define the path to the root data/local directory
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "local"
DB_FILE = DATA_DIR / "mock_database.xlsx"

# The required sheets as defined in the handover brief
SHEETS = [
    "Events", "StandardQuestions", "StandardAnswers", 
    "Questionnaires", "GeneratedQuestions", "InterviewSessions", 
    "InterviewAnswers", "Assets", "ProcessingJobs"
]

class ExcelDatabase:
    def __init__(self):
        self._initialize_db()

    def _initialize_db(self):
        """Creates the Excel file with all required sheets if it doesn't exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DB_FILE.exists():
            with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
                for sheet in SHEETS:
                    pd.DataFrame().to_excel(writer, sheet_name=sheet, index=False)

    def save_record(self, sheet_name: str, record_dict: dict):
        """Appends a single dictionary record to the specified sheet."""
        df = pd.read_excel(DB_FILE, sheet_name=sheet_name)
        
        # Convert datetime objects to strings for Excel compatibility
        for key, value in record_dict.items():
            if isinstance(value, datetime):
                record_dict[key] = value.isoformat()
                
        new_row = pd.DataFrame([record_dict])
        df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
        
        with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    def get_all_records(self, sheet_name: str) -> list[dict]:
        """Retrieves all records from a specific sheet as a list of dictionaries."""
        df = pd.read_excel(DB_FILE, sheet_name=sheet_name)

        # Replace NaN/NaT with None so FastAPI can serialize it to JSON
        df = df.replace({pd.NA: None, float("nan"): None})
        df = df.where(pd.notnull(df), None)

        return df.to_dict(orient='records')

    def _restore_excel_record(self, record: dict) -> dict:
        restored_record = {}
        for key, value in record.items():
            if isinstance(value, str):
                try:
                    restored_record[key] = ast.literal_eval(value)
                    continue
                except (ValueError, SyntaxError):
                    pass
            restored_record[key] = value
        return restored_record
