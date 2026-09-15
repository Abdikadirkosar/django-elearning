from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address', 'class': 'form-input'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a strong password', 'class': 'form-input'})
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a unique username', 'class': 'form-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters long.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-input'})
    )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-input'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


from .models import UserProfile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'headline', 'bio', 'phone', 'avatar']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-input'}),
            'headline': forms.TextInput(attrs={'placeholder': 'e.g. Computer Science Student', 'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about your learning journey...', 'class': 'form-input', 'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': '+252 61 XXX XXXX', 'class': 'form-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input'}),
        }

