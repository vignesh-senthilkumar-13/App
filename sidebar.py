import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import requests
# import plotly.express as px
GITHUB_URL = "https://raw.githubusercontent.com/vignesh-senthilkumar-13/App/main/Device_Management.xlsx"
LOCAL_FILE = r"C:\Users\vigneshs1\Desktop\Device_Management.xlsx"
st.set_page_config(page_title="Board Shipment Tracker", layout="wide")
st_autorefresh(interval=30000)

excel_file = "Test.xlsx"
from github import Github
import streamlit as st

from github import Github
import streamlit as st

def commit_to_github(repo_name, file_path, commit_message, branch="main"):
    token = st.secrets["GITHUB_TOKEN"]
    g = Github(token)
    repo = g.get_repo(repo_name)

    # Read local file content
    with open(file_path, "rb") as f:
        content = f.read()

    # IMPORTANT: use repo-relative path, not local path
    repo_file_path = "Device_Management.xlsx"  # adjust if inside a folder

    file = repo.get_contents(repo_file_path, ref=branch)
    repo.update_file(
        path=file.path,
        message=commit_message,
        content=content,
        sha=file.sha,
        branch=branch
    )
    st.success("✅ Changes committed to GitHub")

def get_data(sheet: str) -> pd.DataFrame:
    df = pd.read_excel(excel_file, sheet_name=sheet)
    if "DATE" in df.columns:
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    return df
# sidebar_options = [ "Shipment Tracker", "Board Status Editor", "Board Status Dashboard", "Consolidated Dashboard" ]
# --- Sidebar: choose sheet ---
st.sidebar.title("📑 Choose Sheet")
sheet_names = pd.ExcelFile(excel_file).sheet_names
# Define your own custom sidebar options
sidebar_options = [
"Dashboard",
    "Shipment Tracker",
    "Board Status Editor",
"BUG LIST"
]

# Show custom names in the sidebar
selected_display = st.sidebar.selectbox("Select a view", sidebar_options)

# Map custom names back to actual sheet names
if selected_display == "Dashboard":
    selected_sheet = "DASHBOARD"
elif selected_display == "Shipment Tracker":
    selected_sheet = "BOARDS"
elif selected_display == "Board Status Editor":
    selected_sheet = "BOARD STATUS"
elif selected_display == "BUG LIST":
    selected_sheet = "BUG LIST"

# --- First sheet: full tracker with deadlines ---
st.title("📊 Dashboard" )

