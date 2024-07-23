# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TaxForm1040
from .serializers import TaxForm1040Serializer
from .services.taxParser import ingest_pdf, validate_input
from .utils import calculate_and_enrich_pay_amount
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class PDFUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        value_results = ingest_pdf(request)

        return Response({
            'message': 'PDF Successfully Ingested',
            'values': value_results,
        }, status=status.HTTP_201_CREATED)


# Method for validation of a given entry, used for learning purposes
class Validate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        validate_input(request)

        return Response({
            'message': 'Document validated and updated successfully.',
        }, status=status.HTTP_201_CREATED)


class GetTaxForm1040ByID(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        document_id = kwargs.get('document_id')
        try:
            tax_form = TaxForm1040.objects.get(id=int(document_id))
            enriched_data = calculate_and_enrich_pay_amount(tax_form)
            return Response(enriched_data, status=status.HTTP_200_OK)
        except TaxForm1040.DoesNotExist:
            return Response({'message': 'Tax form 1040 not found.'}, status=status.HTTP_404_NOT_FOUND)


class GetAllTaxForm1040(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tax_form_values = TaxForm1040.objects.all()
        data = []

        for tax_form_value in tax_form_values:
            enriched_data = calculate_and_enrich_pay_amount(tax_form_value)

            # Append updated serialized data into the data list
            data.append(enriched_data)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaxForm1040Serializer(data=request.data)
        if serializer.is_valid():
            tax_form = serializer.save()
            return Response(calculate_and_enrich_pay_amount(tax_form), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
