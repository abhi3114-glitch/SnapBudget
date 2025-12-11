import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date
import json

# Name of the Google Sheet to use.
# Ideally this is in secrets, but a default constant is fine for the code structure.
SHEET_NAME = "SnapBudget Expenses"

def get_client():
    """Context manager to authenticate with Google Sheets using Streamlit secrets."""
    # Based on Streamlit secrets format:
    # [gsheets]
    # service_account = { ... json content ... }
    
    # Alternatively, look for specific keys directly.
    # We will assume a 'connections' style or direct 'gcp_service_account' in secrets.
    
    try:
        # Load credentials from Streamlit secrets
        # We expect st.secrets["gcp_service_account"] to be a dictionary
        creds_dict = st.secrets["gcp_service_account"]
        
        # Define the scope
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {e}")
        st.help("Make sure you have set up `.streamlit/secrets.toml` correctly with `[gcp_service_account]`.")
        return None

def init_db():
    """
    Ensures the Google Sheet exists and has the correct headers.
    Returns the Sheet object.
    """
    client = get_client()
    if not client:
        return None

    try:
        # Try to open the sheet
        spreadsheet = client.open(SHEET_NAME)
        return spreadsheet.sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        # If not found, creating it might require higher permissions or manual creation.
        # Usually service accounts can only create sheets in their own Drive.
        # Easier workflow: User creates sheet and shares it with service account email.
        st.warning(f"Spreadsheet '{SHEET_NAME}' not found. Please create it and share it with the service account email.")
        return None
    except Exception as e:
        st.error(f"Error accessing sheet: {e}")
        return None

def ensure_headers(sheet):
    """Check if headers exist, if not, create them."""
    if not sheet:
        return
        
    try:
        # Check first row
        headers = sheet.row_values(1)
        expected_headers = ["Date", "Amount", "Raw Text", "Category"]
        
        if not headers:
            sheet.insert_row(expected_headers, 1)
        elif headers != expected_headers:
            # If different, we might just append or warn. Let's just assume it's okay for now.
            pass
    except Exception as e:
        st.error(f"Error checking headers: {e}")

def add_expense(amount, expense_date, raw_text=""):
    """Appends a new expense row to the Google Sheet."""
    sheet = init_db()
    ensure_headers(sheet)
    
    if not sheet:
        return

    if isinstance(expense_date, date):
        expense_date = expense_date.isoformat()

    # Append row
    try:
        sheet.append_row([expense_date, amount, raw_text, "Uncategorized"])
    except Exception as e:
        st.error(f"Failed to save to Google Sheets: {e}")

def get_recent_expenses(limit=10):
    """Fetches expenses from Google Sheet."""
    sheet = init_db()
    if not sheet:
        return pd.DataFrame() # Empty

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # If empty
        if df.empty:
            return pd.DataFrame(columns=["Date", "Amount", "Raw Text", "Category"])
            
        # Standardize column names strictly for internal use if needed, 
        # but here we just use what's in the sheet.
        # df keys: 'Date', 'Amount', ...
        
        # Rename to lower case for consistency with previous app logic if we want
        df.columns = [c.lower() for c in df.columns]
        
        # Sort by date usually? Or just invert index to show newest first?
        # Sheet appends to bottom, so newest is last.
        df = df.iloc[::-1].head(limit)
        
        return df
    except Exception as e:
        # If headers exist but no data, get_all_records might fail or return empty.
        st.error(f"Error reading data: {e}")
        return pd.DataFrame()

def get_monthly_total(year, month):
    """Calculates monthly total from data frame."""
    sheet = init_db()
    if not sheet:
        return 0.0
        
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            return 0.0
            
        # Ensure we have Date and Amount
        if "Date" not in df.columns or "Amount" not in df.columns:
            return 0.0

        # Filter
        # Parse Dates
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        
        # Filter by month/year
        mask = (df['Date'].dt.year == year) & (df['Date'].dt.month == month)
        monthly_df = df[mask]
        
        total = monthly_df["Amount"].sum()
        return 0.0
    except Exception as e:
        st.error(f"Error calculating total: {e}")
        return 0.0

def delete_expense(row_index):
    """Deletes a row from the Google Sheet (1-based index)."""
    sheet = init_db()
    if not sheet:
        return False
    try:
        sheet.delete_rows(row_index)
        return True
    except Exception as e:
        st.error(f"Error deleting row {row_index}: {e}")
        return False

def update_expense(row_index, date_val, amount, category, raw_text):
    """Updates a row in the Google Sheet."""
    sheet = init_db()
    if not sheet:
        return False
    try:
        # Check if date is date object
        if isinstance(date_val, date):
            date_val = date_val.isoformat()
            
        # Update the specific cells. 
        # Optimize: update_row is better if we update all columns.
        # Columns: Date, Amount, Raw Text, Category
        sheet.update(range_name=f"A{row_index}:D{row_index}", values=[[date_val, amount, raw_text, category]])
        return True
    except Exception as e:
        st.error(f"Error updating row {row_index}: {e}")
        return False

def get_all_expenses_with_id():
    """
    Fetches all expenses and returns a DataFrame WITH a 'Row Number' column.
    Useful for edit/delete operations.
    """
    sheet = init_db()
    if not sheet:
        return pd.DataFrame()

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Add 1-based Row Number (approximate, assumes get_all_records aligns with sheet rows starting at 2)
        # get_all_records uses header at row 1. Data starts at row 2.
        # df index 0 -> Sheet Row 2.
        df['row_index'] = df.index + 2 
        
        # Sort by date desc (optional, but good for UI)
        # Reorder columns
        if not df.empty:
            df = df[['row_index', 'Date', 'Amount', 'Category', 'Raw Text']]
            
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
