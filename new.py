#import external functions
from .google_drive_folder_downloader import *


# Google Drive authentication
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Library for converting PDF to image
# from reportlab.pdfgen import canvas # Not directly used for conversion here
#import PIL
#from PIL import Image


# Convert pdf to image
# from pdf2image import convert_from_path, convert_from_bytes # PyMuPDF (fitz) is used below

# Libraries to handle files
import os
import io # Keep io
import logging # Added logging


# Configure Google Drive
# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "Google_drive.json") # Use absolute path
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json") # Use absolute path
SCOPES = ["https://www.googleapis.com/auth/drive"]

#import library
# from simple_salesforce import Salesforce # No longer needed here for direct instantiation

#read file content for creds

logger = logging.getLogger(__name__) # Added logger


def check_for_files(sf_client, salesforce_id):
    """
    Checks for processable files (PDF, PNG, JPEG, JPG > 10KB) linked to a Salesforce record.
    Accepts an authenticated Salesforce client instance.
    Returns a set of ContentDocumentIds or None if an error occurs or no files are found.
    """
    # === Query ContentDocumentLinks (files related to the record) ===
    query = f"SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId = '{salesforce_id}'"
    #query=f"SELECT Id,FileExtension, Title, VersionData FROM ContentVersion WHERE ContentDocumentId = '{salesforce_id}' ORDER BY VersionNumber DESC LIMIT 1"
    try:
        all_files_result = sf_client.query(query)
        all_files_records = all_files_result.get('records', [])
    except Exception as e:
        logger.error(f"Error querying ContentDocumentLink for Salesforce ID {salesforce_id}: {e}", exc_info=True)
        return set()


    if not all_files_records:
        logger.warning(f"No files linked to Salesforce ID: {salesforce_id}")
        return set() # Return empty set
    # else: # This else is not strictly needed as the next block handles file filtering
        # SOQL query
    query = f"""
    SELECT ContentDocumentId 
    FROM ContentDocumentLink 
    WHERE LinkedEntityId = '{salesforce_id}'
    AND ContentDocument.FileExtension IN ('pdf', 'png', 'jpeg', 'jpg') 
    AND ContentDocument.ContentSize >= 10240
    """
    try:
        # Execute query
        files_to_download_result = sf_client.query(query)
        files_to_download_records = files_to_download_result.get('records', [])
        # All the file ids
        if not files_to_download_records:
            logger.warning(f"No processable files found for Salesforce ID: {salesforce_id} (after filtering by size/type).")
            return set() # Return empty set
        document_ids = {record["ContentDocumentId"] for record in files_to_download_records}
        return document_ids
    except Exception as e:
        logger.error(f"Error querying processable files for Salesforce ID {salesforce_id}: {e}", exc_info=True)
        return set()

def sanitize_filename(filename):
    # Replace colons, slashes, and other problematic characters
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # Remove leading/trailing spaces and periods
    sanitized = sanitized.strip('. ')
    return sanitized

# Removed validate_sf() function as authentication will be handled by the calling view.

def Download_files(sf_client, DOWNLOAD_DIR, filtered_document_ids):
    """
    Downloads files from Salesforce.
    Accepts an authenticated Salesforce client instance.
    Returns a list of successfully downloaded file paths.
    """
    downloaded_paths = []
    if not os.path.exists(DOWNLOAD_DIR):
        try:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            logger.info(f"Created download directory: {DOWNLOAD_DIR}")
        except OSError as e:
            logger.error(f"Could not create download directory {DOWNLOAD_DIR}: {e}", exc_info=True)
            return downloaded_paths # Return empty list if dir creation fails

    for content_document_id in filtered_document_ids:
        try:
            # Get Latest Version of the File
            content_version_query = f"SELECT Id,FileExtension, Title, VersionData FROM ContentVersion WHERE ContentDocumentId = '{content_document_id}' ORDER BY VersionNumber DESC LIMIT 1"
            version_result = sf_client.query(content_version_query)
            
            if not version_result['records']:
                logger.error(f"Could not find ContentVersion for ContentDocumentId: {content_document_id}")
                continue # Skip to next document ID
                
            version_data = version_result['records'][0]
            version_id = version_data['Id']
            file_name = sanitize_filename(version_data['Title']) + "." + version_data['FileExtension']

            # Download File
            file_url = f"{sf_client.base_url}sobjects/ContentVersion/{version_id}/VersionData"
            file_response = requests.get(file_url, headers={'Authorization': f'Bearer {sf_client.session_id}'})

            if file_response.status_code == 200:
                file_path = os.path.join(DOWNLOAD_DIR, file_name)
                with open(file_path, 'wb') as file:
                    file.write(file_response.content)
                logger.info(f"Downloaded: {file_name} to {file_path}")
                downloaded_paths.append(file_path)
            else:
                logger.warning(f"Failed to download {file_name}. HTTP Status: {file_response.status_code}. Response: {file_response.text}")
        except Exception as e:
            logger.error(f"Error processing Salesforce record {content_document_id if 'content_document_id' in locals() else 'unknown'} for download: {e}", exc_info=True)
            continue
        
    logger.info(f"Salesforce file download process completed. {len(downloaded_paths)} files downloaded to: {DOWNLOAD_DIR}")
    return downloaded_paths

def delete_all_pdfs(folder_path):
    deleted_files_count = 0
    # Check if the folder path exists
    if not os.path.exists(folder_path):
        logger.warning(f"Folder to delete PDFs from does not exist: {folder_path}")
        return deleted_files_count

    # Loop through each file in the folder
    logger.info(f"Attempting to delete PDF files in: {folder_path}")
    for file_name in os.listdir(folder_path):
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the file is a PDF and delete it
        if os.path.isfile(file_path) and file_name.lower().endswith('.pdf'):
            try:
                os.remove(file_path)
                logger.info(f"Deleted PDF: {file_path}")
                deleted_files_count +=1
            except OSError as e:
                logger.error(f"Error deleting PDF {file_path}: {e}", exc_info=True)
    return deleted_files_count


# extract_gdrive_folder_id is imported from .google_drive_folder_downloader
# def extract_folder_id(url):
    """Extracts the folder ID from a Google Drive folder URL."""
#    if 'folders/' in url:
#        parts = url.split('/')
#        return parts[parts.index('folders') + 1]
#    return url

def authenticate_google_drive():
    """Authenticate and return the Google Drive service.
    WARNING: Uses InstalledAppFlow, which is not suitable for unattended server environments.
    Consider using a Service Account for server-side Google Drive access.
    """
    creds = None
    logger.warning("Attempting Google Drive authentication using InstalledAppFlow. This is not recommended for server environments.")

    # Load saved credentials if they exist
    if os.path.exists(CREDENTIALS_FILE):
        try:
            creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)
        except Exception as e:
            logger.error(f"Error loading credentials from {CREDENTIALS_FILE}: {e}", exc_info=True)
            creds = None # Ensure creds is None if loading fails
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing Google Drive token: {e}", exc_info=True)
                creds = None # Refresh failed
        else: # No creds, or creds exist but no refresh token (e.g. first time or bad creds file)
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                # run_local_server will attempt to open a browser, which won't work on a headless server.
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Error during Google Drive InstalledAppFlow (run_local_server): {e}", exc_info=True)
                raise ConnectionError(f"Failed to authenticate with Google Drive via interactive flow: {e}") # Raise a more specific error
        
        # Save the credentials for the next run if successfully obtained
        if creds and creds.valid:
            try:
                with open(CREDENTIALS_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Error saving Google Drive credentials to {CREDENTIALS_FILE}: {e}", exc_info=True)
    
    if not creds or not creds.valid:
        raise ConnectionError("Could not obtain valid Google Drive credentials.")

    service = build("drive", "v3", credentials=creds)
    return service

def download_gdrive_file_content(service, file_id):
    """Downloads a single file's content from Google Drive into memory."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            logger.debug(f"GDrive Download progress for file ID {file_id}: {int(status.progress() * 100)}%")
    fh.seek(0) # Reset stream position to the beginning
    return fh


def download_folder(service, folder_id, download_path):
    """Downloads all files from a Google Drive folder."""
    downloaded_file_paths = []
    messages = []

    # Ensure the download path exists
    try:
        os.makedirs(download_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create download path {download_path}: {e}", exc_info=True)
        messages.append(f"Error: Could not create download directory {download_path}.")
        return downloaded_file_paths, messages


    page_token = None
    while True:
        try:
            results = service.files().list(
                pageSize=100, fields="nextPageToken, files(id, name, mimeType)", # Added mimeType
                q=f"'{folder_id}' in parents and trashed=false", # Exclude trashed files
                pageToken=page_token
            ).execute()
        except Exception as e:
            logger.error(f"Error listing files in GDrive folder {folder_id}: {e}", exc_info=True)
            messages.append(f"Error listing files in Google Drive folder: {e}")
            break # Stop if listing fails

        files = results.get("files", [])
        if not files:
            msg = f"No files found in Google Drive folder ID: {folder_id}"
            messages.append(msg)
            logger.info(msg)
            break

        for file_data in files:
            # Skip Google Workspace files like Google Docs, Sheets, Slides unless explicitly handled
            if file_data['mimeType'].startswith('application/vnd.google-apps'):
                logger.info(f"Skipping Google Workspace file: {file_data['name']} (MIME type: {file_data['mimeType']})")
                messages.append(f"Skipped Google Workspace file: {file_data['name']}")
                continue

            messages.append(f"Preparing to retrieve: {file_data['name']}")
            logger.info(f"Preparing to retrieve GDrive file: {file_data['name']}")
            
            # download_file now refers to the one defined in this script
            downloaded_path = download_file(service, file_data["id"], download_path, file_data["name"])
            if downloaded_path:
                downloaded_file_paths.append(downloaded_path)
            else:
                messages.append(f"Failed to download {file_data['name']}.") # Add failure message
        
        page_token = results.get("nextPageToken", None)
        if page_token is None:
            break
    return downloaded_file_paths, messages

def download_file(service, file_id, download_path, filename):
    """Downloads a single file from Google Drive to a local path."""
    local_file_path = os.path.join(download_path, filename)
    try:
        fh_memory = download_gdrive_file_content(service, file_id) # Get content in memory
        with open(local_file_path, 'wb') as f_disk:
            f_disk.write(fh_memory.read())
        logger.info(f"GDrive file {filename} saved to {local_file_path}.")
        return local_file_path
    except Exception as e:
        logger.error(f"Error downloading or writing GDrive file {filename} (ID: {file_id}) to {local_file_path}: {e}", exc_info=True)
        return None


def delete_files_in_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Iterate over all the files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Check if it is a file, not a directory
            if os.path.isfile(file_path):
                try:
                    # Delete the file
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
                except OSError as e:
                    logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
    else:
        logger.warning(f"Folder not found or not a directory, cannot delete files: {folder_path}")


def extract_salesforce_record_id(url): # Renamed for clarity
    # Split the URL by '/' character
    parts = url.split('/')

    # Loop through the parts using enumerate
    for _, part in enumerate(parts):
        # Salesforce IDs are typically 15 or 18 characters long and follow a specific pattern
        if (len(part) == 18 or len(part) == 15) and part.isalnum():
            # Further check if it's likely an ID (e.g., starts with common prefixes like 001, 003, 500, etc.)
            # This is a loose check, as ID prefixes vary.
            if len(part) == 18 or (len(part) == 15 and re.match(r"^[a-zA-Z0-9]{15}$", part)):
                 # Check for common Salesforce ID patterns (alphanumeric)
                if re.match(r"^[a-zA-Z0-9]+$", part):
                    # Check if it's not part of a known non-ID path segment like 'sObject'
                    # This is a heuristic and might need refinement based on URL structures
                    if 'sobjects' not in url.lower() or part.lower() != 'sobjects':
                        logger.debug(f"Extracted Salesforce ID candidate: {part} from URL: {url}")
                        return part
    
    logger.warning(f"No valid Salesforce ID found in URL: {url}")
    return None


def validate_link(link_input, link_type_from_user_selection):
    """
    Validates if the provided link matches the expected type (Salesforce or Google Drive).
    Args:
        link_input (str): The URL to validate.
        link_type_from_user_selection (str): "Salesforce" or "Google Drive".
    Returns:
        tuple: (is_valid_boolean, message_string, detected_link_type_string_or_None)
    """
    # Set up validation patterns
    # Salesforce pattern updated to be more inclusive of Experience Cloud sites and standard domains
    #salesforce_pattern = r"https?://([a-zA-Z0-9\-]+\.)*(salesforce\.com|force\.com|visualforce\.com|lightning\.force\.com|vf\.force\.com|my\.site\.com|sandbox\.my\.salesforce\.com|vf\.force\.com|my\.salesforce\.com)([:\d+])?/.*"
    salesforce_pattern = r"https?://([a-zA-Z0-9\-]+\.)*(salesforce\.com|force\.com|visualforce\.com|lightning\.force\.com|vf\.force\.com|my\.site\.com|sandbox\.my\.salesforce\.com|my\.salesforce\.com)([:\d+])?/.*"

    #google_drive_pattern = r"https?://([\w-]+\.)*drive\.google\.com/(file/d/|drive/folders/|folderview\?id=).*"
    google_drive_pattern = r"https?://([\w-]+\.)*drive\.google\.com(/.*/folders/|/folderview\?id=)([a-zA-Z0-9_-]{20,}).*"


    is_valid = False
    message = ""
    detected_type = None

    if not link_input or not isinstance(link_input, str):
        message = "Link input is empty or not a string."
        return is_valid, message, detected_type

    if link_type_from_user_selection == "Salesforce":
        if re.match(salesforce_pattern, link_input, re.IGNORECASE):
            is_valid = True
            message = "Valid Salesforce link detected."
            detected_type = "Salesforce"
        else:
            message = "This doesn't appear to be a valid Salesforce link. Expected domains like 'salesforce.com', 'force.com', 'my.site.com', etc."
    elif link_type_from_user_selection == "Google Drive":
        if re.match(google_drive_pattern, link_input, re.IGNORECASE):
            is_valid = True
            message = "Valid Google Drive link detected."
            detected_type = "Google Drive"
        else:
            message = "This doesn't appear to be a valid Google Drive link. Expected 'drive.google.com/file/...', 'drive.google.com/drive/folders/...', or 'drive.google.com/folderview?id=...'."
    else:
        message = f"Unknown link type for validation: {link_type_from_user_selection}"

    logger.info(f"Link validation for '{link_input}' (type: {link_type_from_user_selection}): Valid={is_valid}, Message='{message}', Detected='{detected_type}'")
    return is_valid, message, detected_type


def get_web_accessible_url(absolute_file_path):
    """
    Converts an absolute file path on the server to a web-accessible URL,
    assuming the file is within Django's MEDIA_ROOT.
    """
    if not absolute_file_path:
        logger.warning("get_web_accessible_url received an empty path.")
        return None

    media_root_str = str(settings.MEDIA_ROOT)
    if settings.MEDIA_ROOT and absolute_file_path.startswith(media_root_str):
        media_root_for_relpath = media_root_str if media_root_str.endswith(os.sep) else media_root_str + os.sep
        try:
            relative_path = os.path.relpath(absolute_file_path, media_root_for_relpath)
        except ValueError as e: # Can happen if paths are on different drives on Windows
            logger.error(f"Could not determine relative path for {absolute_file_path} from {media_root_for_relpath}: {e}")
            return None

        media_url_prefix = settings.MEDIA_URL
        if not media_url_prefix.endswith('/'):
            media_url_prefix += '/'
        
        # Ensure relative_path parts are URL-encoded if they contain special characters,
        # though os.sep replacement handles the common case.
        # For more complex scenarios, urllib.parse.quote might be needed per path segment.
        final_url = urljoin(media_url_prefix, relative_path.replace(os.sep, "/"))
        logger.debug(f"Generated web URL: {final_url} from relative_path: {relative_path}")
        return final_url
    else:
        logger.error(f"File path {absolute_file_path} is NOT under MEDIA_ROOT ({media_root_str}). Cannot generate web URL.")
        return None

def convert_pdf_to_jpeg_pymupdf(pdf_folder, output_folder, dpi=300):
    """
    Alternative PDF to JPEG conversion using PyMuPDF.
    Now also includes original image files found in the pdf_folder.
    Returns a list of dictionaries, each representing a file (PDF or original image) and its displayable image paths.
    """
    processed_files_list = []
    if not os.path.exists(pdf_folder):
        logger.error(f"PDF folder not found: {pdf_folder}")
        return processed_files_list

    if not output_folder:
        logger.warning("Output folder not specified for PDF conversion, using PDF folder as output.")
        output_folder = pdf_folder
    
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder, exist_ok=True)
            logger.info(f"Created output folder for JPEGs: {output_folder}")
        except OSError as e:
            logger.error(f"Could not create output folder {output_folder}: {e}", exc_info=True)
            return processed_files_list

    # Set to keep track of original filenames that have been processed (either as PDF or original image)
    handled_original_filenames = set()

    # Pass 1: Process PDFs
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"): # Make check case-insensitive
            original_pdf_path = os.path.join(pdf_folder, filename)
            original_pdf_name_no_ext = os.path.splitext(filename)[0]

            handled_original_filenames.add(filename) # Mark this original PDF filename as handled

            pdf_entry = {
                "id": original_pdf_name_no_ext, # Used as a base for display name
                "original_file_name_full": filename,
                "original_file_path": os.path.abspath(original_pdf_path),
                "status": "pending"
            }
            pdf_entry["image_paths"] = [] # Initialize image_paths for this PDF
            pdf_entry["file_type"] = "pdf"

            try:
                # Open the PDF
                pdf_document = fitz.open(original_pdf_path)
                logger.info(f"Processing PDF: {filename} with {len(pdf_document)} pages using PyMuPDF")
                
                if len(pdf_document) == 0:
                    logger.warning(f"PDF {filename} has 0 pages. Skipping conversion.")
                    pdf_entry["status"] = "skipped_empty"
                    pdf_document.close()
                    processed_files_list.append(pdf_entry)
                    continue

                # Process each page
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    # Use a matrix for higher DPI. Default is 72 DPI. Matrix(zoom_x, zoom_y)
                    # For 300 DPI, zoom = 300/72
                    zoom = dpi / 72.0
                    matrix = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=matrix)
                    
                    jpeg_filename = f"{original_pdf_name_no_ext}-page-{page_num + 1}.jpg"
                    output_file = os.path.join(output_folder, jpeg_filename)
                    pix.save(output_file, "jpeg") # Specify format
                    pdf_entry["image_paths"].append(os.path.abspath(output_file))
                    logger.info(f"Page {page_num + 1} of {filename} saved as {output_file} using PyMuPDF.")
                
                pdf_document.close()
                pdf_entry["status"] = "success"
                logger.info(f"PDF {filename} converted successfully using PyMuPDF.")
            except Exception as e:
                logger.error(f"Error converting {filename} using PyMuPDF: {str(e)}", exc_info=True)
                pdf_entry["status"] = "error"
                pdf_entry["error_message"] = str(e)
                # Ensure pdf_document is closed if it was opened
                if 'pdf_document' in locals() and hasattr(pdf_document, 'close') and not pdf_document.is_closed:
                    pdf_document.close()
            processed_files_list.append(pdf_entry)

    # Pass 2: Process original image files (JPG, PNG, JPEG) that were not PDFs
    # Collect all PDF base names to help identify JPEGs generated in Pass 1
    pdf_base_names_from_pass1 = set()
    for entry in processed_files_list:
        if entry.get("file_type") == "pdf":
            pdf_base_names_from_pass1.add(os.path.splitext(entry["original_file_name_full"])[0])

    for filename in os.listdir(pdf_folder):
        if filename in handled_original_filenames:
            continue # Already processed (likely as a PDF in the first pass)

        file_lower = filename.lower()
        if file_lower.endswith(('.jpg', '.jpeg', '.png')):
            # Check if this image was generated from a PDF in Pass 1
            is_generated_jpeg = False
            for pdf_base in pdf_base_names_from_pass1:
                if filename.startswith(pdf_base + "-page-") and file_lower.endswith(".jpg"):
                    is_generated_jpeg = True
                    break
            if is_generated_jpeg:
                logger.debug(f"Skipping '{filename}' in Pass 2 as it appears to be a generated JPEG from a PDF.")
                continue # Skip JPEGs that were generated from PDFs in the first pass

            original_image_path = os.path.join(pdf_folder, filename)
            original_image_name_no_ext = os.path.splitext(filename)[0]
            
            image_entry = {
                "id": original_image_name_no_ext,
                "original_file_name_full": filename,
                "original_file_path": os.path.abspath(original_image_path),
                "file_type": "image",
                "image_paths": [os.path.abspath(original_image_path)], # The image itself is its "page"
                "status": "success" # Original images are considered "successfully processed"
            }
            processed_files_list.append(image_entry)
            logger.info(f"Added original downloaded image {filename} to processed list.")
            handled_original_filenames.add(filename) # Mark as handled to avoid re-adding if logic changes

    logger.info(f"Finished processing download folder. Total items for display: {len(processed_files_list)}")
    return processed_files_list
