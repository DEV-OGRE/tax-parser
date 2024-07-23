# urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import PDFUploadView, Validate, GetTaxForm1040ByID, GetAllTaxForm1040

urlpatterns = [

    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('pdf_upload/', PDFUploadView.as_view(), name='pdf_upload'),
    path('validate/', Validate.as_view(), name='validate'),
    path('tax-forms/<int:document_id>/', GetTaxForm1040ByID.as_view()),
    path('tax-forms/', GetAllTaxForm1040.as_view()),


]
