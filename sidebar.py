import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
#from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Board Shipment Tracker", layout="wide")
#st_autorefresh(interval=30000)

excel_file = "Device_Management.xlsx"

def get_data(sheet: str) -> pd.DataFrame:
    df = pd.read_excel(excel_file, sheet_name=sheet)
    if "DATE" in df.columns:
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    return df

# --- Sidebar: choose sheet ---
st.sidebar.title("📑 Choose Sheet")
sheet_names = pd.ExcelFile(excel_file).sheet_names
selected_sheet = st.sidebar.selectbox("Select a sheet", sheet_names)

# --- First sheet: full tracker with deadlines ---
if selected_sheet == "BOARDS":
    df1 = get_data("BOARDS")
    st.title("📦 Board Shipment Tracker – BOARDS")

    col1, col2 = st.columns([1, 2])

    with col2:
        st.subheader("📊 Full Shipment Data (Filter + Edit)")
        # Filters
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
                    "DATE": st.column_config.DateColumn("Shipment Date", format="YYYY-MM-DD", step=1),
                    "Quantity": st.column_config.NumberColumn("Quantity", format="%d", step=1, min_value=0)
                }
            )
            save1 = st.form_submit_button("💾 Save Updates")
            if save1:
                edited_df1["DATE"] = pd.to_datetime(edited_df1["DATE"], errors="coerce")
                with pd.ExcelWriter(excel_file, mode="a", if_sheet_exists="replace") as writer:
                    edited_df1.to_excel(writer, sheet_name="BOARDS", index=False)
                st.success("✅ Updates saved to Sheet1")

    with col1:
        st.subheader("⚠️ Upcoming Deadlines (within 7 days)")
        today = datetime.today().date()
        upcoming = edited_df1[edited_df1["DATE"].dt.date <= today + timedelta(days=7)]
        if not upcoming.empty:
            st.metric("Boards Due Soon", len(upcoming))
            upcoming_display = upcoming.copy()
            upcoming_display["Quantity"] = upcoming_display["Quantity"].fillna(0).astype(int)
            st.table(upcoming_display[["Board Name","Boards","DATE","Quantity","Remaining Boards to send"]])
        else:
            st.info("No upcoming deadlines within 7 days.")

# --- Second sheet: simple data viewer/editor ---
elif selected_sheet == "BOARD STATUS":
    df2 = get_data("BOARD STATUS")
    st.title("📊 Data Viewer – BOARD STATUS")

    with st.form("edit_form2"):
        edited_df2 = st.data_editor(
            df2,
            num_rows="dynamic",
            height=600
        )

        save2 = st.form_submit_button("💾 Save BOARD STATUS Updates")
        if save2:
            with pd.ExcelWriter(excel_file, mode="a", if_sheet_exists="replace") as writer:
                edited_df2.to_excel(writer, sheet_name="BOARD STATUS", index=False)
            st.success("✅ Updates saved to BOARD STATUS")

