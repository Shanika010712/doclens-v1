#thread testing 
from extractors_2324 import *
from extractors_2425 import *
from extractors_2223 import *
from extractors_2122 import *
from extractors_2021 import *
from extractors_1920 import *
from extractors_1920_d import *
from extractors_2021_d import *
from extractors_2122_d import *
from extractors_2223_d import *
from extractors_2324_d import *
from extractors_2425_d import *
import threading
from PIL import Image

def _load_images(image_paths_or_obj):
    """Load images from paths if a list of paths is given."""
    if isinstance(image_paths_or_obj, list):
        images = []
        for path in image_paths_or_obj:
            try:
                images.append(Image.open(path))
            except Exception as e:
                print(f"Error opening image {path}: {e}")
                # Depending on desired behavior, you might want to return None or raise
        return images
    return image_paths_or_obj # Assume it's already a PIL image or list of images

def run_parallel_employment_1920(image):
    results = {}
    loaded_image = _load_images(image)
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = employment_1920_multiple(img)
        else:
            results['v1'] = employment_1920(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = employment_1920_multiple_d(img)
        else:
            results['v2'] = employment_1920_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(loaded_image,))
    thread2 = threading.Thread(target=wrapper2, args=(loaded_image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_employment_2021(image):
    results = {}
    loaded_image = _load_images(image)
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = employment_2021_multiple(img)
        else:
            results['v1'] = employment_2021(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = employment_2021_multiple_d(img)
        else:
            results['v2'] = employment_2021_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(loaded_image,))
    thread2 = threading.Thread(target=wrapper2, args=(loaded_image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_employment_2122(image):
    results = {}
    loaded_image = _load_images(image)
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = employment_2122_multiple(img)
        else:
            results['v1'] = employment_2122(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = employment_2122_multiple_d(img)
        else:
            results['v2'] = employment_2122_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(loaded_image,))
    thread2 = threading.Thread(target=wrapper2, args=(loaded_image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_employment_2223(image):
    results = {}
    loaded_image = _load_images(image)
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = employment_2223_multiple(img)
        else:
            results['v1'] = employment_2223(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = employment_2223_multiple_d(img)
        else:
            results['v2'] = employment_2223_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(loaded_image,))
    thread2 = threading.Thread(target=wrapper2, args=(loaded_image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_employment_2324(image):
    results = {}
    loaded_image = _load_images(image)
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = employment_2324_multiple(img)
        else:
            results['v1'] = employment_2324(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = employment_2324_multiple_d(img)
        else:
            results['v2'] = employment_2324_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(loaded_image,))
    thread2 = threading.Thread(target=wrapper2, args=(loaded_image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_employment_2425(image):
    results = {}
    loaded_image = _load_images(image)
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = employment_2425_multiple(img)
        else:
            results['v1'] = employment_2425(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = employment_2425_multiple_d(img)
        else:
            results['v2'] = employment_2425_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(loaded_image,))
    thread2 = threading.Thread(target=wrapper2, args=(loaded_image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')