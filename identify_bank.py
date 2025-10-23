#shanika
#AI library
import google.generativeai as vision_genai


import os # Added os import
import logging # Added logging
logger = logging.getLogger(__name__)

#read file function
from .read_file import read_file_content # Relative import for Django

# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#get the identifer prompt
#identify_prompt = "identify.txt"
#prompt = read_file_content(identify_prompt)

#setup ai model
api_filename = "gemini_api.txt" # Consistent naming
key = read_file_content(os.path.join(SCRIPT_DIR, api_filename)) # Use SCRIPT_DIR
vision_genai.configure(api_key=key)
vision_model = vision_genai.GenerativeModel('gemini-2.0-flash')
#shanika
#def identify(image):
   # st.write("bank identification is in progress......")
    #txt_response = vision_model.generate_content([prompt,image])
    #txt_response.resolve()
    #assign response to list
    #text = txt_response.text
    #st.write("Document identification completed.")
    #return text.split(",")

#now this will check the bank,hsbc.....etc
banktype_iden_filename = "bank_identifier_prompt.txt" # Consistent naming
banktype_iden_prompt = read_file_content(os.path.join(SCRIPT_DIR, banktype_iden_filename)) # Use SCRIPT_DIR

def banktype_identify(image):
  if image is None:
      logger.error("banktype_identify received a None image.")
      return "Error: No image provided"
  if not banktype_iden_prompt:
      logger.error("banktype_identify: Bank identifier prompt is not loaded.")
      return "Error: Prompt not loaded"
  try:
    logger.info("Identifying specific bank type...")
    bankdetails = vision_model.generate_content([banktype_iden_prompt,image], safety_settings={
        'HATE': 'BLOCK_NONE', 'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE', 'DANGEROUS' : 'BLOCK_NONE'})
    bankdetails.resolve()
    logger.info(f"Bank type identification complete. Raw response: {bankdetails.text}")
    return bankdetails.text
  except Exception as e:
    logger.error(f"Error in banktype_identify Gemini call: {e}", exc_info=True)
    return f"Error during bank type identification: {str(e)}"
# ...existing code...

# get bank identifier prompt
#bank_identifier_prompt_file = "Bank_identifier_prompt.txt"
#bank_identifier_prompt = read_file_content(bank_identifier_prompt_file)


    

# ...existing code...
