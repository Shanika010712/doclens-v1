#AI library
import google.generativeai as vision_genai
import os

#read file function
from read_file import read_file_content

# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#setup ai model
api_filename = "gemini_api.txt"
key = read_file_content(os.path.join(SCRIPT_DIR, api_filename))
vision_genai.configure(api_key=key)
vision_model = vision_genai.GenerativeModel('gemini-2.0-flash')


#get prompts for document types
emp_2021_txt = "employement_2021.txt"
int_inc_2021_txt = "bank_2021.txt"
int_inc_2021m_txt = "bank_2021_m.txt"
int_inc_2021q_txt = "bank_2021_q.txt"
int_balance_2021_txt="balance_2021.txt"
#wealth
wealth_2021_txt = "wealth_manage_2021.txt"

#for multiple images
int_inc_2021_multi_txt = "bank_2021_multi.txt"
int_inc_2021m_multi_txt = "bank_2021_m_multi.txt"
int_inc_2021q_multi_txt = "bank_2021_q_multi.txt"

#calling prompts
emp_2021_prompt = read_file_content(os.path.join(SCRIPT_DIR, emp_2021_txt))
int_2021_prompt = read_file_content(os.path.join(SCRIPT_DIR, int_inc_2021_txt))
int_2021_m_prompt = read_file_content(os.path.join(SCRIPT_DIR, int_inc_2021m_txt))
int_2021_q_prompt = read_file_content(os.path.join(SCRIPT_DIR, int_inc_2021q_txt))
wealth_2021_prompt= read_file_content(os.path.join(SCRIPT_DIR, wealth_2021_txt))
balance_2021_prompt=read_file_content(os.path.join(SCRIPT_DIR, int_balance_2021_txt))

#for multiple images
int_2021_multi_prompt = read_file_content(os.path.join(SCRIPT_DIR, int_inc_2021_multi_txt))
int_2021_m_multi_prompt = read_file_content(os.path.join(SCRIPT_DIR, int_inc_2021m_multi_txt))
int_2021_q_multi_prompt = read_file_content(os.path.join(SCRIPT_DIR, int_inc_2021q_multi_txt))

def balance_2021(image):
  details = vision_model.generate_content([balance_2021_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

def balance_2021_multiple(image):
  details = vision_model.generate_content([balance_2021_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text


#wealth management
def wealth_2021(image):
  details = vision_model.generate_content([wealth_2021_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management with multiple images
def wealth_2021_multiple(image):
  details = vision_model.generate_content([wealth_2021_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment 
def employment_2021(image):
  details = vision_model.generate_content([emp_2021_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment with multiple docs
def employment_2021_multiple(image):
  details = vision_model.generate_content([emp_2021_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank
def int_inc_2021(image):
  details = vision_model.generate_content([int_2021_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2021_m(image):
  details = vision_model.generate_content([int_2021_m_prompt,image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_2021_q(image):
  details = vision_model.generate_content([int_2021_q_prompt,image],
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
def int_inc_2021_multiple(image):
  details = vision_model.generate_content([int_2021_multi_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2021_m_multiple(image):
  details = vision_model.generate_content([int_2021_m_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_2021_q_multiple(image):
  details = vision_model.generate_content([int_2021_q_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text
