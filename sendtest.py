#import library
from simple_salesforce import Salesforce

#read file content for creds
from read_file import read_file_content

#get the timestamp
from time_stamp import timenow


import base64

import pandas as pd

import re

def limit_acc():
    # Step 1: Get the length of list1
    my_list = st.session_state.accounts_list
    #get the unique count
    unique_count = len(set(tuple(item) for item in my_list))
    st.session_state.user_accounts = st.session_state.user_accounts[-unique_count:]

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

            st.write("File uploaded and linked successfully!")
    except Exception as e:
        st.write("Error uploading file or linking document:", e)

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

    # Step 2: Fill null values in "First period", "Second period", "WHT", "Closing balance" with 0
    df[["Interest","WHT","Closing balance"]] = df[["Interest","WHT","Closing balance"]].fillna("0")

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

def validate_sf():
    #read creds
    sf_username = read_file_content("sf_username.txt")
    sf_password = read_file_content("sf_password.txt")
    sf_sec_token = read_file_content("sf_sec_token.txt")

    # Create a connection to Salesforce instance
    sf = Salesforce(
                    username=sf_username,
                    password=sf_password,
                    security_token=sf_sec_token
                    )
    return sf

def read_file_content(file_name):
    with open(file_name, 'r') as file:
        return file.read().strip()

def timenow():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S")

def df_to_dic_m(df,count,input_list):
    data_Scan_result_Interest_income = {
    "Year_of_assesment__c": st.session_state.assessment_year,
    "Name_of_the_bank__c": input_list[0],
    "NIC_of_the_client__c": input_list[2],
    "WHT_Agent_TIN__c": input_list[4],
    "email_of_the_client__c": input_list[6],
    "Account_no_user_input__c": st.session_state.user_accounts[count][0],
    "is_a_joint_account__c": st.session_state.user_accounts[count][2],
    "Gross_interest_earned_for_M1_user_input__c": df.loc[df['Month'] == 'April', 'Interest'].values[0],
    "Gross_interest_earned_for_M2_user_input__c": df.loc[df['Month'] == 'May', 'Interest'].values[0],
    "Gross_interest_earned_for_M3_user_input__c": df.loc[df['Month'] == 'June', 'Interest'].values[0],
    "Gross_interest_earned_for_M4_user_input__c": df.loc[df['Month'] == 'July', 'Interest'].values[0],
    "Gross_interest_earned_for_M5_user_input__c": df.loc[df['Month'] == 'August', 'Interest'].values[0],
    "Gross_interest_earned_for_M6_user_input__c": df.loc[df['Month'] == 'September', 'Interest'].values[0],
    "Gross_interest_earned_for_M7_user_input__c": df.loc[df['Month'] == 'October', 'Interest'].values[0],
    "Gross_interest_earned_for_M8_user_input__c": df.loc[df['Month'] == 'November', 'Interest'].values[0],
    "Gross_interest_earned_for_M9_user_input__c": df.loc[df['Month'] == 'December', 'Interest'].values[0],
    "Gross_interest_earned_for_M10_user_input__c": df.loc[df['Month'] == 'January', 'Interest'].values[0],
    "Gross_interest_earned_for_M11_user_input__c": df.loc[df['Month'] == 'February', 'Interest'].values[0],
    "Gross_interest_earned_for_M12_user_input__c": df.loc[df['Month'] == 'March', 'Interest'].values[0],
    "WHT_deducted_for_M1_User_input__c": df.loc[df['Month'] == 'April', 'WHT'].values[0],
    "WHT_deducted_for_M2_User_input__c": df.loc[df['Month'] == 'May', 'WHT'].values[0],
    "WHT_deducted_for_M3_User_input__c": df.loc[df['Month'] == 'June', 'WHT'].values[0],
    "WHT_deducted_for_M4_User_input__c": df.loc[df['Month'] == 'July', 'WHT'].values[0],
    "WHT_deducted_for_M5_User_input__c": df.loc[df['Month'] == 'August', 'WHT'].values[0],
    "WHT_deducted_for_M6_User_input__c": df.loc[df['Month'] == 'September', 'WHT'].values[0],
    "WHT_deducted_for_M7_User_input__c": df.loc[df['Month'] == 'October', 'WHT'].values[0],
    "WHT_deducted_for_M8_User_input__c": df.loc[df['Month'] == 'November', 'WHT'].values[0],
    "WHT_deducted_for_M9_User_input__c": df.loc[df['Month'] == 'December', 'WHT'].values[0],
    "WHT_deducted_for_M10_User_input__c": df.loc[df['Month'] == 'January', 'WHT'].values[0],
    "WHT_deducted_for_M11_User_input__c": df.loc[df['Month'] == 'February', 'WHT'].values[0],
    "WHT_deducted_for_M12_User_input__c": df.loc[df['Month'] == 'March', 'WHT'].values[0]
    }
    return data_Scan_result_Interest_income

