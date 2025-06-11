import streamlit as st
import pandas as pd
from utils import preprocess_name, find_matches
import io
from datetime import datetime, timedelta

# Initialize session state for sidebar authentication
if 'sidebar_authenticated' not in st.session_state:
    st.session_state['sidebar_authenticated'] = False
if 'auth_expiry' not in st.session_state:
    st.session_state['auth_expiry'] = None

# Page configuration
st.set_page_config(
    page_title="Family Name Matcher",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide"
)

# Title and description
st.title("🛡️ European Family Name Matcher")
st.markdown("""
This app helps you find the original European versions of Americanized family names using 
phonetic matching algorithms. Add a name and hit enter to see results.
""")

# Sidebar
st.sidebar.header("Database Management")

# Check sidebar authentication
def check_sidebar_password():
    """Check if the password is correct and handle authentication for sidebar."""
    if st.session_state['sidebar_authenticated'] and st.session_state['auth_expiry']:
        if datetime.now() < st.session_state['auth_expiry']:
            return True
        else:
            st.session_state['sidebar_authenticated'] = False
            st.session_state['auth_expiry'] = None

    password = st.sidebar.text_input(
        "Enter password for database management:",
        type="password",
        key="sidebar_password_input"
    )

    if password:
        if password == "namefinder2025":
            st.session_state['sidebar_authenticated'] = True
            st.session_state['auth_expiry'] = datetime.now() + timedelta(hours=24)
            return True
        else:
            st.sidebar.error("Incorrect password")
    return False

# Show authentication message if not authenticated
if not st.session_state['sidebar_authenticated']:
    st.sidebar.info("Please enter the password to manage the database.")

# Only show database management features if authenticated
if check_sidebar_password():
    st.sidebar.markdown("""
    **Add Names to Database:**
    1. Upload a CSV file with new names
    2. The new names will be merged with existing database
    3. Duplicates will be kept in the database

    **CSV Format:**
    - Single column with header 'family_name'
    - One name per row
    """)

    # Load sample data
    sample_data = pd.read_csv('sample_data.csv')

    # View database button in sidebar
    st.sidebar.subheader("Database Viewer")
    with st.sidebar.expander("Click to View/Hide Database", expanded=False):
        st.dataframe(sample_data[['family_name']], use_container_width=True)

    # Add single name input in sidebar
    st.sidebar.subheader("Add Single Name")
    new_name = st.sidebar.text_input("Enter a new family name:")
    if st.sidebar.button("Add Name"):
        if new_name:
            new_name_df = pd.DataFrame({'family_name': [new_name]})
            combined_df = pd.concat([sample_data, new_name_df], ignore_index=True)
            combined_df.to_csv('sample_data.csv', index=False)
            st.sidebar.success(f"Added '{new_name}' to database. Total database size: {len(combined_df)} names.")
            names_df = combined_df
        else:
            st.sidebar.error("Please enter a name to add.")

    # File upload for database addition
    st.sidebar.subheader("Add Names from File")
    new_names_file = st.sidebar.file_uploader("Upload additional names (CSV)", type=['csv'])

    if new_names_file is not None:
        try:
            new_names_df = pd.read_csv(new_names_file)
            if 'family_name' not in new_names_df.columns:
                new_names_df.columns = ['family_name']

            combined_df = pd.concat([sample_data, new_names_df], ignore_index=True)
            combined_df.to_csv('sample_data.csv', index=False)
            st.sidebar.success(f"Added {len(new_names_df)} new names. Total database size: {len(combined_df)} names.")
            names_df = combined_df
        except Exception as e:
            st.sidebar.error("Error: Please ensure your CSV file is properly formatted")
            names_df = sample_data
    else:
        names_df = sample_data

    # Display current database size
    st.sidebar.info(f"Current database size: {len(names_df)} names")

    # Add delete database section at the bottom of the sidebar with confirmation
    st.sidebar.markdown("---")  # Add a divider
    st.sidebar.subheader("Delete Database")

    # Initialize the session state for delete confirmation if it doesn't exist
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = False

    # First button to initiate deletion
    if not st.session_state.delete_confirmation:
        if st.sidebar.button("🗑️ Delete Database", type="primary", help="Remove all names from the database"):
            st.session_state.delete_confirmation = True

    # Show confirmation button if first button was clicked
    if st.session_state.delete_confirmation:
        st.sidebar.warning("⚠️ Are you sure? This action cannot be undone!")
        col1, col2 = st.sidebar.columns(2)

        if col1.button("✔️ Yes, Delete", type="primary"):
            empty_df = pd.DataFrame(columns=['family_name'])
            empty_df.to_csv('sample_data.csv', index=False)
            st.sidebar.success("Database cleared successfully! All names have been removed.")
            names_df = empty_df
            st.session_state.delete_confirmation = False

        if col2.button("❌ Cancel"):
            st.session_state.delete_confirmation = False

else:
    # Load the database in read-only mode for searching
    names_df = pd.read_csv('sample_data.csv')

# Main content area (search functionality) - No password required
# Input for Americanized name
name_input = st.text_input("Enter Americanized Family Name:", placeholder="e.g., Smith")

if name_input:
    # Preprocess input
    processed_name = preprocess_name(name_input)

    if processed_name:
        # Find matches
        matches = find_matches(processed_name, names_df['family_name'].tolist())

        # Filter matches to only show 85% or higher similarity
        matches = [match for match in matches if match[1] >= 0.85]

        # Display results
        st.subheader("Matching Results")

        if matches:
            results_df = pd.DataFrame(matches, columns=['Original Name', 'Similarity Score', 'Matching Method'])
            results_df['Similarity Score'] = results_df['Similarity Score'].map('{:.1%}'.format)
            st.dataframe(results_df, use_container_width=True)
        else:
            st.warning("No matches found 😢")
    else:
        st.error("Please enter a valid family name (letters only).")

# Example section
with st.expander("See Examples"):
    st.markdown("""
    Try these Americanized names:
    - Schmidt (German: Schmidt, Schmitt)
    - Miller (German: Müller, Mueller)
    - Brown (German: Braun)
    - Fisher (German: Fischer)
    - Cooper (German: Küfer, Kuefer)
    """)