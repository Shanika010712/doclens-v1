import os
import shutil
import json
from simple_salesforce import Salesforce
from salesforce_downloader import *
from identify import identify, bank_identify
from read_file import read_image_file
from sf_update2 import *
import boto3
import json
import re
import smtplib
import sys
import uuid
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
from urllib.parse import unquote_plus
from compare import *
from colorama import Fore
from scan_emp import run_parallel_employment_1920, run_parallel_employment_2021, run_parallel_employment_2122, run_parallel_employment_2223, run_parallel_employment_2324, run_parallel_employment_2425
from scan_bank import *
from scan_balance import *
from google_sheets_logger import log_to_google_sheet # Import the new logger
from process import parse_structured_bank_details, process_bank_text_output, process_bank_text_output_y

# Salesforce authentificate
sf_username = 'tax-jj4a@force.com'
sf_password = 'YA2025Q2'
sf_security_token = 'Wl5AfqUsCWqqlJ3WWmor2O1xH'

# Create the S3 client to download and upload objects from S3
s3_client = boto3.client('s3')

#error handing function
def handle_error(str, e, test_mode=False):
    print(f"{str} - {e}")
    # Convert the error object to a string
    error_str = f"<html><body><h2>{str}</h2><pre>{e}</pre></body></html>"
    if test_mode:
        send_email(["datasci.lankatax@gmail.com"], "Test Error", error_str)
    else:
        send_email([ "datasci.lankatax@gmail.com"], "Error", error_str)
    sys.exit(1)

"""def send_email(receiver_emails, subject, html_body):
    print("\nSending Email ...\n")

    html_body = re.sub(r"^```html\s*|\s*```$", "", html_body.strip())

    # Email configuration
    smtp_server = "smtp.gmail.com"  # For Gmail; adjust for other providers
    smtp_port = 587  # Standard port for TLS
    sender_email = "commaut.lankatax@gmail.com"
    password = "irvf mxwf nkqo nyns"

    # Ensure receiver_emails is a list (convert if it's a single string)
    if isinstance(receiver_emails, str):
        receiver_emails = [receiver_emails]

    # Create the email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)  # Join recipients with commas
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)  # Log in
            server.sendmail(sender_email, receiver_emails, message.as_string())  # Send email
            print("Email sent successfully to:", ", ".join(receiver_emails))
    except Exception as e:
        print("Error sending email:", e)"""


#download from bucket
def download_s3_object(event):
    print("Downloading From Bucket ...\n")
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])  # Decode the S3 object key

            # Save the file without a file extension
            download_path = f'/tmp/{uuid.uuid4()}'  # File with no extension
            s3_client.download_file(bucket, key, download_path)
            print(f"File downloaded from bucket: {bucket}, key: {key}. Saved to: {download_path}")
            return download_path

    except Exception as e:
        handle_error("Error: downloading from bucket", e)

#read doclens event
def read_doclens_event(download_path, test_mode=False):
    
    print("\nReading Comm Event ...\n")
    try:
        with open(download_path, 'r') as file:
            cdc_event = json.load(file)

            # Check changeType and print context
            change_event_header = cdc_event.get("ChangeEventHeader", {})
            change_type = change_event_header.get("changeType", "")
            if change_type == "CREATE":
                print("The event type is CREATE. A new record was added.")
            elif change_type == "UPDATE":  # throw error if update
                raise ValueError("The event type is UPDATE. An existing record was modified.")
            else:
                raise ValueError("Unknown event type in Change Data Capture (CDC) event.")

            # Extract the desired fields
            name = cdc_event.get("Name", "Not Found")
            customer_c = cdc_event.get("Customer__c", "Not Found")
            tax_file_id = cdc_event.get("Tax_File_ID__c", "Not Found")
            #record_id=cdc_event.get("recordIds", "Not Found")
            #channel = cdc_event.get("Channel__c", "Not Found")
            #is_email = channel.lower() == "email" if isinstance(channel, str) else False
           # from_email = cdc_event.get("ks_sn__FromEmail__c", "Not Found")
            object_name = change_event_header.get("entityName", "Not Found")
            record_ids = change_event_header.get("recordIds", [])

            rec_id = record_ids[0] if record_ids else "Not Found"

            # Print the extracted fields
            print(f'Related to ID: "{rec_id}",')
            print(f'Object: "{object_name}"')

            if rec_id == "Not Found":
                raise ValueError("related_to_id not found")
            if object_name != "Tick_Upload_File_names__c":
                raise ValueError("object not tick_upload_file_names__c")
            

        return tax_file_id,name,customer_c
    except Exception as e:
        print(f"Error: reading comm data: {e}")

def _clean_and_extract_pipe_data(raw_text: str | None) -> str | None:
    """
    Extracts the pipe-separated data string from raw AI output,
    ignoring any leading text, numbering, or explanations.
    If no pipe-separated string is found, it cleans and joins numbered lists.
    """
    if not isinstance(raw_text, str):
        return None
    
    # Find a pattern that looks like a pipe-separated string with at least 4 pipes.
    # This is more robust for data extraction.
    pipe_match = re.search(r'((?:[^|\n]+[|]){4,}[^|\n]+)', raw_text)
    if pipe_match:
        return pipe_match.group(1).strip()
    
    # Fallback for numbered lists (e.g., "1. ...\n2. ...")
    lines = raw_text.strip().split('\n')
    if all(re.match(r'^\s*\d+\.\s*', line) for line in lines if line.strip()):
        cleaned_lines = [re.sub(r'^\s*\d+\.?\s*', '', line).strip() for line in lines]
        return '|'.join(cleaned_lines)
        
    return raw_text # Return original if no specific format is detected

def identify_bank_period_from_all_images(image_paths):
    """
    Identifies the bank document period (monthly/yearly) by checking all images.
    It iterates through images until a definitive period is found.
    """
    print(Fore.CYAN + "    - Identifying bank period from all available images...")
    # Default to the result of the first page if no specific period is found in others
    first_page_period = "unknown"

    for i, image_path in enumerate(image_paths):
        try:
            pil_image = read_image_file(image_path)
            period_type = bank_identify(pil_image)
            
            if i == 0:
                first_page_period = period_type  # Store the first page's result as a fallback

            if "month" in period_type.lower() or "year" in period_type.lower():
                print(Fore.GREEN + f"      - Definitive period '{period_type}' found on page {i+1}.")
                return period_type  # Return as soon as a clear type is found
        except Exception as e:
            print(Fore.RED + f"      - Could not process image {image_path} for period identification: {e}")
    
    print(Fore.YELLOW + f"      - No definitive period found. Falling back to first page result: '{first_page_period}'.")
    return first_page_period

def get_contact_id_from_tax_file(sf_client, tax_file_id):
    """
    Queries Salesforce to get the Contact ID from a Tax_File__c record.
    """
    print(f"  - Fetching Contact ID for Tax File: {tax_file_id}")
    try:
        query = f"SELECT Contact_ID__c FROM Tax_File__c WHERE Id = '{tax_file_id}' LIMIT 1"
        result = sf_client.query(query)
        if result['totalSize'] > 0 and result['records'][0].get('Contact_ID__c'):
            contact_id = result['records'][0]['Contact_ID__c']
            print(f"  - Found Contact ID: {contact_id}")
            return contact_id, None
        else:
            err_msg = f"No Contact_ID__c found for Tax_File__c ID: {tax_file_id}"
            print(Fore.RED + f"  - {err_msg}")
            return None, err_msg
    except Exception as e:
        err_msg = f"Error querying for Contact ID: {e}"
        print(Fore.RED + f"  - {err_msg}")
        return None, err_msg

def get_customer_id_from_tax_file(sf_client, tax_file_id):
    """
    Queries Salesforce to get the parent Customer ID from a Tax_File__c record.
    This is useful for constructing contextual URLs.
    """
    print(f"  - Fetching Customer ID for Tax File: {tax_file_id}")
    try:
        # The field linking Tax_File__c to Customer__c is named Customer_ID__c
        query = f"SELECT Customer_ID__c FROM Tax_File__c WHERE Id = '{tax_file_id}' LIMIT 1"
        result = sf_client.query(query)
        if result['totalSize'] > 0 and result['records'][0].get('Customer_ID__c'):
            customer_id = result['records'][0]['Customer_ID__c']
            print(f"  - Found Customer ID: {customer_id}")
            return customer_id, None
        else:
            err_msg = f"No Customer_ID__c found for Tax_File__c ID: {tax_file_id}"
            print(Fore.RED + f"  - {err_msg}")
            return None, err_msg
    except Exception as e:
        err_msg = f"Error querying for Customer ID: {e}"
        print(Fore.RED + f"  - {err_msg}")
        return None, err_msg

def _get_document_id(sf_client, record_id, name):
    """Fetches and validates the ContentDocumentId to be processed."""
    print(Fore.YELLOW + f"Step 2: Fetching all document titles for Tax File ID: {record_id}")
    title_to_id_map, err = get_doc_list(sf_client, record_id)
    if err:
        raise ValueError(f"Failed to get document list: {err}")
    print(Fore.GREEN + f"Step 2: Found {len(title_to_id_map)} documents available for this Tax File.")

    print(Fore.YELLOW + f"Step 3: Fetching specific document title to be processed for Tax File ID: {record_id}")
    # FIX: Unpack all three return values from get_specific_document_title
    specific_title, err, is_already_processed = get_specific_document_title(sf_client, name)
    if err:
        # If there's an error (like "Document already processed"), return that status.
        if is_already_processed:
            return None, True
        raise ValueError(f"Failed to get specific title: {err}")
    print(Fore.GREEN + f"Step 3: Specific title to process is '{specific_title}'.")

    print(Fore.YELLOW + f"Step 4: Comparing specific title with the list of available documents...")
    matched_title = find_best_title_match(specific_title, title_to_id_map.keys())
    if not matched_title:
        raise ValueError(f"Title '{specific_title}' not found in the list of available documents for this Tax File.")

    print(Fore.GREEN + f"Step 4: Match found! The corresponding title in Salesforce is '{matched_title}'.")
    document_id_to_download = title_to_id_map[matched_title]
    print(Fore.CYAN + f"Step 4: The ContentDocumentId to download is: {document_id_to_download}")
    return document_id_to_download, is_already_processed

def _prepare_and_download_document(sf_client, document_id, record_id, test_mode):
    """Downloads the specified document and returns the local file paths."""
    document_details_list, message = get_document_details_by_id(sf_client, document_id)
    if not document_details_list:
        raise FileNotFoundError(f"Could not get document details for the matched ID: {message}")
    print(Fore.GREEN + f"Step 4: Found {len(document_details_list)} document(s) to download.")

    print(Fore.MAGENTA + "Step 5: Preparing download directory...")
    if test_mode:
        import tempfile
        download_dir = os.path.join(tempfile.gettempdir(), 'development.tmp', f"sf_download_{record_id}")
    else:
        download_dir = os.path.join('/tmp', 'deployment.tmp', f"sf_download_{record_id}")
    os.makedirs(download_dir, exist_ok=True)
    print(Fore.GREEN + f"Step 5: Download directory set to: {download_dir}")

    print(Fore.MAGENTA + "Step 6: Downloading files from Salesforce...")
    downloaded_files = download_salesforce_files(sf_client, document_details_list, download_dir)
    if not downloaded_files:
        raise FileNotFoundError("No files were downloaded from Salesforce.")
    print(Fore.GREEN + f"Step 6: Successfully downloaded {len(downloaded_files)} files.")
    return downloaded_files

def _convert_to_images(file_path, sf_client, record_id, contact_id, document_id):
    """Converts a file (PDF or image) to a list of image paths."""
    file_basename = os.path.basename(file_path)
    if file_basename.lower().endswith('.pdf'):
        pdf_name_no_ext = os.path.splitext(file_basename)[0]
        safe_pdf_name = sanitize_filename(pdf_name_no_ext)
        pdf_image_dir = os.path.join('/tmp', safe_pdf_name)
        os.makedirs(pdf_image_dir, exist_ok=True)
        
        print(Fore.YELLOW + "Step 7: Converting PDF to images...")
        image_paths = convert_pdf_to_jpeg_pymupdf(file_path, pdf_image_dir)
        if not image_paths:
            create_case(
                sf_client, record_id, contact_id,
                subject="Scan Incomplete",
                description=f"Automated scan for {file_basename} is incomplete. The system failed to convert the PDF document to images for processing. Please check the file and try again.",
                # No URL needed here as it's a technical failure.
                case_sub_type="PDF-to-images conversion failed",
                inquiry_type="Internal Bug report",
                assigned_team="Tech",
                case_type="Scan Incomplete",
                content_document_id=document_id)
            return None
        print(Fore.GREEN + f"Step 7: PDF converted to {len(image_paths)} image(s).")
        return image_paths
    elif file_basename.lower().endswith(('.png', '.jpg', '.jpeg')): # noqa: E125
        print(Fore.GREEN + "Step 7: File is an image. Using it directly.")
        return [file_path]
    else:
        print(Fore.YELLOW + f"Step 7: Skipping unsupported file type: {file_basename}")
        return None

