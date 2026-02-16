from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    secret_code = forms.CharField(
        max_length=100, 
        required=True,
        help_text="Секретный код для регистрации",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'secret_code']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def clean_secret_code(self):
        secret_code = self.cleaned_data.get('secret_code')
        
        # СПИСОК РАЗРЕШЕННЫХ КОДОВ - ИЗМЕНИТЕ НА СВОИ!
        valid_codes = [
            'зачем',           # Основной код для девушки
            'aryn',             # Альтернативный код
            'быть',        # Еще вариант
            'secret123',        # Для тестирования
        ]
        
        if secret_code not in valid_codes:
            raise forms.ValidationError("❌ Неверный секретный код. Получи код у создателя сайта.")
        return secret_code