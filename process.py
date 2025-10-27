import logging 
import re 

from identify import *
#image handler
import PIL.Image
from PIL import Image

#extractors
#year 1920
from extractors_1920 import *# . need to add when importing from the same direcotory.....-

#year 2021
from extractors_2021 import *

#year 2122
from extractors_2122 import *

#year 2223
from extractors_2223 import *

#year 2324
from extractors_2324 import *

#from .process_2324_mul import *

from extractors_2425 import *

# Assuming process_2324_mul.py and process_2425_mul.py will also be refactored.
# For now, their direct usage might be commented out or adapted if their new API is known.
# from process_2324_mul import process_2023_2024_mul_refactored # Example of refactored import
# from process_2425_mul import process_2024_2025_mul_refactored # Example of refactored import

logger = logging.getLogger(__name__)

def process_bank_text_output(text_output):
    if not text_output or not isinstance(text_output, str):
        logger.warning(f"process_bank_text_output received invalid input: {text_output}")
        return []

    # Strip leading/trailing whitespace from the input
    processed_text = text_output.strip()

    # Use regex to find all occurrences of content within square brackets [...]
    # This handles cases like "[block1]\n[block2]" or "[block1],[block2]"
    # It extracts the content *inside* the brackets.
    # Example: "[data1|data2]\n[data3|data4]" -> findall gives ["data1|data2", "data3|data4"]
    raw_blocks_content = re.findall(r'\[([^\]]*)\]', processed_text)

    # --- FIX: Handle cases where the first block is not bracketed ---
    # Check if the string starts with text before the first found bracket
    first_bracket_match = re.search(r'\[', processed_text)
    if first_bracket_match and first_bracket_match.start() > 0:
        # There is un-bracketed text at the beginning
        unbracketed_prefix = processed_text[:first_bracket_match.start()].strip(' ,')
        if '|' in unbracketed_prefix: # Check if it looks like a data block
            logger.warning("Found un-bracketed prefix. Prepending it to the list of blocks.")
            raw_blocks_content.insert(0, unbracketed_prefix)

    if not raw_blocks_content:
        logger.warning(f"No data blocks found in AI output using regex: {processed_text}")
        return []

    final_cleaned_list_of_lists = []
    for block_content_str in raw_blocks_content:
        # block_content_str is now the string of items separated by '|', e.g., "item1|item2|item3"
        sub_items_list = []
        for sub_item_raw in block_content_str.split('|'):
            cleaned_sub_item = sub_item_raw.strip() # Strip whitespace from each item
            sub_items_list.append(cleaned_sub_item)
        final_cleaned_list_of_lists.append(sub_items_list)
    return final_cleaned_list_of_lists

def process_bank_text_output_y(text_output):
    if not text_output or not isinstance(text_output, str):
        logger.warning(f"process_bank_text_output_y received invalid input: {text_output}")
        return []

    processed_text = text_output.strip()
    if processed_text.startswith("(") and processed_text.endswith(")"):
        processed_text = processed_text[1:-1]
    if processed_text.startswith("[") and processed_text.endswith("]"):
        processed_text = processed_text[1:-1]

    items_str_list = processed_text.split("),(") # Main difference is the splitter for yearly data

    final_cleaned_list_of_lists = []
    for group_str in items_str_list:
        cleaned_group_str = group_str.strip().strip("()")
        sub_items_list = [s.strip().strip("[]()") for s in cleaned_group_str.split('|')]
        final_cleaned_list_of_lists.append(sub_items_list)
        
    return final_cleaned_list_of_lists

def _wrap_bank_extraction(pil_image_or_list, year_str, period_char, doc_type_code, extractor_func, text_processor_func, is_multiple):
    """Helper function to reduce repetition in bank wrapper functions."""
    logger.info(f"Performing bank extraction for year {year_str}, period {period_char}, multiple: {is_multiple}")
    response_text = extractor_func(pil_image_or_list) # This is the raw AI output
    logger.debug(f"Raw AI response: {response_text}")
    extracted_data = text_processor_func(response_text)
    logger.info("Extraction and text processing completed.")
    return {
        "assessment_year": year_str,
        "bank_type": period_char,
        "raw_ai_output": response_text, # Added raw AI output
        "extracted_data": extracted_data,
        "doc_type": doc_type_code
    }

# --- Wrappers for 2024/2025 ---
def wrap_2425_y(pil_image):
    return _wrap_bank_extraction(pil_image, '2024/2025', "Y", 2, int_inc_2425, process_bank_text_output_y, False)

