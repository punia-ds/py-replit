import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Heraldry Data Viewer",
    page_icon="🛡️",
    layout="wide"
)

# Title
st.title("Heraldry Data Viewer")
st.markdown("View and download family heraldry data")

# Load the data
df = pd.read_csv('heraldry_data.csv')

# Display basic statistics
st.subheader("Dataset Statistics")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Entries", len(df))
with col2:
    st.metric("Unique Family Names", df['Family Name'].nunique())

# Display the data
st.subheader("Heraldry Data")
st.dataframe(df)

# Download button
csv = df.to_csv(index=False)
st.download_button(
    label="Download Heraldry Data",
    data=csv,
    file_name="heraldry_data.csv",
    mime="text/csv",
)
