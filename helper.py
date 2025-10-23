# In a helpers.py or directly in your views.py
# from django.conf import settings
import os
import re # Import regex module for string manipulation
import logging
from simple_salesforce import SalesforceAuthenticationFailed
import requests

logger = logging.getLogger(__name__)

def get_user_temp_processing_dir(user):
    """
    Generates a path for the user's temporary processing directory.
    Example: <MEDIA_ROOT>/user_processing_temp/<user_id>/
    """
    if not user or not user.is_authenticated:
        logger.warning("Attempted to get temp dir for unauthenticated user.")
        return None

    # Define a base directory for all user-specific temporary files
    # This could be a subdirectory within MEDIA_ROOT or another path
    # Ensure 'user_processing_temp' directory exists or is created during app setup/deployment
    base_temp_dir = os.path.join(settings.MEDIA_ROOT, 'user_processing_temp')

    user_specific_dir = os.path.join(base_temp_dir, str(user.id))
    return user_specific_dir

def execute_with_salesforce_retry(request, max_retries, function_to_execute, *args, **kwargs):
    """
    A wrapper to execute a function that interacts with Salesforce, with retry logic for session expiry.

    Args:
        request: The Django request object (needed to clear the session).
        max_retries (int): The maximum number of attempts (e.g., 2 for one initial try and one retry).
        function_to_execute (callable): The function that performs the Salesforce operations.
        *args: Positional arguments to pass to function_to_execute.
        **kwargs: Keyword arguments to pass to function_to_execute.

    Returns:
        The result of function_to_execute if successful.
    
    Raises:
        The final exception if all retries fail.
    """
    attempt = 0
    last_exception = None

    while attempt < max_retries:
        try:
            if attempt > 0:
                logger.info(f"Retrying Salesforce operation (Attempt {attempt + 1}/{max_retries}).")
            
            return function_to_execute(*args, **kwargs)

        except (SalesforceAuthenticationFailed, requests.exceptions.RequestException, ConnectionError) as e:
            logger.error(f"Salesforce API call failed (Attempt {attempt + 1}/{max_retries}): {e}", exc_info=True)
            last_exception = e
            attempt += 1
            
            if 'oauth_token' in request.session:
                logger.info("Clearing expired/invalid oauth_token from session to force refresh on next attempt.")
                del request.session['oauth_token']
                request.session.modified = True
            
            if attempt >= max_retries:
                logger.error("All Salesforce retries failed.")
                raise last_exception

def getfile_name_from_path(file_path):
    """
    Extracts and standardizes the file name from a given file path to match
    the format stored in Salesforce's System_File_Name__c field.
    
    Args:
        file_path (str): The full path to the file.
    
    Returns:
        str: The transformed filename (compare_name) for Salesforce lookup.
    """
    # First, get the base filename (e.g., "my_document.pdf")
    base_filename_with_ext = os.path.basename(file_path)
    
    # Then, remove the extension (e.g., "my_document")
    file_name_no_ext, _ = os.path.splitext(base_filename_with_ext)
    compare_name = file_name_no_ext

    # Define patterns for different filename formats
    # Pattern 1: For ISO-like dates, e.g., "...Date - 2025-06-03 04_16_30Z" (now correctly handles optional 'Z')
    date_pattern_iso = re.compile(r"^(.* Date - \d{4}-\d{2}-\d{2} )(\d{2}_\d{2}_\d{2})(Z?)$") # Added (Z?) to capture optional 'Z'
    match_iso = date_pattern_iso.match(file_name_no_ext)

    # Pattern 2: For US-like dates, e.g., "...Date - 12_19_2024 12_06_05 PM"
    date_pattern_us = re.compile(r"^(.*? Date-)(\d{2}_\d{2}_\d{4})\s+(\d{2}_\d{2}_\d{2})\s+(AM|PM)$", re.IGNORECASE)
    match_us = date_pattern_us.match(file_name_no_ext)

    # Pattern 4 (new): For filenames like "1 2024_2025 _ Cust..."
    cust_year_pattern = re.compile(r"^(.*?)(\d{4})_(\d{4})(\s+_\s+)(.*)$")
    match_cust_year = cust_year_pattern.match(file_name_no_ext)

    if file_name_no_ext.endswith('___'): # This pattern should be checked first if it's a higher priority
        # Pattern 3: Handle the triple underscore case
        compare_name = file_name_no_ext[:-3] + ':'
        logger.info(f"Transformed filename '{file_name_no_ext}' to '{compare_name}' (Pattern 3: replaced '___' with ':').")
    
    elif match_cust_year:
        # Handles "1 2024_2025 _ Cust..." -> "1 2024/2025 : Cust..."
        prefix = match_cust_year.group(1)
        year1 = match_cust_year.group(2)
        year2 = match_cust_year.group(3)
        # group 4 is the " _ " which we replace with " : "
        suffix_raw = match_cust_year.group(5)

        # Also check if the suffix contains a time part that needs reformatting (like in Pattern 1)
        time_match_in_suffix = re.search(r"(\d{2}_\d{2}_\d{2})(Z?)$", suffix_raw)
        if time_match_in_suffix:
            time_part_with_underscores = time_match_in_suffix.group(1)
            time_part_with_colons = time_part_with_underscores.replace('_', ':')
            # Rebuild the suffix with the corrected time format
            suffix_final = suffix_raw.replace(time_part_with_underscores, time_part_with_colons)
        else:
            suffix_final = suffix_raw

        compare_name = f"{prefix}{year1}/{year2} : {suffix_final}"
        logger.info(f"Transformed filename '{file_name_no_ext}' to '{compare_name}' (Pattern 4: custom YYYY_YYYY _ Cust format with time correction).")

    elif match_iso:
        prefix = match_iso.group(1)
        time_part_with_underscores = match_iso.group(2)
        z_suffix = match_iso.group(3) # This will be 'Z' or '' (empty string)
        # Replace underscores in the time part with colons
        time_part_with_colons = time_part_with_underscores.replace('_', ':')
        # Reconstruct the name, now including the captured 'Z' suffix
        compare_name = f"{prefix}{time_part_with_colons}{z_suffix}"
        logger.info(f"Transformed filename '{file_name_no_ext}' to '{compare_name}' (Pattern 1: reformatted ISO-like time).")

    elif match_us:
        # This logic is preserved from a previous implementation for backward compatibility
        prefix_raw, date_part_raw, time_part_raw, am_pm = match_us.groups()
        try:
            prefix_standardized = prefix_raw.replace('_', '/').replace(' _ ', ' ').replace(' - ', '-')
            datetime_str_raw = f"{date_part_raw} {time_part_raw} {am_pm}"
            datetime_obj = datetime.strptime(datetime_str_raw, "%m_%d_%Y %I_%M_%S %p")
            date_part_formatted = datetime_obj.strftime("%Y%m%d")
            time_part_formatted = datetime_obj.strftime("%H%M%S")
            compare_name = f"{prefix_standardized.strip()}{date_part_formatted} {time_part_formatted}"
            logger.info(f"Transformed filename '{file_name_no_ext}' to '{compare_name}' (Pattern 2: reformatted US-like date/time).")
        except ValueError as ve:
            logger.error(f"Could not parse date/time from filename '{file_name_no_ext}' during transformation: {ve}. Using original name.")
            compare_name = file_name_no_ext # Fallback to original name on parsing error
    
    else:
        # If no specific pattern matches, use the filename without extension as is.
        logger.info(f"Filename '{file_name_no_ext}' does not match known transformation patterns. Using as is.")

    return compare_name
