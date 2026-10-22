from django import forms
from .models import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['resume_file']

    def clean_resume_file(self):
        file = self.cleaned_data['resume_file']

        if not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")

        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be less than 5 MB.")

        return file