def wrap_2425_m(pil_image):
    return _wrap_bank_extraction(pil_image, '2024/2025', "M", 2, int_inc_2425_m, process_bank_text_output, False)

def wrap_2425_q(pil_image):
    return _wrap_bank_extraction(pil_image, '2024/2025', "Q", 2, int_inc_2425_q, process_bank_text_output, False)

def wrap_2425_y_mul(pil_images_list):
    # Call the 2425 multi-image yearly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "Y", 2, int_inc_2425_multiple, process_bank_text_output_y, True)

def wrap_2425_m_mul(pil_images_list):
    # Call the 2425 multi-image monthly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "M", 2, int_inc_2425_m_multiple, process_bank_text_output, True)

def wrap_2425_q_mul(pil_images_list):
    # Call the 2425 multi-image quarterly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "Q", 2, int_inc_2425_q_multiple, process_bank_text_output, True)

def wrap_com_2425_m_mul(pil_images_list):
    # Call the 2425 multi-image ComBank monthly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "M", 2, int_inc_com_2425_m_multiple, process_bank_text_output, True)

def wrap_hsbc_2425_m_mul(pil_images_list):
    # Call the 2425 multi-image HSBC monthly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "M", 2, int_inc_hsbc_2425_m_multiple, process_bank_text_output, True)

def wrap_hnb_2425_m_mul(pil_images_list):
    # Call the 2425 multi-image HNB monthly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "M", 2, int_inc_hnb_2425_m_multiple, process_bank_text_output, True)

def wrap_seylan_2425_m_mul(pil_images_list):
    # Call the 2425 multi-image Seylan monthly extractor
    return _wrap_bank_extraction(pil_images_list, '2024/2025', "M", 2, int_inc_seylan_2425_m_multiple, process_bank_text_output, True)

# --- Add other wrap_YYYY_P and wrap_YYYY_P_mul functions here, following the pattern ---
# Example for 2324:
def wrap_2324_y(pil_image):
    return _wrap_bank_extraction(pil_image, '2023/2024', "Y", 2, int_inc_2324, process_bank_text_output_y, False)
def wrap_2324_m(pil_image):
    return _wrap_bank_extraction(pil_image, '2023/2024', "M", 2, int_inc_2324_m, process_bank_text_output, False)
def wrap_2324_q(pil_image):
    return _wrap_bank_extraction(pil_image, '2023/2024', "Q", 2, int_inc_2324_q, process_bank_text_output, False)
def wrap_2324_y_mul(pil_images_list):
    return _wrap_bank_extraction(pil_images_list, '2023/2024', "Y", 2, int_inc_2324_multiple, process_bank_text_output_y, True)
def wrap_2324_m_mul(pil_images_list):
    return _wrap_bank_extraction(pil_images_list, '2023/2024', "M", 2, int_inc_2324_m_multiple, process_bank_text_output, True)
def wrap_2324_q_mul(pil_images_list):
    return _wrap_bank_extraction(pil_images_list, '2023/2024', "Q", 2, int_inc_2324_q_multiple, process_bank_text_output, True)

# ... (repeat for 2223, 2122, 2021, 1920, using doc_type 94 or 2 as appropriate)

def wrap_2223_y(pil_image): return _wrap_bank_extraction(pil_image, '2022/2023', "Y", 94, int_inc_2223, process_bank_text_output_y, False)
def wrap_2223_m(pil_image): return _wrap_bank_extraction(pil_image, '2022/2023', "M", 94, int_inc_2223_m, process_bank_text_output, False)
def wrap_2223_q(pil_image): return _wrap_bank_extraction(pil_image, '2022/2023', "Q", 94, int_inc_2223_q, process_bank_text_output, False)
def wrap_2223_y_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2022/2023', "Y", 94, int_inc_2223_multiple, process_bank_text_output_y, True)
def wrap_2223_m_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2022/2023', "M", 94, int_inc_2223_m_multiple, process_bank_text_output, True)
def wrap_2223_q_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2022/2023', "Q", 94, int_inc_2223_q_multiple, process_bank_text_output, True)

