#AI library
import google.generativeai as vision_genai
import re
import os # Import the os module to work with file paths


import logging
logger = logging.getLogger(__name__)


# Get the absolute path to the directory where this script (identify.py) is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#read file function

def read_file_content(filename):
  """Reads the content of a text file and stores it in a string.

  Args:
      filename: The path to the text file.

  Returns:
      A string containing the content of the text file, or None if the
      file could not be found or read.
  """
  try:
    with open(filename, "r",encoding='utf-8') as f:
      content = f.read()
    return content
  except FileNotFoundError:
    logger.warning(f"File not found: {filename}")
    return None
  except IOError as e:
    logger.error(f"IOError reading file {filename}: {e}")
    return None
  
#get the identifer prompt(this one for identify bank or emp)
identify_prompt_filename = "identify.txt"
prompt = read_file_content(os.path.join(SCRIPT_DIR, identify_prompt_filename))

#setup ai model
api_filename = "gemini_api.txt"
key = read_file_content(os.path.join(SCRIPT_DIR, api_filename))
vision_genai.configure(api_key=key)
vision_model = vision_genai.GenerativeModel('gemini-2.0-flash')

def identify(image_or_images):
    print("Document identification is in progress......")
    
    # Prepare content for Gemini, handling both single image and list of images
    if isinstance(image_or_images, list):
        # It's a list of images, use the splat operator
        content_parts = [prompt, *image_or_images]
    else:
        # It's a single image
        content_parts = [prompt, image_or_images]
        
    txt_response = vision_model.generate_content(content_parts)
    txt_response.resolve()
    #assign response to list
    text = txt_response.text 
    # Remove spaces around the slash in the year format (e.g., "2023 / 2024" -> "2023/2024")
    cleaned_text = re.sub(r'\s*/\s*', '/', text)
    print("Document identification completed.")
    return cleaned_text.split(",")


#can't include bank identifier here bs it use another model

#get bank period identifier
bank_iden_filename = "bank_iden.txt"
bank_iden_prompt = read_file_content(os.path.join(SCRIPT_DIR, bank_iden_filename))

def bank_identify(image):
  details = vision_model.generate_content([bank_iden_prompt,image])
  details.resolve()
  return details.text