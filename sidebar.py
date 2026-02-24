import streamlit as st

pk = st.secrets["gcp_service_account"]["private_key"]
print(repr(pk[:100]))  # show first 100 chars
