import logging
import pandas as pd  # For DataFrame construction if needed for bank data
import os # For os.path.basename
import json
from helper import*
from salesforce_update import *
import requests
from datetime import datetime


logger = logging.getLogger(__name__)

def create_case(sf_client, tax_file_id, contact_id, subject, description, case_sub_type=None, inquiry_type=None, assigned_team=None, case_type=None, status='New', origin='AI Scan', content_document_id=None, sf_url=None):
    """
    Creates a Case record in Salesforce linked to a Tax_File__c record.

    Args:
        sf_client: Authenticated Salesforce client.
        tax_file_id (str): The ID of the parent Tax_File__c record.
        subject (str): The subject line for the case.
        description (str): The detailed description for the case.
        case_sub_type (str, optional): The specific sub-type for the case.
        inquiry_type (str, optional): The inquiry type for the case.
        assigned_team (str, optional): The team to assign the case to.
        case_type (str, optional): The overall type of the case.
        status (str): The status of the case (e.g., 'New', 'Closed').
        origin (str): The origin of the case (e.g., 'AI Scan', 'Web').
        content_document_id (str, optional): The ID of the ContentDocument to link to the case.
        sf_url (str, optional): A Salesforce URL to include in the description for manual processing.

    Returns:
        tuple: (success_bool, message_str, case_id_or_none)
    """
    if not tax_file_id:
        logger.error("Cannot create Case without a tax_file_id.")
        return False, "Tax File ID is missing for Case creation.", None

    final_description = description
    # If a Salesforce URL is provided, append the manual processing instructions to the description.
    if sf_url:
        manual_instructions = (
            f"\n\nPlease use manual scanning at https://scan.lanka.tax by pasting the following link:\n{sf_url}"
        )
        final_description += manual_instructions

    try:
        case_payload = {
            'Subject': subject,
            'Description': final_description,
            'Comments': final_description, # FIX: Add the description content to the internal Comments field as well.
            'ContactId': contact_id,
            'Status': status,
            'Origin': origin,
            'Tax_File__c': tax_file_id,  # Custom lookup field to Tax_File__c
        }
        # Add new fields only if they are provided
        #if case_sub_type:
            #case_payload['Case_Sub_Type__c'] = case_sub_type
        if inquiry_type:
            case_payload['Inquiry_type__c'] = inquiry_type
        if assigned_team:
            case_payload['Assigned_team__c'] = assigned_team
        if case_type:
            case_payload['Type'] = case_type

        logger.info(f"Creating Case with subject: '{subject}' for Tax File ID: {tax_file_id}")
        case_record = sf_client.Case.create(case_payload)
        case_id = case_record.get('id')

        if case_id:
            logger.info(f"Successfully created Case with ID: {case_id}")

            # If a content_document_id is provided, link it to the new case
            if content_document_id:
                try:
                    link_payload = {
                        'ContentDocumentId': content_document_id,
                        'LinkedEntityId': case_id,
                        'ShareType': 'V',  # 'V' for Viewer access
                        'Visibility': 'AllUsers'
                    }
                    sf_client.ContentDocumentLink.create(link_payload)
                    logger.info(f"Successfully linked ContentDocument {content_document_id} to Case {case_id}.")
                except Exception as link_e:
                    logger.error(f"Failed to link document {content_document_id} to case {case_id}: {link_e}")
                    # The case was created, so we don't change the overall success, but we log the linking failure.
            logger.info(f"Successfully created Case with ID: {case_id}")
            return True, f"Case '{subject}' created successfully.", case_id
        else:
            logger.error(f"Failed to create Case. Response: {case_record}")
            return False, f"Failed to create Case. Response: {case_record}", None
    except Exception as e:
        logger.error(f"An error occurred during Case creation: {e}", exc_info=True)
        return False, f"Error creating Case: {e}", None


def is_valid_nic(nic):
    """
    Valid if NIC is either exactly 12 digits or exactly 9 digits followed by V/v.
    """
    if not nic:
        return False
    pattern_long = re.compile(r'^[0-9]{12}$')  # 12 digits
    pattern_old = re.compile(r'^[0-9]{9}[Vv]$')
    return bool(pattern_long.match(nic)) or bool(pattern_old.match(nic))

def is_valid_employer_tin(tin):
    """
    Valid if TIN is exactly 9 digits.
    """
    if not tin:
        return False
    # Pattern for exactly 9 digits
    pattern = re.compile(r'^[0-9]{1,9}$') # Changed to allow 1 to 9 digits
    return bool(pattern.match(tin))