def _process_document_images(sf_client, record_id, customer_c, contact_id, document_id, file_path, image_paths, sf_url):
    """Identifies and extracts data from a list of document images."""
    idx = 1 # For logging steps
    print(Fore.CYAN + f"Step 8.{idx}: Identifying document type from all {len(image_paths)} image(s)...")
    all_pil_images = [read_image_file(path) for path in image_paths]
    identification_results = identify(all_pil_images)
    print(Fore.CYAN + f"Step 8.{idx}: Identification results: {identification_results}")

    doc_type_code = get_doc_type_code(identification_results)
    print(Fore.MAGENTA + f"Step 8.{idx}: Document type code: {doc_type_code}")

    tax_year = None
    for item in identification_results:
        match = re.search(r'(\d{4}/\d{4})', str(item))
        if match:
            tax_year = match.group(1)
            break
    
    is_multipage = len(image_paths) > 1
    print(Fore.CYAN + f"Step 9.{idx}: Document has {len(image_paths)} page(s). Identified as doc type {doc_type_code} for year {tax_year}.")
    input_data = all_pil_images if is_multipage else all_pil_images[0]
    print(Fore.GREEN + f"Step 10.{idx}: Processing as a {'multi-page' if is_multipage else 'single-page'} document.")

    if doc_type_code == 1:  # Employment
        print(Fore.MAGENTA + "  - Document Type: Employment")
        employment_extractors = {
            "2024/2025": run_parallel_employment_2425, "2023/2024": run_parallel_employment_2324,
            "2022/2023": run_parallel_employment_2223, "2021/2022": run_parallel_employment_2122,
            "2020/2021": run_parallel_employment_2021, "2019/2020": run_parallel_employment_1920,
        }
        extraction_func = employment_extractors.get(tax_year)
        if extraction_func:
            print(Fore.YELLOW + f"    - Year: {tax_year}")
            result1, result2 = extraction_func(input_data)
            clean_res1 = _clean_and_extract_pipe_data(result1)
            clean_res2 = _clean_and_extract_pipe_data(result2)
            
            success, final_result = compare_results(clean_res1, clean_res2)
            if not success and clean_res1 and clean_res2:
                print(Fore.YELLOW + "Initial comparison failed. Attempting AI decider...")
                success, final_result = decide_with_ai(clean_res1, clean_res2, input_data)
            
            if success and final_result:
                update_success, msg, _ = call_salesforce_update(sf_client, doc_type_code, final_result.split('|'), file_path, record_id, customer_c, tax_year=tax_year)
                if update_success:
                    print(Fore.GREEN + "Data successfully updated in Salesforce.")
                    create_case(sf_client, record_id, contact_id, "Scan Successful", f"Data from {os.path.basename(file_path)} was successfully extracted and updated.", inquiry_type="Perform tax computation", case_type="Scan Successful", content_document_id=document_id)
                else:
                    print(Fore.RED + f"Salesforce update failed: {msg}")
                    create_case(sf_client, record_id, contact_id, "Scan Failed", f"Automated scan for {os.path.basename(file_path)} failed during Salesforce update. Reason: {msg}.", case_sub_type="Salesforce update failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id, sf_url=sf_url)
            else:
                print(Fore.RED + "Extraction comparison and AI decider failed. No update performed.")
                create_case(sf_client, record_id, contact_id, "Scan Failed", f"Automated scan failed for {os.path.basename(file_path)}. All extraction and decision models failed.", case_sub_type="AI decider failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id, sf_url=sf_url)
        else:
            print(Fore.RED + f"    - Unsupported year for Employment: {tax_year}")
            create_case(sf_client, record_id, contact_id, "Scan Failed", f"Automated scan for {os.path.basename(file_path)} failed. Unsupported year for Employment: {tax_year}.", case_sub_type="Unsupported tax year", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id, sf_url=sf_url)

    elif doc_type_code == 2:  # Bank Confirmation
        handle_bank_document_extraction(sf_client, doc_type_code, tax_year, all_pil_images[0], image_paths, file_path, record_id, customer_c, contact_id, document_id)
    
    elif doc_type_code == 4: # Balance Confirmation
        handle_balance_confirmation_extraction(sf_client, doc_type_code, tax_year, input_data, file_path, record_id, customer_c, contact_id, document_id)

    else:
        print(Fore.RED + f"Step 10.{idx}: Unknown document type. No extraction performed.")
        # If the document type is not one of the processable types, create a "Scan Incomplete" case.
        create_case(
            sf_client, record_id, contact_id,
            subject="Scan Incomplete",
            description=f"Automated scan for {os.path.basename(file_path)} is incomplete. The document was identified as a type that is not supported for automated processing.",
            case_sub_type="Unsupported document type",
            inquiry_type="Perform tax computation",
            assigned_team="Processing",
            case_type="Scan Incomplete",
            content_document_id=document_id)

#agent function
def doclens(record_id, name, customer_c, test_mode=False):
    sf_client = None
    contact_id_for_case = None
    document_id_to_download = None
    # --- FIX: Initialize is_already_processed ---
    is_already_processed = False
    # --- End of FIX ---
    sf_url_for_case = None
    try:
        print(Fore.CYAN + "Step 1: Authenticating with Salesforce...")
        sf_client = Salesforce(username=sf_username, password=sf_password, security_token=sf_security_token)
        print(Fore.GREEN + "Step 1: Salesforce client authenticated.")

        contact_id_for_case, err = get_contact_id_from_tax_file(sf_client, record_id)
        if err:
            print(Fore.RED + f"Warning: Could not retrieve Contact ID. Cases will not be linked to a Contact. Reason: {err}")

        # --- Generate the Salesforce URL for manual processing instructions ---
        customer_id_for_url, err = get_customer_id_from_tax_file(sf_client, record_id)
        if customer_id_for_url and not err:
            instance_url = sf_client.base_url.replace(".my.salesforce.com", ".lightning.force.com")
            workspace_path = f"/lightning/r/Customer__c/{customer_id_for_url}/view"
            sf_url_for_case = f"{instance_url}/lightning/r/Tax_File__c/{record_id}/view?ws={workspace_path}"
            print(Fore.GREEN + f"Generated Salesforce URL for cases: {sf_url_for_case}")

        # --- FIX: Get the 'is_already_processed' status ---
        document_id_to_download, is_already_processed = _get_document_id(sf_client, record_id, name)
        if is_already_processed:
            # --- FIX: Create a case when skipping an already processed document ---
            skip_message = f"Document for record '{name}' has already been processed. Skipping scan."
            print(Fore.YELLOW + skip_message)
            create_case(
                sf_client, record_id, contact_id_for_case,
                subject="Scan Incomplete",
                description=f"Automated scan was triggered for a document that has already been processed (Record Name: {name}). The scan was skipped to prevent duplication. No further action is needed unless this is unexpected.",
                case_sub_type="Duplicate scan trigger",
                inquiry_type="Internal Bug report",
                assigned_team="Tech",
                case_type="Scan Incomplete"
            )
            return  # Exit gracefully after creating the case
        # --- End of FIX ---
        
        downloaded_files = _prepare_and_download_document(sf_client, document_id_to_download, record_id, test_mode)

        for file_path in downloaded_files:
            try:
                print(Fore.BLUE + f"\nProcessing file: {os.path.basename(file_path)}")
                image_paths = _convert_to_images(file_path, sf_client, record_id, contact_id_for_case, document_id_to_download)
                
                if image_paths:
                    _process_document_images(sf_client, record_id, customer_c, contact_id_for_case, document_id_to_download, file_path, image_paths, sf_url_for_case)

            except Exception as e:
                print(Fore.RED + f"An error occurred while processing document {file_path}: {e}")
                create_case(
                    sf_client, record_id, contact_id_for_case, 
                    subject="Scan Failed", 
                    description=f"An unexpected error occurred while processing {os.path.basename(file_path)}. Error: {e}. Please use manual scanning at scan.lanka.tax",
                    case_sub_type="Data extraction failed",
                    inquiry_type="Perform tax computation",
                    assigned_team="Processing",
                    case_type="Scan Failed",
                    content_document_id=document_id_to_download,
                    sf_url=sf_url_for_case)
                continue

    except Exception as e:
        print(Fore.RED + f"A critical error occurred in doclens main execution: {e}")
        if sf_client and record_id:
            create_case(
                sf_client, record_id, contact_id_for_case,
                subject="Scan Incomplete",
                description=f"A critical error occurred during the scan process. Error: {e}.",
                case_sub_type="S3 bucket data download failed",
                inquiry_type="Internal Bug report",
                assigned_team="Tech", case_type="Scan Incomplete",
                content_document_id=document_id_to_download,
                sf_url=sf_url_for_case)

def find_best_title_match(specific_title, title_list):
    """
    Finds the best match for a specific title in a list of titles,
    ignoring common formatting differences.
    """
    def normalize(title):
        # Lowercase, remove spaces, and replace common separators with a standard one
        return re.sub(r'[\s:/-]+', '', title.lower())

    normalized_specific = normalize(specific_title)
    for title in title_list:
        if normalize(title) == normalized_specific:
            return title
    return None
        
def handle_bank_document_extraction(sf_client, doc_type_code, tax_year, pil_image, image_paths, pdf_path, record_id, customer_c, contact_id_for_case, document_id_to_download):
    """
    Identifies bank document period (monthly/yearly) and triggers the correct extraction.
    This function is called when the document type is 2 (Bank Confirmation).
    It uses all images for extraction.
    """
    print(Fore.MAGENTA + "  - Document Type: Bank Confirmation")
    # Use the new function to identify period from all images
    bank_period_type = identify_bank_period_from_all_images(image_paths)
    print(Fore.CYAN + f"    - Identified Bank Period: {bank_period_type}")

    result1, result2 = None, None
    period_is_monthly = "month" in bank_period_type.lower()
    period_is_yearly = "year" in bank_period_type.lower()
    
    # Determine which extraction function to call based on year and period
    extraction_map = {
        "2024/2025": {"month": run_parallel_bank_m_2425, "year": run_parallel_bank_y_2425},
        "2023/2024": {"month": run_parallel_bank_m_2324, "year": run_parallel_bank_y_2324},
        "2022/2023": {"month": run_parallel_bank_m_2223, "year": run_parallel_bank_y_2223},
        "2021/2022": {"month": run_parallel_bank_m_2122, "year": run_parallel_bank_y_2122},
        "2020/2021": {"month": run_parallel_bank_m_2021, "year": run_parallel_bank_y_2021},
        "2019/2020": {"month": run_parallel_bank_m_1920, "year": run_parallel_bank_y_1920},
    }

    year_extractors = extraction_map.get(tax_year)
    if year_extractors:
        extraction_func = None
        if period_is_monthly:
            extraction_func = year_extractors.get("month")
        elif period_is_yearly:
            extraction_func = year_extractors.get("year")

        if not extraction_func:
            print(Fore.RED + f"    - Unsupported combination for Bank Confirmation: Year {tax_year}, Period {bank_period_type}")
            create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan for {os.path.basename(pdf_path)} failed. Unsupported bank document for Year: {tax_year} and Period: {bank_period_type}.", case_sub_type="Unsupported tax year", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url_for_case) # sf_url is not defined here, need to pass it
            return

        print(Fore.YELLOW + f"    - Year: {tax_year}")
        # Use all image_paths for multi-page, or just the single pil_image for single-page
        # --- FIX: Load all images into PIL objects for the extractor ---
        print(Fore.CYAN + "    - Loading all page images for extraction...")
        all_pil_images = [read_image_file(path) for path in image_paths]
        input_data = all_pil_images
        result1, result2 = extraction_func(input_data)

    if result1 is None:
        print(Fore.RED + "Extraction for bank data returned an empty result. No update performed.")
        create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", "Automated scan failed for {os.path.basename(pdf_path)}. AI model returned no data.", case_sub_type="Data extraction failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url_for_case)
        return

    print(Fore.YELLOW + f"Extracted result 1 (raw): {result1}")
    print(Fore.YELLOW + f"Extracted result 2 (raw): {result2}")
    
    # --- NEW: Add comparison and AI decider logic for bank documents ---
    success, final_result = compare_results(result1, result2)
    if not success and result1 and result2:
        print(Fore.YELLOW + "Initial comparison failed for bank data. Attempting AI decider...")
        success, final_result = decide_with_ai(result1, result2, input_data)

    if not success or not final_result:
        print(Fore.RED + "Bank data extraction comparison and AI decider failed. No update performed.")
        create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan failed for {os.path.basename(pdf_path)}. All extraction and decision models failed for the bank document.", case_sub_type="AI decider failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url_for_case)
        return
    # --- End of new logic ---

    bank_period_char = "Y" if period_is_yearly else "M" if period_is_monthly else None
    
    # The raw AI output is a string that needs to be processed into a list of lists.
    if bank_period_char == "Y":
        processed_list = process_bank_text_output_y(final_result) # Use final_result
    else: # Monthly or Quarterly
        processed_list = process_bank_text_output(final_result) # Use final_result
    
    if processed_list:
        # This list is then parsed into the final dictionary structure.
        parsed_data = parse_structured_bank_details(processed_list, bank_period_char, tax_year)
        
        if parsed_data:
            update_success, msg, _ = call_salesforce_update(sf_client, doc_type_code, parsed_data, pdf_path, record_id, 
                                                             customer_c, bank_period_type=bank_period_char, tax_year=tax_year)

            if update_success:
                print(Fore.GREEN + "Data successfully updated in Salesforce.")
                create_case(sf_client, record_id, contact_id_for_case, "Scan Successful", f"Data from {os.path.basename(pdf_path)} was successfully extracted and updated.", inquiry_type="Perform tax computation", case_type="Scan Successful", content_document_id=document_id_to_download)
            else:
                print(Fore.RED + f"Salesforce update failed: {msg}")
                create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan for {os.path.basename(pdf_path)} failed during Salesforce update. Reason: {msg}.", case_sub_type="Salesforce update failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url_for_case)
        else:
            print(Fore.RED + "Bank data parsing returned no data. No update performed.")
            create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan failed for {os.path.basename(pdf_path)}. Could not parse the data from the AI model.", case_sub_type="Data extraction failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url_for_case)
    else:
        print(Fore.RED + "Bank data processing returned an empty list. No update performed.")
        create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan failed for {os.path.basename(pdf_path)}. AI model returned no parsable data.", case_sub_type="Data extraction failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url_for_case)
