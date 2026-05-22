# core/forms.py
from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Form for the public contact page.

    We use ModelForm because it automatically:
        - Generates fields from the model
        - Validates data types (email format, max lengths)
        - Saves to the database with one save() call

    The 'widgets' dictionary customises the HTML rendering of each field,
    adding Bootstrap CSS classes and placeholder text.
    """

    class Meta:
        model = ContactMessage
        fields = [
            'name',
            'email',
            'phone',
            'enquiry_type',
            'subject',
            'message',
        ]
        # Excludes: status, submitted_at, staff_notes (these are internal)

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+234 800 000 0000 (optional)',
            }),
            'enquiry_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subject line',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'How can we help you? Please provide as much detail as possible.',
                'required': True,
            }),
        }

    def clean_message(self):
        """
        Additional validation: prevent extremely short messages
        that are likely spam or accidental submissions.
        """
        message = self.cleaned_data.get('message', '')
        if len(message.strip()) < 10:
            raise forms.ValidationError(
                'Please provide a bit more detail (at least 10 characters).'
            )
        return message
    
# core/forms.py — add below ContactForm

from .models import ProspectusRequest, Application


class ProspectusRequestForm(forms.ModelForm):
    """
    Form for the 'Request a Prospectus' section of the admissions page.
    Tightly scoped to capture just enough to send the right prospectus.
    """
    class Meta:
        model = ProspectusRequest
        fields = ['parent_name', 'parent_email', 'parent_phone', 'child_name', 'child_age_group', 'message']
        widgets = {
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'parent_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+234 800 000 0000',
            }),
            'child_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Child's full name",
            }),
            'child_age_group': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional: any specific programmes or questions?',
            }),
        }


class ApplicationForm(forms.ModelForm):
    """
    Full admissions application form.
    File upload fields use ClearableFileInput with Bootstrap classes.
    """
    class Meta:
        model = Application
        fields = [
            'student_first_name', 'student_last_name', 'student_date_of_birth',
            'student_gender', 'proposed_entry_year', 'current_school',
            'current_grade', 'parent_name', 'parent_email', 'parent_phone',
            'parent_address', 'how_heard',
            'birth_certificate', 'last_report_card', 'additional_document',
        ]
        widgets = {
            'student_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'student_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'student_date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',  # HTML5 date picker
            }),
            'student_gender': forms.Select(attrs={'class': 'form-select'}),
            'proposed_entry_year': forms.Select(attrs={'class': 'form-select'}),
            'current_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current school (if any)'}),
            'current_grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Year 4'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary contact name'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'parent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full address'}),
            'how_heard': forms.Select(attrs={'class': 'form-select'}),
            'birth_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'last_report_card': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_student_date_of_birth(self):
        dob = self.cleaned_data.get('student_date_of_birth')
        if dob:
            import datetime
            from django.core.exceptions import ValidationError
            # Ensure the child is at least 2 years old
            if dob > datetime.date.today() - datetime.timedelta(days=365*2):
                raise ValidationError("The student must be at least 2 years old to apply.")
            # Ensure the child is under 20
            if dob < datetime.date.today() - datetime.timedelta(days=365*20):
                raise ValidationError("Please check the date of birth. The student seems older than expected.")
        return dob# core/forms.py — add below ContactForm

from .models import ProspectusRequest, Application


class ProspectusRequestForm(forms.ModelForm):
    """
    Form for the 'Request a Prospectus' section of the admissions page.
    Tightly scoped to capture just enough to send the right prospectus.
    """
    class Meta:
        model = ProspectusRequest
        fields = ['parent_name', 'parent_email', 'parent_phone', 'child_name', 'child_age_group', 'message']
        widgets = {
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'parent_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+234 800 000 0000',
            }),
            'child_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Child's full name",
            }),
            'child_age_group': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional: any specific programmes or questions?',
            }),
        }


class ApplicationForm(forms.ModelForm):
    """
    Full admissions application form.
    File upload fields use ClearableFileInput with Bootstrap classes.
    """
    class Meta:
        model = Application
        fields = [
            'student_first_name', 'student_last_name', 'student_date_of_birth',
            'student_gender', 'proposed_entry_year', 'current_school',
            'current_grade', 'parent_name', 'parent_email', 'parent_phone',
            'parent_address', 'how_heard',
            'birth_certificate', 'last_report_card', 'additional_document',
        ]
        widgets = {
            'student_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'student_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'student_date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',  # HTML5 date picker
            }),
            'student_gender': forms.Select(attrs={'class': 'form-select'}),
            'proposed_entry_year': forms.Select(attrs={'class': 'form-select'}),
            'current_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current school (if any)'}),
            'current_grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Year 4'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary contact name'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'parent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full address'}),
            'how_heard': forms.Select(attrs={'class': 'form-select'}),
            'birth_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'last_report_card': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_student_date_of_birth(self):
        dob = self.cleaned_data.get('student_date_of_birth')
        if dob:
            import datetime
            from django.core.exceptions import ValidationError
            # Ensure the child is at least 2 years old
            if dob > datetime.date.today() - datetime.timedelta(days=365*2):
                raise ValidationError("The student must be at least 2 years old to apply.")
            # Ensure the child is under 20
            if dob < datetime.date.today() - datetime.timedelta(days=365*20):
                raise ValidationError("Please check the date of birth. The student seems older than expected.")
        return dob
class ApplicationDocumentForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['birth_certificate', 'last_report_card', 'additional_document']
        widgets = {
            'birth_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'last_report_card': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }