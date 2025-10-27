import streamlit as st
import pandas as pd
import calendar


def dates_to_months(cell):
    """Converts a date or date‐string to a month name, if possible."""
    months = list(calendar.month_name)[1:]
    try:
        # Try converting cell to pd.Timestamp
        date = pd.to_datetime(cell, errors='coerce')
        if pd.notnull(date):
            return date.strftime('%B')
    except Exception:
        pass
    # If cell is already a month or cannot convert, return original
    return cell

def clean_list(details_list, limit):
    """Ensures details_list has at least 'limit' items by padding with empty strings."""
    details_list = list(details_list)  # make a copy
    while len(details_list) < limit:
        details_list.append("")
    return details_list

def display_wealth(details_list, file_path):
    """
    Returns HTML for displaying Wealth Management data as a form.
    Expects details_list to have 5 elements.
    """
    details_list = clean_list(details_list, 5)
    html = f'''
    <form method="post" action="/salesforce/send/">
      <label>Year of Assessment:</label>
      <input type="text" name="year_assessment" value="{details_list[0]}" /><br/>
      <label>Name of the Person:</label>
      <input type="text" name="person_name" value="{details_list[1]}" /><br/>
      <label>Name of the Employer:</label>
      <input type="text" name="employer_name" value="{details_list[2]}" /><br/>
      <label>Realized Gains:</label>
      <input type="text" name="realized_gains" value="{details_list[3]}" /><br/>
      <label>Unrealized Gains:</label>
      <input type="text" name="unrealized_gains" value="{details_list[4]}" /><br/>
      <label>Customer ID:</label>
      <input type="text" name="customer_id" value=""/><br/>
      <button type="submit">Send to Salesforce</button>
    </form>
    '''
    return html

def display_emp_split(details_list, file_path):
    """
    Returns HTML for displaying Employment data (split format) as a form.
    Expects details_list to have 12 elements.
    """
    details_list = clean_list(details_list, 12)
    html = f'''
    <form method="post" action="/salesforce/send/">
      <label>Year of Assessment:</label>
      <input type="text" name="year_assessment" value="{details_list[0]}" /><br/>
      <label>Employer's TIN No.:</label>
      <input type="text" name="employer_tin" value="{details_list[1]}" /><br/>
      <label>NIC No.:</label>
      <input type="text" name="nic" value="{details_list[2]}" /><br/>
      <label>Total Gross Remuneration (Period 1):</label>
      <input type="text" name="gross1" value="{details_list[3]}" /><br/>
      <label>Total Gross Remuneration (Period 2):</label>
      <input type="text" name="gross2" value="{details_list[4]}" /><br/>
      <label>Benefits Excluded (Period 1):</label>
      <input type="text" name="benefits1" value="{details_list[5]}" /><br/>
      <label>Benefits Excluded (Period 2):</label>
      <input type="text" name="benefits2" value="{details_list[6]}" /><br/>
      <label>Tax Deducted (Period 1):</label>
      <input type="text" name="tax1" value="{details_list[7]}" /><br/>
      <label>Tax Deducted (Period 2):</label>
      <input type="text" name="tax2" value="{details_list[8]}" /><br/>
      <label>Total Remitted:</label>
      <input type="text" name="remitted" value="{details_list[9]}" /><br/>
      <label>Name of the Employer:</label>
      <input type="text" name="employer_name" value="{details_list[10]}" /><br/>
      <label>Date:</label>
      <input type="text" name="date" value="{details_list[11]}" /><br/>
      <label>Email:</label>
      <input type="email" name="email" value="default@example.com" /><br/>
      <button type="submit">Send to Salesforce</button>
    </form>
    '''
    return html

def display_emp(details_list, file_path):
    """
    Returns HTML for displaying Employment data (full format) as a form.
    Expects details_list to have 9 elements.
    """
    details_list = clean_list(details_list, 9)
    html = f'''
    <form method="post" action="/salesforce/send/">
      <label>Year of Assessment:</label>
      <input type="text" name="year_assessment" value="{details_list[0]}" /><br/>
      <label>Employer's TIN No.:</label>
      <input type="text" name="employer_tin" value="{details_list[1]}" /><br/>
      <label>NIC No.:</label>
      <input type="text" name="nic" value="{details_list[2]}" /><br/>
      <label>Total Gross Remuneration:</label>
      <input type="text" name="gross" value="{details_list[3]}" /><br/>
      <label>Benefits Excluded:</label>
      <input type="text" name="benefits" value="{details_list[4]}" /><br/>
      <label>Total Tax Deducted:</label>
      <input type="text" name="tax" value="{details_list[5]}" /><br/>
      <label>Total Remitted:</label>
      <input type="text" name="remitted" value="{details_list[6]}" /><br/>
      <label>Name of the Employer:</label>
      <input type="text" name="employer_name" value="{details_list[7]}" /><br/>
      <label>Date:</label>
      <input type="text" name="date" value="{details_list[8]}" /><br/>
      <label>Email:</label>
      <input type="email" name="email" value="default@example.com" /><br/>
      <button type="submit">Send to Salesforce</button>
    </form>
    '''
    return html

