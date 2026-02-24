import streamlit as st

pk = st.secrets["gcp_service_account"]["private_key"]
st.write(repr(pk[:200]))
