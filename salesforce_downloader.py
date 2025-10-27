import re
import requests
import logging
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from read_file import read_file_content # Assuming read_file.py is in the same utils directory
#from django.conf import settings
import os
logger = logging.getLogger(__name__)
from urllib.parse import unquote_plus,urlparse,urlunparse

# A dictionary to store mappings between sanitized and original filenames
filename_map = {}

# --- Salesforce Configuration ---
# For a production environment, consider moving these to Django settings or environment variables.
# Ensure these files exist in the 'app1/utils/' directory or adjust paths accordingly.

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_salesforce_client(request):
    """
    Provides an authenticated Salesforce client.
    1. Tries to use the OAuth token from the user's session.
    2. If the access token is expired, it attempts to use the refresh token.
    
    Raises ValueError if credentials are not found or ConnectionError if auth fails.
    """
    session_token_data = request.session.get('oauth_token')

    # --- 1. Attempt to use session OAuth token ---
    if session_token_data and 'access_token' in session_token_data and 'instance_url' in session_token_data:
        try:
            logger.info("Attempting Salesforce connection using session OAuth token.")
            sf = Salesforce(
                instance_url=session_token_data['instance_url'],
                session_id=session_token_data['access_token']
            )
            sf.limits()  # Lightweight call to check token validity
            logger.info("Salesforce session token is valid.")
            return sf
        except Exception as e_session:
            logger.warning(f"Salesforce session token failed (likely expired): {e_session}. Attempting to refresh token.")
            
            # --- 2. Attempt to refresh the token ---
            refresh_token = session_token_data.get('refresh_token')
            
            if refresh_token:
                try:
                    token_url = 'https://login.salesforce.com/services/oauth2/token'
                    refresh_payload = {
                        'grant_type': 'refresh_token',
                        'client_id': settings.SALESFORCE_CLIENT_ID,
                        'client_secret': settings.SALESFORCE_CLIENT_SECRET,
                        'refresh_token': refresh_token
                    }

                    response = requests.post(token_url, data=refresh_payload, timeout=10)
                    response.raise_for_status()
                    new_token_data = response.json()

                    # Defensive check for required fields
                    if 'access_token' not in new_token_data or 'instance_url' not in new_token_data:
                        raise ValueError("Incomplete token data received from Salesforce.")

                    # Update session token data
                    session_token_data['access_token'] = new_token_data['access_token']
                    session_token_data['instance_url'] = new_token_data['instance_url']
                    if 'refresh_token' in new_token_data:
                        session_token_data['refresh_token'] = new_token_data['refresh_token']

                    request.session['oauth_token'] = session_token_data
                    request.session.modified = True

                    logger.info("Salesforce token refreshed successfully. Re-initializing client.")
                    return Salesforce(
                        instance_url=session_token_data['instance_url'],
                        session_id=session_token_data['access_token']
                    )
                
                except Exception as refresh_e:
                    logger.error(f"Salesforce token refresh failed: {refresh_e}", exc_info=True)
                    if 'oauth_token' in request.session:
                        del request.session['oauth_token']
                        request.session.modified = True
                    raise ConnectionError(f"Salesforce token refresh failed due to: {refresh_e}") from refresh_e
            else:
                logger.error("No refresh token found in session. Cannot refresh.")
                if 'oauth_token' in request.session:
                    del request.session['oauth_token']
                    request.session.modified = True
                raise ConnectionError("No refresh token available. User needs to re-authenticate.")
    
    raise ValueError("No valid Salesforce session found. User needs to authenticate.")

