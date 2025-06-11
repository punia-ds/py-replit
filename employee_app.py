import streamlit as st
import pandas as pd
from utils import preprocess_name, find_matches

# Page configuration
st.set_page_config(
    page_title="Family Name Matcher - Employee Portal",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide"
)

# Title and description
st.title("European Family Name Search Tool")
st.markdown("""
Welcome to the Family Name Search Tool! This tool helps you find potential original 
European versions of Americanized family names using phonetic matching algorithms.
""")

# Load the database (read-only)
@st.cache_data
def load_database():
    return pd.read_csv('sample_data.csv')

names_df = load_database()

# Create two columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # Input for Americanized name
    name_input = st.text_input(
        "Enter Americanized Family Name:",
        placeholder="e.g., Smith",
        help="Type an Americanized family name to find potential European origins"
    )

    if name_input:
        # Preprocess input
        processed_name = preprocess_name(name_input)

        if processed_name:
            # Find matches
            matches = find_matches(processed_name, names_df['family_name'].tolist())

            # Display results
            st.subheader("Matching Results")

            if matches:
                results_df = pd.DataFrame(matches, columns=['Original Name', 'Similarity Score', 'Matching Method'])
                results_df['Similarity Score'] = results_df['Similarity Score'].map('{:.1%}'.format)
                st.dataframe(results_df, use_container_width=True)

                # Download results
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download Results",
                    data=csv,
                    file_name="name_matches.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No matches found in our database.")
        else:
            st.error("Please enter a valid family name (letters only).")

with col2:
    # Example section
    st.subheader("Example Names")
    st.markdown("""
    Try these Americanized names:
    - Schmidt (German: Schmidt, Schmitt)
    - Miller (German: Müller, Mueller)
    - Brown (German: Braun)
    - Fisher (German: Fischer)
    - Cooper (German: Küfer, Kuefer)
    """)