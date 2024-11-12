# inventory/forms.py
from django import forms
from .models import Drug, Stock, Category
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class DrugForm(forms.ModelForm):
    available_stock = forms.IntegerField(label="Initial Stock Quantity", min_value=0)

    class Meta:
        model = Drug
        fields = ['drug_name', 'category', 'price', 'discount']

    def save(self, commit=True):
        # Override save method to create a Stock instance when a Drug is saved
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Create or update stock associated with the drug
            stock, created = Stock.objects.get_or_create(drug=instance)
            stock.available_stock = self.cleaned_data['available_stock']
            stock.stock_status = stock.available_stock > 0  # Update stock status based on availability
            stock.save()
        return instance

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        # Set is_staff based on role
        role = self.cleaned_data['role']
        if role == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False

        if commit:
            user.save()
        return user