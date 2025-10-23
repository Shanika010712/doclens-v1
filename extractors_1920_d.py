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


#get prompts for document types
emp_1920_txt = "employement_1920.txt"
int_inc_1920_txt = "bank_1920.txt"
int_inc_1920m_txt = "bank_1920_m.txt"
int_inc_1920q_txt = "bank_1920_q.txt"
int_balance_1920_txt ="balance_1920.txt"
#wealth
wealth_1920_txt = "wealth_manage_1920.txt"

#for multiple images
int_inc_1920_multi_txt = "bank_1920_multi.txt"
int_inc_1920m_multi_txt = "bank_1920_m_multi.txt"
int_inc_1920q_multi_txt = "bank_1920_q_multi.txt"

#calling prompts
emp_1920_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, emp_1920_txt))
int_1920_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_1920_txt))
int_1920_m_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_1920m_txt))
int_1920_q_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_1920q_txt))
int_balance_prompt= read_file_content_txt(os.path.join(SCRIPT_DIR, int_balance_1920_txt))
wealth_1920_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, wealth_1920_txt))

#for multiple images
int_1920_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_1920_multi_txt))
int_1920_m_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_1920m_multi_txt))
int_1920_q_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_1920q_multi_txt))


def balance_1920_d(image):
  details = vision_model.generate_content([int_balance_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#balance confirmation multiple images
def balance_1920_multiple_d(image):
  details = vision_model.generate_content([int_balance_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management
def wealth_1920_d(image):
  details = vision_model.generate_content([wealth_1920_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management with multiple images
def wealth_1920_multiple_d(image):
  details = vision_model.generate_content([wealth_1920_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment 
def employment_1920_d(image):
  details = vision_model.generate_content([emp_1920_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment with multiple docs
def employment_1920_multiple_d(image):
  details = vision_model.generate_content([emp_1920_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank
def int_inc_1920_d(image):
  details = vision_model.generate_content([int_1920_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_1920_m_d(image):
  details = vision_model.generate_content([int_1920_m_prompt,image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_1920_q_d(image):
  details = vision_model.generate_content([int_1920_q_prompt,image],
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
def int_inc_1920_multiple_d(image):
  details = vision_model.generate_content([int_1920_multi_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_1920_m_multiple_d(image):
  details = vision_model.generate_content([int_1920_m_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_1920_q_multiple_d(image):
  details = vision_model.generate_content([int_1920_q_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text