def wrap_2122_y(pil_image): return _wrap_bank_extraction(pil_image, '2021/2022', "Y", 2, int_inc_2122, process_bank_text_output_y, False)
def wrap_2122_m(pil_image): return _wrap_bank_extraction(pil_image, '2021/2022', "M", 2, int_inc_2122_m, process_bank_text_output, False)
def wrap_2122_q(pil_image): return _wrap_bank_extraction(pil_image, '2021/2022', "Q", 2, int_inc_2122_q, process_bank_text_output, False)
def wrap_2122_y_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2021/2022', "Y", 2, int_inc_2122_multiple, process_bank_text_output_y, True)
def wrap_2122_m_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2021/2022', "M", 2, int_inc_2122_m_multiple, process_bank_text_output, True)
def wrap_2122_q_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2021/2022', "Q", 2, int_inc_2122_q_multiple, process_bank_text_output, True)

def wrap_2021_y(pil_image): return _wrap_bank_extraction(pil_image, '2020/2021', "Y", 2, int_inc_2021, process_bank_text_output_y, False)
def wrap_2021_m(pil_image): return _wrap_bank_extraction(pil_image, '2020/2021', "M", 2, int_inc_2021_m, process_bank_text_output, False)
def wrap_2021_q(pil_image): return _wrap_bank_extraction(pil_image, '2020/2021', "Q", 2, int_inc_2021_q, process_bank_text_output, False)
def wrap_2021_y_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2020/2021', "Y", 2, int_inc_2021_multiple, process_bank_text_output_y, True)
def wrap_2021_m_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2020/2021', "M", 2, int_inc_2021_m_multiple, process_bank_text_output, True)
def wrap_2021_q_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2020/2021', "Q", 2, int_inc_2021_q_multiple, process_bank_text_output, True)

def wrap_1920_y(pil_image): return _wrap_bank_extraction(pil_image, '2019/2020', "Y", 94, int_inc_1920, process_bank_text_output_y, False)
def wrap_1920_m(pil_image): return _wrap_bank_extraction(pil_image, '2019/2020', "M", 94, int_inc_1920_m, process_bank_text_output, False)
def wrap_1920_q(pil_image): return _wrap_bank_extraction(pil_image, '2019/2020', "Q", 94, int_inc_1920_q, process_bank_text_output, False)
def wrap_1920_y_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2019/2020', "Y", 94, int_inc_1920_multiple, process_bank_text_output_y, True)
def wrap_1920_m_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2019/2020', "M", 94, int_inc_1920_m_multiple, process_bank_text_output, True)
def wrap_1920_q_mul(pil_images_list): return _wrap_bank_extraction(pil_images_list, '2019/2020', "Q", 94, int_inc_1920_q_multiple, process_bank_text_output, True)


def extract_employment_data(assessment_year, pil_image_or_list, is_multiple):
    """
    Extracts employment data based on the assessment year and image(s).
    Args:
        assessment_year (str): e.g., "2023/2024"
        pil_image_or_list: A single PIL.Image object or a list of PIL.Image objects.
        is_multiple (bool): True if pil_image_or_list is a list for multiple images.
    Returns:
        tuple: (list_of_extracted_strings, doc_type_code) or (None, None) if error.
    """
    extractor_map = {
        "2024/2025": (employment_2425_multiple if is_multiple else employment_2425, 1),
        "2023/2024": (employment_2324_multiple if is_multiple else employment_2324, 1),
        "2022/2023": (employment_2223_multiple if is_multiple else employment_2223, 93),
        "2021/2022": (employment_2122_multiple if is_multiple else employment_2122, 1),
        "2020/2021": (employment_2021_multiple if is_multiple else employment_2021, 1),
        "2019/2020": (employment_1920_multiple if is_multiple else employment_1920, 93),
    }
    if assessment_year in extractor_map:
        extractor_func, doc_type_code = extractor_map[assessment_year]
        logger.info(f"Extracting employment data for {assessment_year}, multiple: {is_multiple}, using: {extractor_func.__name__}, input type: {type(pil_image_or_list)}")

        # Rigorous input validation for employment_data
        if is_multiple:
            if not isinstance(pil_image_or_list, list) or not pil_image_or_list:
                logger.error(f"EMPLOYMENT EXTRACTION ERROR: Expected a non-empty list of images for multi-page, got: {pil_image_or_list}")
                return None, None
            # Check if any element in the list is not a PIL Image (this includes None)
            if any(not isinstance(img, Image.Image) for img in pil_image_or_list):
                invalid_elements_details = [(type(img), img is None) for img in pil_image_or_list if not isinstance(img, Image.Image)]
                logger.error(f"EMPLOYMENT EXTRACTION ERROR: Multi-page list contains non-Image elements or None. Details (type, is_none): {invalid_elements_details}")
                return None, None
        else:  # Single image
            if not isinstance(pil_image_or_list, Image.Image):  # This also catches if pil_image_or_list is None
                logger.error(f"EMPLOYMENT EXTRACTION ERROR: Expected a PIL.Image.Image for single-page, got type: {type(pil_image_or_list)}, value: {pil_image_or_list}")
                return None, None
        
        try:
            if is_multiple:
                contents = [extractor_func.prompt] + pil_image_or_list
                response_text = extractor_func.model.generate_content(contents).text
            else:
                response_text = extractor_func(pil_image_or_list)
            if response_text is None: # Extractor itself might return None (e.g. if API call fails silently)
                logger.error(f"EMPLOYMENT EXTRACTION WARNING: Extractor function {extractor_func.__name__} returned None text output.")
                return None, None
            logger.info(f"Employment data extraction by {extractor_func.__name__} successful. Raw response length: {len(response_text)}")
            return response_text.split("|"), doc_type_code
        except Exception as e_gemini:
            # This will catch errors from the vision_model.generate_content call, including the Blob error
            logger.error(f"EMPLOYMENT EXTRACTION CRITICAL: Error during Gemini call with {extractor_func.__name__}: {e_gemini}", exc_info=True)
            return None, None
    else:
        logger.warning(f"Assessment year {assessment_year} not classified for employment extraction.")
        return None, None


