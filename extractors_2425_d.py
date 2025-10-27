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
vision_model = vision_genai.GenerativeModel('gemini-2.5-flash')
#com bank model
vision_model_combank= vision_genai.GenerativeModel('gemini-2.5-flash')
#hsbc
vision_model_hsbc= vision_genai.GenerativeModel('gemini-2.0-flash')
#hnb
vision_model_hnb= vision_genai.GenerativeModel('gemini-2.0-flash')



#get prompts for document types
emp_2425_txt = "employement_2425.txt"
int_inc_2425_txt = "bank_2425.txt"
int_inc_2425m_txt = "bank_2425_m.txt"
int_inc_2425q_txt = "bank_2425_q.txt"
int_balance_2425_txt ="balance_2425.txt"
#int_inc_2425com_txt="Commercial bank_2425_m_prompt.txt" # Updated comment
#wealth
wealth_2425_txt = "wealth_manage_2425.txt"

#for multiple images
int_inc_2425_multi_txt = "bank_2425_multy.txt"
int_inc_2425m_multi_txt = "bank_2425_m_multy.txt"
int_inc_2425q_multi_txt = "bank_2425_q_multy.txt" # Updated filename string
int_inc_2425com_multi_txt="com_2425_m_multy.txt" # Updated filename string
int_inc_2425hsbc_multi_txt="HSBC_2425_m_multy.txt" # Updated filename string
int_inc_2425hnb_multi_txt="HNB_2425_m_multy.txt" # Updated filename string
int_inc_2425seylan_multi_txt="seylan_2425_m_multy.txt" # Updated filename string

#calling prompts
emp_2425_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, emp_2425_txt))
int_2425_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425_txt))
int_2425_m_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425m_txt))
int_2425_q_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425q_txt))
int_2425com_prompt= read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425com_multi_txt)) 
wealth_2425_prompt =read_file_content_txt(os.path.join(SCRIPT_DIR, wealth_2425_txt))
balance_2425_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_balance_2425_txt))


#for multiple images
int_2425_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425_multi_txt))
int_2425_m_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425m_multi_txt))
int_2425_q_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425q_multi_txt))
int_2425com_multy_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425com_multi_txt))
int_2425hsbc_multy_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425hsbc_multi_txt))
int_2425hnb_multy_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425hnb_multi_txt))
int_2425seylan_multy_prompt=read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2425seylan_multi_txt))


def balance_2425_d(image):
  details = vision_model.generate_content([balance_2425_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

def balance_2425_multiple_d(image):
  details = vision_model.generate_content([balance_2425_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management single image
def wealth_2425_d(image): # Renamed function
  details = vision_model.generate_content([wealth_2425_prompt,image],safety_settings={ # Use updated prompt var
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
         'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management multiple images
def wealth_2425_multiple_d(image): # Renamed function
  details = vision_model.generate_content([wealth_2425_prompt, *image],safety_settings={ # Use updated prompt var
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text


#employment
def employment_2425_d(image): # Renamed function
  details = vision_model.generate_content([emp_2425_prompt,image],safety_settings={ # Use updated prompt var
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment with multiple docs
def employment_2425_multiple_d(image): # Renamed function
  details = vision_model.generate_content([emp_2425_prompt, *image],safety_settings={ # Use updated prompt var
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank
def int_inc_2425_d(image): # Renamed function
  details = vision_model.generate_content([int_2425_prompt,image],safety_settings={ # Use updated prompt var
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2425_m_d(image): # Renamed function
  details = vision_model.generate_content([int_2425_m_prompt,image], # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_2425_q_d(image): # Renamed function
  details = vision_model.generate_content([int_2425_q_prompt,image], # Use updated prompt var
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
def int_inc_2425_multiple_d(image): # Renamed function
  details = vision_model.generate_content([int_2425_multi_prompt, *image],safety_settings={ # Use updated prompt var
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2425_m_multiple_d(image): # Renamed function
  details = vision_model_combank.generate_content([int_2425_m_multi_prompt, *image], # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  print("AI Output for int_inc_2425_m_multiple:", details.text)
  return details.text

def int_inc_com_2425_m_multiple_d(image): # Renamed function
  details = vision_model_combank.generate_content([int_2425com_multy_prompt, *image], # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #print(int_2425com_multy_prompt) # Updated comment
  details.resolve()
  return details.text



def int_inc_hsbc_2425_m_multiple_d(image): # Renamed function
  details = vision_model_hsbc.generate_content([int_2425hsbc_multy_prompt, *image], # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2425com_multy_prompt) # Updated comment (though it references com prompt)
  details.resolve()
  return details.text


def int_inc_hnb_2425_m_multiple_d(image): # Renamed function
  details = vision_model_hnb.generate_content([int_2425hnb_multy_prompt, *image],
    # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2425hnb_multy_prompt) # Updated comment (though it references com prompt)
  details.resolve()
  return details.text

def int_inc_seylan_2425_m_multiple_d(image): # Renamed function
  details = vision_model_hnb.generate_content([int_2425seylan_multy_prompt, *image], # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  #st.write(int_2425com_multy_prompt) # Updated comment (though it references com prompt)
  details.resolve()
  return details.text


#bank quarter
def int_inc_2425_q_multiple_d(image): # Renamed function
  details = vision_model.generate_content([int_2425_q_multi_prompt, *image], # Use updated prompt var
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text
