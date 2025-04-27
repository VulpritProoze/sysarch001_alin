from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Registration
from .choices import COURSE_CHOICES, LEVEL_CHOICES

class RegistrationForm(UserCreationForm):
      
    idno = forms.IntegerField()
    lastname = forms.CharField(max_length=100)
    firstname = forms.CharField(max_length=100)
    middlename = forms.CharField(max_length=100)
    course = forms.ChoiceField(choices=COURSE_CHOICES, required=True)
    level = forms.ChoiceField(choices=LEVEL_CHOICES, required=True)
    email = forms.EmailField()
    address = forms.CharField(max_length=255)
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def clean_idno(self):
        idno = self.cleaned_data.get('idno')

        if Registration.objects.filter(idno=idno).exists():
            raise forms.ValidationError("The ID number already exists. Please choose a different one.")
        
        return idno

class StudyLoadUploadForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['study_load']
    
    def clean_study_load(self):
        study_load = self.cleaned_data.get('study_load')
        if study_load:
            # Validate file size (5MB max)
            if study_load.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large (max 5MB)")
            # Validate file extension
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if not any(study_load.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Unsupported file format. Please upload a JPEG or PNG file.")
        return study_load