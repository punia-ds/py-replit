import jellyfish
import re
from Levenshtein import ratio
from typing import List, Tuple, Dict
from functools import lru_cache
import pandas as pd

@lru_cache(maxsize=10000)
def preprocess_name(name: str) -> str:
    """Clean and preprocess the input name with caching."""
    if not name:
        return ""
    # Remove non-alphabetic characters and convert to lowercase
    cleaned = re.sub(r'[^a-zA-Z]', '', name)
    return cleaned.lower()

@lru_cache(maxsize=10000)
def calculate_phonetic_codes(name: str) -> Tuple[str, str, str]:
    """Calculate and cache phonetic codes for a name."""
    return (
        jellyfish.soundex(name),
        jellyfish.metaphone(name),
        jellyfish.nysiis(name)
    )

def calculate_similarity_scores(input_name: str, reference_name: str, ref_codes: Tuple[str, str, str]) -> Tuple[float, str]:
    """Calculate similarity scores using pre-computed phonetic codes."""
    # Check for exact match first (case-insensitive)
    if input_name.lower() == reference_name.lower():
        return 1.0, "Exact match"

    # Get cached phonetic codes for input name
    input_codes = calculate_phonetic_codes(input_name)

    # Compare phonetic matches using pre-computed codes
    soundex_match = input_codes[0] == ref_codes[0]
    metaphone_match = input_codes[1] == ref_codes[1]
    nysiis_match = input_codes[2] == ref_codes[2]

    # Calculate Levenshtein ratio only if there's a phonetic match
    if any([soundex_match, metaphone_match, nysiis_match]):
        lev_ratio = ratio(input_name, reference_name)
    else:
        lev_ratio = 0

    # Calculate final score
    final_score = lev_ratio
    if soundex_match: final_score += 0.2
    if metaphone_match: final_score += 0.2
    if nysiis_match: final_score += 0.2

    final_score = min(final_score, 0.99)  # Cap non-exact matches at 0.99

    # Determine matching method
    methods = []
    if soundex_match: methods.append("Soundex")
    if metaphone_match: methods.append("Metaphone")
    if nysiis_match: methods.append("NYSIIS")
    if lev_ratio > 0.8: methods.append("Levenshtein")

    matching_method = " & ".join(methods) if methods else "Partial Match"

    return final_score, matching_method

def find_matches(input_name: str, reference_names: List[str], threshold: float = 0.3) -> List[Tuple[str, float, str]]:
    """Find matching names above the similarity threshold using optimized algorithm."""
    matches = []
    processed_input = preprocess_name(input_name)
    if not processed_input:
        return matches

    # Pre-compute phonetic codes for input name
    input_codes = calculate_phonetic_codes(processed_input)

    # First pass: check for exact matches
    exact_matches = []
    for ref_name in reference_names:
        if processed_input == preprocess_name(ref_name):
            exact_matches.append((ref_name, 1.0, "Exact match"))

    # Process reference names in batches for non-exact matches
    batch_size = 1000
    for i in range(0, len(reference_names), batch_size):
        batch = reference_names[i:i + batch_size]

        # Process each name in the batch
        for ref_name in batch:
            processed_ref = preprocess_name(ref_name)
            if not processed_ref or processed_ref == processed_input:  # Skip exact matches as they're already handled
                continue

            # Pre-compute phonetic codes for reference name
            ref_codes = calculate_phonetic_codes(processed_ref)

            # Quick filter: skip if no phonetic matches
            if input_codes[0][:2] != ref_codes[0][:2] and \
               input_codes[1][:2] != ref_codes[1][:2] and \
               input_codes[2][:2] != ref_codes[2][:2]:
                continue

            similarity_score, matching_method = calculate_similarity_scores(
                processed_input, processed_ref, ref_codes
            )

            if similarity_score >= threshold:
                matches.append((ref_name, similarity_score, matching_method))

    # Combine exact matches with other matches and sort
    all_matches = exact_matches + sorted(matches, key=lambda x: x[1], reverse=True)

    # Return top 10 matches
    return all_matches[:10]