def handle_balance_confirmation_extraction(sf_client, doc_type_code, tax_year, input_data, file_path, record_id, customer_c, contact_id_for_case, document_id_to_download, sf_url):
    """
    Handles the extraction logic for Bank Balance Confirmation documents.
    """
    from process import parse_balance_confirmation_output # Local import to break circular dependency

    print(Fore.MAGENTA + "  - Document Type: Balance Confirmation")

    balance_extractors = {
        "2024/2025": run_parallel_balance_2425,
        "2023/2024": run_parallel_balance_2324,
        "2022/2023": run_parallel_balance_2223,
        "2021/2022": run_parallel_balance_2122,
        "2020/2021": run_parallel_balance_2021,
        "2019/2020": run_parallel_balance_1920,
    }
    extraction_func = balance_extractors.get(tax_year)

    if extraction_func:
        print(Fore.YELLOW + f"    - Year: {tax_year}")
        result1, result2 = extraction_func(input_data)
        clean_res1 = _clean_and_extract_pipe_data(result1)
        clean_res2 = _clean_and_extract_pipe_data(result2)

        success, final_result = compare_results(clean_res1, clean_res2)
        if not success and clean_res1 and clean_res2:
            print(Fore.YELLOW + "Initial comparison failed. Attempting AI decider...")
            success, final_result = decide_with_ai(clean_res1, clean_res2, input_data)

        if success and final_result:
            # The final_result for balance confirmation is a pipe-separated string
            # that needs to be parsed into the correct dictionary structure for sf_update2
            parsed_data = parse_balance_confirmation_output(final_result)
            update_success, msg, _ = call_salesforce_update(sf_client, doc_type_code, parsed_data, file_path, record_id, customer_c, tax_year=tax_year)
            if update_success:
                print(Fore.GREEN + "Data successfully updated in Salesforce.")
                create_case(sf_client, record_id, contact_id_for_case, "Scan Successful", f"Data from {os.path.basename(file_path)} was successfully extracted and updated.", inquiry_type="Perform tax computation", case_type="Scan Successful", content_document_id=document_id_to_download)
            else:
                print(Fore.RED + f"Salesforce update failed: {msg}")
                create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan for {os.path.basename(file_path)} failed during Salesforce update. Reason: {msg}.", case_sub_type="Salesforce update failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url)
        else:
            print(Fore.RED + "Extraction comparison and AI decider failed for Balance Confirmation. No update performed.")
            create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan for {os.path.basename(file_path)} failed. All extraction and decision models failed for Balance Confirmation.", case_sub_type="AI decider failed", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url)
    else:
        print(Fore.RED + f"    - Unsupported year for Balance Confirmation: {tax_year}")
        create_case(sf_client, record_id, contact_id_for_case, "Scan Failed", f"Automated scan for {os.path.basename(file_path)} failed. Unsupported year for Balance Confirmation: {tax_year}.", case_sub_type="Unsupported tax year", inquiry_type="Perform tax computation", assigned_team="Processing", case_type="Scan Failed", content_document_id=document_id_to_download, sf_url=sf_url)

        