def display_bank_m(updated_items, file_path):
    """
    Returns HTML for displaying Bank data as a form.
    'updated_items' is expected to be a list where:
      - The first element contains general bank data (list with 6 items).
      - Subsequent elements represent account details which may include period details.
    """
    # Render general bank information (first list)
    bank_details = updated_items[0]
    html = f'''
    <form method="post" action="/salesforce/send/">
      <label>Bank:</label>
      <input type="text" name="bank" value="{bank_details[0]}" /><br/>
      <label>Customer Name:</label>
      <input type="text" name="customer_name" value="{bank_details[1]}" /><br/>
      <label>NIC:</label>
      <input type="text" name="nic" value="{bank_details[2]}" /><br/>
      <label>Issued Date:</label>
      <input type="text" name="issued_date" value="{bank_details[3]}" /><br/>
      <label>TIN of WHT Agent:</label>
      <input type="text" name="tin" value="{bank_details[4]}" /><br/>
      <label>WHT Certification Number:</label>
      <input type="text" name="cert_no" value="{bank_details[5]}" /><br/>
      <label>Email:</label>
      <input type="email" name="email" value="default@example.com" /><br/>
    '''
    # Render each account’s details (starting from index 1)
    html += '<div>'
    for idx, account in enumerate(updated_items[1:], start=1):
        # Assume account is structured as [account_no, currency, period_details]
        html += f'<div style="margin-bottom:20px; border:1px solid #ccc; padding:10px;">'
        html += f'<label>Account {idx} Number:</label> <input type="text" name="account_{idx}_number" value="{account[0]}" /><br/>'
        html += f'<label>Currency:</label> <input type="text" name="account_{idx}_currency" value="{account[1]}" /><br/>'
        # If period details exist, render them as a table
        if len(account) > 2 and isinstance(account[2], list) and account[2]:
            html += '<table border="1" cellpadding="5"><thead><tr><th>Month</th><th>Interest</th><th>WHT</th></tr></thead><tbody>'
            for period in account[2]:
                if len(period) == 3:
                    html += '<tr>'
                    html += f'<td><input type="text" name="account_{idx}_month" value="{period[0]}" /></td>'
                    html += f'<td><input type="text" name="account_{idx}_interest" value="{period[1]}" /></td>'
                    html += f'<td><input type="text" name="account_{idx}_wht" value="{period[2]}" /></td>'
                    html += '</tr>'
            html += '</tbody></table>'
        html += '</div>'
    html += '</div>'
    html += '<button type="submit">Send to Salesforce</button></form>'
    return html

def display_bank_y(updated_items, file_path):
     """
    Returns HTML for displaying Bank data as a form.
    'updated_items' is expected to be a list where:
      - The first element contains general bank data (list with 6 items).
      - Subsequent elements represent account details which may include period details.
    """
    # Render general bank information (first list)
    bank_details = updated_items[0]
    html = f'''
    <form method="post" action="/salesforce/send/">
      <label>Bank:</label>
      <input type="text" name="bank" value="{bank_details[0]}" /><br/>
      <label>Customer Name:</label>
      <input type="text" name="customer_name" value="{bank_details[1]}" /><br/>
      <label>NIC:</label>
      <input type="text" name="nic" value="{bank_details[2]}" /><br/>
      <label>Issued Date:</label>
      <input type="text" name="issued_date" value="{bank_details[3]}" /><br/>
      <label>TIN of WHT Agent:</label>
      <input type="text" name="tin" value="{bank_details[4]}" /><br/>
      <label>WHT Certification Number:</label>
      <input type="text" name="cert_no" value="{bank_details[5]}" /><br/>
      <label>Email:</label>
      <input type="email" name="email" value="default@example.com" /><br/>
    '''
    # Render each account’s details (starting from index 1)
    html += '<div>'
    for idx, account in enumerate(updated_items[1:], start=1):
        # Assume account is structured as [account_no, currency, period_details]
        html += f'<div style="margin-bottom:20px; border:1px solid #ccc; padding:10px;">'
        html += f'<label>Account {idx} Number:</label> <input type="text" name="account_{idx}_number" value="{account[0]}" /><br/>'
        html += f'<label>Currency:</label> <input type="text" name="account_{idx}_currency" value="{account[1]}" /><br/>'
        # If period details exist, render them as a table
        if len(account) > 2 and isinstance(account[2], list) and account[2]:
            html += '<table border="1" cellpadding="5"><thead><tr><th>Month</th><th>Interest</th><th>WHT</th></tr></thead><tbody>'
            for period in account[2]:
                if len(period) == 3:
                    html += '<tr>'
                    html += f'<td><input type="text" name="account_{idx}_month" value="{period[0]}" /></td>'
                    html += f'<td><input type="text" name="account_{idx}_interest" value="{period[1]}" /></td>'
                    html += f'<td><input type="text" name="account_{idx}_wht" value="{period[2]}" /></td>'
                    html += '</tr>'
            html += '</tbody></table>'
        html += '</div>'
    html += '</div>'
    html += '<button type="submit">Send to Salesforce</button></form>'
    return html
   
# For example:
#
# from app1.utils.display import display_bank, display_emp, ...
#
# def bank_display_view(request):
#     # Process your bank data into a Python list (updated_items)
#     html_output = display_bank(updated_items, file_path="/path/to/file")
#     return HttpResponse(html_output)

