import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Fix private key formatting
secrets = dict(st.secrets["gcp_service_account"])
secrets["private_key"] = secrets["private_key"].replace("\\n", "\n")

creds = Credentials.from_service_account_info(secrets, scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "1moWLEIQxMImvZnaJbiwstK0bGfn50g_N5gNz0aHsIak"
WORKSHEET_NAME = "BUG LIST"

worksheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
print("✅ Connected to Google Sheets!")
print(worksheet.get_all_records()[:5])
