from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, ProductImage, Category
from .models import UserProfile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
        
class CustomRegisterForm(UserCreationForm):
    phone = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'phone', 'password1', 'password2']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'province', 'postcode', 'phone'] 


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']