from django.shortcuts import render

# Create your views here.
# exams/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.models import Student
from .models import Exam, ExamSubject, ExamTimetable, StudentEnrolment, ExamResult
from .forms import EnrolmentForm, ResultEntryForm  # We'll create these
from django.contrib.auth.decorators import user_passes_test
from .forms import ExamForm, ExamSubjectForm, ExamTimetableFormSet


def is_staff(user):
    return user.is_authenticated and hasattr(user, 'teacher_profile') or user.role == 'exams_officer'

def is_teacher(user):
    return (user.is_authenticated and hasattr(user, 'teacher_profile')) or user.role == 'exams_officer' 

def get_teacher_exam_subjects(user):
    """Return exam subjects where this teacher is assigned."""
    if not is_teacher(user):
        return ExamSubject.objects.none()
    return ExamSubject.objects.filter(teacher=user.teacher_profile)

@login_required
def exam_list(request):
    if not is_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    exams = Exam.objects.all().order_by('-academic_year', '-start_date')
    return render(request, 'exams/exam_list.html', {'exams': exams})


@login_required
def exam_detail(request, exam_id):
    if not is_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    exam = get_object_or_404(Exam, pk=exam_id)
    subjects = ExamSubject.objects.filter(exam=exam).select_related('class_group', 'subject', 'teacher')
    return render(request, 'exams/exam_detail.html', {'exam': exam, 'subjects': subjects})


@login_required
def manage_enrolment(request, exam_id, subject_id):
    if not is_teacher(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    exam_subject = get_object_or_404(
        get_teacher_exam_subjects(request.user),
        pk=subject_id,
        exam_id=exam_id
    )
    students_in_class = Student.objects.filter(class_group=exam_subject.class_group, is_active=True)

    if request.method == 'POST':
        form = EnrolmentForm(request.POST, students_queryset=students_in_class, exam_subject=exam_subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrolment updated.')
            return redirect('exams:exam_detail', exam_id=exam_id)
    else:
        form = EnrolmentForm(students_queryset=students_in_class, exam_subject=exam_subject)
    existing_enrolments = StudentEnrolment.objects.filter(exam_subject=exam_subject).values_list('student_id', flat=True)
    ...
    
    return render(request, 'exams/manage_enrolment.html', {
        'exam_subject': exam_subject,
        'form': form,
        'students': students_in_class,
        'enrolled_ids': list(existing_enrolments),   # <-- NEW
    })

@login_required
def result_entry(request, exam_id, subject_id):
    if not is_teacher(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    exam_subject = get_object_or_404(
        get_teacher_exam_subjects(request.user),
        pk=subject_id,
        exam_id=exam_id
    )
    if exam_subject.teacher and exam_subject.teacher.user != request.user:
        messages.error(request, 'You are not the assigned teacher for this exam.')
        return redirect('exams:exam_detail', exam_id=exam_id)
    enrolments = StudentEnrolment.objects.filter(exam_subject=exam_subject).select_related('student')

    if request.method == 'POST':
        form = ResultEntryForm(request.POST, enrolments=enrolments, exam_subject=exam_subject)
        for enrolment in enrolments:
            enrolment.marks_field = form[
            f"student_{enrolment.student.id}_marks"
        ]
        for enrolment in enrolments:
            enrolment.grade_field = form[
            f"student_{enrolment.student.id}_grade"
        ]
        if form.is_valid():
            form.save(entered_by=request.user)
            messages.success(request, 'Results saved.')
            return redirect('exams:exam_detail', exam_id=exam_id)
    else:
        form = ResultEntryForm(enrolments=enrolments, exam_subject=exam_subject)
        for enrolment in enrolments:
            enrolment.marks_field = form[
            f"student_{enrolment.student.id}_marks"
        ]
            enrolment.grade_field = form[
            f"student_{enrolment.student.id}_grade"
        ]

    return render(request, 'exams/result_entry.html', {
        'exam_subject': exam_subject,
        'form': form,
        'enrolments': enrolments,
    })


@login_required
def student_results(request):
    # Student view: own results
    if not request.user.is_authenticated or not hasattr(request.user, 'student_profile'):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    student = request.user.student_profile
    results = ExamResult.objects.filter(student=student).select_related(
        'exam_subject__exam', 'exam_subject__subject', 'exam_subject__class_group'
    ).order_by('-exam_subject__exam__start_date')
    return render(request, 'exams/student_results.html', {'results': results, 'student': student})

def exam_timetable(request, exam_id):
    """
    Displays the timetable for a given exam period.
    Accessible to all authenticated users (staff, parents, students).
    """
    exam = get_object_or_404(Exam, pk=exam_id)
    timetable_entries = ExamTimetable.objects.filter(
        exam_subject__exam=exam
    ).select_related(
        'exam_subject__subject',
        'exam_subject__class_group'
    ).order_by('date', 'start_time')

    return render(request, 'exams/timetable.html', {
        'exam': exam,
        'timetable_entries': timetable_entries,
    })
    

def is_exams_officer(user):
    return user.is_authenticated and user.role == 'exams_officer'

@login_required
@user_passes_test(is_exams_officer, login_url='core:home')
def officer_dashboard(request):
    exams = Exam.objects.all().order_by('-academic_year', '-start_date')
    return render(request, 'exams/officer_dashboard.html', {'exams': exams})

@login_required
@user_passes_test(is_exams_officer, login_url='core:home')
def officer_create_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.name}" created.')
            return redirect('exams:officer_dashboard')
    else:
        form = ExamForm()
    return render(request, 'exams/officer_exam_form.html', {'form': form, 'title': 'Create Exam'})

@login_required
@user_passes_test(is_exams_officer, login_url='core:home')
def officer_edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated.')
            return redirect('exams:officer_dashboard')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/officer_exam_form.html', {'form': form, 'title': 'Edit Exam', 'exam': exam})

@login_required
@user_passes_test(is_exams_officer, login_url='core:home')
def officer_manage_subjects(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    exam_subjects = ExamSubject.objects.filter(exam=exam).select_related('class_group', 'subject', 'teacher')
    return render(request, 'exams/officer_exam_subjects.html', {'exam': exam, 'exam_subjects': exam_subjects})

@login_required
@user_passes_test(is_exams_officer, login_url='core:home')
def officer_add_subject(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':
        form = ExamSubjectForm(request.POST, exam=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added to exam.')
            return redirect('exams:officer_manage_subjects', exam_id=exam.id)
    else:
        form = ExamSubjectForm(exam=exam)
    return render(request, 'exams/officer_subject_form.html', {'form': form, 'exam': exam})

@login_required
@user_passes_test(is_exams_officer, login_url='core:home')
def officer_manage_timetable(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    exam_subjects = ExamSubject.objects.filter(exam=exam)
    if request.method == 'POST':
        formset = ExamTimetableFormSet(request.POST, exam_subjects=exam_subjects)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Timetable saved.')
            return redirect('exams:officer_manage_timetable', exam_id=exam.id)
    else:
        formset = ExamTimetableFormSet(exam_subjects=exam_subjects)
    return render(request, 'exams/officer_timetable.html', {'exam': exam, 'formset': formset})

@login_required
def teacher_exam_subjects(request):
    if not is_teacher(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    subjects = ExamSubject.objects.filter(
        teacher=request.user.teacher_profile
    ).select_related('exam', 'class_group', 'subject').order_by('exam__start_date')
    return render(request, 'exams/teacher_exam_subjects.html', {'subjects': subjects})


    # rest of the view unchanged


    # rest unchanged