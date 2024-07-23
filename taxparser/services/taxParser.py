from decimal import Decimal

from taxparser.models import TaxDocumentValues, TaxDocument, TaxFormValues, PDFDocument, TaxForm1040
from taxparser.utils import remove_non_numeric, do_ocr_on_image, enhance_image, find_object_by_tax_line, \
    get_value_by_tax_line, calculate_and_enrich_pay_amount
from pdf2image import convert_from_path


def grab_next_word(i, tax_line, text_data, value_results):
    # If there is no object for the specific location, attempt to grab the next word to the right
    # TODO: For sake of time, this is woefully underdone, there's a ton of heuristics that can be done here
    if i < len(text_data['text']) - 1:
        next_word = text_data['text'][i + 1]
        value_results.append({'name': f"Line {tax_line}", 'value': next_word, 'tax_line': tax_line})


# Primary Ingest Method
def ingest_pdf(request):
    pdf_file = request.data['file']
    tax_form_name = request.data['tax_form']
    # create row in db
    pdf_document = PDFDocument(file=pdf_file, name=pdf_file.name, tax_form=tax_form_name)
    pdf_document.save()
    document_id = pdf_document.id
    # path where the pdf is saved
    pdf_path = pdf_document.file.path
    # This will return a list of PIL Image objects
    images = convert_from_path(pdf_path)
    # Initialize a dictionary to hold the OCR results
    ocr_results = {}
    formValues = TaxFormValues.objects.filter(tax_form=tax_form_name)
    for i, image in enumerate(images):
        # save each image in the 'documents/images/' directory,
        # with name as 'document_name_page_number.png'
        image_path = f"documents/images/{pdf_document.name.strip('.pdf')}_{i}.png"
        image.save(image_path, 'PNG')

        # enhance the image, increasing the contrast for better parsing
        image = enhance_image(image_path)

        # run OCR on the enhanced image
        text = do_ocr_on_image(image)

        # Store the OCR results in the dict, using the page number as the key
        ocr_results[f'page_{i + 1}'] = text
    # At this point, ocr_results contains the OCR'd text for each page in the PDF
    value_results = []
    key_locations = []
    for value in formValues:
        value_to_check = value.value
        tax_line = value.tax_line
        word_found = False
        for page, text_data in ocr_results.items():
            for i in range(len(text_data['text'])):
                # create a list of unique words in valueToCheck
                unique_words = list(set(value_to_check.split()))

                # count the number of unique words
                num_unique_words = len(unique_words)

                # concatenate text_data['text'] elements up to num_unique_words
                concatenated_texts = ' '.join(text_data['text'][i:i + num_unique_words])

                if value_to_check.lower() in concatenated_texts.lower():
                    # Get the left top corner of the bounding box, we use that as the consistent grounding point
                    x_coordinate = int(text_data['left'][i])
                    y_coordinate = int(text_data['top'][i])

                    # checking to see if we've already found a key at this location
                    document = TaxDocument.objects.filter(x_position=x_coordinate,
                                                          y_position=y_coordinate,
                                                          tax_form=tax_form_name,
                                                          key=value_to_check).first()

                    if document:
                        values = document.get_values()

                        if values:

                            # TODO Very oversimplified for quickness, you can do actual calculations here
                            # to make sure I didn't get lose the forest for the trees, kept it simple for
                            # the assignment
                            highest_value_object = max(values, key=lambda obj: obj.get('occurrenceCount', 0))

                            x_value = highest_value_object['x']
                            y_value = highest_value_object['y']

                            # Find the closest word in `ocr_results`
                            min_distance = float('inf')
                            closest_word = None
                            for j in range(len(text_data['text'])):
                                # Calculate the distance between the two points
                                distance = ((x_value - text_data['left'][j]) ** 2 + (
                                        y_value - text_data['top'][j]) ** 2) ** 0.5
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_word = text_data['text'][j]

                            # Save that word to the `value_results` array
                            value_results.append(
                                {'name': f"Line {tax_line}",
                                 'value': remove_non_numeric(closest_word),
                                 'tax_line': tax_line})
                        else:
                            grab_next_word(i, tax_line, text_data, value_results)
                    else:
                        # TODO: For sake of time, I did not do any sort of transform checks here,
                        # which would solve the issue of if the document was photographed or scanned.
                        # i.e, if there is a consistent transform happening (i.e, every key is shifted down
                        # and to the left due to a not perfect scan, we can determine the transform and pivot
                        # to data we already have in our dataset
                        grab_next_word(i, tax_line, text_data, value_results)
                    key_locations.append(
                        {'key': value_to_check,
                         'tax_line': tax_line,
                         'x_coordinate': x_coordinate,
                         'y_coordinate': y_coordinate})
                    tax_document_val = TaxDocument.objects.filter(x_position=x_coordinate,
                                                                  y_position=y_coordinate,
                                                                  tax_form=tax_form_name,
                                                                  key=value_to_check).first()
                    if not tax_document_val:
                        # if there is no value recorded in the dataset for that key and position,
                        # make a new record
                        new_tax_document_val = TaxDocument(x_position=x_coordinate,
                                                           y_position=y_coordinate,
                                                           tax_form=tax_form_name,
                                                           key=value_to_check,
                                                           tax_line=tax_line,
                                                           values=[])
                        new_tax_document_val.save()
                    word_found = True
                if word_found:
                    break
            if word_found:
                break
    new_form = TaxDocumentValues(document_id=document_id, values=value_results, key_locations=key_locations,
                                 raw_ocr=ocr_results)

    if tax_form_name == '1040':
        new_1040 = TaxForm1040(document=pdf_document,
                           line_9=Decimal(get_value_by_tax_line(value_results, '9')),
                           line_11=Decimal(get_value_by_tax_line(value_results, '11')),
                           line_12=Decimal(get_value_by_tax_line(value_results, '12')),
                           line_15=Decimal(get_value_by_tax_line(value_results, '15')),
                           line_34=Decimal(get_value_by_tax_line(value_results, '34')),
                           line_37=Decimal(get_value_by_tax_line(value_results, '37')),
                           )
        new_form.save()
        new_1040.save()
        return calculate_and_enrich_pay_amount(new_1040)
    else:
        new_form.save()
        return value_results




