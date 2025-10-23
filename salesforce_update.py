#import library
from simple_salesforce import Salesforce
#
import logging

#read file content for creds
from read_file import *

#get the timestamp
#from time_stamp import timenow
import base64

import pandas as pd

import re
logger = logging.getLogger(__name__) # Ensure logger is defined

# def limit_acc():
#     # Step 1: Get the length of list1
#     my_list = st.session_state.accounts_list
#     #get the unique count
#     unique_count = len(set(tuple(item) for item in my_list))
#     st.session_state.user_accounts = st.session_state.user_accounts[-unique_count:]

def clean_value(value):
    # Use regex to remove all non-numeric characters and commas
    value = str(value)
    cleaned_value = re.sub(r'[^0-9.]', '', value)
    if cleaned_value == '':
        cleaned_value = 0
    return cleaned_value

# link employee T10 image
def upload_image_and_link(parent_record_id, image_file_path):
    try:
        # Read Salesforce credentials
        sf_username = read_file_content("sf_username.txt")
        sf_password = read_file_content("sf_password.txt")
        sf_sec_token = read_file_content("sf_sec_token.txt")

        # Create a connection to Salesforce instance
        sf = Salesforce(
            username=sf_username,
            password=sf_password,
            security_token=sf_sec_token
        )
        for paths in image_file_path:
            # Upload the image file to Salesforce
            file_name = paths.split('/')[-1]

            # Read the file in binary mode and encode it in base64
            with open(paths, 'rb') as file:
                file_data = file.read()
                base64_file_data = base64.b64encode(file_data).decode('utf-8')

            # Create ContentVersion record
            content_version = sf.ContentVersion.create({
                'Title': file_name,
                'PathOnClient': file_name,
                'VersionData': base64_file_data
            })

            # Retrieve the ContentDocumentId by querying the created ContentVersion
            content_version_id = content_version['id'][:15]
            query = f"SELECT ContentDocumentId FROM ContentVersion WHERE Id = '{content_version_id}'"
            content_version_record = sf.query(query)
            content_document_id = content_version_record['records'][0]['ContentDocumentId']

            # Link the uploaded document to the parent record
            content_document_link = sf.ContentDocumentLink.create({
                'ContentDocumentId': content_document_id,
                'LinkedEntityId': parent_record_id,
                'ShareType': 'V',  # 'V' for Viewer, 'C' for Collaborator, etc.
                'Visibility': 'AllUsers'  # or 'InternalUsers' for internal use only
            })

            logger.info("File uploaded and linked successfully!")
    except Exception as e:
        print("Error uploading file or linking document:", e)

def process_data(data, pos):
    # Iterate through the list and clean only the elements at positions in pos
    for i in range(len(data)):
        if i in pos:
            data[i] = clean_value(data[i])
    return data

def remove_duplicate_months(df):
    """
    This function removes rows with duplicate month values in the 'Month' column,
    keeps only the first occurrence of each duplicate value, drops the fourth column,
    and removes all characters from columns 2 and 3 except for numbers and periods.
    
    Parameters:
    df (pandas.DataFrame): The input DataFrame with a 'Month' column and other data columns.
    
    Returns:
    pandas.DataFrame: A DataFrame with the fourth column removed and cleaned columns 2 and 3.
    """
    # Drop the fourth column
    #df = df.drop(df.columns[3], axis=1)

    # Remove all characters except numbers and periods in columns 2 and 3
    df.iloc[:, 1] = (
    df.iloc[:, 1]
    .astype(str)
    .apply(lambda x: re.sub(r'[^0-9.]', '', x))  # Remove non-numeric characters
    .replace('', '0')  # Replace empty strings with '0'
    .astype(float)  # Convert to float
    )

    df.iloc[:, 2] = (
    df.iloc[:, 2]
    .astype(str)
    .apply(lambda x: re.sub(r'[^0-9.]', '', x))  # Remove non-numeric characters
    .replace('', '0')  # Replace empty strings with '0'
    .astype(float)  # Convert to float
    )

    # Fill missing values with zeros in columns 2 and 3
    df.iloc[:, 1:3] = df.iloc[:, 1:3].fillna('0')
    
    # Check for duplicates in the 'Month' column, keep the first occurrence and remove subsequent ones
    df_cleaned = df.drop_duplicates(subset='Month', keep='first')
    
    return df_cleaned

def remove_duplicate_quarters(df):
    """
    This function removes rows with duplicate month values in the 'Quarter' column,
    keeps only the first occurrence of each duplicate value, drops the fourth column,
    and removes all characters from columns 2 and 3 except for numbers and periods.
    
    Parameters:
    df (pandas.DataFrame): The input DataFrame with a 'Quarter' column and other data columns.
    
    Returns:
    pandas.DataFrame: A DataFrame with the fourth column removed and cleaned columns 2 and 3.
    """
    # Drop the fourth column
    df = df.drop(df.columns[3], axis=1)
    
    # Remove all characters except numbers and periods in columns 2 and 3
    df.iloc[:, 1] = (
    df.iloc[:, 1]
    .astype(str)
    .apply(lambda x: re.sub(r'[^0-9.]', '', x))  # Remove non-numeric characters
    .replace('', '0')  # Replace empty strings with '0'
    .astype(float)  # Convert to float
    )
    
    df.iloc[:, 2] = (
    df.iloc[:, 2]
    .astype(str)
    .apply(lambda x: re.sub(r'[^0-9.]', '', x))  # Remove non-numeric characters
    .replace('', '0')  # Replace empty strings with '0'
    .astype(float)  # Convert to float
    )

    # Fill missing values with zeros in columns 2 and 3
    df.iloc[:, 1:3] = df.iloc[:, 1:3].fillna('0')
    
    # Check for duplicates in the 'Quarter' column, keep the first occurrence and remove subsequent ones
    df_cleaned = df.drop_duplicates(subset='Quarter', keep='first')
    
    return df_cleaned

def fill_dfs_m(df_dict):
    # Iterate over dictionary of DataFrames and process each one
    for key in df_dict:
        df_dict[key] = process_dataframe_m(df_dict[key])
    return df_dict
def fill_dfs_f(df_dict):
    # Iterate over dictionary of DataFrames and process each one
    for key in df_dict:
        df_dict[key] = process_dataframe_yf(df_dict[key])
    return df_dict

def fill_dfs_q(df_dict):
    # Iterate over dictionary of DataFrames and process each one
    for key in df_dict:
        df_dict[key] = process_dataframe_q(df_dict[key])
    return df_dict


def process_dataframe_m(df):
    # Create a list of months from April to March for sorting
    months_order = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'January', 'February', 'March']
    
    # Check if all 12 months are present
    existing_months = df['Month'].tolist()
    missing_months = [month for month in months_order if month not in existing_months]
    
    # If there are missing months, create a DataFrame with zeros for those months
    if missing_months:
        missing_df = pd.DataFrame({'Month': missing_months, 'Value': [0] * len(missing_months)})  # Assuming the column with data is named 'Value'
        df = pd.concat([df, missing_df])
    
    # Sort by the custom month order (April to March)
    df['Month'] = pd.Categorical(df['Month'], categories=months_order, ordered=True)
    df = df.sort_values('Month').reset_index(drop=True)

    #remove dupliate rows and replace null values
    remove_duplicate_months(df)
    return df

def process_dataframe_q(df):
    # Create a list of months from April to March for sorting
    quarter_order = ['Q1','Q2','Q3','Q4']
    
    # Check if all 12 months are present
    existing_quarters = df['Quarter'].tolist()
    missing_quarters = [quarter for quarter in quarter_order if quarter not in existing_quarters]
    
    # If there are missing months, create a DataFrame with zeros for those months
    if missing_quarters:
        missing_df = pd.DataFrame({'Quarter': missing_quarters, 'Value': [0] * len(missing_quarters)})  # Assuming the column with data is named 'Value'
        df = pd.concat([df, missing_df])
    
    # Sort by the custom quarter order (1 to 4)
    df['Quarter'] = pd.Categorical(df['Quarter'], categories=quarter_order, ordered=True)
    df = df.sort_values('Quarter').reset_index(drop=True)

    remove_duplicate_quarters(df)
    
    return df

def process_dataframe_yf(df):
    # Step 1: Drop rows where "Account no." is null
    df = df.dropna(subset=["Account no."])

    # Step 2: Clean and convert numeric columns by removing commas and converting to float
    numeric_cols = ["Interest", "WHT", "Closing balance"]
    for col in numeric_cols:
        if col in df.columns:
            # Convert to string first to handle various types, then remove commas
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            # Convert to numeric, coerce errors to NaN, then fill NaN with 0.0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # Step 3: Fill null values in "Currency" column with 'LKR'
    df["Currency"] = df["Currency"].fillna("LKR")
    return df

