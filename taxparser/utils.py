from PIL import Image, ImageEnhance
import pytesseract
from pytesseract import Output
import re

from taxparser.serializers import TaxForm1040Serializer


def enhance_image(image_path):
    image = Image.open(image_path)

    # Convert image to greyscale
    image = image.convert('L')

    # Increase contrast of the image
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    image.save(image_path)

    return image


def do_ocr_on_image(image):
    # Run OCR on the image and get detailed output
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    # Return the entire text data
    return data


# Util for safely retrieving a key via a tax_line value
# This can be more generic, but kept it simple
def find_object_by_tax_line(key_locations, tax_line):
    for obj in key_locations:
        if 'tax_line' in obj and obj['tax_line'] == tax_line:
            return obj

    # Return None if no matching object is found
    return None


# I don't like that I wrote two very similar helpers, feels jank but don't want to spend
# too much time on it
def get_value_by_tax_line(arr, tax_line):
    for obj in arr:
        if obj['tax_line'] == tax_line:
            if obj['value'] != '':
                return obj['value']
            else:
                return 0
    return 0


def remove_non_numeric(s):
    return re.sub('[^0-9]', '', s)


def calculate_and_enrich_pay_amount(instance):
    line_34 = instance.line_34
    line_37 = instance.line_37
    if line_37 > 0:
        pay_this_amount_value = line_37 * -1
    elif line_34 > 0:
        pay_this_amount_value = line_34
    else:
        pay_this_amount_value = 0

    # Serialize individual instance
    serializer = TaxForm1040Serializer(instance)
    serialized_data = serializer.data

    # Add the 'pay_this_amount_value' into serialized data
    serialized_data['pay_this_amount'] = str(pay_this_amount_value)
    return serialized_data