if selected_sheet == "DASHBOARD":
    col1, col2, col3 = st.columns((1, 1.5, 1))
    with col1:
        df3 = get_data("BOARD STATUS")
        df3 = df3.reset_index(drop=True)
        # Ensure DATE column is datetime
        if "DATE" in df3.columns:
            df3["DATE"] = pd.to_datetime(df3["DATE"], errors="coerce")

        st.title("BOARD STATUS")

        # --- Upcoming deadlines section ---
        st.subheader("⚠️ Upcoming Deadlines (within 7 days)")
        today = datetime.today().date()
        upcoming = df3[df3["DATE"].dt.date <= today + timedelta(days=7)]

        if not upcoming.empty:
            st.metric("Entries Due Soon", len(upcoming))
            upcoming_display = upcoming.copy()
            st.table(upcoming_display[["Device", "Version", "Status", "DATE"]])
        else:
            st.info("No upcoming deadlines within 7 days.")
    with col2:
        df1 = get_data("BOARDS")
        df1 = df1.reset_index(drop=True)
        # Ensure DATE column is datetime
        if "DATE" in df1.columns:
            df1["DATE"] = pd.to_datetime(df1["DATE"], errors="coerce")

        st.title("📦 Board Shipment Tracker")

        # --- Upcoming deadlines section ---
        st.subheader("⚠️ Upcoming Deadlines (within 7 days)")
        today = datetime.today().date()
        upcoming_boards = df1[df1["DATE"].dt.date <= today + timedelta(days=7)]

        if not upcoming_boards.empty:
            st.metric("Shipments Due Soon", len(upcoming_boards))
            upcoming_display = upcoming_boards.copy()
            upcoming_display["Quantity"] = upcoming_display["Quantity"].fillna(0).astype(int)
            st.table(
                upcoming_display[["Product", "Boards", "Remaining Boards to send", "Sent from", "DATE", "Quantity"]])
        else:
            st.info("No upcoming shipments within 7 days.")
    with col3:
        st.title("🐞 Bugs Pending Verification")

        # --- Load BUG LIST ---
        df_bug = get_data("BUG LIST")

        if "STATUS" in df_bug.columns:
            # Filter only NOT VERIFIED entries
            not_verified_df = df_bug[df_bug["STATUS"] == "NOT VERIFIED"]


            # Device filter
            device_filter = st.multiselect("Filter by Device", df_bug["DEVICE"].dropna().unique())

            filtered_not_verified = not_verified_df.copy()
            if device_filter:
                filtered_not_verified = filtered_not_verified[filtered_not_verified["DEVICE"].isin(device_filter)]

            if not filtered_not_verified.empty:
                st.metric("Total NOT VERIFIED Bugs", len(filtered_not_verified))
                st.dataframe(
                    filtered_not_verified[["DEVICE", "TEST", "BUG", "VERSION"]],
                    height=400
                )
            else:
                st.info("No bugs are currently marked as NOT VERIFIED for the selected device(s).")


    # Assuming df3 is your BOARD STATUS DataFrame
    import streamlit as st
    import pandas as pd
    
    # Load BOARD STATUS data from Excel
    df3 = get_data("BOARD STATUS")
    df3 = df3.reset_index(drop=True)
    
    # Ensure DATE column is datetime
    if "DATE" in df3.columns:
        df3["DATE"] = pd.to_datetime(df3["DATE"], errors="coerce")
    
    st.title("BOARD STATUS – Stage Flow")
    
    # Define ordered workflow stages
    status_stages = [
        "PCB INPUTS", "SCH DESIGN", "SCH REVIEW", "PCB-RELEASE",
        "QUOTATION-RECEIVED", "QUOTATION-APPROVED",
        "UNDER FAB", "BOARDS RECEIVED"
    ]
    
    # Clean up Status column (strip spaces, ensure string type)
    df3["Status"] = df3["Status"].astype(str).str.strip()
    
    # Loop through each Device–Version pair
    for (device, version), group in df3.groupby(["Device", "Version"]):
        st.subheader(f"Device {device} – Version {version}")
    
        # Find the latest status for this pair
        if not group.empty:
            current_status = group.sort_values("DATE")["Status"].iloc[-1]
        else:
            current_status = status_stages[0]  # default to first stage
    
        # Ensure current_status is valid
        if current_status not in status_stages:
            current_status = status_stages[0]
    
        # Stage slider
        stage = st.select_slider(
            f"Progression for Device {device}, Version {version}",
            options=status_stages,
            value=current_status,
            key=f"slider_{device}_{version}"
        )
    
        # Display the selected stage
        st.write(f"➡️ Current Stage: **{stage}**")
        # Stage slider (unchanged)


        # --- NEW: Show full timeline with all stage names ---
        current_index = status_stages.index(stage)
        timeline = []
        for i, s in enumerate(status_stages):
            if i < current_index:
                timeline.append(f"<span style='color:green'>✔ {s}</span>")
            elif i == current_index:
                timeline.append(f"<span style='color:blue'><b>➡ {s}</b></span>")
            else:
                timeline.append(f"<span style='color:gray'>○ {s}</span>")
        
        st.markdown(" → ".join(timeline), unsafe_allow_html=True)

  #-------------------------------------------------------------------------  
    import streamlit as st
    import pandas as pd
    
    # Load BOARD STATUS data from Excel
    df3 = get_data("BOARD STATUS")
    df3 = df3.reset_index(drop=True)
    
    # Ensure DATE column is datetime
    if "DATE" in df3.columns:
        df3["DATE"] = pd.to_datetime(df3["DATE"], errors="coerce")
    
    st.title("BOARD STATUS – Stage Flow")
    
    # Define ordered workflow stages
    status_stages = [
        "PCB INPUTS", "SCH DESIGN", "SCH REVIEW", "PCB-RELEASE",
        "QUOTATION-RECEIVED", "QUOTATION-APPROVED",
        "UNDER FAB", "BOARDS RECEIVED"
    ]
    
    # Clean up Status column
    df3["Status"] = df3["Status"].astype(str).str.strip()
    
    # Loop through each Device–Version pair
    for (device, version), group in df3.groupby(["Device", "Version"]):
        st.subheader(f"Device {device} – Version {version}")
    
        # Find the latest status for this pair
        if not group.empty:
            current_status = group.sort_values("DATE")["Status"].iloc[-1]
        else:
            current_status = status_stages[0]
    
        # Ensure current_status is valid
        if current_status not in status_stages:
            current_status = status_stages[0]
    
        # Build stage flow with color coding
        current_index = status_stages.index(current_status)
        stage_flow = []
        for i, s in enumerate(status_stages):
            if i < current_index:
                stage_flow.append(f"<span style='color:green'>✔ {s}</span>")
            elif i == current_index:
                stage_flow.append(f"<span style='color:blue'><b>➡ {s}</b></span>")
            else:
                stage_flow.append(f"<span style='color:gray'>○ {s}</span>")
    
        # Render inline with arrows
        st.markdown(" → ".join(stage_flow), unsafe_allow_html=True)

    

