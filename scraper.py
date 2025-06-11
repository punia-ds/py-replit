import trafilatura
import re
from typing import List, Tuple
import pandas as pd

def extract_names_and_blazons(url: str) -> List[Tuple[str, str]]:
    """
    Extract family names and their corresponding blazons from the Rietstap armorial website.
    Returns a list of tuples containing (family_name, blazon_description)
    """
    # Download the webpage content
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise Exception("Failed to fetch the webpage")

    # Extract the main content
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
    if not text:
        raise Exception("No content found on the page")

    # Split the content into lines
    lines = text.split('\n')

    # Process the lines to extract names and blazons
    results = []
    current_name = None
    current_blazon = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Names are typically in uppercase
        if line.isupper() and len(line) > 1:
            # If we have a complete entry, add it to results
            if current_name and current_blazon:
                # Clean the name by removing vertical bars and extra spaces
                cleaned_name = current_name.replace('|', '').strip()
                results.append((cleaned_name, current_blazon))

            # Start new entry
            current_name = line
            current_blazon = None
        elif current_name and not current_blazon:
            # Clean the blazon by removing trailing vertical bar and extra spaces
            current_blazon = line.replace('|', '').strip()

    # Add the last entry if exists
    if current_name and current_blazon:
        cleaned_name = current_name.replace('|', '').strip()
        results.append((cleaned_name, current_blazon))

    return results

def main():
    url = "http://www.coats-of-arms-heraldry.com/armoriaux/rietstap/blasons_FAYN_FELI.html"
    try:
        entries = extract_names_and_blazons(url)

        # Convert to DataFrame
        df = pd.DataFrame(entries, columns=['Family Name', 'Blazon'])

        # Save to CSV
        df.to_csv('heraldry_data.csv', index=False)
        print(f"Successfully extracted {len(entries)} entries and saved to heraldry_data.csv")

        # Display first few entries
        print("\nFirst few entries:")
        print(df.head().to_string())

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()