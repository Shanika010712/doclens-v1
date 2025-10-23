# process_2425_mul.
import streamlit as st
from identify import bank_identify
from identify_bank import banktype_identify
import PIL.Image
from PIL import Image
# Import from the 2425 extractors file
from extractors_2425 import *
from bank_text_ouput import * # Assuming this is generic and doesn't need a year-specific version

# --- Renamed Wrapper Functions for 2024/2025 ---

def wrap_2425_y_mul(image):
    # Call the 2425 multi-image yearly extractor
    response_bank_2425 = int_inc_2425_multiple(image)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "Y"
    out_bank = process_bank_text_output_y(response_bank_2425)
    st.session_state.out_emp = out_bank
    # Set doc_type (Assuming 2 like 23/24, change to 94 if it's a split year)
    st.session_state.doc_type = 2

def wrap_2425_m_mul(image):
    # Call the 2425 multi-image monthly extractor
    response_bank_2425 = int_inc_2425_m_multiple(image)
    #st.write(response_bank_2425)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "M"
    out_bank = process_bank_text_output(response_bank_2425)
    st.session_state.out_emp = out_bank
    # Set doc_type
    st.session_state.doc_type = 2

def wrap_2425_q_mul(image):
    # Call the 2425 multi-image quarterly extractor
    response_bank_2425 = int_inc_2425_q_multiple(image)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "Q"
    out_bank = process_bank_text_output(response_bank_2425)
    st.session_state.out_emp = out_bank
    # Set doc_type
    st.session_state.doc_type = 2

def wrap_com_2425_m_mul(image):
    # Call the 2425 multi-image ComBank monthly extractor
    response_bank_2425 = int_inc_com_2425_m_multiple(image)
    #st.write(response_bank_2425)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "M"
    out_bank = process_bank_text_output(response_bank_2425)
    #st.write(out_bank)
    st.session_state.out_emp = out_bank
    # Set doc_type
    st.session_state.doc_type = 2

def wrap_hsbc_2425_m_mul(image):
    # Call the 2425 multi-image HSBC monthly extractor
    response_bank_2425 = int_inc_hsbc_2425_m_multiple(image)
    st.write(response_bank_2425)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "M"
    out_bank = process_bank_text_output(response_bank_2425)
    st.write(out_bank)
    st.session_state.out_emp = out_bank
    # Set doc_type
    st.session_state.doc_type = 2

def wrap_hnb_2425_m_mul(image):
    # Call the 2425 multi-image HNB monthly extractor
    response_bank_2425 = int_inc_hnb_2425_m_multiple(image)
    #st.write(response_bank_2425)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "M"
    out_bank = process_bank_text_output(response_bank_2425)
    #st.write(out_bank)
    st.session_state.out_emp = out_bank
    # Set doc_type
    st.session_state.doc_type = 2

def wrap_seylan_2425_m_mul(image):
    # Call the 2425 multi-image Seylan monthly extractor
    response_bank_2425 = int_inc_seylan_2425_m_multiple(image)
    #st.write(response_bank_2425)
    st.write("Extraction is completed")
    # Set assessment year to 24/25
    st.session_state.assessment_year = '2024/2025'
    st.session_state.bank_type = "M"
    out_bank = process_bank_text_output(response_bank_2425)
    #st.write(out_bank)
    st.session_state.out_emp = out_bank
    # Set doc_type
    st.session_state.doc_type = 2

# --- Renamed Main Processing Function for 2024/2025 ---