def get_nic_from_tax_file_id(sf_client, tax_file_id):
    """
    Retrieves the client's NIC number from a Tax File ID by chaining three queries.
    1. Tax_File__c -> Contact_ID__c
    2. Contact -> Customer__c
    3. Customer__c -> National_Identity_Card_Number_NIC__c
    """
    try:
        # 1. Get Contact_ID__c from Tax_File__c
        contact_query = f"SELECT Contact_ID__c FROM Tax_File__c WHERE Id = '{tax_file_id}'"
        contact_result = sf_client.query(contact_query)
        if not contact_result['records']:
            logger.warning(f"No Tax_File__c record found for ID: {tax_file_id}")
            return None
        contact_id = contact_result['records'][0].get('Contact_ID__c')
        if not contact_id:
            logger.warning(f"Tax_File__c record {tax_file_id} does not have a Contact_ID__c.")
            return None

        # 2. Get Customer__c from Contact
        customer_query = f"SELECT Customer__c FROM Contact WHERE Id = '{contact_id}'"
        customer_result = sf_client.query(customer_query)
        if not customer_result['records']:
            logger.warning(f"No Contact record found for ID: {contact_id}")
            return None
        customer_id = customer_result['records'][0].get('Customer__c')
        if not customer_id:
            logger.warning(f"Contact record {contact_id} does not have a Customer__c link.")
            return None

        # 3. Get NIC from Customer__c
        nic_query = f"SELECT National_Identity_Card_Number_NIC__c FROM Customer__c WHERE Id = '{customer_id}'"
        nic_result = sf_client.query(nic_query)
        if not nic_result['records']:
            logger.warning(f"No Customer__c record found for ID: {customer_id}")
            return None
        
        return nic_result['records'][0].get('National_Identity_Card_Number_NIC__c')

    except Exception as e:
        logger.error(f"Error retrieving NIC from Tax File ID {tax_file_id}: {e}", exc_info=True)
        return None

def extract_salesforce_record_id_from_url(url):
    """
    Extracts a Salesforce record ID (15 or 18 characters) from a URL.
    More robustly looks for IDs in path segments.
    """
    # Regex to find 15 or 18 character alphanumeric Salesforce IDs that are typical path components
    match = re.search(r'/([a-zA-Z0-9]{18}|[a-zA-Z0-9]{15})(?=[/?#]|$)', url)
    if match:
        record_id = match.group(1)
        logger.info(f"Extracted Salesforce Record ID: {record_id} from URL: {url}")
        return record_id
    logger.warning(f"Could not extract Salesforce Record ID using regex from URL: {url}")
    return None

def get_doc_list(sf_client, tax_file_id):
    """
    Queries Salesforce for all ContentDocument titles related to a Tax File ID.
    """
    print(f"  - Inside get_doc_list for Tax File ID: {tax_file_id}. Fetching Title and ContentDocumentId.")
    query = f"""
    SELECT ContentDocument.Id, ContentDocument.Title
    FROM ContentDocumentLink
    WHERE LinkedEntityId = '{tax_file_id}'
    """
    try:
        results = sf_client.query_all(query)
        # Create a dictionary mapping titles to their IDs
        title_to_id_map = {
            record['ContentDocument']['Title']: record['ContentDocument']['Id']
            for record in results['records'] if record.get('ContentDocument') and record['ContentDocument'].get('Title')
        }
        print(f"  - Found {len(title_to_id_map)} documents. Map: {title_to_id_map}")
        return title_to_id_map, None
    except Exception as e:
        logger.error(f"Error in get_doc_list for Tax File ID {tax_file_id}: {e}", exc_info=True)
        return [], f"Error querying for all document titles: {e}"

def get_specific_document_title(sf_client, record_name):
    """
    Gets the specific document title from the latest 'Tick_Upload_File_names__c' record
    that has not been processed yet for a given Tax File ID.
    """
    print(f"  - Inside get_specific_document_title using system file name for record Name: {record_name}") # noqa
    query = f"""
    SELECT System_File_Name__c, AI_scan_status__c FROM Tick_Upload_File_names__c
    WHERE Name = '{record_name}' AND AI_scan_status__c = FALSE
    ORDER BY CreatedDate DESC
    LIMIT 1
    """
    try:
        result = sf_client.query(query)
        if result['totalSize'] > 0 and result['records'][0].get('System_File_Name__c'):
            full_filename = result['records'][0]['System_File_Name__c']
            # Remove the file extension
            title_without_extension = os.path.splitext(full_filename)[0]
            print(f"  - Found unprocessed title to process: '{title_without_extension}'")
            return title_without_extension, None, False # is_already_processed = False

        # If no unprocessed record is found, check if it was already processed to avoid an error.
        already_processed_query = f"SELECT Id FROM Tick_Upload_File_names__c WHERE Name = '{record_name}' AND AI_scan_status__c = TRUE LIMIT 1"
        already_processed_result = sf_client.query(already_processed_query)
        if already_processed_result['totalSize'] > 0:
            print(f"  - Warning: A record for '{record_name}' was found, but it has already been processed.")
            return None, "Document already processed.", True # is_already_processed = True

        return None, "No unprocessed documents found for this Tax File.", False
    except Exception as e:
        logger.error(f"Error in get_specific_document_title for record Name {record_name}: {e}", exc_info=True)
        return None, f"Error querying for the specific document title: {e}", False

