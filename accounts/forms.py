from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Geli email-kaaga', 'class': 'form-input'})
    )
    password = forms.CharField(
        label='Furaha Sirta ah',
        widget=forms.PasswordInput(attrs={'placeholder': 'Geli furaha sirta ah oo adag', 'class': 'form-input'})
    )
    confirm_password = forms.CharField(
        label='Xaqiiji Furaha Sirta ah',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mar kale ku celi furaha sirta ah', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Dooro magaca isticmaalaha', 'class': 'form-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError("Magacan isticmaale hore ayaa loo qaatay. Fadlan dooro mid kale.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("Akoon leh email-kan hore ayaa loo diiwaangeliyay.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Furaha sirta ah iyo xaqiijintu isma laha. (Passwords do not match.)")
        
        if password and len(password) < 6:
            self.add_error('password', "Furaha sirta ahi waa inuu ka koobnaadaa ugu yaraan 6 xaraf/tiro.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username'].strip()
        user.email = self.cleaned_data['email'].strip()
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(
        label='Magaca Isticmaalaha ama Email-ka',
        widget=forms.TextInput(attrs={'placeholder': 'Geli magacaaga isticmaalaha ama email-ka', 'class': 'form-input'})
    )
    password = forms.CharField(
        label='Furaha Sirta ah',
        widget=forms.PasswordInput(attrs={'placeholder': 'Geli furahaaga sirta ah', 'class': 'form-input', 'id': 'loginPassword'})
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label='I xasuuso (Remember Me)'
    )


class PasswordResetRequestForm(forms.Form):
    identifier = forms.CharField(
        label='Email-kaaga ama Magacaaga Isticmaalaha',
        widget=forms.TextInput(attrs={
            'placeholder': 'Geli email-kaaga (arday@gmail.com) ama magacaaga',
            'class': 'form-input'
        })
    )


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='Furaha Cusub',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Geli furaha cusub (ugu yaraan 6 xaraf/tiro)',
            'class': 'form-input',
            'id': 'newPasswordInput'
        })
    )
    confirm_password = forms.CharField(
        label='Ku Celi Furaha Cusub',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mar kale xaqiiji furaha cusub',
            'class': 'form-input',
            'id': 'confirmPasswordInput'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')

        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Labada fure isma laha. Fadlan hubi inaad si sax ah u qortay.')

        if p1 and len(p1) < 6:
            self.add_error('new_password', 'Furaha sirta ahi waa inuu ka koobnaadaa ugu yaraan 6 xaraf/tiro.')

        return cleaned_data


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Furaha Hadda Kuu Yaalla (Current Password)',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Geli furahaaga hadda jira',
            'class': 'form-input',
            'id': 'currentPasswordInput'
        })
    )
    new_password = forms.CharField(
        label='Furaha Cusub (New Password)',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Geli furaha cusub oo adag',
            'class': 'form-input',
            'id': 'profileNewPasswordInput'
        })
    )
    confirm_password = forms.CharField(
        label='Ku Celi Furaha Cusub (Confirm New Password)',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mar kale qor furaha cusub',
            'class': 'form-input',
            'id': 'profileConfirmPasswordInput'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        cur = self.cleaned_data.get('current_password')
        if not self.user.check_password(cur):
            raise forms.ValidationError('Furahaaga hadda jira ma saxna.')
        return cur

    def clean(self):
        cleaned_data = super().clean()
        cur = cleaned_data.get('current_password')
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')

        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Labada fure ee cusub isma laha.')

        if p1 and cur and p1 == cur:
            self.add_error('new_password', 'Furaha cusubi waa inuu ka duwanaadaa kii hore.')

        if p1 and len(p1) < 6:
            self.add_error('new_password', 'Furaha cusub waa inuu ka koobnaadaa ugu yaraan 6 xaraf/tiro.')

        return cleaned_data



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Cinwaanka email-ka', 'class': 'form-input'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Magaca koowaad', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Magaca qoyska', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


from .models import UserProfile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['headline', 'bio', 'phone', 'avatar']
        widgets = {
            'headline': forms.TextInput(attrs={'placeholder': 'tusaale: Arday Barata Cilmiga Kumbuyuutarka', 'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Wax nooga sheeg safarkaaga waxbarasho...', 'class': 'form-input', 'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': '+252 61 XXX XXXX', 'class': 'form-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input'}),
        }

