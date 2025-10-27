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
 
# The _load_images helper is removed as the agent now passes loaded PIL.Image objects directly.
 
def run_parallel_bank_m_1920(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_1920_m_multiple(img)
        else:
            results['v1'] = int_inc_1920_m(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_1920_m_multiple_d(img)
        else:
            results['v2'] = int_inc_1920_m_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_y_1920(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_1920_multiple(img)
        else:
            results['v1'] = int_inc_1920(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_1920_multiple_d(img)
        else:
            results['v2'] = int_inc_1920_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_m_2021(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2021_m_multiple(img)
        else:
            results['v1'] = int_inc_2021_m(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2021_m_multiple_d(img)
        else:
            results['v2'] = int_inc_2021_m_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_y_2021(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2021_multiple(img)
        else:
            results['v1'] = int_inc_2021(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2021_multiple_d(img)
        else:
            results['v2'] = int_inc_2021_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_m_2122(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2122_m_multiple(img)
        else:
            results['v1'] = int_inc_2122_m(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2122_m_multiple_d(img)
        else:
            results['v2'] = int_inc_2122_m_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_y_2122(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2122_multiple(img)
        else:
            results['v1'] = int_inc_2122(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2122_multiple_d(img)
        else:
            results['v2'] = int_inc_2122_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_m_2223(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2223_m_multiple(img)
        else:
            results['v1'] = int_inc_2223_m(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2223_m_multiple_d(img)
        else:
            results['v2'] = int_inc_2223_m_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_y_2223(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2223_multiple(img)
        else:
            results['v1'] = int_inc_2223(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2223_multiple_d(img)
        else:
            results['v2'] = int_inc_2223_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_m_2324(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2324_m_multiple(img)
        else:
            results['v1'] = int_inc_2324_m(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2324_m_multiple_d(img)
        else:
            results['v2'] = int_inc_2324_m_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_y_2324(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2324_multiple(img)
        else:
            results['v1'] = int_inc_2324(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2324_multiple_d(img)
        else:
            results['v2'] = int_inc_2324_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_m_2425(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2425_m_multiple(img)
        else:
            results['v1'] = int_inc_2425_m(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2425_m_multiple_d(img)
        else:
            results['v2'] = int_inc_2425_m_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')

def run_parallel_bank_y_2425(image):
    results = {}
    def wrapper1(img):
        if isinstance(img, list):
            results['v1'] = int_inc_2425_multiple(img)
        else:
            results['v1'] = int_inc_2425(img)
    def wrapper2(img):
        if isinstance(img, list):
            results['v2'] = int_inc_2425_multiple_d(img)
        else:
            results['v2'] = int_inc_2425_d(img)
    thread1 = threading.Thread(target=wrapper1, args=(image,))
    thread2 = threading.Thread(target=wrapper2, args=(image,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Return both results as a tuple
    return results.get('v1'), results.get('v2')