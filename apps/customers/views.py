from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema

from .models import Customer, Address, Cart
from .serializers import CustomerSerializer, LoginSerializer, ResetPasswordSerializer, ForgotPasswordSerializer, VerifyCodeSerializer, AddressSerializer, CartSerializer

class CustomerCreateView(APIView):
    @swagger_auto_schema(operation_description="Crea un nuevo consumidor.", request_body=CustomerSerializer, responses={200: CustomerSerializer}, tags=['Authentication'])
    def post(self, request):
        email = request.data.get('email')
        if Customer.objects.filter(email=email).exists():
            return Response({'message': 'Este correo electronico ya existe.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            token, created = Token.objects.get_or_create(user=serializer.instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(operation_description="Inicia sesión.", request_body=LoginSerializer, tags=['Authentication'])
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    @swagger_auto_schema(operation_description="Solicita restablecer contraseña.", request_body=ForgotPasswordSerializer, tags=['Authentication'])
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                return Response({'message': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            
            code = get_random_string(length=6, allowed_chars='0123456789')
            user.forgot_password_code = code
            user.save()
            subject = 'Código de restablecimiento de contraseña'
            message = f'Su código de restablecimiento de contraseña es: {code}'
            from_email = 'your_email@example.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)
            return Response({'message': 'Código de restablecimiento de contraseña enviado.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyCodeView(APIView):
    @swagger_auto_schema(operation_description="Verifica código de restablecimiento de contraseña.", request_body=VerifyCodeSerializer, tags=['Authentication'])
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                return Response({'message': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            
            if not user.forgot_password_code:
                return Response({'message': 'No se ha solicitado restablecer la contraseña.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.forgot_password_code == code or user.email != email:
                return Response({'message': 'Código de restablecimiento de contraseña incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'user': user.email}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordView(APIView):
    @swagger_auto_schema(operation_description="Restablece contraseña.", request_body=ResetPasswordSerializer, tags=['Authentication'])
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            password = serializer.validated_data['password']
            try:
                user = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                return Response({'message': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            
            if not user.forgot_password_code:
                return Response({'message': 'No se ha solicitado restablecer la contraseña.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.forgot_password_code == code or user.email != email:
                return Response({'message': 'Código de restablecimiento de contraseña incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(password) < 8:
                return Response({'message': 'La contraseña debe tener al menos 8 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.forgot_password_code == code:
                user.set_password(password)
                user.forgot_password_code = None
                user.save()
                return Response({'message': 'Contraseña restablecida con éxito.'}, status=status.HTTP_200_OK)
            return Response({'message': 'Código de restablecimiento de contraseña incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def change_password(self, request):
        customer = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if customer.check_password(old_password):
            customer.set_password(new_password)
            customer.save()
            return Response({'message': 'Password changed successfully'})
        else:
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(customer=self.request.user)
    
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)
    
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })