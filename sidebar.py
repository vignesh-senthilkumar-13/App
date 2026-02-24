import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

# Your sheet ID
SHEET_ID = "1moWLEIQxMImvZnaJbiwstK0bGfn50g_N5gNz0aHsIak"

# Pick a worksheet (tab) name
WORKSHEET_NAME = "BUG LIST"

st.title("🔧 Google Sheets Test")

# Read data
worksheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.subheader("📊 Current Data")
st.write(df)

# Append a test row
new_row = ["TEST-ROW", "BUG-123", "DeviceX", "v1.0", "NOT VERIFIED"]
worksheet.append_row(new_row)

st.success("✅ Added a test row to Google Sheets!")

# Show updated data
updated_data = worksheet.get_all_records()
updated_df = pd.DataFrame(updated_data)

st.subheader("📊 Updated Data")
st.write(updated_df)
