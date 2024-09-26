# Tax Parser Proof of Concept

Simple Tax Parser created as a proof of concept

## Description

Built in Python, specifically python 3.9 (did not realize that was my system default until a while in ha)

## Getting Started

### Dependencies

* Python 3
* Django
* Pipenv
* Tesseract
* Pillow
* pdf2image
* pytesseract

### Installing

* Standard Issue Python Django Application
  * The one thing you will need beyond the standard package install is to install Tesseract directly to your machine
  * See https://tesseract-ocr.github.io/tessdoc/Installation.html

### Executing program

* Run using `python3 manage.py runserver`
* One thing to be aware of is that I did not write any seeding scripts for getting the initial key/values into the SQLite DB for the parsing algorithm to work
* For sake of ease of evaluation I'm including the `db.sqllite3` file in the POC, however, if you want to use an empty DB, add these rows to `TaxFormValues`:
``````
    id, tax_form, value, tax_line
    1,1040,total,9
    2,1040,adjusted,11
    3,1040,deductions,12
    4,1040,taxable income,15
    5,1040,overpaid,34
    6,1040,amount you owe,37
```````
* `id` doesn't matter of course, but included it to show the whole table

## API Reference

# /taxparser/api/token/
    Returns a standard Django Auth Token to use in the header of your requests.  
    POST endpoint:

    {
        username: string,
        password: string
    }

# /register
    Standard Django Register Endpoint, I disabled CSRF checks due to there being no front-end (less hassle when 
    eval'ing from Postman

# /taxparser/pdf_upload
    POST Endpoint for uploading your 1040 PDFs to, which does the following:
    * Ingests the PDF
    * Converts it to a collection of images
    * Increases the contrast of the blacks in the text for easier OCR
    * Using a very barebones ML set, looks for positional repeatability via key parsing
    * Crossreferencing existing dataset, attemps to look for pre-existing known locations of values
    * Updates the dataset if a new key coordinate set is found
    * Updates the parsing part of the DB, adds newly added Tax Form to the DB for regular API interaction

```
POST EXAMPLE:
{
    file: PDFfile.pdf
    tax_form: '1040' -> '1040-SR is also in the dataset but has no API Access or non-parsing DB Entries
}
```

# /taxparser/validate
    Main feedback loop for ML set, this is used as the learning step in the algorithm.  As the algo stands, 
    there are no hueristics at play when choosing a value that is not found in the dataset, so this step 
    is needed at least once to see the 'magic' at play from an empty DB

```
POST EXAMPLE:
{
    "document_id": 60,
    "values": 
        [{"tax_line": "9", "value": "91"}, {"tax_line": "11", "value": "111"}, {"tax_line": "12", "value": "121"}, {"tax_line": "15", "value": "151"}, {"tax_line": "34", "value": "341"}, {"tax_line": "37", "value": "371"}]
}
```

# /taxparser/tax-forms/<int:document_id>/
    Grabs a Tax Form by it's ID in the URL.

# /taxparser/tax-forms/ GET
    Retrieve all 1040 Tax Forms persisted in the DB

# /taxparser/tax-forms/ POST
    If you don't want to upload through the PDF route you can manually put data in this way. There will be no associated PDF as a result.

## Trials and Tribulations
There were some things I just did not do as I was really running the clock for how much time I wanted to spend on this, some are obvious, some are a little more hidden.
* I did not set up proper PKs and Foreign keys across the whole DB, fully aware the parsing portion is a non-normalized wild west 
* Disabling CSRF on /register/ mostly because I didn't want to finangle with Postman to get it to work for this POC
* Used SQLite as opposed to something a little more bulletproof like Postgres. This was somewhat intential however, wanted the
app easy to open and explore without _too_ many dependencies dragging the install down
* The ML set is in SQLite. This one bummed me out, as it _really_ should be in a non-relational DB due to access times at scale, but for the life of me I could not figure out how to get the mongo wrapper to actually work
  * On that note, that's why that part of the DB is utterly filled with JSON objects.  I was originally planning for that slice to _be_ Mongo, and being as such having the JSON values on access with one pull is ideal. Made sure to not let it bleed to the requested part of the DB (TaxForm1040)
* The Parsing Algo does not take transforms into account when deriving values, i.e, if the PDF is slightly ajar.  I thought of adding it, but realized it would take too much time to implement. But it parses the digitally delivered forms just fine.
* having the app be a sub-app of the main project was a goof early on but I figured I should just keep chugging along as time was limited.
* Stuff like the PDF file, images, and the raw OCR output are inefficient where they are.  Heavy load on the DB to have the raw OCR output there, would rather dump it off somewhere like S3 if I had infinite money/time
* The idea folder snuck its way into the branch and no matter what I do to gitignore it's not biting.

## Author

Zack D
