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


#get prompts for document types
emp_2122_txt = "employement_2122.txt"
int_inc_2122_txt = "bank_2122.txt"
int_inc_2122m_txt = "bank_2122_m.txt"
int_inc_2122q_txt = "bank_2122_q.txt"
int_balance_1920_txt ="balance_1920.txt"
#wealth
wealth_2122_txt = "wealth_manage_2122.txt"


#for multiple images
int_inc_2122_multi_txt = "bank_2122_multi.txt"
int_inc_2122m_multi_txt = "bank_2122_m_multi.txt"
int_inc_2122q_multi_txt = "bank_2122_q_multi.txt"

#calling prompts
emp_2122_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, emp_2122_txt))
int_2122_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2122_txt))
int_2122_m_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2122m_txt))
int_2122_q_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2122q_txt))
wealth_2122_prompt= read_file_content_txt(os.path.join(SCRIPT_DIR, wealth_2122_txt))
int_balance_prompt= read_file_content_txt(os.path.join(SCRIPT_DIR, int_balance_1920_txt))

#for multiple images
int_2122_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2122_multi_txt))
int_2122_m_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2122m_multi_txt))
int_2122_q_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2122q_multi_txt))


def balance_2122(image):
  details = vision_model.generate_content([int_balance_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

def balance_2122_multiple(image):
  details = vision_model.generate_content([int_balance_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text


#wealth management
def wealth_2122(image):
  details = vision_model.generate_content([wealth_2122_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#wealth management with multiple images
def wealth_2122_multiple(image):
  details = vision_model.generate_content([wealth_2122_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment 
def employment_2122(image):
  details = vision_model.generate_content([emp_2122_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#employment with multiple docs
def employment_2122_multiple(image):
  details = vision_model.generate_content([emp_2122_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank
def int_inc_2122(image):
  details = vision_model.generate_content([int_2122_prompt,image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2122_m(image):
  details = vision_model.generate_content([int_2122_m_prompt,image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_2122_q(image):
  details = vision_model.generate_content([int_2122_q_prompt,image],
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
def int_inc_2122_multiple(image):
  details = vision_model.generate_content([int_2122_multi_prompt, *image],safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
  details.resolve()
  return details.text

#bank month
def int_inc_2122_m_multiple(image):
  details = vision_model.generate_content([int_2122_m_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text

#bank quarter
def int_inc_2122_q_multiple(image):
  details = vision_model.generate_content([int_2122_q_multi_prompt, *image],
    safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
  details.resolve()
  return details.text
