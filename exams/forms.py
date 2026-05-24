# exams/forms.py
from django import forms
from .models import StudentEnrolment, ExamResult


class EnrolmentForm(forms.Form):
    def __init__(self, *args, students_queryset, exam_subject, **kwargs):
        super().__init__(*args, **kwargs)
        self.students = students_queryset
        self.exam_subject = exam_subject
        # Get existing enrolments
        existing = StudentEnrolment.objects.filter(exam_subject=exam_subject).values_list('student_id', flat=True)
        for student in students_queryset:
            self.fields[f'student_{student.id}'] = forms.BooleanField(
                required=False,
                initial=student.id in existing,
                label=f'{student.first_name} {student.last_name}'
            )

    def save(self):
        # Clear enrolments and re-add based on selected
        StudentEnrolment.objects.filter(exam_subject=self.exam_subject).delete()
        enrolments = []
        for student in self.students:
            if self.cleaned_data.get(f'student_{student.id}'):
                enrolments.append(StudentEnrolment(
                    student=student,
                    exam_subject=self.exam_subject
                ))
        StudentEnrolment.objects.bulk_create(enrolments)


class ResultEntryForm(forms.Form):
    def __init__(self, *args, enrolments, exam_subject, **kwargs):
        super().__init__(*args, **kwargs)
        self.enrolments = enrolments
        self.exam_subject = exam_subject
        for enrolment in enrolments:
            student = enrolment.student
            prefix = f'student_{student.id}'
            # Try to load existing result
            try:
                result = ExamResult.objects.get(student=student, exam_subject=exam_subject)
                initial_marks = result.marks_obtained
                initial_grade = result.grade
            except ExamResult.DoesNotExist:
                initial_marks = None
                initial_grade = ''
            self.fields[f'{prefix}_marks'] = forms.DecimalField(
                max_digits=6, decimal_places=2, required=False,
                initial=initial_marks,
                label=f'{student.first_name} {student.last_name} - Marks'
            )
            self.fields[f'{prefix}_grade'] = forms.CharField(
                max_length=5, required=False,
                initial=initial_grade,
                label='Grade'
            )

    def save(self, entered_by):
        for enrolment in self.enrolments:
            student = enrolment.student
            prefix = f'student_{student.id}'
            marks = self.cleaned_data.get(f'{prefix}_marks')
            grade = self.cleaned_data.get(f'{prefix}_grade')
            if marks is not None or grade:
                ExamResult.objects.update_or_create(
                    student=student,
                    exam_subject=self.exam_subject,
                    defaults={
                        'marks_obtained': marks,
                        'grade': grade,
                        'entered_by': entered_by
                    }
                )
                
from .models import Exam, ExamSubject, ExamTimetable

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'academic_year', 'exam_type', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ExamSubjectForm(forms.ModelForm):
    class Meta:
        model = ExamSubject
        fields = ['class_group', 'subject', 'max_marks', 'passing_marks', 'teacher', 'supervisor']
        widgets = {
            'class_group': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, exam, **kwargs):
        super().__init__(*args, **kwargs)
        self.exam = exam

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.exam = self.exam
        if commit:
            instance.save()
        return instance
    
class ExamTimetableForm(forms.ModelForm):
    class Meta:
        model = ExamTimetable
        fields = ['exam_subject', 'date', 'start_time', 'end_time', 'room']
        widgets = {
            'exam_subject': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, exam_subjects=None, **kwargs):
            super().__init__(*args, **kwargs)
            if exam_subjects:
                self.fields['exam_subject'].queryset = exam_subjects
class BaseExamTimetableFormSet(forms.BaseModelFormSet):
    """
    Custom formset to capture 'exam_subjects' at the formset level 
    and safely pass it down to every individual child form.
    """
    def __init__(self, *args, exam_subjects=None, **kwargs):
        # 1. Capture the custom parameter and save it to the formset instance
        self.exam_subjects = exam_subjects
        
        # 2. Call the parent class __init__ so standard formset setup isn't broken
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        # 1. Grab the standard dictionary of arguments Django prepares for the child form
        kwargs = super().get_form_kwargs(index)
        
        # 2. Inject our saved exam_subjects into that dictionary
        # This matches the 'exam_subjects=None' argument in your ExamTimetableForm.__init__
        kwargs['exam_subjects'] = self.exam_subjects
        
        return kwargs


# 2. THE FACTORY UPDATE
# We register our custom formset using the 'formset' parameter.
ExamTimetableFormSet = forms.modelformset_factory(
    ExamTimetable,
    form=ExamTimetableForm,
    formset=BaseExamTimetableFormSet,  # <-- Tell the factory to use our custom behavior
    extra=5,
    can_delete=True
)