def df_to_dic_q(df,count,input_list):
    data_Scan_result_Interest_income = {
    "Year_of_assesment__c": st.session_state.assessment_year,
    "Name_of_the_bank__c": input_list[0],
    "NIC_of_the_client__c": input_list[2],
    "WHT_Agent_TIN__c": input_list[4],
    "email_of_the_client__c": input_list[6],
    "Account_no_user_input__c": st.session_state.user_accounts[count][0],
    "is_a_joint_account__c": st.session_state.user_accounts[count][2],
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

def df_to_dic_ys(bank_data,index,input_list):
    data_Scan_result_Interest_income = {
    "Year_of_assesment__c": st.session_state.assessment_year,
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

def df_to_dic_yf(bank_data,index,input_list):
    data_Scan_result_Interest_income = {
    "Year_of_assesment__c": st.session_state.assessment_year,
    "Name_of_the_bank__c": input_list[0],
    "NIC_of_the_client__c": input_list[2],
    "WHT_Agent_TIN__c": input_list[4],
    "email_of_the_client__c": input_list[6],
    "Account_no_user_input__c": bank_data["Account no."][index],
    "is_a_joint_account__c": bank_data["joint account"][index],
    "currency_type__c": bank_data["Currency"][index],
    "Gross_interest_earned_for_M1_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M2_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M3_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M4_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M5_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M6_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M7_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M8_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M9_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M10_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M11_user_input__c":float(bank_data["Interest"][index])/12,
    "Gross_interest_earned_for_M12_user_input__c":float(bank_data["Interest"][index])/12,
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

# for split years employment details
def emp_update_split(emp_detail, check_list, input_list,file_path):
    try:
        #clearing the list
        pos = [3,4,5,6,7,8,9]
        emp_detail = process_data(emp_detail, pos)
        input_list = process_data(input_list, pos)
        st.write("list cleared and ready auth")

        # Read Salesforce credentials
        sf_username = read_file_content("sf_username.txt")
        sf_password = read_file_content("sf_password.txt")
        sf_sec_token = read_file_content("sf_sec_token.txt")

        # Create a connection to Salesforce instance
        sf = validate_sf()
        st.write("func auth successfully")

        data = {
            "APIT_deducted_M1__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M1_incorrect__c": check_list[7],
            "APIT_deducted_M1_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M10__c": float(emp_detail[8]) / 3,
            "APIT_deducted_M10_incorrect__c": check_list[8],
            "APIT_deducted_M10_user_input__c": float(input_list[8]) / 3,
            "APIT_deducted_M11__c": float(emp_detail[8]) / 3,
            "APIT_deducted_M11_incorrect__c": check_list[8],
            "APIT_deducted_M11_user_input__c": float(input_list[8]) / 3,
            "APIT_deducted_M12__c": float(emp_detail[8]) / 3,
            "APIT_deducted_M12_incorrect__c": check_list[8],
            "APIT_deducted_M12_user_input__c": float(input_list[8]) / 3,
            "APIT_deducted_M2__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M2_incorrect__c": check_list[7],
            "APIT_deducted_M2_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M3__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M3_incorrect__c": check_list[7],
            "APIT_deducted_M3_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M4__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M4_incorrect__c": check_list[7],
            "APIT_deducted_M4_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M5__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M5_incorrect__c": check_list[7],
            "APIT_deducted_M5_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M6__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M6_incorrect__c": check_list[7],
            "APIT_deducted_M6_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M7__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M7_incorrect__c": check_list[7],
            "APIT_deducted_M7_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M8__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M8_incorrect__c": check_list[7],
            "APIT_deducted_M8_user_input__c": float(input_list[7]) / 9,
            "APIT_deducted_M9__c": float(emp_detail[7]) / 9,
            "APIT_deducted_M9_incorrect__c": check_list[7],
            "APIT_deducted_M9_user_input__c": float(input_list[7]) / 9,
            "APIT_paid__c": emp_detail[9],
            "APIT_paid_incorrect__c": check_list[9],
            "APIT_paid_user_input__c": input_list[9],
            "Date_Issued__c": emp_detail[11],
            "Date_Issued_incorrect__c": check_list[11],
            "Date_Issued_user_input__c": input_list[11],
            "employer_TIN__c": emp_detail[1],
            "employer_TIN_user_input__c": input_list[1],
            "Employer_s_TIN_No_incorrect__c": check_list[1],
            "Excluded_employement_income_M1__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M1_incorrect__c": check_list[5],
            "Excluded_employement_income_M1_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M10__c": float(emp_detail[6]) / 3,
            "Excluded_employement_income_M10_incorrec__c": check_list[6],
            "Excluded_employement_income_M10_user_inp__c": float(input_list[6]) / 3,
            "Excluded_employement_income_M11__c": float(emp_detail[6]) / 3,
            "Excluded_employement_income_M11_incorrec__c": check_list[6],
            "Excluded_employement_income_M11_user_inp__c": float(input_list[6]) / 3,
            "Excluded_employement_income_M12__c": float(emp_detail[6]) / 3,
            "Excluded_employement_income_M12_incorrec__c": check_list[6],
            "Excluded_employement_income_M12_user_inp__c": float(input_list[6]) / 3,
            "Excluded_employement_income_M2__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M2_incorrect__c": check_list[5],
            "Excluded_employement_income_M2_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M3__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M3_incorrect__c": check_list[5],
            "Excluded_employement_income_M3_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M4__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M4_incorrect__c": check_list[5],
            "Excluded_employement_income_M4_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M5__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M5_incorrect__c": check_list[5],
            "Excluded_employement_income_M5_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M6__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M6_incorrect__c": check_list[5],
            "Excluded_employement_income_M6_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M7__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M7_incorrect__c": check_list[5],
            "Excluded_employement_income_M7_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M8__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M8_incorrect__c": check_list[5],
            "Excluded_employement_income_M8_user_inpu__c": float(input_list[5]) / 9,
            "Excluded_employement_income_M9__c": float(emp_detail[5]) / 9,
            "Excluded_employement_income_M9_incorrect__c": check_list[5],
            "Excluded_employement_income_M9_user_inpu__c": float(input_list[5]) / 9,
            "Name_of_the_employer__c": emp_detail[10],
            "Name_of_the_Employer_incorrect__c": check_list[10],
            "Name_of_the_employer_user_input__c": input_list[10],
            "NIC_Number_incorrect__c": check_list[2],
            "NIC_of_the_client__c": emp_detail[2],
            "NIC_of_the_client_user_input__c": input_list[2],
            "scan_document_id__c": timenow(),
            "Taxable_employement_income_M1__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M1_incorrect__c": check_list[3],
            "Taxable_employement_income_M1_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M10__c": float(emp_detail[4]) / 3,
            "Taxable_employement_income_M10_incorrect__c": check_list[4],
            "Taxable_employement_income_M10_user_inpu__c": float(input_list[4]) / 3,
            "Taxable_employement_income_M11__c": float(emp_detail[4]) / 3,
            "Taxable_employement_income_M11_incorrect__c": check_list[4],
            "Taxable_employement_income_M11_user_inpu__c": float(input_list[4]) / 3,
            "Taxable_employement_income_M12__c": float(emp_detail[4]) / 3,
            "Taxable_employement_income_M12_incorrect__c": check_list[4],
            "Taxable_employement_income_M12_user_inpu__c": float(input_list[4]) / 3,
            "Taxable_employement_income_M2__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M2_incorrect__c": check_list[3],
            "Taxable_employement_income_M2_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M3__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M3_incorrect__c": check_list[3],
            "Taxable_employement_income_M3_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M4__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M4_incorrect__c": check_list[3],
            "Taxable_employement_income_M4_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M5__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M5_incorrect__c": check_list[3],
            "Taxable_employement_income_M5_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M6__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M6_incorrect__c": check_list[3],
            "Taxable_employement_income_M6_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M7__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M7_incorrect__c": check_list[3],
            "Taxable_employement_income_M7_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M8__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M8_incorrect__c": check_list[3],
            "Taxable_employement_income_M8_user_input__c": float(input_list[3]) / 9,
            "Taxable_employement_income_M9__c": float(emp_detail[3]) / 9,
            "Taxable_employement_income_M9_incorrect__c": check_list[3],
            "Taxable_employement_income_M9_user_input__c": float(input_list[3]) / 9,
            "Year_of_assessment__c": emp_detail[0],
            "Year_of_Assessment_incorrect__c": check_list[0],
            "Year_of_assessment_user_input__c": input_list[0],
            "email_of_the_client__c": input_list[12]
        }


        # Create the record in Salesforce
        parent_record = sf.Scan_result_employement__c.create(data)
        parent_record_id = parent_record['id'][:15] # Truncate to 15 characters
        st.write("Record created successfully!")
        upload_image_and_link(parent_record_id,file_path)
        
    except Exception as e:
        st.write("Error creating record:", e)


def emp_update(emp_detail, check_list, input_list,file_path):
    try:
        #clearing the list
        pos = [3,4,5,6]
        emp_detail = process_data(emp_detail, pos)
        input_list = process_data(input_list, pos)

        st.write("list cleared and ready auth")

        #read creds
        sf_username = read_file_content("sf_username.txt")
        sf_password = read_file_content("sf_password.txt")
        sf_sec_token = read_file_content("sf_sec_token.txt")

        # Create a connection to Salesforce instance
        sf = validate_sf()

        st.write("func auth successfully")
        data={
        "APIT_deducted_M1__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M1_incorrect__c":check_list[5],
        "APIT_deducted_M1_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M10__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M10_incorrect__c":check_list[5],
        "APIT_deducted_M10_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M11__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M11_incorrect__c":check_list[5],
        "APIT_deducted_M11_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M12__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M12_incorrect__c":check_list[5],
        "APIT_deducted_M12_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M2__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M2_incorrect__c":check_list[5],
        "APIT_deducted_M2_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M3__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M3_incorrect__c":check_list[5],
        "APIT_deducted_M3_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M4__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M4_incorrect__c":check_list[5],
        "APIT_deducted_M4_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M5__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M5_incorrect__c":check_list[5],
        "APIT_deducted_M5_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M6__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M6_incorrect__c":check_list[5],
        "APIT_deducted_M6_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M7__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M7_incorrect__c":check_list[5],
        "APIT_deducted_M7_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M8__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M8_incorrect__c":check_list[5],
        "APIT_deducted_M8_user_input__c":float(input_list[5]) / 12,
        "APIT_deducted_M9__c":float(emp_detail[5]) / 12,
        "APIT_deducted_M9_incorrect__c":check_list[5],
        "APIT_deducted_M9_user_input__c":float(input_list[5]) / 12,
        "APIT_paid__c":emp_detail[6],
        "APIT_paid_incorrect__c":check_list[6],
        "APIT_paid_user_input__c":input_list[6],
        "Date_Issued__c":emp_detail[8],
        "Date_Issued_incorrect__c":check_list[8],
        "Date_Issued_user_input__c":input_list[8],
        "employer_TIN__c":emp_detail[1],
        "employer_TIN_user_input__c":input_list[1],
        "Employer_s_TIN_No_incorrect__c":check_list[1],
        "Excluded_employement_income_M1__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M1_incorrect__c":check_list[4],
        "Excluded_employement_income_M1_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M10__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M10_incorrec__c":check_list[4],
        "Excluded_employement_income_M10_user_inp__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M11__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M11_incorrec__c":check_list[4],
        "Excluded_employement_income_M11_user_inp__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M12__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M12_incorrec__c":check_list[4],
        "Excluded_employement_income_M12_user_inp__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M2__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M2_incorrect__c":check_list[4],
        "Excluded_employement_income_M2_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M3__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M3_incorrect__c":check_list[4],
        "Excluded_employement_income_M3_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M4__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M4_incorrect__c":check_list[4],
        "Excluded_employement_income_M4_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M5__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M5_incorrect__c":check_list[4],
        "Excluded_employement_income_M5_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M6__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M6_incorrect__c":check_list[4],
        "Excluded_employement_income_M6_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M7__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M7_incorrect__c":check_list[4],
        "Excluded_employement_income_M7_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M8__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M8_incorrect__c":check_list[4],
        "Excluded_employement_income_M8_user_inpu__c":float(input_list[4]) / 12,
        "Excluded_employement_income_M9__c":float(emp_detail[4]) / 12,
        "Excluded_employement_income_M9_incorrect__c":check_list[4],
        "Excluded_employement_income_M9_user_inpu__c":float(input_list[4]) / 12,
        "Name_of_the_employer__c":emp_detail[7],
        "Name_of_the_Employer_incorrect__c":check_list[7],
        "Name_of_the_employer_user_input__c":input_list[7],
        "NIC_Number_incorrect__c":check_list[2],
        "NIC_of_the_client__c":emp_detail[2],
        "NIC_of_the_client_user_input__c":input_list[2],
        "scan_document_id__c":timenow(),
        "Taxable_employement_income_M1__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M1_incorrect__c":check_list[3],
        "Taxable_employement_income_M1_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M10__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M10_incorrect__c":check_list[3],
        "Taxable_employement_income_M10_user_inpu__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M11__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M11_incorrect__c":check_list[3],
        "Taxable_employement_income_M11_user_inpu__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M12__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M12_incorrect__c":check_list[3],
        "Taxable_employement_income_M12_user_inpu__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M2__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M2_incorrect__c":check_list[3],
        "Taxable_employement_income_M2_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M3__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M3_incorrect__c":check_list[3],
        "Taxable_employement_income_M3_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M4__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M4_incorrect__c":check_list[3],
        "Taxable_employement_income_M4_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M5__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M5_incorrect__c":check_list[3],
        "Taxable_employement_income_M5_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M6__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M6_incorrect__c":check_list[3],
        "Taxable_employement_income_M6_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M7__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M7_incorrect__c":check_list[3],
        "Taxable_employement_income_M7_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M8__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M8_incorrect__c":check_list[3],
        "Taxable_employement_income_M8_user_input__c":float(input_list[3]) / 12,
        "Taxable_employement_income_M9__c":float(emp_detail[3]) / 12,
        "Taxable_employement_income_M9_incorrect__c":check_list[3],
        "Taxable_employement_income_M9_user_input__c":float(input_list[3]) / 12,
        "Year_of_assessment__c":emp_detail[0],
        "Year_of_Assessment_incorrect__c":check_list[0],
        "Year_of_assessment_user_input__c":input_list[0],
        "email_of_the_client__c":input_list[9]
        }

        # Create the record in Salesforce
        parent_record = sf.Scan_result_employement__c.create(data)
        parent_record_id = parent_record['id'][:15] # Truncate to 15 characters
        st.write("Record created successfully!")
        upload_image_and_link(parent_record_id,file_path)

    except Exception as e:
        st.write("Error creating record: ",e)

def upload_bank_image_and_link(parent_record_ids, image_file_path):
    pass

def bank_update_m(bank_data, input_list, file_path):
    bank_data = fill_dfs_m(bank_data)
    st.write("Data ready")
    #read creds
    sf_username = read_file_content("sf_username.txt")
    sf_password = read_file_content("sf_password.txt")
    sf_sec_token = read_file_content("sf_sec_token.txt")
    st.write("auth ready")

    # Create a connection to Salesforce instance
    sf = validate_sf()

    st.write("sf auth complete")

    data_Scan_result_bank = {
            "Name_of_the_bank_user_input__c": input_list[0],
            "NIC_of_the_client_user_input__c": input_list[2],
            "Year_of_assesment__c": st.session_state.assessment_year, 
            "Bank_TIN_user_input__c": input_list[4],
            "WHT_certification_no_user_input__c": input_list[5],
            "email_of_the_client__c": input_list[6]
        }

    # Create the Scan_result_bank__c record in Salesforce
    parent_bank_record = sf.Scan_result_bank__c.create(data_Scan_result_bank)
    parent_bank_record_id = parent_bank_record['id']
    st.write("Scan_result_bank__c record created successfully!")

    # List to store all created parent record IDs
    parent_record_ids = [parent_bank_record_id]
    limit_acc()

    for items in range(len(st.session_state.user_accounts)):
        data_Scan_result_bank_balance = {
                "Name_of_the_bank__c": input_list[0],
                "NIC_of_the_client__c": input_list[2],
                "email_of_the_client__c": input_list[6],
                "Account_no_user_input__c": st.session_state.user_accounts[items][0],
                "currency_type_user_input__c": st.session_state.user_accounts[items][1],
                "Year_of_assesment__c": st.session_state.assessment_year
            }
        # Create the Scan_result_bank_balance__c record in Salesforce
        parent_balance_record = sf.Scan_result_bank_balance__c.create(data_Scan_result_bank_balance)
        parent_balance_record_id = parent_balance_record['id']
        parent_record_ids.append(parent_balance_record_id)
        st.write("Scan_result_bank_balance__c record created successfully for account number:", st.session_state.user_accounts[items][0])

    count = 0

    for dfs in bank_data:
        data_Scan_result_Interest_income = df_to_dic_m(bank_data[dfs],count,input_list)
        cleaned_data_Scan_result_Interest_income = {k: (0 if pd.isna(v) else v) for k, v in data_Scan_result_Interest_income.items()}
        # Create the Scan_result_Interest_income__c record in Salesforce
        parent_interest_income_record = sf.Scan_result_Interest_income__c.create(cleaned_data_Scan_result_Interest_income)
        parent_interest_income_record_id = parent_interest_income_record['id']
        parent_record_ids.append(parent_interest_income_record_id)
        st.write("Scan_result_Interest_income__c record created successfully for account number:", st.session_state.user_accounts[count][0])
        count += 1

    #upload_image_and_link(parent_record_ids,file_path)

    st.write("files not uploaded")

def bank_update_q(bank_data, input_list, file_path):
    bank_data = fill_dfs_q(bank_data)
    st.write("Data ready")
    #read creds
    sf_username = read_file_content("sf_username.txt")
    sf_password = read_file_content("sf_password.txt")
    sf_sec_token = read_file_content("sf_sec_token.txt")

    # Create a connection to Salesforce instance
    sf = validate_sf()

    st.write("sf auth")

    data_Scan_result_bank = {
            "Name_of_the_bank_user_input__c": input_list[0],
            "NIC_of_the_client_user_input__c": input_list[2],
            "Year_of_assesment__c": st.session_state.assessment_year, 
            "Bank_TIN_user_input__c": input_list[4],
            "WHT_certification_no_user_input__c": input_list[5],
            "email_of_the_client__c": input_list[6]
        }

    # Create the Scan_result_bank__c record in Salesforce
    parent_bank_record = sf.Scan_result_bank__c.create(data_Scan_result_bank)
    parent_bank_record_id = parent_bank_record['id']
    st.write("Scan_result_bank__c record created successfully!")

    # List to store all created parent record IDs
    parent_record_ids = [parent_bank_record_id]
    limit_acc()

    for items in range(len(st.session_state.user_accounts)):
        data_Scan_result_bank_balance = {
                "Name_of_the_bank__c": input_list[0],
                "NIC_of_the_client__c": input_list[2],
                "email_of_the_client__c": input_list[6],
                "Account_no_user_input__c": st.session_state.user_accounts[items][0],
                "currency_type_user_input__c": st.session_state.user_accounts[items][1],
                "Year_of_assesment__c": st.session_state.assessment_year
            }
        # Create the Scan_result_bank_balance__c record in Salesforce
        parent_balance_record = sf.Scan_result_bank_balance__c.create(data_Scan_result_bank_balance)
        parent_balance_record_id = parent_balance_record['id']
        parent_record_ids.append(parent_balance_record_id)
        st.write("Scan_result_bank_balance__c record created successfully for account number:", st.session_state.user_accounts[items][0])

    count = 0
    for dfs in bank_data:
        data_Scan_result_Interest_income = df_to_dic_q(bank_data[dfs],count,input_list)
        cleaned_data_Scan_result_Interest_income = {k: (0 if pd.isna(v) else v) for k, v in data_Scan_result_Interest_income.items()}
        # Create the Scan_result_Interest_income__c record in Salesforce
        parent_interest_income_record = sf.Scan_result_Interest_income__c.create(cleaned_data_Scan_result_Interest_income)
        parent_interest_income_record_id = parent_interest_income_record['id']
        parent_record_ids.append(parent_interest_income_record_id)
        st.write("Scan_result_Interest_income__c record created successfully for account number:", st.session_state.user_accounts[count][0])
        count += 1

    #upload_image_and_link(parent_record_ids,file_path)

    st.write("files not uploaded")

def bank_update_s(bank_data, input_list, file_path):
    #read creds
    st.write("sf auth ready")
    sf_username = read_file_content("sf_username.txt")
    sf_password = read_file_content("sf_password.txt")
    sf_sec_token = read_file_content("sf_sec_token.txt")

    # Create a connection to Salesforce instance
    sf = validate_sf()

    st.write("sf auth")

    data_Scan_result_bank = {
            "Name_of_the_bank_user_input__c": input_list[0],
            "NIC_of_the_client_user_input__c": input_list[2],
            "Year_of_assesment__c": st.session_state.assessment_year, 
            "Bank_TIN_user_input__c": input_list[4],
            "WHT_certification_no_user_input__c": input_list[5],
            "email_of_the_client__c": input_list[6]
        }

    # Create the Scan_result_bank__c record in Salesforce
    parent_bank_record = sf.Scan_result_bank__c.create(data_Scan_result_bank)
    parent_bank_record_id = parent_bank_record['id']
    st.write("Scan_result_bank__c record created successfully!")

    # List to store all created parent record IDs
    parent_record_ids = [parent_bank_record_id]

    bank_data = process_dataframe_ys(bank_data)

    #bank balance needed to be sent droped for now

    for index,row in bank_data.iterrows():
        data_Scan_result_Interest_income = df_to_dic_ys(bank_data,index,input_list)
        cleaned_data_Scan_result_Interest_income = {k: (0 if pd.isna(v) else v) for k, v in data_Scan_result_Interest_income.items()}
        # Create the Scan_result_Interest_income__c record in Salesforce
        parent_interest_income_record = sf.Scan_result_Interest_income__c.create(cleaned_data_Scan_result_Interest_income)
        parent_interest_income_record_id = parent_interest_income_record['id']
        parent_record_ids.append(parent_interest_income_record_id)
    st.write("Scan_result_Interest_income__c records created successfully")

    #upload_image_and_link(parent_record_ids,file_path)

    st.write("files not uploaded")

def bank_update_f(bank_data, input_list, file_path):
    #read creds
    st.write("sf auth ready")
    sf_username = read_file_content("sf_username.txt")
    sf_password = read_file_content("sf_password.txt") 
    sf_sec_token = read_file_content("sf_sec_token.txt")

    # Create a connection to Salesforce instance
    sf = validate_sf()
    
    st.write("sf auth")

    data_Scan_result_bank = {
            "Name_of_the_bank_user_input__c": input_list[0],
            "NIC_of_the_client_user_input__c": input_list[2],
            "Year_of_assesment__c": st.session_state.assessment_year, 
            "Bank_TIN_user_input__c": input_list[4],
            "WHT_certification_no_user_input__c": input_list[5],
            "email_of_the_client__c": input_list[6]
        }

    # Create the Scan_result_bank__c record in Salesforce
    parent_bank_record = sf.Scan_result_bank__c.create(data_Scan_result_bank)
    parent_bank_record_id = parent_bank_record['id']
    st.write("Scan_result_bank__c records created successfully!")

    # List to store all created parent record IDs
    parent_record_ids = [parent_bank_record_id]

    bank_data = process_dataframe_yf(bank_data)

    #bank balance needed to be sent droped for now

    for index,row in bank_data.iterrows():
        data_Scan_result_Interest_income = df_to_dic_yf(bank_data,index,input_list)
        cleaned_data_Scan_result_Interest_income = {k: (0 if pd.isna(v) else v) for k, v in data_Scan_result_Interest_income.items()}
        # Create the Scan_result_Interest_income__c record in Salesforce
        parent_interest_income_record = sf.Scan_result_Interest_income__c.create(cleaned_data_Scan_result_Interest_income)
        parent_interest_income_record_id = parent_interest_income_record['id']
        parent_record_ids.append(parent_interest_income_record_id)
    st.write("Scan_result_Interest_income__c records created successfully")
    
    #upload_image_and_link(parent_record_ids,file_path)

    st.write("files not uploaded")

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
            st.warning(f"No Tax_File__c record found for Customer ID: {customer_id} and Assessment Year: {assessment_year}")
            return None

    except Exception as e:
        st.error(f"Error retrieving Tax_File__c record: {e}")
        return None

def wealth_update(user_id, input_list,file_path):
    """
    Updates or creates a TFO Investment Income record in Salesforce.

    Args:
        user_id: The user id.
        input_list: User input data.
    """
    try:
        sf = validate_sf()

        # Extract relevant data from input_list
        assessment_year = input_list[0]
        employer_name = input_list[2]
        unrealized_gains = input_list[4]
        user_income = input_list[3]
       
        user_id = input_list[5]

        # 1. Get the actual Customer ID
        actual_customer_id = get_actual_customer_id(sf, user_id)
        if not actual_customer_id:
            return  # Stop if no actual customer ID is found
        print(f"Actual Customer ID: {actual_customer_id}")

        # 2. Get all tax files for the customer
        tax_files = get_tax_files_for_customer(sf, actual_customer_id)
        print(f"Tax Files: {tax_files}")

        # 3. Get the correct tax file for the year
        target_tax_file = get_tax_file_for_year(tax_files, assessment_year)
        print(f"Target Tax File: {target_tax_file}")
        
        tax_fileID=get_tax_file_id_by_customer_and_year(actual_customer_id, target_tax_file)
        print(tax_fileID)

        # Data create
        data = {
            "Year_of_Assessment__c": assessment_year,
            "Name_of_the_employer__c": employer_name,
            "Income_type__c": "Unit Trust",  # Corrected: Use the API name directly
            "UT_Unrealized_Gains__c": unrealized_gains, 
            "Income_M6__c": user_income,
            "Tax_File__c": tax_fileID,  # Link to Tax_File__c
            
        }

        #st.write("Data to be sent to Salesforce:", data)
        print(data)
        # 4. Create the record
        parent_record = sf.TFO_Investment_Income__c.create(data)
        target_record_id = parent_record['id']
        st.success(f"Record created successfully! Record ID: {target_record_id}")
        print(f"Record created successfully! Record ID: ")
        st.write(" records created successfully")
        
        
    except Exception as e:
        st.error(f"Error creating or updating record: {e}")