def extract_wealth_management_data(assessment_year, pil_image_or_list, is_multiple):
    """
    Extracts wealth management data based on the assessment year and image(s).
    Args:
        assessment_year (str): e.g., "2023/2024"
        pil_image_or_list: A single PIL.Image object or a list of PIL.Image objects.
        is_multiple (bool): True if pil_image_or_list is a list for multiple images.
    Returns:
        tuple: (list_of_extracted_strings, doc_type_code) or (None, None) if error.
    """
    extractor_map = {
        "2024/2025": (wealth_2425_multiple if is_multiple else wealth_2425, 3),
        "2023/2024": (wealth_2324_multiple if is_multiple else wealth_2324, 3),
        "2022/2023": (wealth_2223_multiple if is_multiple else wealth_2223, 3), # Assuming doc_type 3
        "2021/2022": (wealth_2122_multiple if is_multiple else wealth_2122, 3),
        "2020/2021": (wealth_2021_multiple if is_multiple else wealth_2021, 3),
        "2019/2020": (wealth_1920_multiple if is_multiple else wealth_1920, 3),
    }
    if assessment_year in extractor_map:
        extractor_func, doc_type_code = extractor_map[assessment_year]
        logger.info(f"Extracting wealth data for {assessment_year}, multiple: {is_multiple}, using: {extractor_func.__name__}, input type: {type(pil_image_or_list)}")

        # Rigorous input validation for wealth_management_data
        if is_multiple:
            if not isinstance(pil_image_or_list, list) or not pil_image_or_list:
                logger.error(f"WEALTH EXTRACTION ERROR: Expected a non-empty list of images for multi-page, got: {pil_image_or_list}")
                return None, None
            if any(not isinstance(img, Image.Image) for img in pil_image_or_list):
                invalid_elements_details = [(type(img), img is None) for img in pil_image_or_list if not isinstance(img, Image.Image)]
                logger.error(f"WEALTH EXTRACTION ERROR: Multi-page list contains non-Image elements or None. Details (type, is_none): {invalid_elements_details}")
                return None, None
        else:  # Single image
            if not isinstance(pil_image_or_list, Image.Image):
                logger.error(f"WEALTH EXTRACTION ERROR: Expected a PIL.Image.Image for single-page, got type: {type(pil_image_or_list)}, value: {pil_image_or_list}")
                return None, None
        
        try:
            if is_multiple:
                contents = [extractor_func.prompt] + pil_image_or_list
                response_text = extractor_func.model.generate_content(contents).text
            else:
                response_text = extractor_func(pil_image_or_list)
            if response_text is None:
                logger.error(f"WEALTH EXTRACTION WARNING: Extractor function {extractor_func.__name__} returned None text output.")
                return None, None
            logger.info(f"Wealth management data extraction by {extractor_func.__name__} successful. Raw response length: {len(response_text)}")
            return response_text.split("|"), doc_type_code
        except Exception as e_gemini:
            logger.error(f"WEALTH EXTRACTION CRITICAL: Error during Gemini call with {extractor_func.__name__}: {e_gemini}", exc_info=True)
            return None, None
    else:
        logger.warning(f"Assessment year {assessment_year} not classified for wealth management extraction.")
        return None, None

