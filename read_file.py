import logging
import tempfile
from PIL import Image
from pdf2image import convert_from_bytes # For processing PDF file bytes

logger = logging.getLogger(__name__)


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

def process_uploaded_file(uploaded_file_object, content_type):
    """
    Processes an uploaded file (PDF or image) and returns a PIL Image object.
    For PDFs, it converts the first page to an image.

    Args:
        uploaded_file_object: A file-like object (e.g., Django UploadedFile).
                              Must support read() method.
        content_type: The MIME type of the file (e.g., "application/pdf", "image/jpeg").

    Returns:
        A PIL.Image object if successful, None otherwise.
    """
    pil_image = None
    try:
        if content_type == "application/pdf":
            file_bytes = uploaded_file_object.read() # Read bytes from the file object
            # Use a temporary directory if pdf2image needs file paths for intermediate steps,
            # though convert_from_bytes primarily works with bytes.
            with tempfile.TemporaryDirectory() as path:
                images_from_pdf = convert_from_bytes(file_bytes, fmt='jpeg', output_folder=path)
                if images_from_pdf:
                    pil_image = images_from_pdf[0]  # Return the first page as a PIL Image
                else:
                    logger.error("Failed to convert PDF to image: No images returned from conversion.")
        elif content_type and content_type.startswith("image/"):
            pil_image = Image.open(uploaded_file_object)
        else:
            logger.warning(f"Unsupported file type for processing: {content_type}")
    except Exception as e:
        logger.error(f"An error occurred while processing uploaded file: {e}", exc_info=True)
        return None # Ensure None is returned on any exception during processing

    return pil_image

def read_image_file(file_path):
    return Image.open(file_path)

def read_file_content_txt(filename):
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