elif selected_sheet == "BOARD STATUS":
    df3 = get_data("BOARD STATUS")

    # Ensure DATE column is datetime
    if "DATE" in df3.columns:
        df3["DATE"] = pd.to_datetime(df3["DATE"], errors="coerce")

    st.title("📊 Dashboard – BOARD STATUS")

    # Filters
    device_filter = st.multiselect("Filter by Device", df3["Device"].dropna().unique())
    version_filter = st.multiselect("Filter by Version", df3["Version"].dropna().unique())
    status_filter = st.multiselect("Filter by Status", df3["Status"].dropna().unique())

    # Date filter (range)
    # date_range = st.date_input("Filter by Date Range", [])
    filtered_df3 = df3.copy()

    if device_filter:
        filtered_df3 = filtered_df3[filtered_df3["Device"].isin(device_filter)]
    if version_filter:
        filtered_df3 = filtered_df3[filtered_df3["Version"].isin(version_filter)]
    if status_filter:
        filtered_df3 = filtered_df3[filtered_df3["Status"].isin(status_filter)]
    # if date_range:
    #     if len(date_range) == 2:  # start and end selected
    #         start_date, end_date = date_range
    #         filtered_df3 = filtered_df3[
    #             (filtered_df3["DATE"].dt.date >= start_date) &
    #             (filtered_df3["DATE"].dt.date <= end_date)
    #         ]
    #     elif len(date_range) == 1:  # only one date selected
    #         start_date = date_range[0]
    #         filtered_df3 = filtered_df3[filtered_df3["DATE"].dt.date == start_date]

    with st.form("edit_form3"):
        edited_df3 = st.data_editor(
            filtered_df3,
            num_rows="dynamic",
            height=600,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["PCB INPUTS", "SCH DESIGN", "SCH REVIEW", "PCB-RELEASE", "QUOTATION-RECEIVED", "QUOTATION-APPROVED","UNDER FAB","BOARDS RECEIVED"],
                    width="medium"
                ),
                "DATE": st.column_config.DateColumn(
                    "Date",
                    format="YYYY-MM-DD",
                    step=1,
                    width="medium"
                )
            }
        )

        save3 = st.form_submit_button("💾 Save BOARD STATUS Dashboard Updates")
        if save3:
            if "DATE" in edited_df3.columns:
                edited_df3["DATE"] = pd.to_datetime(edited_df3["DATE"], errors="coerce")

            with pd.ExcelWriter(excel_file, mode="a", if_sheet_exists="replace") as writer:
                edited_df3.to_excel(writer, sheet_name="BOARD STATUS", index=False)

            st.success("✅ Updates saved to BOARD STATUS")
            commit_to_github(repo_name="vignesh-senthilkumar-13/App", file_path=excel_file, commit_message="Update BOARD STATUS sheet")

