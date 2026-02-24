import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from google.oauth2.service_account import Credentials
import gspread

creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = gspread.authorize(creds)


SHEET_ID = "https://docs.google.com/spreadsheets/d/1moWLEIQxMImvZnaJbiwstK0bGfn50g_N5gNz0aHsIak/edit?usp=sharing"  # replace with your Google Sheet ID

def get_data(sheet_name: str) -> pd.DataFrame:
    worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def save_data(sheet_name: str, df: pd.DataFrame):
    worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- BUG LIST Section ---
if selected_sheet == "BUG LIST":
    df_bug = get_data("BUG LIST")

    st.title("🐞 Bug Tracking Dashboard – BUG LIST")

    # Filters
    test_filter = st.multiselect("Filter by Test", df_bug["TEST"].dropna().unique())
    bug_filter = st.multiselect("Filter by Bug", df_bug["BUG"].dropna().unique())
    device_filter = st.multiselect("Filter by Device", df_bug["DEVICE"].dropna().unique())
    version_filter = st.multiselect("Filter by Version", df_bug["VERSION"].dropna().unique())
    status_filter = st.multiselect("Filter by Status", df_bug["STATUS"].dropna().unique())

    filtered_df_bug = df_bug.copy()
    if test_filter:
        filtered_df_bug = filtered_df_bug[filtered_df_bug["TEST"].isin(test_filter)]
    if bug_filter:
        filtered_df_bug = filtered_df_bug[filtered_df_bug["BUG"].isin(bug_filter)]
    if device_filter:
        filtered_df_bug = filtered_df_bug[filtered_df_bug["DEVICE"].isin(device_filter)]
    if version_filter:
        filtered_df_bug = filtered_df_bug[filtered_df_bug["VERSION"].isin(version_filter)]
    if status_filter:
        filtered_df_bug = filtered_df_bug[filtered_df_bug["STATUS"].isin(status_filter)]

    with st.form("edit_form_bug"):
        edited_df_bug = st.data_editor(
            filtered_df_bug,
            num_rows="dynamic",
            height=500,
            column_config={
                "STATUS": st.column_config.SelectboxColumn(
                    "Status",
                    options=["NOT VERIFIED", "IN PROGRESS", "VERIFIED", "CLOSED"],
                    width="medium"
                )
            }
        )

        save_bug = st.form_submit_button("💾 Save BUG LIST Updates")
        if save_bug:
            rows_to_add = []

            # Compare edited vs original to find new rows
            new_rows = edited_df_bug.merge(
                df_bug[["BUG", "DEVICE", "VERSION"]],
                on=["BUG", "DEVICE", "VERSION"],
                how="left",
                indicator=True
            )
            new_rows = new_rows[new_rows["_merge"] == "left_only"]

            for _, row in new_rows.iterrows():
                new_bug = row["BUG"]
                new_test = row["TEST"]
                new_device = row["DEVICE"]
                new_version = row["VERSION"]

                # 1. If this bug is new → pair with all existing devices/versions
                if new_bug not in df_bug["BUG"].values:
                    for dev in df_bug["DEVICE"].dropna().unique():
                        for ver in df_bug["VERSION"].dropna().unique():
                            exists = ((edited_df_bug["BUG"] == new_bug) &
                                      (edited_df_bug["DEVICE"] == dev) &
                                      (edited_df_bug["VERSION"] == ver)).any()
                            if not exists:
                                rows_to_add.append({
                                    "TEST": new_test,
                                    "BUG": new_bug,
                                    "DEVICE": dev,
                                    "VERSION": ver,
                                    "STATUS": "NOT VERIFIED"
                                })

                # 2. If this device is new → pair with all existing bugs
                if new_device not in df_bug["DEVICE"].values:
                    for bug in df_bug["BUG"].dropna().unique():
                        exists = ((edited_df_bug["BUG"] == bug) &
                                  (edited_df_bug["DEVICE"] == new_device) &
                                  (edited_df_bug["VERSION"] == new_version)).any()
                        if not exists:
                            test_value = df_bug.loc[df_bug["BUG"] == bug, "TEST"].iloc[0]
                            rows_to_add.append({
                                "TEST": test_value,
                                "BUG": bug,
                                "DEVICE": new_device,
                                "VERSION": new_version,
                                "STATUS": "NOT VERIFIED"
                            })

                # 3. If this version is new → pair with all existing bugs
                if new_version not in df_bug["VERSION"].values:
                    for bug in df_bug["BUG"].dropna().unique():
                        exists = ((edited_df_bug["BUG"] == bug) &
                                  (edited_df_bug["DEVICE"] == new_device) &
                                  (edited_df_bug["VERSION"] == new_version)).any()
                        if not exists:
                            test_value = df_bug.loc[df_bug["BUG"] == bug, "TEST"].iloc[0]
                            rows_to_add.append({
                                "TEST": test_value,
                                "BUG": bug,
                                "DEVICE": new_device,
                                "VERSION": new_version,
                                "STATUS": "NOT VERIFIED"
                            })

            if rows_to_add:
                edited_df_bug = pd.concat([edited_df_bug, pd.DataFrame(rows_to_add)], ignore_index=True)

            # --- Save back to Google Sheets ---
            save_data("BUG LIST", edited_df_bug)

            st.success("✅ BUG LIST updated in Google Sheets")