DOCUMENT_TYPE_MAP = {
    "employment": 1,
    "bank confirmation": 2,
    "balance confirmation": 4, # Changed to 4 to match sf_update2
    #"tax file": 4,
    # Add more types as needed
}
DOC_CODE_TO_INDICATOR = {v: k.upper() for k, v in DOCUMENT_TYPE_MAP.items()}

def normalize_doc_type(doc_type_str):
    # Lowercase, remove spaces and special chars for robust matching
    return re.sub(r'[^a-z0-9]', '', doc_type_str.lower())

def get_doc_type_code(identification_results):
    for item in identification_results:
        norm_item = normalize_doc_type(str(item))
        for key in DOCUMENT_TYPE_MAP:
            if normalize_doc_type(key) in norm_item:
                return DOCUMENT_TYPE_MAP[key]
    return None  # Unknown type

def run(event, test=False):
    print("inside the run function")  # add new log to the code

    if test:
        # In test mode, use the local JSON file.
        download_path = os.path.join(os.path.dirname(__file__), "test1.json")
        if not os.path.exists(download_path):
            print(Fore.RED + f"Test file not found at {download_path}. Aborting.")
            # No case can be created here as we don't have any Salesforce record context.
            return
    else:
        download_path = download_s3_object(event)
        if not download_path:
            print(Fore.RED + "Failed to download file from S3. Aborting.")
            # A "Scan Incomplete" case should be created, but we lack the record_id from the event file. This is a limitation.
            return

    try:
        record_id, name, customer_c = read_doclens_event(download_path)
        if record_id:
            print(f"Extracted Tax File ID: {record_id}")
            doclens(record_id, name, customer_c, test_mode=test)
            print(Fore.CYAN + "doclens processing finished.")
        else: # This part is tricky as we don't have a record_id to link the case to.
            print(Fore.RED + "Failed to extract a valid record_id from the event file. Cannot create a linked case.")
            # We could try to create an unlinked case if we had a sf_client instance here,
            # but the flow is designed to create the client inside doclens.
            # This is a scenario where logging is critical.
    except Exception as e:
        print(Fore.RED + f"An error occurred in the main run function: {e}")
        # This is likely an "event json read failed" scenario.
        # We cannot create a case because we don't have sf_client or record_id.
        # This highlights the importance of external logging for the lambda function itself.


