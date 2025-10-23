from colorama import Fore, Style, init
import re
import google.generativeai as genai
import os


def _get_gemini_client():
    """Initializes and returns a Gemini client."""
    # It's good practice to centralize API key reading if used in multiple places.
    # Assuming read_file_content_txt is available or defining it here.
    from read_file import read_file_content_txt
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    api_key = read_file_content_txt(os.path.join(SCRIPT_DIR, "gemini_api.txt")) # Ensure this file exists
    genai.configure(api_key=api_key)
    # Using a specific model for comparison, can be adjusted.
    return genai.GenerativeModel('gemini-2.0-flash')
init(autoreset=True)

def _normalize_amount(value):
    """
    Extracts a numerical value from a string.
    Removes currency symbols, letters, and commas.
    Returns a float if conversion is successful, otherwise None.
    """
    if not isinstance(value, str):
        return None
    # Remove letters, commas, and spaces
    cleaned_value = re.sub(r'[A-Za-z, ]', '', value)
    try:
        return float(cleaned_value)
    except (ValueError, TypeError):
        return None

def _clean_ai_output(raw_text: str | None) -> str | None:
    """Removes markdown code blocks like ```text ... ``` from the raw AI output."""
    if not isinstance(raw_text, str):
        return raw_text
    # Use regex to find content within ```...```, accounting for optional language hints
    match = re.search(r'```(?:\w*\n)?(.*)```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def compare_results(result1, result2):
    """
    Compares two extraction results by splitting them into lists and comparing each element.
    For numerical values, it compares them as floats (rounded), ignoring currency symbols and formatting.
    Prints the comparison result for each field.
    Returns True if all fields match, False otherwise.
    """
    print(Fore.YELLOW + "--- Entering compare_results ---")
    print(f"Result 1: {result1}")
    print(f"Result 2: {result2}")

    if result1 is None or result2 is None:
        print(Fore.RED + "One or both results are None. Comparison failed.")
        # print(Fore.YELLOW + "--- Exiting compare_results (None value) ---") # This can be noisy
        return False, None

    list1 = [item.strip() for item in _clean_ai_output(str(result1)).split('|')]
    list2 = [item.strip() for item in _clean_ai_output(str(result2)).split('|')]

    if len(list1) != len(list2):
        print(Fore.RED + f"Field count mismatch: Result 1 has {len(list1)} fields, Result 2 has {len(list2)} fields.")
        return False, None

    all_match = True
    for val1, val2 in zip(list1, list2):
        norm_val1 = _normalize_amount(val1)
        norm_val2 = _normalize_amount(val2)

        if norm_val1 is not None and norm_val2 is not None:
            if round(norm_val1, 2) != round(norm_val2, 2):
                all_match = False
                break
        elif val1 != val2:
            all_match = False
            break

    if all_match:
        print(Fore.GREEN + "Results are identical. Comparison successful.")
        print(Fore.YELLOW + "--- Exiting compare_results (identical) ---")
        return True, result1 # They are functionally identical
    
    print(Fore.YELLOW + "Results are not identical. Comparison failed.")
    return False, None

def decide_with_ai(result1: str, result2: str) -> tuple[bool, str | None]:
    """
    Uses a Gemini model to decide the best result between two semantically similar strings.
    """
    print(Fore.CYAN + "--- Entering AI Decider ---")
    try:
        model = _get_gemini_client()
        prompt = f"""
Analyze the two pipe-separated strings below. They are extracted from the same document and may contain minor OCR errors or typos (e.g., 'Hharmaceuticals' vs 'Pharmaceuticals').
Determine the most accurate and correct version and respond with ONLY that single, corrected, pipe-separated string. Do not add any explanations.
If they are too different to merge or decide (e.g., different numbers, names, or dates), respond with ONLY the word 'DIFFERENT'.

String 1:
{result1.strip()}
String 2:
{result2.strip()}
        """

        response = model.generate_content(prompt)
        decision = response.text.strip()

        if 'DIFFERENT' in decision.upper():
            print(Fore.RED + "LLM decided results are semantically different.")
            return False, None
        else:
            print(Fore.CYAN + f"LLM Decider chose: {decision}")
            return True, decision
    except Exception as e:
        print(Fore.RED + f"An error occurred during LLM comparison: {e}")
        return False, None
    finally:
        print(Fore.CYAN + "--- Exiting AI Decider ---")