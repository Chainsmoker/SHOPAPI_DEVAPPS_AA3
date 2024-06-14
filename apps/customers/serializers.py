from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from .models import Address, Cart
from .errors import Error

Customer = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['email', 'password', 'full_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({
                'code': Error.TOO_SHORT['code'],
                'field': 'password',
                'message': Error.TOO_SHORT['message']
            })
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = super().create(validated_data)
        instance.set_password(password)  
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = Customer.objects.get(email=email)
                if user and user.check_password(password):
                    data['user'] = user
                else:
                    raise serializers.ValidationError('Correo o contraseña incorrectos.')
            except Customer.DoesNotExist:
                raise serializers.ValidationError('Correo o contraseña incorrectos.')
        else:
            raise serializers.ValidationError('Correo y contraseña son requeridos.')

        return data
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'city', 'state', 'country', 'zip_code', 'phone', 'is_default']
        extra_kwargs = {
            'id': {'read_only': True},
        }

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'products']
        extra_kwargs = {
            'id': {'read_only': True},
        }