def process_balance_confirmation_output(text_output):
    """
    Parses the AI output for Bank Balance Confirmation, which is a series of
    bracketed, pipe-separated blocks, into a single flat list of items.
    e.g., "[a|b],[c|d|e]" -> ["a", "b", "c", "d", "e"]
    """
    if not text_output or not isinstance(text_output, str):
        logger.warning(f"process_balance_confirmation_output received invalid input: {text_output}")
        return []

    processed_text = text_output.strip()
    # Find all content inside square brackets
    raw_blocks_content = re.findall(r'\[([^\]]*)\]', processed_text)

    if not raw_blocks_content:
        logger.warning(f"No data blocks found in balance confirmation output using regex: {processed_text}")
        return []

    flat_list = []
    for block_content_str in raw_blocks_content:
        flat_list.extend([sub_item.strip() for sub_item in block_content_str.split('|')])
    return flat_list


#extraction for bank balance cnfirmtion 
def extract_bank_balance_data(assessment_year, pil_image_or_list, is_multiple):
    """
    Extracts wealth management data based on the assessment year and image(s).
    Args:
        assessment_year (str): e.g., "2023/2024"
        pil_image_or_list: A single PIL.Image object or a list of PIL.Image objects.
        is_multiple (bool): True if pil_image_or_list is a list for multiple images.
    Returns:
        tuple: (list_of_extracted_strings, doc_type_code) or (None, None) if error.
    """
    extractor_map = {
        "2024/2025": (balance_2425 if is_multiple else balance_2425, 4),
        "2023/2024": (balance_2324 if is_multiple else balance_2324, 4),
        "2022/2023": (balance_2223 if is_multiple else balance_2223, 4), # Assuming doc_type 3
        "2021/2022": (balance_2122 if is_multiple else balance_2122, 4),
        "2020/2021": (balance_2021 if is_multiple else balance_2021, 4),
        "2019/2020": (balance_1920 if is_multiple else balance_1920, 4),
    }
    if assessment_year in extractor_map:
        extractor_func, doc_type_code = extractor_map[assessment_year]
        logger.info(f"Extracting balance data for {assessment_year}, multiple: {is_multiple}, using: {extractor_func.__name__}, input type: {type(pil_image_or_list)}")

        # Rigorous input validation for wealth_management_data
        if is_multiple:
            if not isinstance(pil_image_or_list, list) or not pil_image_or_list:
                logger.error(f"Balance EXTRACTION ERROR: Expected a non-empty list of images for multi-page, got: {pil_image_or_list}")
                return None, None
            if any(not isinstance(img, Image.Image) for img in pil_image_or_list):
                invalid_elements_details = [(type(img), img is None) for img in pil_image_or_list if not isinstance(img, Image.Image)]
                logger.error(f"Balance EXTRACTION ERROR: Multi-page list contains non-Image elements or None. Details (type, is_none): {invalid_elements_details}")
                return None, None
        else:  # Single image
            if not isinstance(pil_image_or_list, Image.Image):
                logger.error(f"Balance EXTRACTION ERROR: Expected a PIL.Image.Image for single-page, got type: {type(pil_image_or_list)}, value: {pil_image_or_list}")
                return None, None
        
        try:
            if is_multiple:
                contents = [extractor_func.prompt] + pil_image_or_list
                response_text = extractor_func.model.generate_content(contents).text
            else:
                response_text = extractor_func(pil_image_or_list)
            # --- This is the correct place to print the raw AI output ---
            print(f"--- Raw AI Output (Bank Balance Confirmation): {response_text} ---", flush=True)
            # --- End of print statement ---
            if response_text is None:
                logger.error(f"Balance EXTRACTION WARNING: Extractor function {extractor_func.__name__} returned None text output.")
                return None, None
            processed_data = process_balance_confirmation_output(response_text)
            logger.info(f"Bank Balance data extraction by {extractor_func.__name__} successful. Parsed into {len(processed_data)} items.")
            return processed_data, doc_type_code
        except Exception as e_gemini:
            logger.error(f"Balance EXTRACTION CRITICAL: Error during Gemini call with {extractor_func.__name__}: {e_gemini}", exc_info=True)
            return None, None
    else:
        logger.warning(f"Assessment year {assessment_year} not classified for bank balance extraction.")
        return None, None
    