elif selected_sheet == "BOARDS":
    df1 = get_data("BOARDS")

    # Ensure DATE column is datetime
    if "DATE" in df1.columns:
        df1["DATE"] = pd.to_datetime(df1["DATE"], errors="coerce")

    st.title("📦 Board Shipment Tracker – BOARDS")

    # --- Upcoming deadlines section ---


    # --- Full Shipment Data (Filter + Edit) ---
    st.subheader("📊 Full Shipment Data (Filter + Edit)")
    product_filter = st.multiselect("Filter by Product", df1["Product"].dropna().unique())
    boards_filter = st.multiselect("Filter by Boards", df1["Boards"].dropna().unique())
    status_filter = st.multiselect("Filter by Status", df1["Remaining Boards to send"].dropna().unique())
    sent_from_filter = st.multiselect("Filter by Sent From", df1["Sent from"].dropna().unique())

    filtered_df = df1.copy()
    if product_filter:
        filtered_df = filtered_df[filtered_df["Product"].isin(product_filter)]
    if boards_filter:
        filtered_df = filtered_df[filtered_df["Boards"].isin(boards_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df["Remaining Boards to send"].isin(status_filter)]
    if sent_from_filter:
        filtered_df = filtered_df[filtered_df["Sent from"].isin(sent_from_filter)]

    with st.form("edit_form1"):
        edited_df1 = st.data_editor(
            filtered_df,
            num_rows="dynamic",
            height=500,
            column_config={
                "DATE": st.column_config.DateColumn(
                    "Shipment Date",
                    format="YYYY-MM-DD",
                    step=1,
                    width="medium"
                ),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    format="%d",
                    step=1,
                    min_value=0,
                    width="medium"
                ),
            }
        )
        save1 = st.form_submit_button("💾 Save Updates")
        if save1:
            edited_df1["DATE"] = pd.to_datetime(edited_df1["DATE"], errors="coerce")
            with pd.ExcelWriter(excel_file, mode="a", if_sheet_exists="replace") as writer:
                edited_df1.to_excel(writer, sheet_name="BOARDS", index=False)
            st.success("✅ Updates saved to BOARDS")
            commit_to_github(repo_name="vignesh-senthilkumar-13/App", file_path=excel_file, commit_message="Update BOARD STATUS sheet")

elif selected_sheet == "BUG LIST":
    df_bug = get_data("BUG LIST")

    st.title("🐞 Bug Tracking Dashboard – BUG LIST")

    # --- Filters on all columns ---
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

    # --- Editable table ---
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
                ),"DEVICE": st.column_config.SelectboxColumn(
                    "DEVICE",
                    options=["4832",'4842','4851','4852','4992'],
                    width="medium")

            }
        )

        save_bug = st.form_submit_button("💾 Save BUG LIST Updates")
        if save_bug:
            with pd.ExcelWriter(excel_file, mode="a", if_sheet_exists="replace") as writer:
                edited_df_bug.to_excel(writer, sheet_name="BUG LIST", index=False)
            st.success("✅ Updates saved to BUG LIST")
            commit_to_github(repo_name="vignesh-senthilkumar-13/App", file_path=excel_file, commit_message="Update BOARD STATUS sheet")






































