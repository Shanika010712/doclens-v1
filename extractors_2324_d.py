#AI library
import google.generativeai as vision_genai
import os
#read file function
from read_file import read_file_content_txt

# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#setup ai model
api_filename = "gemini_api.txt"
key = read_file_content_txt(os.path.join(SCRIPT_DIR, api_filename))
vision_genai.configure(api_key=key)
vision_model = vision_genai.GenerativeModel('gemini-2.0-flash')

vision_model_test=vision_genai.GenerativeModel('gemini-2.5-flash')
#com bank model
vision_model_combank= vision_genai.GenerativeModel('gemini-2.5-flash')
#hsbc
vision_model_hsbc= vision_genai.GenerativeModel('gemini-2.0-flash')
#hnb
vision_model_hnb= vision_genai.GenerativeModel('gemini-2.0-flash')



#get prompts for document types
emp_2324_txt = "employement_2324.txt"
int_inc_2324_txt = "bank_2324.txt"
int_inc_2324m_txt = "bank_2324_m.txt"
int_inc_2324q_txt = "bank_2324_q.txt"
int_balance_2324_txt ="balance_2324.txt"
#int_inc_2324com_txt="Commercial bank_2324_m_prompt.txt"
#wealth
wealth_2324_txt = "wealth_manage_2324.txt"

#for multiple images
int_inc_2324_multi_txt = "bank_2324_multi.txt"
int_inc_2324m_multi_txt = "bank_2324_m_multi.txt"
int_inc_2324q_multi_txt = "bank_2324_q_multi.txt"
int_inc_2324com_multi_txt="com_2324_m_multy.txt"
int_inc_2324hsbc_multi_txt="HSBC_2324_m_multy.txt"
int_inc_2324hnb_multi_txt="HNB_2324_m.txt"
int_inc_2324seylan_multi_txt="seylan_2324_m_multy.txt"

#calling prompts
emp_2324_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, emp_2324_txt))
int_2324_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324_txt))
int_2324_m_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324m_txt))
int_2324_q_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324q_txt))
int_2324com_prompt= read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324com_multi_txt)) # Assuming this was intended for com_multi
wealth_2324_prompt =read_file_content_txt(os.path.join(SCRIPT_DIR, wealth_2324_txt))
balance_2324_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_balance_2324_txt))


#for multiple images
int_2324_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324_multi_txt))
int_2324_m_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324m_multi_txt))
int_2324_q_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324q_multi_txt))
int_2324com_multy_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324com_multi_txt))
int_2324hsbc_multy_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324hsbc_multi_txt))
int_2324hnb_multy_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324hnb_multi_txt))
int_2324seylan_multy_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2324seylan_multi_txt))

def balance_2324_d(image):
  details = vision_model.generate_content([balance_2324_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

def balance_2324_multiple_d(image):
  details = vision_model.generate_content([balance_2324_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text


#wealth management single image
def wealth_2324_d(image):
  details = vision_model.generate_content([wealth_2324_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
         'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management multiple images
def wealth_2324_multiple_d(image):
  details = vision_model.generate_content([wealth_2324_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text


#employment 
def employment_2324_d(image):
  details = vision_model.generate_content([emp_2324_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment with multiple docs
def employment_2324_multiple_d(image):
  details = vision_model.generate_content([emp_2324_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

def employment_2324_multiple_v2_d(image):
  details = vision_model_test.generate_content([emp_2324_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank
def int_inc_2324_d(image):
  details = vision_model.generate_content([int_2324_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2324_m_d(image):
  details = vision_model.generate_content([int_2324_m_prompt,image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_2324_q_d(image):
  details = vision_model.generate_content([int_2324_q_prompt,image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank multiple images
#bank year 
def int_inc_2324_multiple_d(image):
  details = vision_model.generate_content([int_2324_multi_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2324_m_multiple_d(image):
  details = vision_model.generate_content([int_2324_m_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

def int_inc_com_2324_m_multiple_d(image):
  details = vision_model_combank.generate_content([int_2324com_multy_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2324com_multy_prompt)
  details.resolve()
  return details.text



def int_inc_hsbc_2324_m_multiple_d(image):
  details = vision_model_hsbc.generate_content([int_2324hsbc_multy_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2324com_multy_prompt)
  details.resolve()
  return details.text


def int_inc_hnb_2324_m_multiple_d(image):
  details = vision_model_hnb.generate_content([int_2324hnb_multy_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2324com_multy_prompt)
  details.resolve()
  return details.text

def int_inc_seylan_2324_m_multiple_d(image):
  details = vision_model_hnb.generate_content([int_2324seylan_multy_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2324com_multy_prompt)
  details.resolve()
  return details.text









#bank quarter
def int_inc_2324_q_multiple(image):
  details = vision_model.generate_content([int_2324_q_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text