def process_select(response_iden):
    if response_iden[0] == "employment":
        return "E"
    elif response_iden[0] == "bankconfirmation":
        return "B"
    elif response_iden[0] == "wealthmanagement":
        return "W"
    else:
        logger.warning(f"Document type '{response_iden[0]}' is not classified for selection mapping.")
        return None

def dispatch_bank_extraction(assessment_year, period_type, pil_image_or_list, is_multiple, specific_bank_model):
    """
    Dispatches to the correct bank extraction wrapper function.
    Args:
        assessment_year (str): e.g., "2024/2025"
        period_type (str): "Y", "M", or "Q"
        pil_image_or_list: A single PIL.Image or a list of PIL.Image objects.
        is_multiple (bool): True if processing multiple images/pages.
        specific_bank_model (str, optional): e.g., "com", "hsbc", "hnb", "seylan" for 24/25 monthly.
    Returns:
        dict: The result from the corresponding wrap_... function, or None if no match.
    """
    year_map_single = {
        "2024/2025": {"Y": wrap_2425_y, "M": wrap_2425_m, "Q": wrap_2425_q},
        "2023/2024": {"Y": wrap_2324_y, "M": wrap_2324_m, "Q": wrap_2324_q},
        "2022/2023": {"Y": wrap_2223_y, "M": wrap_2223_m, "Q": wrap_2223_q},
        "2021/2022": {"Y": wrap_2122_y, "M": wrap_2122_m, "Q": wrap_2122_q},
        "2020/2021": {"Y": wrap_2021_y, "M": wrap_2021_m, "Q": wrap_2021_q},
        "2019/2020": {"Y": wrap_1920_y, "M": wrap_1920_m, "Q": wrap_1920_q},
    }
    year_map_multiple = {
        "2024/2025": {
            "Y": wrap_2425_y_mul, "M": wrap_2425_m_mul, "Q": wrap_2425_q_mul,
            "M_com": wrap_com_2425_m_mul, "M_hsbc": wrap_hsbc_2425_m_mul,
            "M_hnb": wrap_hnb_2425_m_mul, "M_seylan": wrap_seylan_2425_m_mul
        },
        "2023/2024": {"Y": wrap_2324_y_mul, "M": wrap_2324_m_mul, "Q": wrap_2324_q_mul},
        "2022/2023": {"Y": wrap_2223_y_mul, "M": wrap_2223_m_mul, "Q": wrap_2223_q_mul},
        "2021/2022": {"Y": wrap_2122_y_mul, "M": wrap_2122_m_mul, "Q": wrap_2122_q_mul},
        "2020/2021": {"Y": wrap_2021_y_mul, "M": wrap_2021_m_mul, "Q": wrap_2021_q_mul},
        "2019/2020": {"Y": wrap_1920_y_mul, "M": wrap_1920_m_mul, "Q": wrap_1920_q_mul},
    }

    selected_map = year_map_multiple if is_multiple else year_map_single
    
    if assessment_year in selected_map:
        period_dispatch_key = period_type
        if is_multiple and assessment_year == "2024/2025" and period_type == "M" and specific_bank_model:
            period_dispatch_key = f"M_{specific_bank_model.lower()}"

        if period_dispatch_key in selected_map[assessment_year]:
            extractor_func = selected_map[assessment_year][period_dispatch_key]
            return extractor_func(pil_image_or_list)
        else:
            logger.error(f"No bank extractor found for year {assessment_year}, period key '{period_dispatch_key}', multiple={is_multiple}")
            return None
    else:
        logger.error(f"No bank extractor map found for year {assessment_year}")
        return None