def process_2024_2025_mul(images, first_bank_img):
    st.session_state.multiple_images = True
    banktype_name = banktype_identify(first_bank_img)
    #st.markdown(f"**Bank Name: {banktype_name}**") # Optional display

    # --- Logic for specific banks (using 2425 wrappers and keys) ---
    if "Hatton National Bank." in banktype_name:
        st.write("Hatton National Bank identified.")
        bank_period = bank_identify(first_bank_img)
        st.write(f"Bank Period identified: {bank_period}")

        if "year" in bank_period.lower():
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="y2425mm") # Use 2425 wrapper and key
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="y2425qm") # Use 2425 wrapper and key
            st.button("Extract annually data :large_blue_circle:", on_click=lambda: wrap_2425_y_mul(images), key="y2425ym") # Use 2425 wrapper and key
        elif "month" in bank_period.lower():
            st.button("Extract monthly data :large_blue_circle:", on_click=lambda: wrap_hnb_2425_m_mul(images), key="mhnb2425mm") 
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="m2425qm") # Use 2425 wrapper and key
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="m2425ym") # Use 2425 wrapper and key
        else: # Assume quarterly
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="q2425mm") # Use 2425 wrapper and key
            st.button("Extract quarterly data :large_blue_circle:", on_click=lambda: wrap_2425_q_mul(images), key="q2425qm") # Use 2425 wrapper and key
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="q2425ym") # Use 2425 wrapper and key

    elif "Commercial Bank PLC." in banktype_name:
        st.write("Commercial Bank identified.")
        bank_period = bank_identify(first_bank_img)
        st.write(f"Document Period : {bank_period}")

        if "year" in bank_period.lower():
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda:wrap_2425_m_mul (images), key="y2425mm")
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="y2425qm")
            st.button("Extract annually data :large_blue_circle:", on_click=lambda: wrap_2425_y_mul(images), key="y2425ym")
        elif "month" in bank_period.lower():
            st.button("Extract monthly data :large_green_circle:", on_click=lambda: wrap_com_2425_m_mul(images), key="mcom2425mm") # Use 2425 ComBank wrapper and key
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="m2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="m2425ym")
        else: # Assume quarterly
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_com_2425_m_mul(images), key="q2425mm")
            st.button("Extract quarterly data :large_blue_circle:", on_click=lambda: wrap_2425_q_mul(images), key="q2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="q2425ym")

    elif "Seylon Bank PLC." in banktype_name: # Note: Original had "Seylon", kept it consistent
        st.write("Seylon Bank identified.")
        bank_period = bank_identify(first_bank_img)
        st.write(f"Document Period : {bank_period}")

        if "year" in bank_period.lower():
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="y2425mm")
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="y2425qm")
            st.button("Extract annually data :large_blue_circle:", on_click=lambda: wrap_2425_y_mul(images), key="y2425ym")
        elif "month" in bank_period.lower():
            st.button("Extract monthly data :large_blue_circle:", on_click=lambda: wrap_seylan_2425_m_mul(images), key="msey2425mm") # Use 2425 Seylan wrapper and key
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="m2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="m2425ym")
        else: # Assume quarterly
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="q2425mm")
            st.button("Extract quarterly data :large_blue_circle:", on_click=lambda: wrap_2425_q_mul(images), key="q2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="q2425ym")

    elif "Hongkong and Shanghai Banking Corporation Limited" in banktype_name:
        st.write("HSBC Bank identified.")
        bank_period = bank_identify(first_bank_img)
        st.write(f"Document Period : {bank_period}")

        if "year" in bank_period.lower():
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="y2425mm")
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="y2425qm")
            st.button("Extract annually data :large_blue_circle:", on_click=lambda: wrap_2425_y_mul(images), key="y2425ym")
        elif "month" in bank_period.lower():
            st.button("Extract monthly data :large_blue_circle:", on_click=lambda: wrap_hsbc_2425_m_mul(images), key="mhsbc2425mm") # Use 2425 HSBC wrapper and key
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="m2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="m2425ym")
        else: # Assume quarterly
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="q2425mm")
            st.button("Extract quarterly data :large_blue_circle:", on_click=lambda: wrap_2425_q_mul(images), key="q2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="q2425ym")

    # --- Fallback for normal/unidentified banks (using 2425 wrappers and keys) ---
    elif "This file can be extracted normally." in banktype_name:
        st.write("Normal extraction.")
        bank_period = bank_identify(first_bank_img)
        st.write(f"Document Period : {bank_period}")

        if "year" in bank_period.lower():
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="y2425mm")
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="y2425qm")
            st.button("Extract annually data :large_blue_circle:", on_click=lambda: wrap_2425_y_mul(images), key="y2425ym")
        elif "month" in bank_period.lower():
            st.button("Extract monthly data :large_blue_circle:", on_click=lambda: wrap_2425_m_mul(images), key="m2425mm") # Use generic 2425 monthly wrapper
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="m2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="m2425ym")
        else: # Assume quarterly
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="q2425mm")
            st.button("Extract quarterly data :large_blue_circle:", on_click=lambda: wrap_2425_q_mul(images), key="q2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="q2425ym")
    else: # Bank type not specifically identified, use generic wrappers
        #st.write("Bank type not identified, using generic extraction.")
        bank_period = bank_identify(first_bank_img)
        st.write(f"Document Period : {bank_period}")

        if "year" in bank_period.lower():
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="y2425mm")
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="y2425qm")
            st.button("Extract annually data :large_blue_circle:", on_click=lambda: wrap_2425_y_mul(images), key="y2425ym")
        elif "month" in bank_period.lower():
            st.button("Extract monthly data :large_blue_circle:", on_click=lambda: wrap_2425_m_mul(images), key="m2425mm")
            st.button("Extract quarterly data :large_yellow_circle:", on_click=lambda: wrap_2425_q_mul(images), key="m2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="m2425ym")
        else: # Assume quarterly
            st.button("Extract monthly data :large_yellow_circle:", on_click=lambda: wrap_2425_m_mul(images), key="q2425mm")
            st.button("Extract quarterly data :large_blue_circle:", on_click=lambda: wrap_2425_q_mul(images), key="q2425qm")
            st.button("Extract annually data :large_yellow_circle:", on_click=lambda: wrap_2425_y_mul(images), key="q2425ym")
