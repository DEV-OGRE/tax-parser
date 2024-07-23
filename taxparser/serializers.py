# serializers.py
from rest_framework import serializers
from .models import PDFDocument, TaxForm1040


class PDFDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = '__all__'


class TaxForm1040Serializer(serializers.ModelSerializer):
    class Meta:
        model = TaxForm1040
        fields = ['id', 'document_id', 'line_9', 'line_11', 'line_12', 'line_15', 'line_34', 'line_37']
