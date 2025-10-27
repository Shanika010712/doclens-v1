#AI library
import google.generativeai as vision_genai
import logging # Import logging
import os

#read file function
from read_file import read_file_content_txt

# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__) # Initialize logger for this module

#setup ai model
api_filename = "gemini_api.txt"
key = read_file_content_txt(os.path.join(SCRIPT_DIR, api_filename))
vision_genai.configure(api_key=key)
vision_model = vision_genai.GenerativeModel('gemini-2.0-flash') # Changed model for consistency


emp_2223_txt = "employement_2223.txt"
int_inc_2223_txt = "bank_2223.txt"
int_inc_2223m_txt = "bank_2223_m.txt"
int_inc_2223q_txt = "bank_2223_q.txt"
int_balance_2223_txt ="balance_2223.txt"
#wealth
wealth_2223_txt = "wealth_manage_2223.txt"

#for multiple images
int_inc_2223_multi_txt = "bank_2223_multi.txt"
int_inc_2223m_multi_txt = "bank_2223_m_multi.txt"
int_inc_2223q_multi_txt = "bank_2223_q_multi.txt"

#calling prompts
emp_2223_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, emp_2223_txt))
int_2223_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2223_txt))
int_2223_m_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2223m_txt))
int_2223_q_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2223q_txt))
wealth_2223_prompt =read_file_content_txt(os.path.join(SCRIPT_DIR, wealth_2223_txt))
balance_2223_prompt= read_file_content_txt(os.path.join(SCRIPT_DIR, int_balance_2223_txt))

#for multiple images
int_2223_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2223_multi_txt))
int_2223_m_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2223m_multi_txt))
int_2223_q_multi_prompt = read_file_content_txt(os.path.join(SCRIPT_DIR, int_inc_2223q_multi_txt))