def call_salesforce_update(sf_client, doc_type_code, result, pdf_path, record_id, customer_c, bank_period_type=None, tax_year=None):
    # Create a mock request_user object for the agent environment
    class MockUser:
        email = "agent@example.com"  # Using a placeholder email

    # --- Log the data to Google Sheets before sending to Salesforce ---
    log_to_google_sheet(
        doc_type=DOC_CODE_TO_INDICATOR.get(doc_type_code, "UNKNOWN"),
        contact=customer_c,
        tax_year=tax_year,
        tax_file_id=record_id,
        status="Attempting Salesforce Update",
        data_payload=result
    )
    request_user = MockUser()

    doc_type_indicator = DOC_CODE_TO_INDICATOR.get(doc_type_code)

    return dispatch_salesforce_update(
        sf_client=sf_client,
        doc_type_indicator=doc_type_indicator,
        numeric_doc_type=str(doc_type_code),
        bank_period_type=bank_period_type,
        extracted_data=result, # Pass the result directly (string for emp, dict for bank)
        original_file_path=pdf_path,
        request_user=request_user,
        tax_file_id=record_id,
        assessment_year=tax_year
    )

def sanitize_filename(filename):
    # Replace forbidden and problematic characters with underscore
    return re.sub(r'[\\/:*?"<>|()\s]', '_', filename)