def dispatch_salesforce_update(
    sf_client,
    doc_type_indicator,
    numeric_doc_type,        # NEW Parameter: expected as string ("1", "2", "3", etc.)
    bank_period_type,
    extracted_data,
    original_file_path,     # Can be a list
    request_user,
    comments=None,
    customer_identifier=None,
    tax_file_id=None ,
    request=None, # Pass the request object to access the session
    assessment_year=None
):
    """
    Dispatches the Salesforce update to the appropriate handler.
    This version uses numeric_doc_type if provided; otherwise, it falls back to doc_type_indicator.
    
    Args:
        sf_client: Authenticated Salesforce client.
        doc_type_indicator (str): e.g. "EMPLOYMENT", "BANK CONFIRMATION", "WEALTH MANAGEMENT".
        numeric_doc_type (str): Numeric value as string (e.g. "1" for employment, "2" for bank, "3" for wealth).
        bank_period_type (str): 'M', 'Q', 'Y' (required for bank documents).
        extracted_data: For employment: list with first element as assessment year.
                        For bank: dict with keys: "assessment_year", "general_info", "accounts", etc.
                        For wealth: list with at least 5 elements.
        original_file_paths (list or str): Path(s) to the original document(s).
        request_user: Django user making the request.
        comments (str, optional): User-provided comments for the Case.
        customer_identifier (str, optional): Identifier for the customer (e.g., name, NIC).
        tax_file_id (str, optional): The ID of the Tax_File__c record.
    
    Returns:
        tuple: (success_bool, message_str, record_id_or_none)
    """
    main_record_success = False
    main_record_message = "No Salesforce operation performed for main data."
    main_record_id = None
    sf_operation_details = [] # To collect messages from various SF operations
    if request and hasattr(request, 'session'):
        tax_file_id = request.session.get('tax_file_id')
    try:
        logger.info(
            f"Dispatching Salesforce update: doc_type_indicator='{doc_type_indicator}', " +
            f"numeric_doc_type='{numeric_doc_type}', bank_period_type='{bank_period_type}'"
        )
        
        # Ensure numeric_doc_type is converted to string
        if numeric_doc_type:
            nd = str(numeric_doc_type)
            effective_doc = None
            if nd.strip() == "1":
                effective_doc = "EMPLOYMENT"
            elif nd.strip() == "2":
                effective_doc = "BANK CONFIRMATION"
            elif nd.strip() == "3": # This was incorrect, it should be BANK BALANCE CONFIRMATION
                effective_doc = "BANK BALANCE CONFIRMATION"
            elif nd.strip() == "4":
                effective_doc = "BANK BALANCE CONFIRMATION"
            else:
                effective_doc = doc_type_indicator  # Fallback
        else:
            effective_doc = doc_type_indicator
        
        if effective_doc.upper() == "EMPLOYMENT":
            if not extracted_data or not isinstance(extracted_data, list):
                logger.error("Extracted data for employment is invalid.")
                return False, "Invalid employment data.", None

            nic_extracted = extracted_data[2]
            if not is_valid_nic(nic_extracted):
                logger.error(f"Invalid NIC in employment data: {nic_extracted}")
                return False, "Invalid NIC. Please check your NIC and try again.", None

            # Validate Employer TIN
            employer_tin_extracted = extracted_data[1]
            if not is_valid_employer_tin(employer_tin_extracted):
                logger.error(f"Invalid Employer TIN in employment data: {employer_tin_extracted}")
                return False, "Invalid Employer TIN. It must be exactly 9 digits.", None

            if not assessment_year:
                assessment_year = extracted_data[0]
            if assessment_year=="2022/2023" or assessment_year=="2019/2020":
             logger.info("Calling emp_update for employment.")
             return emp_update_split(sf_client, extracted_data, original_file_path, request_user, assessment_year)
            else:
             logger.info("Calling emp_update for employment.")
             # Call the original emp_update function
             main_record_success, main_record_message, main_record_id = emp_update(sf_client, extracted_data, original_file_path, request_user, assessment_year)

        elif effective_doc.upper() == "BANK CONFIRMATION":
            if not bank_period_type:
                logger.error("Bank period type (M, Q, Y) is required for bank confirmation update.")
                return False, "Bank period type missing.", None
            
            # Define these first by extracting from `extracted_data`
            if not assessment_year:
                assessment_year = extracted_data.get("assessment_year")
            general_info_from_payload = extracted_data.get("general_info", {})
            accounts_from_payload = extracted_data.get("accounts", [])

            nic_extracted = general_info_from_payload.get("nic") # Now get NIC
            if not is_valid_nic(nic_extracted):
                logger.error(f"Invalid NIC in bank data: {nic_extracted}")
                return False, "Invalid NIC. Please check your NIC and try again.", None

            general_bank_info_list = [
                general_info_from_payload.get("bank_name", ""),
                general_info_from_payload.get("customer_name", ""),
                nic_extracted, # Use the validated NIC
                general_info_from_payload.get("issued_date", ""),
                general_info_from_payload.get("wht_agent_tin", ""),
                general_info_from_payload.get("wht_cert_no", ""),
                request_user.email if request_user and hasattr(request_user, 'email') else ""
            ]

            # Initialize lists/dicts for bank data processing
            bank_data_dfs = {} # This will hold the DataFrames keyed by account number
            user_accounts_details_list = [] # Initialize user_accounts_details_list here
            extracted_accounts_data = [] # Changed from user_accounts_details_list
            is_joint_global = extracted_data.get("is_joint", False) # Default for yearly
            joint_persons_global = extracted_data.get("joint_persons", "") # Default for yearly

            if bank_period_type.upper() == "M":
                for acc_detail in accounts_from_payload:
                    account_no = acc_detail.get("account_no")
                    if not account_no or not account_no.strip():
                        logger.warning(f"Skipping monthly account detail due to missing or empty 'account_no': {acc_detail}")
                        continue

                    # Create a dictionary for each account
                    extracted_accounts_data.append({
                        "account_no": account_no,
                        "currency": acc_detail.get("currency", "LKR"),
                        "balance": acc_detail.get("balance", "0"),
                        "is_joint": acc_detail.get("is_joint", False),
                        "joint_persons": acc_detail.get("joint_persons", "")
                    })

                    # Create DataFrame for periods
                    periods_data = acc_detail.get("periods", [])
                    if periods_data:
                        df = pd.DataFrame(periods_data)
                        if 'period_name' in df.columns:
                            df.rename(columns={'period_name': 'Month'}, inplace=True)
                        # RENAME columns to match what df_to_dic_m expects
                        rename_map = {'interest': 'Interest', 'wht': 'WHT', 'wht_cert_no': 'wht_cert_no'}
                        df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

                        bank_data_dfs[account_no] = df
                main_record_success, main_record_message, main_record_id = bank_update_m(sf_client, bank_data_dfs, general_bank_info_list, original_file_path,
                                     request_user, assessment_year, extracted_accounts_data)
            elif bank_period_type.upper() == "Q":
                for acc_detail in accounts_from_payload:
                    account_no = acc_detail.get("account_no")
                    if not account_no or not account_no.strip():
                        logger.warning(f"Skipping quarterly account detail due to missing or empty 'account_no': {acc_detail}")
                        continue

                    extracted_accounts_data.append({
                        "account_no": account_no,
                        "currency": acc_detail.get("currency", "LKR"),
                        "is_joint": acc_detail.get("is_joint", False),
                        "joint_persons": acc_detail.get("joint_persons", "")
                    })

                    # Create DataFrame for periods
                    periods_df = pd.DataFrame(acc_detail.get("periods", []))
                    if not periods_df.empty:
                        periods_df = periods_df.rename(
                            columns={"period_name": "Quarter", "interest": "Interest", "wht": "WHT", "wht_cert_no": "wht_cert_no"}
                        )
                    bank_data_dfs[account_no] = periods_df
                main_record_success, main_record_message, main_record_id = bank_update_q(sf_client, bank_data_dfs, general_bank_info_list, original_file_path,
                                     request_user, assessment_year, extracted_accounts_data)
            elif bank_period_type.upper() == "Y":
                # Extract global joint account info for yearly
                is_joint_global = extracted_data.get("is_joint", False)
                joint_persons_global = extracted_data.get("joint_persons", "")
                
                for acc_detail in accounts_from_payload:
                    account_no = acc_detail.get("account_no")
                    if not account_no or not account_no.strip():
                        logger.warning(f"Skipping yearly account detail due to missing 'account_no': {acc_detail}")
                        continue

                    user_accounts_details_list.append([
                        account_no,
                        acc_detail.get("currency", "LKR"),
                        acc_detail.get("is_joint", is_joint_global),
                        acc_detail.get("joint_persons", joint_persons_global)
                    ])

                    df = pd.DataFrame([acc_detail])
                    bank_data_dfs[account_no] = df

                main_record_success, main_record_message, main_record_id = bank_update_f(
                    sf_client, bank_data_dfs, general_bank_info_list, original_file_path, request_user, assessment_year, user_accounts_details_list
                )
            else:
                logger.error(f"Unknown bank_period_type: {bank_period_type}")
                return False, f"Update logic not defined for bank period type: {bank_period_type}", None

        elif effective_doc.upper() == "WEALTH MANAGEMENT":
            if not extracted_data or not isinstance(extracted_data, list) or len(extracted_data) < 5:
                logger.error("Extracted data for wealth management is invalid or too short.")
                return False, "Invalid wealth management data.", None
            assessment_year = extracted_data[0]
            logger.info("Calling wealth_update.")
            # The wealth_update function in salesforce_update.py needs to be adjusted to accept sf_client and request_user
            main_record_success, main_record_message, main_record_id = wealth_update(sf_client, extracted_data, original_file_path, request_user, assessment_year, tax_file_id)
        
        elif effective_doc.upper() == "BANK BALANCE CONFIRMATION":
            if not extracted_data or not isinstance(extracted_data, dict):
                logger.error("Extracted data for bank balance confirmation is invalid.")
                return False, "Invalid bank balance confirmation data.", None

            general_info = extracted_data.get("general_info", {})
            accounts = extracted_data.get("accounts", [])

            nic_extracted = general_info.get("nic_of_the_person")
            if not is_valid_nic(nic_extracted):
                logger.error(f"Invalid NIC in bank balance confirmation data: {nic_extracted}")
                return False, "Invalid NIC. Please check your NIC and try again.", None
            
            if not assessment_year:
                assessment_year = general_info.get("year_of_assessment")

            logger.info("Calling bank_update_c for bank balance confirmation.")
            main_record_success, main_record_message, main_record_id = bank_update_c(
                sf_client, extracted_data, original_file_path, request_user, assessment_year
            )
        else:
            logger.error(f"Unknown document type indicator for Salesforce update: {effective_doc}")
            return False, f"Update logic not defined for document type: {effective_doc}", None

        # --- CORRECTED: Append comment to the main Tax_File__c record ---
        if tax_file_id and comments and comments.strip():
            try:
                logger.info(f"Attempting to append comment to Tax_File__c record ID: {tax_file_id} from session.")
                
                # 1. Query for the existing comments on the Tax_File__c record
                tax_file_query = f"SELECT scan_comments__c FROM Tax_File__c WHERE Id = '{tax_file_id}' LIMIT 1"
                tax_file_result = sf_client.query(tax_file_query)

                if tax_file_result and tax_file_result.get('totalSize', 0) > 0:
                    tax_file_record = tax_file_result['records'][0]
                    existing_comments = tax_file_record.get('scan_comments__c') or ""
                    
                    # 2. Prepare the new comment entry
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_comment_entry = f"[{timestamp} by {request_user.email}]: {comments}"
                    
                    # 3. Append the new comment
                    updated_comments = f"{existing_comments.strip()}\n\n---\n\n{new_comment_entry}" if existing_comments.strip() else new_comment_entry
                    
                    # 4. Update the record
                    update_payload = {'scan_comments__c': updated_comments}
                    update_result = sf_client.Tax_File__c.update(tax_file_id, update_payload)

                    if update_result == 204:
                        logger.info(f"Successfully appended comment to Tax_File__c record {tax_file_id}.")
                        sf_operation_details.append(f"Comment added to Tax File {tax_file_id}.")
                    else:
                        logger.error(f"Failed to update Tax_File__c record {tax_file_id}. Response: {update_result}")
                        sf_operation_details.append(f"(Warning: Failed to add comment. SF Response: {update_result})")
                else:
                    logger.warning(f"Could not find Tax_File__c record with ID {tax_file_id} to append comment.")
                    sf_operation_details.append(f"(Warning: Could not find Tax File {tax_file_id} to add comment.)")
            except Exception as e_comment:
                logger.error(f"Failed to append comment to Tax_File__c {tax_file_id}: {e_comment}", exc_info=True)
                sf_operation_details.append(f"(Warning: Failed to add comment: {str(e_comment)})")
        
        # Combine main message with any tick update messages
        final_message = main_record_message + " " + " ".join(sf_operation_details)
        return main_record_success, final_message.strip(), main_record_id

    except Exception as e:
        logger.error(f"An error occurred during Salesforce update dispatch: {e}", exc_info=True)
        return False, f"Internal error during Salesforce update: {str(e)}", None