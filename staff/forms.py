# staff/forms.py
from django import forms
from core.models import ClassGroup, Student, ClassRelationship, Subject, TeacherProfile


class ClassUpdateForm(forms.ModelForm):
    class_teacher = forms.ModelChoiceField(
        queryset=TeacherProfile.objects.select_related('user').all(),
        required=False,
        label='Class teacher',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ClassGroup
        fields = ['name', 'academic_year', 'class_teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['class_teacher'].initial = getattr(self.instance, 'class_teacher', None)

    def save(self, commit=True):
        class_group = super().save(commit=commit)
        selected_teacher = self.cleaned_data.get('class_teacher')
        current_teacher = getattr(class_group, 'class_teacher', None)

        if current_teacher and current_teacher != selected_teacher:
            current_teacher.class_taught = None
            if commit:
                current_teacher.save(update_fields=['class_taught'])

        if selected_teacher and selected_teacher.class_taught_id != class_group.pk:
            selected_teacher.class_taught = class_group
            if commit:
                selected_teacher.save(update_fields=['class_taught'])

        return class_group


class StudentAssignForm(forms.Form):
    selected_students = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, all_students, current_ids, **kwargs):
        super().__init__(*args, **kwargs)
        current_ids = [str(student_id) for student_id in current_ids]
        self.fields['selected_students'].choices = [
            (str(s.pk), f"{s.first_name} {s.last_name}")
            for s in all_students
        ]
        self.initial['selected_students'] = current_ids
        self.student_rows = [
            {
                'value': str(student.pk),
                'label': f"{student.first_name} {student.last_name}",
                'admission_number': student.admission_number,
                'checked': str(student.pk) in current_ids,
            }
            for student in all_students
        ]


class SubjectAssignForm(forms.Form):
    def __init__(self, *args, class_group, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_group = class_group
        existing = ClassRelationship.objects.filter(class_group=class_group)
        existing_dict = {cs.subject_id: cs for cs in existing}
        self.subject_rows = []
        for subject in Subject.objects.all():
            cs = existing_dict.get(subject.id)
            checked_field_name = f'subject_{subject.id}_checked'
            teacher_field_name = f'subject_{subject.id}_teacher'
            self.fields[checked_field_name] = forms.BooleanField(
                required=False, initial=(cs is not None),
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
            self.fields[teacher_field_name] = forms.ModelChoiceField(
                queryset=TeacherProfile.objects.all(), required=False,
                initial=cs.teacher_id if cs else None,
                widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
            )
            self.subject_rows.append({
                'subject': subject,
                'checked_field': self[checked_field_name],
                'teacher_field': self[teacher_field_name],
            })

    def save(self):
        ClassRelationship.objects.filter(class_group=self.class_group).delete()
        for row in self.subject_rows:
            if self.cleaned_data.get(f'subject_{row["subject"].id}_checked'):
                teacher = self.cleaned_data.get(f'subject_{row["subject"].id}_teacher')
                ClassRelationship.objects.create(
                    class_group=self.class_group,
                    subject=row['subject'],
                    teacher=teacher
                ).academic_year

class OfficerStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'class_group', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_group': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }