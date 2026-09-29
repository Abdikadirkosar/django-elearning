from django import forms
from .models import Course, Enrollment, LessonComment, Review


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'instructor', 'category', 'price', 'image', 'duration', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Course title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Course description'}),
            'instructor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Instructor name'}),
            'category': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Web Development'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00 (USD)', 'step': '0.01'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 5 Hours, 4 Weeks'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'price': 'Qiimaha Koorsada ($ USD — 0 = Bilaash)',
        }


class CourseCheckoutForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tusaale: +252 63 4812030'
        }),
        label="Lambarkaaga Telefoonka (Sender Mobile Number)"
    )

    class Meta:
        model = Enrollment
        fields = ['payment_method', 'transaction_id', 'payment_receipt']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-input'}),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tusaale: TXN-894102 ama Number-ka Fariinta'
            }),
            'payment_receipt': forms.FileInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'payment_method': 'Qaabka Lacag-bixinta (Payment Method)',
            'transaction_id': 'Lambarka Tixraaca (Transaction ID / Reference)',
            'payment_receipt': 'Sawirka Rasiidka / Fariinta (Screenshot)',
        }


class LessonCommentForm(forms.ModelForm):
    class Meta:
        model = LessonComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Qor su\'aashaada ama faalladaada ku saabsan casharkan...'
            }),
        }
        labels = {
            'content': 'Su\'aashaada (Your Question)'
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Qor faalladaada iyo aragtidaada koorsadan...'
            }),
        }
        labels = {
            'rating': 'Qiimeynta (Rating Stars)',
            'comment': 'Faalladaada (Your Review)',
        }
