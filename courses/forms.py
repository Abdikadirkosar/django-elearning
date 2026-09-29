from django import forms
from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'instructor', 'category', 'image', 'duration', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Course title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Course description'}),
            'instructor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Instructor name'}),
            'category': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Web Development'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 5 Hours, 4 Weeks'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