def get_document_details_by_id(sf_client, content_document_id):
    """
    Queries Salesforce for a single ContentDocument's details by its ID.
    This is a more direct way to get details for a known document.
    """
    print(f"  - Inside get_document_details_by_id for ContentDocumentId: {content_document_id}")
    query = f"""
    SELECT Id, Title, FileExtension, ContentSize
    FROM ContentDocument
    WHERE Id = '{content_document_id}' 
    AND FileExtension IN ('pdf', 'png', 'jpeg', 'jpg', 'txt')
    AND ContentSize >= 10240
    LIMIT 1
    """
    try:
        result = sf_client.query(query)
        if result['totalSize'] > 0:
            record = result['records'][0]
            doc_details = [{'id': record['Id'], 'title': record['Title'], 'extension': record['FileExtension']}]
            print(f"  - Successfully found details for document: {doc_details}")
            return doc_details, f"Found 1 processable document."
        else:
            logger.warning(f"No processable file found for ContentDocumentId: {content_document_id} (may not meet size/type criteria).")
            return [], "The specific document does not meet the criteria for processing (PDF, PNG, JPG, JPEG, TXT & >= 10KB)."
    except Exception as e:
        logger.error(f"Error querying for ContentDocumentId {content_document_id}: {e}", exc_info=True)
        return None, f"Error querying for document by ID: {e}"

def get_salesforce_document_details(sf_client, salesforce_record_id):
    """
    Queries Salesforce for ContentDocument details (Id, Title, FileExtension)
    related to a given record ID, filtering for processable file types and a minimum size.
    Returns a list of document details and a status message.
    """
    if not salesforce_record_id:
        logger.error("No Salesforce record ID provided to get_salesforce_document_details.")
        return None, "No Salesforce record ID provided."

    query = f"""
    SELECT ContentDocument.Id, ContentDocument.Title, ContentDocument.FileExtension
    FROM ContentDocumentLink
    WHERE LinkedEntityId = '{salesforce_record_id}'
    AND ContentDocument.FileExtension IN ('pdf', 'png', 'jpeg', 'jpg')
    AND ContentDocument.ContentSize >= 10240
    """ # Example: 10KB minimum size, adjust if needed

    try:
        results = sf_client.query_all(query) # Use query_all for potentially many records
        if results['totalSize'] == 0:
            logger.warning(f"No processable files found for Salesforce record ID: {salesforce_record_id}")
            return [], "No processable files (PDF, PNG, JPG, JPEG >= 10KB) found for this record."

        document_details = []
        for record in results['records']:
            # Access fields from the related ContentDocument object
            content_document = record.get('ContentDocument')
            if content_document:
                doc_id = content_document.get('Id')
                title = content_document.get('Title')
                extension = content_document.get('FileExtension')
                if doc_id and title and extension:
                    document_details.append({'id': doc_id, 'title': title, 'extension': extension})
                else:
                    logger.warning(f"Skipping record due to missing ContentDocument details: {record}")
            else:
                logger.warning(f"Skipping record because ContentDocument is missing: {record}")

        logger.info(f"Found {len(document_details)} processable documents for Salesforce record ID: {salesforce_record_id}")
        return document_details, f"Found {len(document_details)} processable documents."
    except Exception as e:
        logger.error(f"Error querying files for Salesforce record ID {salesforce_record_id}: {e}", exc_info=True)
        return None, f"Error querying files: {e}"


def sanitize_filename(filename):
    """
    Replaces problematic characters in filenames, ensures it's not too long,
    and stores a mapping from the sanitized name back to the original.
    """
    original_filename = str(filename)  # Ensure it's a string for mapping
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', original_filename)
    sanitized = sanitized.strip('. ')
    sanitized = sanitized[:200]  # Limit filename length

    # Store the mapping from the sanitized version to the original
    if sanitized:
        # We store the mapping from the sanitized name (without extension) to the original name (without extension)
        filename_map[sanitized] = original_filename
        logger.debug(f"Stored filename mapping: '{sanitized}' -> '{original_filename}'")

    return sanitized


def get_original_filename(sanitized_name):
    """
    Retrieves the original filename from a sanitized one using the map.
    Falls back to returning the sanitized name if no mapping is found.
    """
    return filename_map.get(sanitized_name, sanitized_name)

