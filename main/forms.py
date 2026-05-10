from django import forms
from django.contrib.auth.models import User
from .models import Budget

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    terms = forms.BooleanField(required=False, label='Я погоджуюсь з умовами використання')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise forms.ValidationError("Паролі не збігаються")
        return password_confirmation

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ім'я користувача вже зайнято.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ця електронна адреса вже зареєстрована.")
        return email

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise forms.ValidationError("Ви повинні погодитись з умовами використання.")
        return terms



from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['income', 'expenses']
        widgets = {
            'income': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введіть дохід'}),
            'expenses': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введіть витрати'}),
        }
