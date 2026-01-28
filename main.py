import streamlit as st

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Cell Point",
    page_icon="📱",
    layout="centered"
)

# ===============================
# MAIN UI
# ===============================
st.markdown(
    "<h1 style='text-align:center; color:red;'>CELL POINT</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align:center;'>Management Dashboard</h4>",
    unsafe_allow_html=True
)

st.write("")
st.write("")

col1, col2,col3 = st.columns(3)

with col1:
    if st.button("📊 Sales Report", use_container_width=True):
        st.switch_page("pages/sales.py")

with col2:
    if st.button("👥 Employees Report", use_container_width=True):
        st.switch_page("pages/employee.py")

with col3:
    if st.button("📊 cellsum Report", use_container_width=True):
        st.switch_page("pages/cellsum.py")

st.markdown(
    "<p style='text-align:center; font-size:12px;'>© Cell Point</p>",
    unsafe_allow_html=True
)
