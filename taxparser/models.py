from django.db import models

from django.db.models import JSONField


# Create your models here.
class PDFDocument(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    tax_form = models.CharField(max_length=200, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class TaxDocument(models.Model):
    x_position = models.DecimalField(max_digits=4, decimal_places=0)
    y_position = models.DecimalField(max_digits=4, decimal_places=0)
    key = models.CharField(max_length=200, blank=False, null=False)
    tax_form = models.CharField(max_length=200, blank=False, null=False)
    values = JSONField(blank=True, null=True)
    tax_line = models.CharField(max_length=200, blank=False, null=False)

    def set_values(self, data):
        self.values = data

    def get_values(self):
        return self.values


class TaxFormValues(models.Model):
    tax_form = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    tax_line = models.CharField(max_length=200)


class TaxDocumentValues(models.Model):
    document_id = models.TextField(primary_key=True)
    values = JSONField(blank=True, null=True)
    key_locations = JSONField(blank=True, null=True)
    raw_ocr = JSONField(blank=True, null=True)

    def set_values(self, data):
        self.values = data

    def get_values(self):
        return self.values

    def set_raw_ocr(self, data):
        self.raw_ocr = data

    def get_raw_ocr(self):
        return self.raw_ocr

    def set_key_location(self, data):
        self.key_locations = data

    def get_key_locations(self):
        return self.key_locations

class TaxForm1040(models.Model):
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, null=True, blank=True)
    line_9 = models.DecimalField(max_digits=16, decimal_places=2)
    line_11 = models.DecimalField(max_digits=16, decimal_places=2)
    line_12 = models.DecimalField(max_digits=16, decimal_places=2)
    line_15 = models.DecimalField(max_digits=16, decimal_places=2)
    line_34 = models.DecimalField(max_digits=16, decimal_places=2)
    line_37 = models.DecimalField(max_digits=16, decimal_places=2)