def validate_input(request):
    document_id = request.data['document_id']
    values = request.data['values']
    tax_document = PDFDocument.objects.filter(id=document_id).first()
    form_values = TaxFormValues.objects.filter(tax_form=tax_document.tax_form)
    tax_document_values = TaxDocumentValues.objects.filter(document_id=document_id).first()
    if tax_document_values:
        tax_document_values.values = values
        for value in values:
            value['name'] = f"Line {value['tax_line']}"
        tax_document_values.save()

        # grab the raw_ocr field from TaxDocumentValues, using tax_document_values.raw_ocr
        raw_ocr = tax_document_values.get_raw_ocr()

        for value in values:
            current_tax_form_value = form_values.filter(tax_line=value['tax_line']).first()
            # find the top left corner of bounding box for the value
            for page, text_data in raw_ocr.items():
                for i in range(len(text_data['text'])):
                    if remove_non_numeric(text_data['text'][i]) == remove_non_numeric(value['value']):
                        left_top_corner = (text_data['left'][i], text_data['top'][i])
                        break
                else:
                    continue
                break
            else:
                continue

            # once the top left corner is found, check TaxDocument to see if there is a row that matches its x and y coordinates
            # and use the key from the current value object

            new_x_coordinate = int(left_top_corner[0])
            new_y_coordinate = int(left_top_corner[1])

            tax_document_values_key_location = find_object_by_tax_line(tax_document_values.key_locations,
                                                                       value['tax_line'])

            if tax_document_values_key_location:
                document = TaxDocument.objects.filter(x_position=tax_document_values_key_location['x_coordinate'],
                                                      y_position=tax_document_values_key_location['y_coordinate'],
                                                      tax_line=value['tax_line'],
                                                      tax_form=current_tax_form_value.tax_form).first()

            # if the document exists
            if document:
                # get the 'value' array
                document_values = document.get_values()

                # search the 'value' array for an item that matches the x and y coordinates
                for item in document_values:
                    if 'x' in item and 'y' in item and \
                            item['x'] == new_x_coordinate and item['y'] == new_y_coordinate:
                        # if found, increment the 'occurrence' of that item
                        item['occurrenceCount'] += 1
                        break
                else:
                    # if not found, add a new item to the 'value' array
                    document_values.append({'x': new_x_coordinate, 'y': new_y_coordinate, 'occurrenceCount': 1})

                # save the updated 'value' array back to the document
                document.set_values(document_values)
                document.save()
            else:
                # make a new val
                new_value = {
                    "x": new_x_coordinate,
                    "y": new_y_coordinate,
                    "occurrenceCount": 1,
                }
                new_tax_document = TaxDocument(x_position=tax_document_values_key_location['x_coordinate'],
                                               y_position=tax_document_values_key_location['y_coordinate'],
                                               key=current_tax_form_value.value,
                                               values=new_value,
                                               tax_line=current_tax_form_value.tax_line)
                new_tax_document.save()
