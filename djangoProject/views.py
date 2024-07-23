from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework import status
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response


# Doing this because there is no front end for the assignment, personally just hitting the API directly through Postman
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return Response({
            'message': 'User Successfully Registered',
        }, status=status.HTTP_201_CREATED)