def parse_structured_bank_details(raw_data_list_of_lists, bank_period_type, assessment_year):
    """
    Parses structured bank details for different bank period types.
    
    For yearly data (bank_period_type == "Y"):
      - raw_data_list_of_lists[0] is general info: [bank_name, customer_name, nic, issued_date, wht_agent_tin, wht_cert_no]
      - Subsequent rows are account annual summaries: [account_no, interest, wht, balance, currency]
      Returns a dictionary with keys: "assessment_year", "general_info", and "accounts".
      Each account in "accounts" will have a "periods" list containing one entry for "Annual".
    
    For monthly data (bank_period_type == "M"):
      - raw_data_list_of_lists[0] is general info: [bank_name, customer_name, nic, issued_date, wht_agent_tin, wht_cert_no]
      - Subsequent rows are either account headers [account_no, currency] or period details [period_name, interest, wht].
      Returns a dictionary with keys: "assessment_year", "general_info", and "accounts".
      Each account in "accounts" will have its respective "periods".
    """
    import logging
    logger = logging.getLogger(__name__)
    
    general_info = {}
    accounts_payload = []

    if not raw_data_list_of_lists:
        logger.error(f"No raw data provided for parsing bank details (period: {bank_period_type}).")
        return None

    # Parse General Information (common for all types)
    general_info_raw = raw_data_list_of_lists[0]
    if len(general_info_raw) >= 6:
        general_info = {
            "bank_name": general_info_raw[0].strip() if isinstance(general_info_raw[0], str) else "N/A",
            "customer_name": general_info_raw[1].strip() if isinstance(general_info_raw[1], str) else "",
            # FIX: Clean the NIC value to remove any "NIC:" prefix
            "nic": re.sub(r'^(NIC|nic)\s*[:\-]?\s*', '', general_info_raw[2].strip()).strip() if isinstance(general_info_raw[2], str) else "",
            "issued_date": general_info_raw[3].strip() if isinstance(general_info_raw[3], str) else "",
            "wht_agent_tin": general_info_raw[4].strip() if isinstance(general_info_raw[4], str) else "",
            "wht_cert_no": general_info_raw[5].strip() if isinstance(general_info_raw[5], str) else ""
        }
    elif len(general_info_raw) >= 5: # Fallback if wht_cert_no is missing
        general_info = {
            "bank_name": general_info_raw[0].strip() if isinstance(general_info_raw[0], str) else "N/A",
            "customer_name": general_info_raw[1].strip() if isinstance(general_info_raw[1], str) else "",
            # FIX: Clean the NIC value to remove any "NIC:" prefix
            "nic": re.sub(r'^(NIC|nic)\s*[:\-]?\s*', '', general_info_raw[2].strip()).strip() if isinstance(general_info_raw[2], str) else "",
            "issued_date": general_info_raw[3].strip() if isinstance(general_info_raw[3], str) else "",
            "wht_agent_tin": general_info_raw[4].strip() if isinstance(general_info_raw[4], str) else "",
            "wht_cert_no": "" # Default if not provided
        }
    else:
        logger.warning(f"General info row for period {bank_period_type} has insufficient columns ({len(general_info_raw)}); using defaults. Data: {general_info_raw}")
        general_info = {
            "bank_name": "N/A", "customer_name": "", "nic": "", "issued_date": "", "wht_agent_tin": "", "wht_cert_no": ""
        }

    if bank_period_type == "Y": # Yearly
        logger.info(f"Parsing bank details for YEARLY period type. Rows: {len(raw_data_list_of_lists)}")
        if len(raw_data_list_of_lists) < 1: # Should be at least 1 for general info
            logger.error("Not enough data rows for yearly parsing (missing general info).")
            return None
        
        for i, row in enumerate(raw_data_list_of_lists[1:], start=1): # Skip general info row
            if len(row) >= 5: # Expecting [acc_no, interest, wht, balance, currency]
                acc_no = row[0].strip() if isinstance(row[0], str) else "N/A"
                interest = row[1].strip() if isinstance(row[1], str) else "0"
                wht = row[2].strip() if isinstance(row[2], str) else "0"
                balance = row[3].strip() if isinstance(row[3], str) else "0"
                currency = row[4].strip() if isinstance(row[4], str) else "N/A"
                
                
                    # Currency is per account/period for yearly in this structure
                
                account_obj = {
                    "account_no": acc_no,
                    "interest": interest,
                    "wht": wht,
                    "balance": balance,
                    "currency": currency,

                }
                accounts_payload.append(account_obj)
            else:
                logger.warning(f"Yearly data row at index {i} has insufficient items ({len(row)}). Expected 5. Data: {row}")

    elif bank_period_type == "M" or bank_period_type == "Q": # Monthly or Quarterly
        logger.info(f"Parsing bank details for {bank_period_type} period type. Rows: {len(raw_data_list_of_lists)}")
        current_account_obj = None # type: ignore
        for i, row in enumerate(raw_data_list_of_lists[1:], start=1): # Skip general info row
            # Handle account header: [account_no, currency] or [account_no, currency, balance]
            if len(row) == 2 or len(row) == 3:
                if current_account_obj: # Add previous account if exists
                    accounts_payload.append(current_account_obj)
                
                acc_no = row[0].strip() if isinstance(row[0], str) else "N/A"
                currency = row[1].strip() if isinstance(row[1], str) else "N/A"
                # NEW: Get balance if it exists (for M/Q types)
                balance = row[2].strip() if len(row) > 2 and isinstance(row[2], str) else "0"

                current_account_obj = {
                    "account_no": acc_no,
                    "currency": currency,
                    "balance": balance, # NEW
                    "periods": []
                }
                logger.debug(f"Started new account: {acc_no} / {currency} / Balance: {balance}")

            # FIX: Handle period details with either 3 or 4 items
            elif len(row) >= 3 and isinstance(row[0], str) and re.match(r'^\d{4}/\d{2}$', row[0].strip()): # Period detail: [period_name, interest, wht, (optional) wht_cert_no]
                if not current_account_obj:
                    logger.warning(f"Period data found at index {i} without a preceding account header. Skipping. Data: {row}")
                    # Or create a default/unknown account:
                    # current_account_obj = {"account_no": "Unknown", "currency": "N/A", "balance": "0", "periods": []}
                    # logger.warning(f"Period data found at index {i} without a preceding account header. Creating default account. Data: {row}")
                    continue

                period_name = row[0].strip() if isinstance(row[0], str) else ""
                interest = row[1].strip() if isinstance(row[1], str) else "0"
                wht = row[2].strip() if isinstance(row[2], str) else "0"
                # Handle optional wht_cert_no
                wht_cert_no = row[3].strip() if len(row) > 3 and isinstance(row[3], str) else ""
                period_obj = {
                    "period_name": period_name,
                    "interest": interest,
                    "wht": wht,
                    "wht_cert_no": wht_cert_no # Added wht_cert_no
                }
                current_account_obj["periods"].append(period_obj)
                logger.debug(f"Added period {period_name} to account {current_account_obj['account_no']}")
            else:
                logger.warning(f"{bank_period_type} data row at index {i} has unexpected item count ({len(row)}). Expected 2, 3, or 4. Data: {row}")
        
        if current_account_obj: # Add the last processed account
            accounts_payload.append(current_account_obj)
            logger.debug(f"Added final account: {current_account_obj['account_no']}")

    else:
        logger.error(f"Unsupported bank_period_type: {bank_period_type}")
        return None

    if not accounts_payload and len(raw_data_list_of_lists) > 1 : # If no accounts were parsed but there was data beyond general_info
        logger.warning(f"No accounts were successfully parsed for period type {bank_period_type}, though data rows were present beyond general info.")

    return {
        "assessment_year": assessment_year,
        "general_info": general_info,
        "accounts": accounts_payload
    }