def balance_2223(image):
    details = vision_model.generate_content([balance_2223_prompt,image],safety_settings={
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL' : 'BLOCK_NONE',
            'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    return details.text

def balance_2223_multiple(image):
    details = vision_model.generate_content([balance_2223_prompt, *image],safety_settings={
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL' : 'BLOCK_NONE',
            'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    return details.text

#wealth management
def wealth_2223(image):
  logger.info(f"Executing wealth_2223 with image type: {type(image)}")
  if image is None:
      logger.error("wealth_2223 received a None image.")
      return None
  if wealth_2223_prompt is None:
      logger.error("wealth_2223: Prompt 'wealth_2223_prompt' is None.")
      return None
  try:
    details = vision_model.generate_content([wealth_2223_prompt, image], safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"wealth_2223 - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"wealth_2223 - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("wealth_2223 - Gemini response has no parts.")
        if hasattr(details, 'text'):
            return details.text # Return text even if None, logging will occur in process.py
        else: # Should not happen if generate_content was successful
            logger.error("wealth_2223 - Gemini response has no parts and no text attribute.")
            return None
    return details.text
  except Exception as e:
    logger.error(f"Error in wealth_2223 Gemini call: {e}", exc_info=True)
    return None

#wealth management with multiple images
def wealth_2223_multiple(image_list):
  logger.info(f"Executing wealth_2223_multiple with image list (count: {len(image_list) if image_list else 0})")
  if not image_list or any(img is None for img in image_list):
      logger.error(f"wealth_2223_multiple received an invalid image list: {image_list}")
      return None
  if wealth_2223_prompt is None:
      logger.error("wealth_2223_multiple: Prompt 'wealth_2223_prompt' is None.")
      return None
  try:
    content_parts = [wealth_2223_prompt] + image_list
    details = vision_model.generate_content(content_parts, safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"wealth_2223_multiple - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"wealth_2223_multiple - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("wealth_2223_multiple - Gemini response has no parts.")
        if hasattr(details, 'text'):
            return details.text
        else:
            logger.error("wealth_2223_multiple - Gemini response has no parts and no text attribute.")
            return None
    return details.text
  except Exception as e:
    logger.error(f"Error in wealth_2223_multiple Gemini call: {e}", exc_info=True)
    return None

#employment 
def employment_2223(image):
  logger.info(f"Executing employment_2223 with image type: {type(image)}")
  if image is None:
      logger.error("employment_2223 received a None image.")
      return None
  if not emp_2223_prompt or not emp_2223_prompt.strip():
      logger.error(f"employment_2223: Prompt 'emp_2223_prompt' is None or empty. Prompt content (start): '{str(emp_2223_prompt)[:100]}'. Cannot proceed.")
      return None
  try:
    details = vision_model.generate_content([emp_2223_prompt, image], safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"employment_2223 - Gemini response object: {details}")

    # Log candidate information, including finish_reason
    if details.candidates:
        for i, candidate in enumerate(details.candidates):
            logger.debug(f"employment_2223 - Candidate {i} - Finish Reason: {candidate.finish_reason}")
            # Log if the finish reason is something other than a normal stop or max tokens.
            if hasattr(candidate.finish_reason, 'name') and candidate.finish_reason.name not in ["STOP", "MAX_TOKENS", "UNSPECIFIED", "FINISH_REASON_UNSPECIFIED"]:
                 logger.warning(f"employment_2223 - Candidate {i} had a non-standard finish reason: {candidate.finish_reason.name}")
    else:
        logger.warning("employment_2223 - Gemini response has no candidates. This often means no content was generated or there was an issue.")

    # Check overall prompt feedback for blocking
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"employment_2223 - Prompt was blocked by overall feedback. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    
    if not details.parts:
        logger.warning("employment_2223 - Gemini response has no parts.")
        # Even if no parts, .text might exist or be None.
        if hasattr(details, 'text'):
            if details.text is None:
                 logger.error("employment_2223 - Gemini details.text is None (response had no parts).")
            else:
                 logger.info(f"employment_2223 - details.text (no parts): '{details.text[:200]}...'") # Log snippet
            return details.text
        else:
            logger.error("employment_2223 - Gemini response has no parts and no text attribute.")
            return None

    if details.text is None:
        logger.error(f"employment_2223 - Gemini details.text is None after successful call (had parts). Prompt used (first 100 chars): {emp_2223_prompt[:100] if emp_2223_prompt else 'None'}")
    else:
        logger.info(f"employment_2223 - Successfully extracted text, length: {len(details.text)}. Returning text.")
    return details.text
  except Exception as e:
    logger.error(f"Error in employment_2223 Gemini call: {e}", exc_info=True)
    return None

#employment with multiple docs
def employment_2223_multiple(image_list): # Renamed 'image' to 'image_list' for clarity
  logger.info(f"Executing employment_2223_multiple with image list (count: {len(image_list) if image_list else 0})")
  if not image_list or any(img is None for img in image_list):
      logger.error(f"employment_2223_multiple received an invalid image list (empty or contains None): {image_list}")
      return None
  if not emp_2223_prompt or not emp_2223_prompt.strip():
      logger.error(f"employment_2223_multiple: Prompt 'emp_2223_prompt' is None or empty. Prompt content (start): '{str(emp_2223_prompt)[:100]}'. Cannot proceed.")
      return None
  try:
    content_parts = [emp_2223_prompt] + image_list
    details = vision_model.generate_content(content_parts, safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"employment_2223_multiple - Gemini response object: {details}")

    # Log candidate information, including finish_reason
    if details.candidates:
        for i, candidate in enumerate(details.candidates):
            logger.debug(f"employment_2223_multiple - Candidate {i} - Finish Reason: {candidate.finish_reason}")
            if hasattr(candidate.finish_reason, 'name') and candidate.finish_reason.name not in ["STOP", "MAX_TOKENS", "UNSPECIFIED", "FINISH_REASON_UNSPECIFIED"]:
                 logger.warning(f"employment_2223_multiple - Candidate {i} had a non-standard finish reason: {candidate.finish_reason.name}")
    else:
        logger.warning("employment_2223_multiple - Gemini response has no candidates. This often means no content was generated or there was an issue.")

    # Check overall prompt feedback for blocking
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"employment_2223_multiple - Prompt was blocked by overall feedback. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None

    if not details.parts:
        logger.warning("employment_2223_multiple - Gemini response has no parts.")
        if hasattr(details, 'text'):
            if details.text is None:
                 logger.error("employment_2223_multiple - Gemini details.text is None (response had no parts).")
            else:
                logger.info(f"employment_2223_multiple - details.text (no parts): '{details.text[:200]}...'")
            return details.text
        else:
            logger.error("employment_2223_multiple - Gemini response has no parts and no text attribute.")
            return None
            
    if details.text is None:
        logger.error(f"employment_2223_multiple - Gemini details.text is None after successful call (had parts). Prompt used (first 100 chars): {emp_2223_prompt[:100] if emp_2223_prompt else 'None'}")
    else:
        logger.info(f"employment_2223_multiple - Successfully extracted text, length: {len(details.text)}. Returning text.")
    return details.text
  except Exception as e:
    logger.error(f"Error in employment_2223_multiple Gemini call: {e}", exc_info=True)
    return None

#bank
def int_inc_2223(image):
  logger.info(f"Executing int_inc_2223 with image type: {type(image)}")
  if image is None:
      logger.error("int_inc_2223 received a None image.")
      return None
  if int_2223_prompt is None:
      logger.error("int_inc_2223: Prompt 'int_2223_prompt' is None.")
      return None
  try:
    details = vision_model.generate_content([int_2223_prompt, image], safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"int_inc_2223 - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"int_inc_2223 - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("int_inc_2223 - Gemini response has no parts.")
        if hasattr(details, 'text'): return details.text
        logger.error("int_inc_2223 - Gemini response has no parts and no text attribute.")
        return None
    return details.text
  except Exception as e:
    logger.error(f"Error in int_inc_2223 Gemini call: {e}", exc_info=True)
    return None

#bank month
def int_inc_2223_m(image):
  logger.info(f"Executing int_inc_2223_m with image type: {type(image)}")
  if image is None:
      logger.error("int_inc_2223_m received a None image.")
      return None
  if int_2223_m_prompt is None:
      logger.error("int_inc_2223_m: Prompt 'int_2223_m_prompt' is None.")
      return None
  try:
    details = vision_model.generate_content([int_2223_m_prompt, image], safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"int_inc_2223_m - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"int_inc_2223_m - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("int_inc_2223_m - Gemini response has no parts.")
        if hasattr(details, 'text'): return details.text
        logger.error("int_inc_2223_m - Gemini response has no parts and no text attribute.")
        return None
    return details.text
  except Exception as e:
    logger.error(f"Error in int_inc_2223_m Gemini call: {e}", exc_info=True)
    return None

#bank quarter
def int_inc_2223_q(image):
  logger.info(f"Executing int_inc_2223_q with image type: {type(image)}")
  if image is None:
      logger.error("int_inc_2223_q received a None image.")
      return None
  if int_2223_q_prompt is None:
      logger.error("int_inc_2223_q: Prompt 'int_2223_q_prompt' is None.")
      return None
  try:
    details = vision_model.generate_content([int_2223_q_prompt, image], safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"int_inc_2223_q - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"int_inc_2223_q - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("int_inc_2223_q - Gemini response has no parts.")
        if hasattr(details, 'text'): return details.text
        logger.error("int_inc_2223_q - Gemini response has no parts and no text attribute.")
        return None
    return details.text
  except Exception as e:
    logger.error(f"Error in int_inc_2223_q Gemini call: {e}", exc_info=True)
    return None

#bank multiple images
#bank year 
def int_inc_2223_multiple(image_list):
  logger.info(f"Executing int_inc_2223_multiple with image list (count: {len(image_list) if image_list else 0})")
  if not image_list or any(img is None for img in image_list):
      logger.error(f"int_inc_2223_multiple received an invalid image list: {image_list}")
      return None
  if int_2223_multi_prompt is None:
      logger.error("int_inc_2223_multiple: Prompt 'int_2223_multi_prompt' is None.")
      return None
  try:
    content_parts = [int_2223_multi_prompt] + image_list
    details = vision_model.generate_content(content_parts, safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"int_inc_2223_multiple - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"int_inc_2223_multiple - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("int_inc_2223_multiple - Gemini response has no parts.")
        if hasattr(details, 'text'): return details.text
        logger.error("int_inc_2223_multiple - Gemini response has no parts and no text attribute.")
        return None
    return details.text
  except Exception as e:
    logger.error(f"Error in int_inc_2223_multiple Gemini call: {e}", exc_info=True)
    return None

#bank month
def int_inc_2223_m_multiple(image_list):
  logger.info(f"Executing int_inc_2223_m_multiple with image list (count: {len(image_list) if image_list else 0})")
  if not image_list or any(img is None for img in image_list):
      logger.error(f"int_inc_2223_m_multiple received an invalid image list: {image_list}")
      return None
  if int_2223_m_multi_prompt is None:
      logger.error("int_inc_2223_m_multiple: Prompt 'int_2223_m_multi_prompt' is None.")
      return None
  try:
    content_parts = [int_2223_m_multi_prompt] + image_list
    details = vision_model.generate_content(content_parts, safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"int_inc_2223_m_multiple - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"int_inc_2223_m_multiple - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("int_inc_2223_m_multiple - Gemini response has no parts.")
        if hasattr(details, 'text'): return details.text
        logger.error("int_inc_2223_m_multiple - Gemini response has no parts and no text attribute.")
        return None
    return details.text
  except Exception as e:
    logger.error(f"Error in int_inc_2223_m_multiple Gemini call: {e}", exc_info=True)
    return None

#bank quarter
def int_inc_2223_q_multiple(image_list):
  logger.info(f"Executing int_inc_2223_q_multiple with image list (count: {len(image_list) if image_list else 0})")
  if not image_list or any(img is None for img in image_list):
      logger.error(f"int_inc_2223_q_multiple received an invalid image list: {image_list}")
      return None
  if int_2223_q_multi_prompt is None:
      logger.error("int_inc_2223_q_multiple: Prompt 'int_2223_q_multi_prompt' is None.")
      return None
  try:
    content_parts = [int_2223_q_multi_prompt] + image_list
    details = vision_model.generate_content(content_parts, safety_settings={
          'HATE': 'BLOCK_NONE',
          'HARASSMENT': 'BLOCK_NONE',
          'SEXUAL' : 'BLOCK_NONE',
          'DANGEROUS' : 'BLOCK_NONE'})
    details.resolve()
    logger.debug(f"int_inc_2223_q_multiple - Gemini response object: {details}")
    if details.prompt_feedback and details.prompt_feedback.block_reason:
        logger.error(f"int_inc_2223_q_multiple - Prompt was blocked. Reason: {details.prompt_feedback.block_reason_message or details.prompt_feedback.block_reason}")
        return None
    if not details.parts:
        logger.warning("int_inc_2223_q_multiple - Gemini response has no parts.")
        if hasattr(details, 'text'): return details.text
        logger.error("int_inc_2223_q_multiple - Gemini response has no parts and no text attribute.")
        return None
    return details.text
  except Exception as e:
    logger.error(f"Error in int_inc_2223_q_multiple Gemini call: {e}", exc_info=True)
    return None