def process_dataframe_ys(df):
    # Step 1: Drop rows where "Account no." is null
    df = df.dropna(subset=["Account no."])

    # Step 2: Fill null values in "First period", "Second period", "WHT", "Closing balance" with 0
    df[["First period", "Second period", "WHT", "Closing balance"]] = df[["First period", "Second period", "WHT", "Closing balance"]].fillna("0")

    # Step 3: Fill null values in "Currency" column with 'LKR'
    df["Currency"] = df["Currency"].fillna("LKR")
    return df


def read_file_content(file_name):
    with open(file_name, 'r') as file:
        return file.read().strip()

def timenow():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S")

def df_to_dic_m(df, account_obj, input_list, assessment_year):
    data_Scan_result_Interest_income = {
        "Year_of_assesment__c": assessment_year,
        "Name_of_the_bank__c": input_list[0],
        "NIC_of_the_client__c": input_list[2],
        "WHT_Agent_TIN__c": input_list[4],
        "email_of_the_client__c": input_list[6],
        "Account_no_user_input__c": account_obj['account_no'],
        "Account_no__c": account_obj['account_no'],
        "is_a_joint_account__c": account_obj['is_joint'],
        "Number_of_account_holders__c": account_obj['joint_persons'] if account_obj['is_joint'] else None,
        
        "Gross_interest_earned_for_M1_user_input__c": df.loc[df['Month'] == 'April', 'Interest'].values[0],
        "Gross_interest_earned_for_M1__c":df.loc[df['Month'] == 'April', 'Interest'].values[0],
        "Gross_interest_earned_for_M2_user_input__c": df.loc[df['Month'] == 'May', 'Interest'].values[0],
        "Gross_interest_earned_for_M2__c":df.loc[df['Month'] == 'May', 'Interest'].values[0],
        "Gross_interest_earned_for_M3_user_input__c": df.loc[df['Month'] == 'June', 'Interest'].values[0],
        "Gross_interest_earned_for_M3__c":df.loc[df['Month'] == 'June', 'Interest'].values[0],
        "Gross_interest_earned_for_M4_user_input__c": df.loc[df['Month'] == 'July', 'Interest'].values[0],
        "Gross_interest_earned_for_M4__c":df.loc[df['Month'] == 'July', 'Interest'].values[0],
        "Gross_interest_earned_for_M5_user_input__c": df.loc[df['Month'] == 'August', 'Interest'].values[0],
        "Gross_interest_earned_for_M5__c":df.loc[df['Month'] == 'August', 'Interest'].values[0],
        "Gross_interest_earned_for_M6_user_input__c": df.loc[df['Month'] == 'September', 'Interest'].values[0],
        "Gross_interest_earned_for_M6__c":df.loc[df['Month'] == 'September', 'Interest'].values[0],
        "Gross_interest_earned_for_M7_user_input__c": df.loc[df['Month'] == 'October', 'Interest'].values[0],
        "Gross_interest_earned_for_M7__c": df.loc[df['Month'] == 'October', 'Interest'].values[0],
        "Gross_interest_earned_for_M8_user_input__c": df.loc[df['Month'] == 'November', 'Interest'].values[0],
        "Gross_interest_earned_for_M8__c": df.loc[df['Month'] == 'November', 'Interest'].values[0],
        "Gross_interest_earned_for_M9_user_input__c": df.loc[df['Month'] == 'December', 'Interest'].values[0],
        "Gross_interest_earned_for_M9__c": df.loc[df['Month'] == 'December', 'Interest'].values[0],
        "Gross_interest_earned_for_M10_user_input__c": df.loc[df['Month'] == 'January', 'Interest'].values[0],
        "Gross_interest_earned_for_M10__c": df.loc[df['Month'] == 'January', 'Interest'].values[0],
        "Gross_interest_earned_for_M11_user_input__c": df.loc[df['Month'] == 'February', 'Interest'].values[0],
        "Gross_interest_earned_for_M11__c": df.loc[df['Month'] == 'February', 'Interest'].values[0],
        "Gross_interest_earned_for_M12_user_input__c": df.loc[df['Month'] == 'March', 'Interest'].values[0],
        "Gross_interest_earned_for_M12__c": df.loc[df['Month'] == 'March', 'Interest'].values[0],
        
        "WHT_deducted_for_M1_User_input__c": df.loc[df['Month'] == 'April', 'WHT'].values[0],
        "WHT_deducted_for_M1__c":df.loc[df['Month'] == 'April', 'WHT'].values[0],
        "WHT_deducted_for_M2_User_input__c": df.loc[df['Month'] == 'May', 'WHT'].values[0],
        "WHT_deducted_for_M2__c": df.loc[df['Month'] == 'May', 'WHT'].values[0], # Removed tab
        "WHT_deducted_for_M3_User_input__c": df.loc[df['Month'] == 'June', 'WHT'].values[0], # Assuming this was a copy-paste error in the original, should be June
        "WHT_deducted_for_M3__c": df.loc[df['Month'] == 'June', 'WHT'].values[0],
        "WHT_deducted_for_M4_User_input__c": df.loc[df['Month'] == 'July', 'WHT'].values[0],
        "WHT_deducted_for_M4__c": df.loc[df['Month'] == 'July', 'WHT'].values[0],
        "WHT_deducted_for_M5_User_input__c": df.loc[df['Month'] == 'August', 'WHT'].values[0],
        "WHT_deducted_for_M5__c": df.loc[df['Month'] == 'August', 'WHT'].values[0],
        "WHT_deducted_for_M6_User_input__c": df.loc[df['Month'] == 'September', 'WHT'].values[0],
        "WHT_deducted_for_M6__c": df.loc[df['Month'] == 'September', 'WHT'].values[0],
        "WHT_deducted_for_M7_User_input__c": df.loc[df['Month'] == 'October', 'WHT'].values[0],
        "WHT_deducted_for_M7__c": df.loc[df['Month'] == 'October', 'WHT'].values[0],
        "WHT_deducted_for_M8_User_input__c": df.loc[df['Month'] == 'November', 'WHT'].values[0],
        "WHT_deducted_for_M8__c": df.loc[df['Month'] == 'November', 'WHT'].values[0],
        "WHT_deducted_for_M9_User_input__c": df.loc[df['Month'] == 'December', 'WHT'].values[0],
        "WHT_deducted_for_M9__c": df.loc[df['Month'] == 'December', 'WHT'].values[0],
        "WHT_deducted_for_M10_User_input__c": df.loc[df['Month'] == 'January', 'WHT'].values[0],
        "WHT_deducted_for_M10__c": df.loc[df['Month'] == 'January', 'WHT'].values[0],
        "WHT_deducted_for_M11_User_input__c": df.loc[df['Month'] == 'February', 'WHT'].values[0],
        "WHT_deducted_for_M11__c": df.loc[df['Month'] == 'February', 'WHT'].values[0],
        "WHT_deducted_for_M12_User_input__c": df.loc[df['Month'] == 'March', 'WHT'].values[0],
        "WHT_deducted_for_M12__c": df.loc[df['Month'] == 'March', 'WHT'].values[0],
        
        "Withholding_Tax_Certification_Number_M1__c" :df.loc[df['Month'] == 'April', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M2__c" :df.loc[df['Month'] == 'May', 'wht_cert_no'].values[0], # Removed tab
        "Withholding_Tax_Certification_Number_M3__c" :df.loc[df['Month'] == 'June', 'wht_cert_no'].values[0],
       
        "Withholding_Tax_Certification_Number_M4__c" :df.loc[df['Month'] == 'July', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M5__c" :df.loc[df['Month'] == 'August', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M3__c" :df.loc[df['Month'] == 'June', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M6__c" :df.loc[df['Month'] == 'September', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M7__c" :df.loc[df['Month'] == 'October', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M8__c" :df.loc[df['Month'] == 'November', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M9__c" :df.loc[df['Month'] == 'December', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M10__c" :df.loc[df['Month'] == 'January', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M11__c" :df.loc[df['Month'] == 'February', 'wht_cert_no'].values[0],
        "Withholding_Tax_Certification_Number_M12__c" :df.loc[df['Month'] == 'March', 'wht_cert_no'].values[0],
        
    }
    return data_Scan_result_Interest_income

def df_to_dic_q(df, account_obj, input_list, assessment_year):
    data_Scan_result_Interest_income = {
    "Year_of_assesment__c":assessment_year,
    "Name_of_the_bank__c": input_list[0],
    "NIC_of_the_client__c": input_list[2],
    "Account_no__c": account_obj['account_no'], # Added for consistency
    "WHT_Agent_TIN__c": input_list[4],
    "email_of_the_client__c": input_list[6],
    "Account_no_user_input__c": account_obj['account_no'],
    "is_a_joint_account__c": account_obj['is_joint'],
    "Number_of_account_holders__c": account_obj['joint_persons'] if account_obj['is_joint'] else None, # NEW: Add joint persons
    "Gross_interest_earned_for_M1_user_input__c":float(df.loc[df['Quarter'] == 'Q1', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M2_user_input__c":float(df.loc[df['Quarter'] == 'Q1', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M3_user_input__c":float(df.loc[df['Quarter'] == 'Q1', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M4_user_input__c":float(df.loc[df['Quarter'] == 'Q2', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M5_user_input__c":float(df.loc[df['Quarter'] == 'Q2', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M6_user_input__c":float(df.loc[df['Quarter'] == 'Q2', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M7_user_input__c":float(df.loc[df['Quarter'] == 'Q3', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M8_user_input__c":float(df.loc[df['Quarter'] == 'Q3', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M9_user_input__c":float(df.loc[df['Quarter'] == 'Q3', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M10_user_input__c":float(df.loc[df['Quarter'] == 'Q4', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M11_user_input__c":float(df.loc[df['Quarter'] == 'Q4', 'Interest'].values[0])/4,
    "Gross_interest_earned_for_M12_user_input__c":float(df.loc[df['Quarter'] == 'Q4', 'Interest'].values[0])/4,
    "WHT_deducted_for_M1_User_input__c":float(df.loc[df['Quarter'] == 'Q1', 'WHT'].values[0])/4,
    "WHT_deducted_for_M2_User_input__c":float(df.loc[df['Quarter'] == 'Q1', 'WHT'].values[0])/4,
    "WHT_deducted_for_M3_User_input__c":float(df.loc[df['Quarter'] == 'Q1', 'WHT'].values[0])/4,
    "WHT_deducted_for_M4_User_input__c":float(df.loc[df['Quarter'] == 'Q2', 'WHT'].values[0])/4,
    "WHT_deducted_for_M5_User_input__c":float(df.loc[df['Quarter'] == 'Q2', 'WHT'].values[0])/4,
    "WHT_deducted_for_M6_User_input__c":float(df.loc[df['Quarter'] == 'Q2', 'WHT'].values[0])/4,
    "WHT_deducted_for_M7_User_input__c":float(df.loc[df['Quarter'] == 'Q3', 'WHT'].values[0])/4,
    "WHT_deducted_for_M8_User_input__c":float(df.loc[df['Quarter'] == 'Q3', 'WHT'].values[0])/4,
    "WHT_deducted_for_M9_User_input__c":float(df.loc[df['Quarter'] == 'Q3', 'WHT'].values[0])/4,
    "WHT_deducted_for_M10_User_input__c":float(df.loc[df['Quarter'] == 'Q4', 'WHT'].values[0])/4,
    "WHT_deducted_for_M11_User_input__c":float(df.loc[df['Quarter'] == 'Q4', 'WHT'].values[0])/4,
    "WHT_deducted_for_M12_User_input__c":float(df.loc[df['Quarter'] == 'Q4', 'WHT'].values[0])/4
    }
    return data_Scan_result_Interest_income

def df_to_dic_ys(bank_data,index,input_list, assessment_year):
    data_Scan_result_Interest_income = {
    "Year_of_assesment__c": assessment_year,
    "Name_of_the_bank__c": input_list[0],
    "NIC_of_the_client__c": input_list[2],
    "WHT_Agent_TIN__c": input_list[4],
    "email_of_the_client__c": input_list[6],
    "Account_no_user_input__c": bank_data["Account no."][index],
    "is_a_joint_account__c": bank_data["joint account"][index],
    "currency_type__c": bank_data["Currency"][index],
    "Gross_interest_earned_for_M1_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M2_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M3_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M4_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M5_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M6_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M7_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M8_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M9_user_input__c":float(bank_data["First period"][index])/9,
    "Gross_interest_earned_for_M10_user_input__c":float(bank_data["Second period"][index])/3,
    "Gross_interest_earned_for_M11_user_input__c":float(bank_data["Second period"][index])/3,
    "Gross_interest_earned_for_M12_user_input__c":float(bank_data["Second period"][index])/3,
    "WHT_deducted_for_M1_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M2_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M3_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M4_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M5_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M6_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M7_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M8_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M9_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M10_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M11_User_input__c":float(bank_data["WHT"][index])/12,
    "WHT_deducted_for_M12_User_input__c":float(bank_data["WHT"][index])/12
    }
    return data_Scan_result_Interest_income

def df_to_dic_yf(df, account_obj, input_list, assessment_year):

    interest_val = float(df.loc[0, "Interest"]) if "Interest" in df.columns and not pd.isna(df.loc[0, "Interest"]) else 0.0
    wht_val = float(df.loc[0, "WHT"]) if "WHT" in df.columns and not pd.isna(df.loc[0, "WHT"]) else 0.0
    wht_cert_no_val = df.loc[0, "Closing balance"] if "Closing balance" in df.columns and not pd.isna(df.loc[0, "Closing balance"]) else ""
    currency_val = df.loc[0, "Currency"] if "Currency" in df.columns and not pd.isna(df.loc[0, "Currency"]) else "LKR"
     

    data_Scan_result_Interest_income = {
    "Year_of_assesment__c": assessment_year,
    "Name_of_the_bank__c": input_list[0],
    "NIC_of_the_client__c": input_list[2], 
    "WHT_Agent_TIN__c": input_list[4],
    "email_of_the_client__c": input_list[6],
    "Account_no_user_input__c": account_obj[0],
    "Account_no__c": account_obj[0],
    "is_a_joint_account__c": account_obj[2],
    "Number_of_account_holders__c": account_obj[3] if account_obj[2] else None,
    "currency_type__c": currency_val, # Currency from the DataFrame
    "Gross_interest_earned_for_M1_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M1__c": interest_val / 12,
    "Gross_interest_earned_for_M2_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M2__c": interest_val / 12,
    "Gross_interest_earned_for_M3_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M3__c": interest_val / 12,
    "Gross_interest_earned_for_M4_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M4__c": interest_val / 12,
    "Gross_interest_earned_for_M5_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M5__c": interest_val / 12,
    "Gross_interest_earned_for_M6_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M6__c": interest_val / 12,
    "Gross_interest_earned_for_M7_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M7__c": interest_val / 12,
    "Gross_interest_earned_for_M8_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M8__c": interest_val / 12,
    "Gross_interest_earned_for_M9_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M9__c": interest_val / 12,
    "Gross_interest_earned_for_M10_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M10__c": interest_val / 12,
    "Gross_interest_earned_for_M11_user_input__c": interest_val / 12,
    "Gross_interest_earned_for_M11__c": interest_val / 12,
    "Gross_interest_earned_for_M12_user_input__c": interest_val / 12,
    "WHT_deducted_for_M1_User_input__c": wht_val / 12,
    "WHT_deducted_for_M2_User_input__c": wht_val / 12,
    "WHT_deducted_for_M3_User_input__c": wht_val / 12,
    "WHT_deducted_for_M4_User_input__c": wht_val / 12,
    "WHT_deducted_for_M5_User_input__c": wht_val / 12,
    "WHT_deducted_for_M6_User_input__c": wht_val / 12,
    "WHT_deducted_for_M7_User_input__c": wht_val / 12,
    "WHT_deducted_for_M8_User_input__c": wht_val / 12,
    "WHT_deducted_for_M9_User_input__c": wht_val / 12,
    "WHT_deducted_for_M10_User_input__c": wht_val / 12,
    "WHT_deducted_for_M11_User_input__c": wht_val / 12,
    "WHT_deducted_for_M12_User_input__c": wht_val / 12,
    
    "Withholding_Tax_Certification_Number_M1__c": wht_cert_no_val, # Map the yearly WHT Cert No
    }
    return data_Scan_result_Interest_income

# for split years employment details
def emp_update_split(sf_client, emp_data, file_paths, request_user, assessment_year):
    """
    Sends employment details to Salesforce.
    Args:
        sf_client: An authenticated Salesforce client.
        emp_data: List of strings representing the employment details.
                  Expected order:
                  [Year of Assessment,
                   Client TIN,
                   Client NIC,
                   Total Gross Remuneration,
                   Value of Benefits Excluded for Tax,
                   Total Amount of Tax Deducted,
                   Total Amount Remitted to the Inland Revenue Department,
                   Name of the Employer,
                   Date]
        file_paths: List of file paths (attachments) if any.
        request_user: The Django user making the request.
        assessment_year: The assessment year as a string.
    Returns:
        tuple: (success_bool, message_str, record_id or None)
    """
    try:
        # Helper: clean numeric strings by removing commas and converting to float
        def clean_num(val):
            try:
                return float(val.replace(",", ""))
            except Exception:
                return 0.0

        # Get total values and distribute equally among 12 months
        taxable_total_9 = clean_num(emp_data[3])
        taxable_total_3 = clean_num(emp_data[4])
        excluded_total_9 = clean_num(emp_data[5])
        excluded_total_3 = clean_num(emp_data[6])
        apit_deducted_total_9 = clean_num(emp_data[7])
        apit_deducted_total_3 = clean_num(emp_data[8])

        taxable_monthly_9 = taxable_total_9 / 9 if taxable_total_9 else ""
        taxable_monthly_3 =taxable_total_3 / 3 if taxable_total_3 else ""
        excluded_monthly_9 = excluded_total_9 / 9 if excluded_total_9 else ""
        excluded_monthly_3 = excluded_total_9 / 9 if excluded_total_3 else ""
        apit_deducted_monthly_9 = apit_deducted_total_9 / 9 if apit_deducted_total_9 else ""
        apit_deducted_monthly_3 = apit_deducted_total_3 / 3 if apit_deducted_total_3 else ""
        

        # Build the payload mapping to all API fields (for monthly breakdown)
        data = {
            # Basic mappings
            "Year_of_assessment__c": emp_data[0],
            "employer_TIN__c": emp_data[1],
            "NIC_of_the_client__c": emp_data[2],
            "NIC_of_the_client_user_input__c": emp_data[2],
            "Year_of_assessment_user_input__c": emp_data[0],
            "Name_of_the_employer__c": emp_data[7],
            "Name_of_the_employer_user_input__c":emp_data[7],
            "Date_Issued__c": emp_data[11],
            "email_of_the_client__c": request_user.email if request_user and hasattr(request_user, "email") else "",
            "Auto_Extracted__c": True,
            "scan_document_id__c": timenow(),
            
            # APIT Deducted values
            "APIT_deducted_M1__c": apit_deducted_monthly_9,
            "APIT_deducted_M1_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M10__c": apit_deducted_monthly_3,
            "APIT_deducted_M10_user_input__c": apit_deducted_monthly_3,
            "APIT_deducted_M11__c": apit_deducted_monthly_3,
            "APIT_deducted_M11_user_input__c": apit_deducted_monthly_3,
            "APIT_deducted_M12__c": apit_deducted_monthly_3,
            "APIT_deducted_M12_user_input__c": apit_deducted_monthly_3,
            "APIT_deducted_M2__c": apit_deducted_monthly_9,
            "APIT_deducted_M2_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M3__c": apit_deducted_monthly_9,
            "APIT_deducted_M3_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M4__c": apit_deducted_monthly_9,
            "APIT_deducted_M4_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M5__c": apit_deducted_monthly_9,
            "APIT_deducted_M5_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M6__c": apit_deducted_monthly_9,
            "APIT_deducted_M6_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M7__c": apit_deducted_monthly_9,
            "APIT_deducted_M7_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M8__c": apit_deducted_monthly_9,
            "APIT_deducted_M8_user_input__c": apit_deducted_monthly_9,
            "APIT_deducted_M9__c": apit_deducted_monthly_9,
            "APIT_deducted_M9_user_input__c": apit_deducted_monthly_9,
            
            # APIT Paid values
            "APIT_paid__c": clean_num(emp_data[7]),
            "APIT_paid_user_input__c": clean_num(emp_data[7]),
            
            # Additional mappings
            "Date_Issued_user_input__c": emp_data[11],
            "employer_TIN_user_input__c": emp_data[1],
            
            # Taxable employment income breakdown
            "Taxable_employement_income_M1__c": taxable_monthly_9,
            "Taxable_employement_income_M2__c": taxable_monthly_9,
            "Taxable_employement_income_M1_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M2_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M3__c": taxable_monthly_9,
            "Taxable_employement_income_M3_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M4__c": taxable_monthly_9,
            "Taxable_employement_income_M4_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M5__c": taxable_monthly_9,
            "Taxable_employement_income_M5_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M6__c": taxable_monthly_9,
            "Taxable_employement_income_M6_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M7__c": taxable_monthly_9,
            "Taxable_employement_income_M7_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M8__c": taxable_monthly_9,
            "Taxable_employement_income_M8_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M9__c": taxable_monthly_9,
            "Taxable_employement_income_M9_user_input__c": taxable_monthly_9,
            "Taxable_employement_income_M10__c": taxable_monthly_3,
            "Taxable_employement_income_M10_user_inpu__c": taxable_monthly_3,
            "Taxable_employement_income_M11__c": taxable_monthly_3,
            "Taxable_employement_income_M11_user_inpu__c": taxable_monthly_3,
            "Taxable_employement_income_M12__c": taxable_monthly_3,
            "Taxable_employement_income_M12_user_inpu__c": taxable_monthly_3,
            
            # Excluded employment income breakdown
            "Excluded_employement_income_M1__c": excluded_monthly_9,
            "Excluded_employement_income_M1_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M2__c": excluded_monthly_9,
            "Excluded_employement_income_M2_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M3__c": excluded_monthly_9,
            "Excluded_employement_income_M3_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M4__c": excluded_monthly_9,
            "Excluded_employement_income_M4_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M5__c": excluded_monthly_9,
            "Excluded_employement_income_M5_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M6__c": excluded_monthly_9,
            "Excluded_employement_income_M6_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M7__c": excluded_monthly_9,
            "Excluded_employement_income_M7_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M8__c": excluded_monthly_9,
            "Excluded_employement_income_M8_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M9__c": excluded_monthly_9,
            "Excluded_employement_income_M9_user_inpu__c": excluded_monthly_9,
            "Excluded_employement_income_M10__c": excluded_monthly_3,

            "Excluded_employement_income_M10_user_inp__": excluded_monthly_3,

            "Excluded_employement_income_M11__c": excluded_monthly_3,
            "Excluded_employement_income_M11_user_inp__c": excluded_monthly_3,
            "Excluded_employement_income_M12__c": excluded_monthly_3,
            "Excluded_employement_income_M12_user_inp__c": excluded_monthly_3
        }
        
        parent_record = sf_client.Scan_result_employement__c.create(data)
        record_id = parent_record.get("id")
        logger.info(f"Employment record created successfully! Record ID: {record_id}")
        # Optionally: call any file attachment upload function here
        return True, "Employment update completed", record_id

    except Exception as e:
        print("Error creating employment record:", e)
        return False, f"Error creating employment record: {e}", None


def emp_update(sf_client, emp_data, file_paths, request_user, assessment_year):
    """
    Sends employment details to Salesforce.
    Args:
        sf_client: An authenticated Salesforce client.
        emp_data: List of strings representing the employment details.
                  Expected order:
                  [Year of Assessment,
                   Client TIN,
                   Client NIC,
                   Total Gross Remuneration,
                   Value of Benefits Excluded for Tax,
                   Total Amount of Tax Deducted,
                   Total Amount Remitted to the Inland Revenue Department,
                   Name of the Employer,
                   Date]
        file_paths: List of file paths (attachments) if any.
        request_user: The Django user making the request.
        assessment_year: The assessment year as a string.
    Returns:
        tuple: (success_bool, message_str, record_id or None)
    """
    try:
        # Helper: clean numeric strings by removing commas and converting to float
        def clean_num(val):
            try:
                return float(val.replace(",", ""))
            except Exception:
                return 0.0

        # Get total values and distribute equally among 12 months
        taxable_total = clean_num(emp_data[3])
        excluded_total = clean_num(emp_data[4])
        apit_deducted_total = clean_num(emp_data[5])

        taxable_monthly = taxable_total / 12 if taxable_total else ""
        excluded_monthly = excluded_total / 12 if excluded_total else ""
        apit_m = apit_deducted_total / 12 if apit_deducted_total else ""

        # Build the payload mapping to all API fields (for monthly breakdown)
        data = {
    # Basic mappings
    "Year_of_assessment__c": emp_data[0],
    "employer_TIN__c": emp_data[1],
    "employer_TIN_user_input__c":emp_data[1],
    "NIC_of_the_client__c": emp_data[2],
    "NIC_of_the_client_user_input__c": emp_data[2],
    "Year_of_assessment_user_input__c": emp_data[0],
    "Name_of_the_employer__c": emp_data[7],
    "Name_of_the_employer_user_input__c":emp_data[7],
    "Date_Issued__c": emp_data[8],
    "email_of_the_client__c": request_user.email if request_user and hasattr(request_user, "email") else "",
    "Auto_Extracted__c": True,
    "scan_document_id__c": timenow(),
    
    # APIT Deducted values
    "APIT_deducted_M1__c": apit_m,
    "APIT_deducted_M1_user_input__c": apit_m,
    "APIT_deducted_M10__c": apit_m,
    "APIT_deducted_M10_user_input__c": apit_m,
    "APIT_deducted_M11__c": apit_m,
    "APIT_deducted_M11_user_input__c": apit_m,
    "APIT_deducted_M12__c": apit_m,
    "APIT_deducted_M12_user_input__c": apit_m,
    "APIT_deducted_M2__c": apit_m,
    "APIT_deducted_M2_user_input__c": apit_m,
    "APIT_deducted_M3__c": apit_m,
    "APIT_deducted_M3_user_input__c": apit_m,
    "APIT_deducted_M4__c": apit_m,
    "APIT_deducted_M4_user_input__c": apit_m,
    "APIT_deducted_M5__c": apit_m,
    "APIT_deducted_M5_user_input__c": apit_m,
    "APIT_deducted_M6__c": apit_m,
    "APIT_deducted_M6_user_input__c": apit_m,
    "APIT_deducted_M7__c": apit_m,
    "APIT_deducted_M7_user_input__c": apit_m,
    "APIT_deducted_M8__c": apit_m,
    "APIT_deducted_M8_user_input__c": apit_m,
    "APIT_deducted_M9__c": apit_m,
    "APIT_deducted_M9_user_input__c": apit_m,
    
    # APIT Paid values
    "APIT_paid__c": clean_num(emp_data[5]),
    "APIT_paid_user_input__c": clean_num(emp_data[5]),
    
    # Employer TIN input
    "employer_TIN_user_input__c": emp_data[1],
    
    # Taxable employment income breakdown (monthly)
    "Taxable_employement_income_M1__c": taxable_monthly,
    "Taxable_employement_income_M2__c": taxable_monthly,
    "Taxable_employement_income_M1_user_input__c": taxable_monthly,
    "Taxable_employement_income_M2_user_input__c": taxable_monthly,
    "Taxable_employement_income_M3__c": taxable_monthly,
    "Taxable_employement_income_M3_user_input__c": taxable_monthly,
    "Taxable_employement_income_M4__c": taxable_monthly,
    "Taxable_employement_income_M4_user_input__c": taxable_monthly,
    "Taxable_employement_income_M5__c": taxable_monthly,
    "Taxable_employement_income_M5_user_input__c": taxable_monthly,
    "Taxable_employement_income_M6__c": taxable_monthly,
    "Taxable_employement_income_M6_user_input__c": taxable_monthly,
    "Taxable_employement_income_M7__c": taxable_monthly,
    "Taxable_employement_income_M7_user_input__c": taxable_monthly,
    "Taxable_employement_income_M8__c": taxable_monthly,
    "Taxable_employement_income_M8_user_input__c": taxable_monthly,
    "Taxable_employement_income_M9__c": taxable_monthly,
    "Taxable_employement_income_M9_user_input__c": taxable_monthly,
    "Taxable_employement_income_M10__c": taxable_monthly,
    "Taxable_employement_income_M10_user_inpu__c": taxable_monthly,
    "Taxable_employement_income_M11__c": taxable_monthly,
    "Taxable_employement_income_M11_user_inpu__c": taxable_monthly,
    "Taxable_employement_income_M12__c": taxable_monthly,
    "Taxable_employement_income_M12_user_inpu__c": taxable_monthly,
    
    # Excluded employment income breakdown (from Value of Benefits Excluded for Tax)
    "Excluded_employement_income_M1__c": excluded_monthly,
    "Excluded_employement_income_M1_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M2__c": excluded_monthly,
    "Excluded_employement_income_M2_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M3__c": excluded_monthly,
    "Excluded_employement_income_M3_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M4__c": excluded_monthly,
    "Excluded_employement_income_M4_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M5__c": excluded_monthly,
    "Excluded_employement_income_M5_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M6__c": excluded_monthly,
    "Excluded_employement_income_M6_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M7__c": excluded_monthly,
    "Excluded_employement_income_M7_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M8__c": excluded_monthly,
    "Excluded_employement_income_M8_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M9__c": excluded_monthly,
    "Excluded_employement_income_M9_user_inpu__c": excluded_monthly,
    "Excluded_employement_income_M10__c": excluded_monthly,
    "Excluded_employement_income_M10_user_inp__c": excluded_monthly,
    "Excluded_employement_income_M11__c": excluded_monthly,
    "Excluded_employement_income_M11_user_inp__c": excluded_monthly,
    "Excluded_employement_income_M12__c": excluded_monthly,
    "Excluded_employement_income_M12_user_inp__c": excluded_monthly,
    # (Additional excluded fields for M3 to M12 would follow with the same naming convention)
}
        
        parent_record = sf_client.Scan_result_employement__c.create(data)
        record_id = parent_record.get("id")
        logger.info(f"Employment record created successfully! Record ID: {record_id}")
        # Optionally: call any file attachment upload function here
        return True, "Employment update completed", record_id

    except Exception as e:
        print("Error creating employment record:", e)
        return False, f"Error creating employment record: {e}", None

def upload_bank_image_and_link(parent_record_ids, image_file_path):
    pass

def bank_update_m(sf_client, bank_data, input_list, file_paths, request_user, assessment_year, extracted_accounts_data):
    """
    Monthly bank update using processed DataFrames.
    Args:
        sf_client: An authenticated Salesforce client.
        bank_data: A dictionary of DataFrames for each account.
        input_list: General bank info list with indices:
                    [0] Name of bank,
                    [2] NIC,
                    [4] Bank TIN,
                    [5] WHT certification number,
                    [6] email.
        file_paths: File path(s) to the original document(s).
        request_user: The Django user making the request.
        assessment_year: The assessment year (string).
        extracted_accounts_data: A list of dictionaries, each representing an account
                                 with 'account_no', 'currency', 'balance', 'is_joint', 'joint_persons', and 'periods'.
    Returns:
        tuple: (success_bool, message_str, list of parent record IDs)
    """
    bank_data = fill_dfs_m(bank_data)
    print("Data ready")
    
    # Using the provided Salesforce client; no need to re-read creds.
    print("sf auth complete")
    data_Scan_result_bank = {
        "Name_of_the_bank_user_input__c": input_list[0],
        "NIC_of_the_client_user_input__c": input_list[2],
        "Year_of_assesment__c": assessment_year, 
        "Bank_TIN_user_input__c": input_list[4],
        "WHT_certification_no_user_input__c": input_list[5],
        "email_of_the_client__c": input_list[6],
        "scan_document_id__c": timenow(),
    }

    # Create the Scan_result_bank__c record in Salesforce
    parent_bank_record = sf_client.Scan_result_bank__c.create(data_Scan_result_bank)
    parent_bank_record_id = parent_bank_record['id']
    logger.info("Scan_result_bank__c record created successfully!")
    
    # List to store all created parent record IDs
    parent_record_ids = [parent_bank_record_id]
    # Instead of st.session_state.accounts_list, use the passed user_accounts_details_list.
    accounts_list = extracted_accounts_data

    for account_obj in accounts_list:
        data_Scan_result_bank_balance = {
            "Name_of_the_bank__c": input_list[0],
            "NIC_of_the_client__c": input_list[2],
            "email_of_the_client__c": input_list[6],
            "Account_no_user_input__c": account_obj['account_no'],
            "currency_type_user_input__c": account_obj['currency'],
            "Balance_as_of_the_end_of_the_year__c": clean_value(account_obj['balance']), # NEW: Add balance
            "Balance_as_of_the_end_of_the_year_user_i__c": clean_value(account_obj['balance']), # NEW: Add balance
            "Year_of_assesment__c": assessment_year,
        }
        parent_balance_record = sf_client.Scan_result_bank_balance__c.create(data_Scan_result_bank_balance)
        parent_balance_record_id = parent_balance_record['id']
        parent_record_ids.append(parent_balance_record_id)
        logger.info(f"Balance record created for account: {account_obj['account_no']}")

    for key in bank_data: # bank_data is a dict of DataFrames, keyed by account_no
        current_account_details = next((acc for acc in accounts_list if acc['account_no'] == key), None)
        if not current_account_details:
            logger.warning(f"Account details not found in extracted_accounts_data for DataFrame key: {key}. Skipping interest income record.")
            continue
        data_Scan_result_Interest_income = df_to_dic_m(bank_data[key], current_account_details, input_list, assessment_year)
        # Clean data if necessary
        cleaned_data = {k: (0 if pd.isna(v) else v) for k, v in data_Scan_result_Interest_income.items()}
        parent_interest_income_record = sf_client.Scan_result_Interest_income__c.create(cleaned_data)
        parent_interest_income_record_id = parent_interest_income_record['id']
        parent_record_ids.append(parent_interest_income_record_id)
        logger.info(f"Interest income record created for account: {current_account_details['account_no']}")
    # Optionally, upload files here:
    # upload_image_and_link(parent_record_ids, file_paths)
    print("Files not uploaded")
    return True, "Monthly bank update completed", parent_record_ids



    #upload_image_and_link(parent_record_ids,file_path)

    #logger.info("files not uploaded")

def bank_update_s(bank_data, input_list, file_path, assessment_year):
    #read creds
    
    sf_username = read_file_content("sf_username.txt")
    sf_password = read_file_content("sf_password.txt")
    sf_sec_token = read_file_content("sf_sec_token.txt")

    # Create a connection to Salesforce instance
    
    

    data_Scan_result_bank = {
            "Name_of_the_bank_user_input__c": input_list[0],
            "NIC_of_the_client_user_input__c": input_list[2],
            "Year_of_assesment__c": assessment_year, 
            "Bank_TIN_user_input__c": input_list[4],
            "WHT_certification_no_user_input__c": input_list[5],
            "email_of_the_client__c": input_list[6],
            "scan_document_id__c": timenow(),
        }

    # Create the Scan_result_bank__c record in Salesforce
    parent_bank_record = sf.Scan_result_bank__c.create(data_Scan_result_bank)
    parent_bank_record_id = parent_bank_record['id']
    logger.info("Scan_result_bank__c record created successfully!")

    # List to store all created parent record IDs
    parent_record_ids = [parent_bank_record_id]

    bank_data = process_dataframe_ys(bank_data)

    #bank balance needed to be sent droped for now

    for index,row in bank_data.iterrows():
        data_Scan_result_Interest_income = df_to_dic_ys(bank_data,index,input_list, assessment_year)
        cleaned_data_Scan_result_Interest_income = {k: (0 if pd.isna(v) else v) for k, v in data_Scan_result_Interest_income.items()}
        # Create the Scan_result_Interest_income__c record in Salesforce
        parent_interest_income_record = sf.Scan_result_Interest_income__c.create(cleaned_data_Scan_result_Interest_income)
        parent_interest_income_record_id = parent_interest_income_record['id']
        parent_record_ids.append(parent_interest_income_record_id)
    logger.info("Scan_result_Interest_income__c records created successfully")

    #upload_image_and_link(parent_record_ids,file_path)

    logger.info("files not uploaded")

def bank_update_f(sf_client, bank_data, input_list, file_paths, request_user, assessment_year, extracted_accounts_data):
    """
    Yearly bank update using processed DataFrames.
    Args:
        sf_client: An authenticated Salesforce client.
        bank_data: Either a DataFrame or a dictionary of DataFrames (or similar objects) containing yearly bank data.
        input_list: General bank info list with indices:
                    [0] Name of bank,
                    [2] NIC,
                    [4] Bank TIN,
                    [5] WHT certification number,
                    [6] email.
        file_paths: File path(s) to the original document(s).
        request_user: The Django user making the request.
        assessment_year: The assessment year (string).
        extracted_accounts_data: A list of dictionaries, each representing an account
                                 with 'account_no', 'currency', 'balance', 'is_joint', 'joint_persons', and 'periods'.
    Returns:
        tuple: (success_bool, message_str, list of parent record IDs)
    """
    try:
        logger.info("Starting yearly bank update (bank_update_f).")

        # No need to call fill_dfs_f(bank_data) here, as bank_data_dfs_y is already processed DataFrames
        # from sf_update2.py. It's already a dict of single-row DataFrames.

        bank_data = fill_dfs_f(bank_data) # This line is crucial for processing the DataFrames

        data_Scan_result_bank = {
                "Name_of_the_bank_user_input__c": input_list[0],
                "NIC_of_the_client_user_input__c": input_list[2],
                "Year_of_assesment__c": assessment_year, 
                "Bank_TIN_user_input__c": input_list[4],
                "WHT_certification_no_user_input__c": input_list[5],
                "email_of_the_client__c": input_list[6],
                "scan_document_id__c": timenow(),
            }

        parent_bank_record = sf_client.Scan_result_bank__c.create(data_Scan_result_bank)
        parent_bank_record_id = parent_bank_record['id']
        logger.info(f"Scan_result_bank__c record created successfully with ID: {parent_bank_record_id}")

        parent_record_ids = [parent_bank_record_id]
        accounts_list = extracted_accounts_data # Use the new structured account objects

        for account_obj in accounts_list: # Iterate through the new structured account objects
            current_account_no = account_obj[0] # Corrected: Access by index for list
            current_account_df = bank_data.get(current_account_no) # Access bank_data with the string key
            if current_account_df is None or current_account_df.empty:
                logger.warning(f"No DataFrame found for account {current_account_no} in bank_data. Skipping interest income record.")
                continue

            balance = current_account_df.loc[0, "Closing balance"] if "Closing balance" in current_account_df.columns and not pd.isna(current_account_df.loc[0, "Closing balance"]) else 0.0
            currency = current_account_df.loc[0, "Currency"] if "Currency" in current_account_df.columns and not pd.isna(current_account_df.loc[0, "Currency"]) else "LKR"

            balance_payload = {
                "Name_of_the_bank__c": input_list[0],
                "NIC_of_the_client__c": input_list[2],
                "Year_of_assesment__c": assessment_year,
                "Account_no_user_input__c": account_obj[0],
                "Account_no__c": account_obj[0],
                "currency_type__c": currency,
                "currency_type_user_input__c": currency,
                "Balance_as_of_the_end_of_the_year__c": clean_value(balance),
                "Balance_as_of_the_end_of_the_year_user_i__c": clean_value(balance),
                "is_a_joint_account__c": account_obj[2],
                "Number_of_account_holders__c": account_obj[3] if account_obj[2] else None,
                "scan_document_id__c": timenow(),
                "email_of_the_client__c": request_user.email if request_user and hasattr(request_user, "email") else "",
            }

            balance_record = sf_client.Scan_result_bank_balance__c.create(balance_payload)
            record_id = balance_record.get('id')
            if record_id:
                parent_record_ids.append(record_id)
                logger.info(f"Successfully created Scan_result_bank_balance__c record for account {account_obj[0]} with ID: {record_id}")
            else:
                logger.error(f"Failed to create Scan_result_bank_balance__c record for account {account_obj[0]}. Response: {balance_record}")

            data_Scan_result_Interest_income = df_to_dic_yf(current_account_df, account_obj, input_list, assessment_year)
            # Clean data if necessary (e.g., convert pd.NA to None for Salesforce)
            cleaned_data = {k: (v if not pd.isna(v) else None) for k, v in data_Scan_result_Interest_income.items()}
            parent_interest_income_record = sf_client.Scan_result_Interest_income__c.create(cleaned_data)
            parent_interest_income_record_id = parent_interest_income_record['id']
            parent_record_ids.append(parent_interest_income_record_id)
            logger.info(f"Scan_result_Interest_income__c record created for account {current_account_no} with ID: {parent_interest_income_record_id}")

        logger.info("Yearly bank update completed successfully.")
        return True, "Yearly bank update completed", parent_record_ids
    except Exception as e:
        logger.error(f"Error during yearly bank update (bank_update_f): {e}", exc_info=True)
        return False, f"Error during yearly bank update: {e}", None

def df_to_dic_yf(df, account_obj, input_list, assessment_year):
    # df is a single-row DataFrame, so always use index 0 for df.loc
    # Ensure values are extracted safely and converted to float
    interest_val = float(df.loc[0, "Interest"]) if "Interest" in df.columns and not pd.isna(df.loc[0, "Interest"]) else 0.0
    wht_val = float(df.loc[0, "WHT"]) if "WHT" in df.columns and not pd.isna(df.loc[0, "WHT"]) else 0.0
    # "Closing balance" from frontend maps to "wht_cert_no" in Salesforce for yearly data
    wht_cert_no_val = df.loc[0, "Closing balance"] if "Closing balance" in df.columns and not pd.isna(df.loc[0, "Closing balance"]) else ""
    currency_val = df.loc[0, "Currency"] if "Currency" in df.columns and not pd.isna(df.loc[0, "Currency"]) else "LKR"

    data_Scan_result_Interest_income = {
        "Year_of_assesment__c": assessment_year,
        "Name_of_the_bank__c": input_list[0],
        "NIC_of_the_client__c": input_list[2],
        "WHT_Agent_TIN__c": input_list[4],
        "email_of_the_client__c": input_list[6],
        "Account_no_user_input__c": account_obj[0], # Corrected: Access by index
        "Account_no__c": account_obj[0], # Corrected: Access by index
        "is_a_joint_account__c": account_obj[2], # Corrected: Access by index
        "Number_of_account_holders__c": account_obj[3] if account_obj[2] else None, # Corrected: Access by index
        "currency_type__c": currency_val, # Currency from the DataFrame
        "Gross_interest_earned_for_M1_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M2_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M3_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M4_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M5_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M6_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M7_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M8_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M9_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M10_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M11_user_input__c": interest_val / 12,
        "Gross_interest_earned_for_M12_user_input__c": interest_val / 12,
        "WHT_deducted_for_M1_User_input__c": wht_val / 12,
        "WHT_deducted_for_M2_User_input__c": wht_val / 12,
        "WHT_deducted_for_M3_User_input__c": wht_val / 12,
        "WHT_deducted_for_M4_User_input__c": wht_val / 12,
        "WHT_deducted_for_M5_User_input__c": wht_val / 12,
        "WHT_deducted_for_M6_User_input__c": wht_val / 12,
        "WHT_deducted_for_M7_User_input__c": wht_val / 12,
        "WHT_deducted_for_M8_User_input__c": wht_val / 12,
        "WHT_deducted_for_M9_User_input__c": wht_val / 12,
        "WHT_deducted_for_M10_User_input__c": wht_val / 12,
        "WHT_deducted_for_M11_User_input__c": wht_val / 12,
        "WHT_deducted_for_M12_User_input__c": wht_val / 12,
        "Withholding_Tax_Certification_Number_M1__c": wht_cert_no_val, # Map the yearly WHT Cert No
    }
    return data_Scan_result_Interest_income

def get_actual_customer_id(sf, display_customer_id):
    """
    Retrieves the actual Salesforce Customer ID based on a display ID.

    Args:
        sf: Salesforce connection object.
        display_customer_id: The display Customer ID (e.g., "760").

    Returns:
        The actual Salesforce Customer ID (18-character string) or None if not found.
    """
    try:
        # Modified query to use 'Name' instead of 'Display_Customer_ID__c'
        query = f"SELECT Id FROM customer__c WHERE Name ='{display_customer_id}'"  # Select the 'Id' field
        result = sf.query(query)
        #print(f"get_actual_customer_id query result: {result}")  # Removed this line

        if result['totalSize'] > 0:
            customer_id = result['records'][0]['Id']
            #print(customer_id) #removed this line
            return customer_id  # Return the 'Id' field
        else:
            #print(f"No customer found with Display Customer ID: {display_customer_id}") #removed this line
            return None
    except Exception as e:
        #print(f"Error retrieving actual Customer ID: {e}") #removed this line
        return None
    
def get_tax_files_for_customer(sf, actual_customer_id):
    """
    Retrieves all available tax years for a given customer from Tax_File__c.

    Args:
        sf: Salesforce connection object.
        actual_customer_id: The actual Salesforce Customer ID.

    Returns:
        A string containing the tax years, each on a new line, or an empty string if none found.
    """
    try:
        query = f"""
           SELECT Id,Tax_Year__c FROM Tax_File__c WHERE Customer_ID__c = '{actual_customer_id}'
        """
        result = sf.query(query)
        #print(f"get_tax_files_for_customer query result: {result}")

        if result['totalSize'] > 0:
            tax_years = ""
            for record in result['records']:
                if record['Tax_Year__c'] is not None:
                    tax_years += record['Tax_Year__c'] + "\n"
            return tax_years.strip()  # Remove trailing newline if any
        else:
            return ""
    except Exception as e:
        print(f"Error retrieving tax files for customer: {e}")
        return ""

def get_tax_file_for_year(tax_files_string, assessment_year):
    """
    Finds the correct Tax_File__c record for a specific assessment year.

    Args:
        tax_files_string: A string containing tax years, each on a new line (e.g., "2021/2022\n2023/2024").
        assessment_year: The assessment year (e.g., "2023/2024").

    Returns:
        The assessment year (string) if found in the tax_files_string, otherwise None.
    """
    if not tax_files_string:
        print(f"No tax files provided.")
        return None

    # Split the tax_files_string by newline to get a list of tax years
    tax_years = tax_files_string.split('\n')  
    for year in tax_years:
        # Directly compare the year and assessment_year strings
        if year == str(assessment_year):  
            return year  # Return the assessment year if found
    print(f"No tax file found for assessment year: {assessment_year}")
    return None

def get_tax_file_id_by_customer_and_year(customer_id, assessment_year):
    """
    Retrieves the Tax_File__c record ID for a given customer and assessment year.

    Args:
        customer_id (str): The Salesforce ID of the customer__c record.
        assessment_year (str): The assessment year (e.g., "2023/2024").

    Returns:
        str: The Salesforce ID of the Tax_File__c record if found, otherwise None.
    """
    try:
        sf = validate_sf()

        # Query to find the Tax_File__c record
        query = f"""
            SELECT Id 
            FROM Tax_File__c 
            WHERE Customer_ID__c = '{customer_id}' 
            AND Tax_Year__c = '{assessment_year}'
        """

        result = sf.query(query)

        if result['totalSize'] > 0:
            # Tax_File__c record found
            tax_file_id = result['records'][0]['Id']
            return tax_file_id
        else:
            # No Tax_File__c record found for the given criteria
            logger.warning(f"No Tax_File__c record found for Customer ID: {customer_id} and Assessment Year: {assessment_year}")
            return None

    except Exception as e:
        logger.error(f"Error retrieving Tax_File__c record: {e}")
        return None

def wealth_update(sf_client, input_list, file_path, request_user, assessment_year, tax_file_id):
    """
    Updates or creates a TFO Investment Income record in Salesforce.

    Args:
        sf_client: An authenticated Salesforce client.
        input_list: User input data.
        file_path: Path to the original file.
        request_user: The user making the request.
        assessment_year: The assessment year.
        tax_file_id: The ID of the parent Tax_File__c record.
    """
    try:
        # Extract relevant data from input_list
        # assessment_year = input_list[0] # Now passed as an argument
        employer_name = input_list[2]
        unrealized_gains = input_list[4]
        user_income = input_list[3]
        user_id = input_list[5]

        if not tax_file_id:
            logger.error("Cannot create TFO Investment Income record without a tax_file_id.")
            return False, "Tax File ID is missing.", None

        # Data create
        data = {
            "Year_of_Assessment__c": assessment_year,
            "Name_of_the_employer__c": employer_name,
            "Income_type__c": "Unit Trust",  # Corrected: Use the API name directly
            "UT_Unrealized_Gains__c": unrealized_gains, 
            "Income_M6__c": user_income,
            "Tax_File__c": tax_file_id,  # Link to Tax_File__c
            
        }

        print(data)
        parent_record = sf_client.TFO_Investment_Income__c.create(data)
        target_record_id = parent_record['id']
        logger.info(f"Record created successfully! Record ID: {target_record_id}")
        return True, "Wealth management record created successfully.", target_record_id
    except Exception as e:
        logger.error(f"Error creating or updating record: {e}")
        return False, f"Error creating wealth management record: {e}", None

def df_to_dic_balance(account, general_info, assessment_year, request_user):
    """
    Prepares a dictionary for creating a Scan_result_Interest_income__c record
    from Bank Balance Confirmation data.
    """
    acc_no = account.get("account_number")
    interest_str = account.get("interest")
    wht_str = account.get("wht")
    is_joint = account.get("is_joint")
    joint_persons = account.get("joint_persons")
    
    bank_name, person_name, nic, statement_date, email = general_info

    interest_val = float(str(interest_str).replace(",", "")) if interest_str else 0.0
    wht_val = float(str(wht_str).replace(",", "")) if wht_str else 0.0
    monthly_interest = interest_val / 12
    monthly_wht = wht_val / 12
    data_Scan_result_Interest_income = {
        "Year_of_assesment__c": assessment_year,
        "Name_of_the_bank__c": bank_name,
        "NIC_of_the_client__c": nic,
        "WHT_Agent_TIN__c": "", # Not available in balance confirmation
        "email_of_the_client__c": request_user.email if request_user and hasattr(request_user, "email") else "",
        "Account_no_user_input__c": acc_no,
        "Account_no__c": acc_no,
        "is_a_joint_account__c": is_joint, 
        "Number_of_account_holders__c": joint_persons,
        "Gross_interest_earned_for_M1_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M2_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M3_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M4_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M5_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M6_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M7_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M8_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M9_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M10_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M11_user_input__c": monthly_interest,
        "Gross_interest_earned_for_M12_user_input__c": monthly_interest,
        "WHT_deducted_for_M1_User_input__c": monthly_wht,
        "WHT_deducted_for_M2_User_input__c": monthly_wht,
        "WHT_deducted_for_M3_User_input__c": monthly_wht,
        "WHT_deducted_for_M4_User_input__c": monthly_wht,
        "WHT_deducted_for_M5_User_input__c": monthly_wht,
        "WHT_deducted_for_M6_User_input__c": monthly_wht,
        "WHT_deducted_for_M7_User_input__c": monthly_wht,
        "WHT_deducted_for_M8_User_input__c": monthly_wht,
        "WHT_deducted_for_M9_User_input__c": monthly_wht,
        "WHT_deducted_for_M10_User_input__c": monthly_wht,
        "WHT_deducted_for_M11_User_input__c": monthly_wht,
        "WHT_deducted_for_M12_User_input__c": monthly_wht,
    }
    return data_Scan_result_Interest_income

def bank_update_c(sf_client, extracted_data, file_paths, request_user, assessment_year):
    """
    Handles Bank Balance Confirmation data update to Salesforce.
    Creates records in Scan_result_bank_balance__c.

    Args:
        sf_client: An authenticated Salesforce client.
        extracted_data (dict): A dictionary containing 'general_info' and 'accounts'.
        file_paths (list): File path(s) to the original document(s).
        request_user: The Django user making the request.
        assessment_year (str): The assessment year.

    Returns:
        tuple: (success_bool, message_str, list of created record IDs)
    """
    try:
        logger.info("Starting bank balance confirmation update (bank_update_c).")
        
        if not extracted_data or not isinstance(extracted_data, dict):
            return False, "Insufficient data for bank balance confirmation.", None

        general_info = extracted_data.get("general_info", {})
        accounts = extracted_data.get("accounts", [])

        bank_name = general_info.get("name_of_the_bank")
        person_name = general_info.get("name_of_the_person")
        nic = general_info.get("nic_of_the_person")
        statement_date = general_info.get("statement_date")
        
        general_info_list = [bank_name, person_name, nic, statement_date, request_user.email if request_user else ""]

        # --- NEW: Create the parent Scan_result_bank__c record ---
        data_Scan_result_bank = {
            "Name_of_the_bank_user_input__c": bank_name,
            "NIC_of_the_client_user_input__c": nic,
            "Year_of_assesment__c": assessment_year, 
            "Bank_TIN_user_input__c": "", # Not available in balance confirmation
            "WHT_certification_no_user_input__c": "", # Not available in balance confirmation
            "email_of_the_client__c": request_user.email if request_user and hasattr(request_user, "email") else "",
            "scan_document_id__c": timenow(),
        }
        parent_bank_record = sf_client.Scan_result_bank__c.create(data_Scan_result_bank)
        parent_bank_record_id = parent_bank_record.get('id')
        logger.info(f"Scan_result_bank__c record created successfully with ID: {parent_bank_record_id}")
        # --- End of new block ---
        created_record_ids = [parent_bank_record_id] if parent_bank_record_id else []

        # Iterate through accounts
        for account in accounts:
            acc_no = account.get("account_number")
            currency = account.get("currency")
            acc_type = account.get("account_type")
            balance = account.get("balance")
            interest = account.get("interest")
            wht = account.get("wht")
            is_joint = account.get("is_joint")
            joint_persons = account.get("joint_persons")

            # Payload for Scan_result_bank_balance__c
            balance_payload = {
                "Name_of_the_bank__c": bank_name,
                "NIC_of_the_client__c": nic,
                "Year_of_assesment__c": assessment_year,
                "Account_no_user_input__c": acc_no,
                "Account_no__c": acc_no,
                "currency_type__c": currency,
                "currency_type_user_input__c": currency,
                "Balance_as_of_the_end_of_the_year__c": clean_value(balance),
                "Balance_as_of_the_end_of_the_year_user_i__c": clean_value(balance),
                "is_a_joint_account__c": is_joint,
                "Number_of_account_holders__c": joint_persons,
                "scan_document_id__c": timenow(),
                "email_of_the_client__c": request_user.email if request_user and hasattr(request_user, "email") else "",
            }

            balance_record = sf_client.Scan_result_bank_balance__c.create(balance_payload)
            record_id = balance_record.get('id')
            if record_id:
                created_record_ids.append(record_id)
                logger.info(f"Successfully created Scan_result_bank_balance__c record for account {acc_no} with ID: {record_id}")
            else:
                logger.error(f"Failed to create Scan_result_bank_balance__c record for account {acc_no}. Response: {balance_record}")
            
            # --- NEW: Create the corresponding Scan_result_Interest_income__c record ---
            interest_payload = df_to_dic_balance(account, general_info_list, assessment_year, request_user)
            interest_record = sf_client.Scan_result_Interest_income__c.create(interest_payload)
            interest_record_id = interest_record.get('id')
            if interest_record_id:
                created_record_ids.append(interest_record_id)
                logger.info(f"Successfully created Scan_result_Interest_income__c record for account {acc_no} with ID: {interest_record_id}")
            # --- End of new block ---

        if not created_record_ids:
            return False, "No records were created for bank balance confirmation.", None

        return True, f"Successfully created {len(created_record_ids)} bank balance record(s).", created_record_ids

    except Exception as e:
        logger.error(f"Error during bank balance confirmation update (bank_update_c): {e}", exc_info=True)
        return False, f"An error occurred during bank balance update: {e}", None

def update_ai_scan_status_to_true(sf_client, record_id, object_name="Tick_Upload_File_names__c"):
    """
    Updates the 'AI_scan_status__c' checkbox field to True for a given Salesforce record.

    Args:
        sf_client: An authenticated simple_salesforce client instance.
        record_id (str): The ID of the Salesforce record to update.
        object_name (str): The API name of the Salesforce object (e.g., "Scan_result_employement__c", 
                           "Scan_result_bank__c", "TFO_Investment_Income__c").
                           Defaults to "Scan_result_employement__c".

    Returns:
        tuple: (success_bool, message_str)
               success_bool is True if the update was successful, False otherwise.
               message_str contains a descriptive message of the outcome.
    """
    if not sf_client:
        logger.error("Salesforce client is not provided.")
        return False, "Salesforce client is not provided."
    if not record_id:
        logger.error("Salesforce record ID is not provided.")
        return False, "Salesforce record ID is not provided."
    if not object_name:
        logger.error("Salesforce object name is not provided.")
        return False, "Salesforce object name is not provided."

    payload = {
        "AI_scan_status__c": True
    }

    try:
        logger.info(f"Attempting to update AI_scan_status__c for {object_name} record ID: {record_id}")
        # Dynamically get the SObject
        sObject = getattr(sf_client, object_name)
        result = sObject.update(record_id, payload)
        
        # simple-salesforce update returns status code 204 (No Content) on success
        if result == 204: 
            logger.info(f"Successfully updated AI_scan_status__c for {object_name} record ID: {record_id}")
            return True, f"AI Scan Status updated successfully for record {record_id}."
        else:
            logger.error(f"Failed to update AI_scan_status__c for {object_name} record ID: {record_id}. SF Response: {result}")
            return False, f"Failed to update AI Scan Status. Salesforce response: {result}"
    except Exception as e:
        logger.error(f"Error updating AI_scan_status__c for {object_name} record ID {record_id}: {e}", exc_info=True)
        sf_error_message = str(e)
        if hasattr(e, 'content') and isinstance(e.content, list) and e.content and isinstance(e.content[0], dict):
            sf_error_message = e.content[0].get('message', str(e))
        return False, f"Error updating AI Scan Status: {sf_error_message}"