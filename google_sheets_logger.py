import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
import time # Import the time module for delays

# --- Google Sheets Configuration ---

# Define the scope for Google Sheets and Drive APIs
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]

# It's best practice to load credentials from environment variables in a production system.
# For AWS Lambda, you can store the JSON key file content in an environment variable.
SERVICE_ACCOUNT_INFO_JSON = os.environ.get('GOOGLE_SERVICE_ACCOUNT_INFO')

if SERVICE_ACCOUNT_INFO_JSON:
    SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_INFO_JSON)
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
else:
    # Fallback for local development (place your service_account.json in the same directory)
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = gspread.authorize(creds)

# The ID of your Google Sheet (from the URL)
SPREADSHEET_ID = '1LtB6duYIV7FpTvFKZfmQtVM1vMxGkzoxydxf20Nc3dQ' # <-- IMPORTANT: Replace with your actual Sheet ID

def log_to_google_sheet(doc_type, contact, tax_year, tax_file_id, status, data_payload):
    """
    Appends a new row with execution details to a specified Google Sheet.
    Includes a retry mechanism for transient errors.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            sheet = client.open_by_key(SPREADSHEET_ID).sheet1

            # Prepare the row data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Convert data payload (list or dict) to a string for logging
            data_str = json.dumps(data_payload) if isinstance(data_payload, (dict, list)) else str(data_payload)

            row = [timestamp, doc_type, contact, tax_year, tax_file_id, status, data_str]
            
            sheet.append_row(row)
            print("Successfully logged data to Google Sheet.")
            return True # Success, exit the function

        except gspread.exceptions.APIError as e:
            # Specifically check for 5xx server errors which are good candidates for a retry
            if e.response.status_code >= 500 and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2 # Wait 2, 4 seconds
                print(f"Warning: Google Sheet API error (Attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error: Failed to log data to Google Sheet after {max_retries} attempts: {e}")
                return False # Final failure
        except Exception as e:
            print(f"Error: An unexpected error occurred while logging to Google Sheet: {e}")
            return False # Non-retryable error
    return False # Should not be reached, but as a fallback