def download_salesforce_files(sf_client, document_details_list, download_dir):
    """
    Downloads specified documents from Salesforce.
    Args:
        sf_client: Authenticated simple_salesforce client.
        document_details_list (list): List of dicts, each with 'id', 'title', 'extension'.
        download_dir (str): Directory to save downloaded files.
    Returns:
        list: Paths of successfully downloaded files.
    """
    os.makedirs(download_dir, exist_ok=True)
    downloaded_file_paths = []

    for doc_info in document_details_list:
        content_document_id = doc_info['id']
        original_title = doc_info['title']
        file_extension = doc_info['extension']

        try:
            content_version_query = (
                f"SELECT Id, VersionData FROM ContentVersion "
                f"WHERE ContentDocumentId = '{content_document_id}' AND IsLatest = true LIMIT 1"
            )
            version_result = sf_client.query(content_version_query)

            if not version_result['records']:
                logger.warning(f"No latest ContentVersion found for ContentDocumentId: {content_document_id}")
                continue

            version_data_url_path = version_result['records'][0]['VersionData']
            # To prevent issues with duplicated paths, parse the base_url to get only the scheme and domain
            parsed_url = urlparse(sf_client.base_url)
            base_instance_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
            # Construct the full URL for the file content.
            file_url = f"{base_instance_url.rstrip('/')}{version_data_url_path}"
            
            logger.info(f"Constructed file download URL: {file_url}")
            file_response = requests.get(file_url, headers={'Authorization': f'Bearer {sf_client.session_id}'}, stream=True)
            file_response.raise_for_status()

            safe_filename_base = sanitize_filename(original_title)
            file_name_with_ext = f"{safe_filename_base}.{file_extension.lower()}"
            file_path = os.path.join(download_dir, file_name_with_ext)

            with open(file_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded_file_paths.append(file_path)
            logger.info(f"Successfully downloaded: {file_name_with_ext} to {file_path}")
        except Exception as e:
            logger.error(f"Error downloading document {original_title} (ID: {content_document_id}): {e}", exc_info=True)

    return downloaded_file_paths

def get_content_document_titles_for_record(sf_client, salesforce_record_id):
    """
    Queries Salesforce for ContentDocument titles linked to a specific record,
    filtered by file extension and minimum content size.

    Args:
        sf_client: An authenticated simple_salesforce client instance.
        salesforce_record_id (str): The Salesforce ID of the LinkedEntity (e.g., Tax_File__c record).

    Returns:
        list: A list of ContentDocument titles (strings) if found.
        str: An error message if the query fails or no titles are found.
    """
    if not sf_client:
        logger.error("Salesforce client is not provided to get_content_document_titles_for_record.")
        return [], "Salesforce client not provided."
    if not salesforce_record_id:
        logger.error("Salesforce record ID is not provided to get_content_document_titles_for_record.")
        return [], "Salesforce record ID not provided."

    query = f"""
    SELECT ContentDocument.Title
    FROM ContentDocumentLink
    WHERE LinkedEntityId = '{salesforce_record_id}'
    AND ContentDocument.FileExtension IN ('pdf', 'png', 'jpeg', 'jpg')
    AND ContentDocument.ContentSize >= 10240
    """
    try:
        results = sf_client.query_all(query)
        titles = [record['ContentDocument']['Title'] for record in results['records'] if record.get('ContentDocument') and record['ContentDocument'].get('Title')]
        logger.info(f"Found {len(titles)} ContentDocument titles for record ID {salesforce_record_id}.")
        return titles, None # Return list of titles and None for error message on success
    except Exception as e:
        logger.error(f"Error querying ContentDocument titles for record ID {salesforce_record_id}: {e}", exc_info=True)
        return [], f"Error querying ContentDocument titles: {e}"
def get_filename_only(full_path):
    """Returns just the file name (with extension) from a full path."""
    return os.path.basename(full_path)

def convert_pdf_to_jpeg_pymupdf(pdf_path, output_dir):
    import fitz  # PyMuPDF

    # Ensure output_dir exists
    os.makedirs(output_dir, exist_ok=True)

    jpeg_file_paths = []
    try:
        pdf_document = fitz.open(pdf_path)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap()
            output_file_path = os.path.join(output_dir, f"page_{page_number + 1}.jpeg")
            pix.save(output_file_path)
            jpeg_file_paths.append(output_file_path)
    except Exception as e:
        print(f"Error converting PDF to JPEG: {e}")

    return jpeg_file_paths