def parse_balance_confirmation_output(pipe_string: str) -> dict | None:
    """
    Parses a pipe-separated string from a Bank Balance Confirmation extraction
    into a structured dictionary suitable for Salesforce update.

    Expected input format:
    "bank_name|person_name|nic|statement_date|year_of_assessment|account_number_1|currency_1|account_type_1|balance_1|interest_1|wht_1|is_joint_1|joint_persons_1|account_number_2|..."

    Returns:
        A dictionary with 'general_info' and a list of 'accounts', or None if parsing fails.
    """
    if not pipe_string or not isinstance(pipe_string, str):
        logger.error("parse_balance_confirmation_output received invalid or empty input.")
        return None

    blocks = re.findall(r'\[([^\]]*)\]', pipe_string)
    if not blocks:
        logger.error(f"Could not find any bracketed blocks in balance confirmation output: {pipe_string}")
        return None
    
    # The first block is always general info
    general_info_parts = [p.strip() for p in blocks[0].split('|')]
    if len(general_info_parts) < 5:
        logger.error(f"Insufficient data for general info in balance confirmation. Parts found: {len(general_info_parts)}. Data: '{blocks[0]}'")
        return None

    general_info = {
        "year_of_assessment": general_info_parts[0],
        "name_of_the_bank": general_info_parts[1],
        "name_of_the_person": general_info_parts[2],
        "nic_of_the_person": general_info_parts[3],
        "statement_date": general_info_parts[4],
    }

    accounts = []
    # Account data starts after the first block (general info)
    account_blocks = blocks[1:]
    for block in account_blocks:
        parts = [p.strip() for p in block.split('|')]
        if len(parts) == 6: # [account number | currency | account type | balance | interest | WHT]
            accounts.append({
                "account_number": parts[0],
                "currency": parts[1],
                "account_type": parts[2],
                "balance": parts[3],
                "interest": parts[4],
                "wht": parts[5],
            })
        else:
            logger.warning(f"Skipping malformed account block in balance confirmation. Expected 6 parts, got {len(parts)}. Data: '{block}'")

    return {"general_info": general_info, "accounts": accounts}