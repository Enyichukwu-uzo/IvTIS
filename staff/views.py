from django.shortcuts import render

# Create your views here.
# staff/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from core.models import ClassGroup, Student, Subject, ClassRelationship, TeacherProfile
from exams.views import is_exams_officer
from .forms import ClassUpdateForm, OfficerStudentForm, StudentAssignForm, SubjectAssignForm


def is_staff(user):
    return user.is_authenticated and user.role == 'staff'


# staff/views.py — replace the dashboard function

@login_required
def dashboard(request):
    if not is_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')

    # Get the teacher profile for the logged-in staff member
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    if not teacher_profile:
        messages.error(request, 'No teacher profile found.')
        return redirect('core:home')

    # Show only the class this teacher is assigned to teach
    classes = ClassGroup.objects.filter(
        class_teacher=teacher_profile
    ).select_related(
        'class_teacher__user',
    ).annotate(
        student_count=Count('students', distinct=True),
        subject_count=Count('class_relationships', distinct=True),
    ).prefetch_related(
        Prefetch(
            'class_relationships',
            queryset=ClassRelationship.objects.select_related('subject', 'teacher__user'),
        ),
    ).all()

    # Also fetch exam subjects assigned to this teacher
    from exams.models import ExamSubject
    exam_subjects = ExamSubject.objects.filter(
        teacher=teacher_profile
    ).select_related('exam', 'class_group', 'subject').order_by('exam__start_date')

    return render(request, 'staff/dashboard.html', {
        'classes': classes,
        'exam_subjects': exam_subjects,
        'teacher': teacher_profile,
    })

@login_required
def class_detail(request, class_id):
    if not (is_staff(request.user) or is_exams_officer(request.user)):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    class_group = get_object_or_404(ClassGroup.objects.select_related(
        'class_teacher__user',
    ).annotate(
        student_count=Count('students', distinct=True),
        subject_count=Count('class_relationships', distinct=True),
    ).prefetch_related(
        Prefetch(
            'class_relationships',
            queryset=ClassRelationship.objects.select_related('subject', 'teacher__user').prefetch_related(
        
            ),
        ),
    ), pk=class_id)
    students = Student.objects.filter(class_group=class_group
    ).distinct().order_by('last_name', 'first_name')

    return render(request, 'staff/class_detail.html', {
        'class_group': class_group,
        'students': students,
    })


@login_required
def class_update(request, class_id):
    if not (is_staff(request.user) or is_exams_officer(request.user)):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    class_group = get_object_or_404(ClassGroup.objects.select_related('class_teacher__user'), pk=class_id)

    if request.method == 'POST':
        form = ClassUpdateForm(request.POST, instance=class_group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class details updated.')
            return redirect('staff:class_detail', class_id=class_id)
    else:
        form = ClassUpdateForm(instance=class_group)
    return render(request, 'staff/class_form.html', {'form': form, 'class_group': class_group})


@login_required
def manage_students(request, class_id):
    if not is_exams_officer(request.user):
        messages.error(request, 'Only the Examinations Officer can manage student assignments.')
        return redirect('staff:dashboard')
    class_group = get_object_or_404(ClassGroup, pk=class_id)
    all_students = Student.objects.filter(is_active=True).order_by('last_name')
    current_student_ids = list(
        Student.objects.filter(class_group=class_group)
        .values_list('id', flat=True)
        .distinct()
    )
    if not current_student_ids:
        current_student_ids = list(class_group.students.values_list('id', flat=True))

    if request.method == 'POST':
        form = StudentAssignForm(request.POST, all_students=all_students, current_ids=current_student_ids)
        if form.is_valid():
            selected_ids = [int(student_id) for student_id in form.cleaned_data['selected_students']]
            selected_students = Student.objects.filter(id__in=selected_ids)
            Student.objects.filter(class_group=class_group).exclude(id__in=selected_ids).update(class_group=None)
            selected_students.update(class_group=class_group)
            messages.success(request, 'Students updated.')
            return redirect('staff:class_detail', class_id=class_id)
    else:
        form = StudentAssignForm(all_students=all_students, current_ids=current_student_ids)

    return render(request, 'staff/manage_students.html', {
        'form': form,
        'class_group': class_group,
    })


@login_required
def manage_subjects(request, class_id):
    if not is_exams_officer(request.user):
        messages.error(request, 'Only the Examinations Officer can manage subject assignments.')
        return redirect('staff:dashboard')
    class_group = get_object_or_404(ClassGroup, pk=class_id)
    current_subjects = ClassRelationship.objects.filter(class_group=class_group).select_related('subject', 'teacher')

    if request.method == 'POST':
        form = SubjectAssignForm(request.POST, class_group=class_group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subjects updated.')
            return redirect('staff:class_detail', class_id=class_id)
    else:
        form = SubjectAssignForm(class_group=class_group)

    return render(request, 'staff/manage_subjects.html', {
        'form': form,
        'class_group': class_group,
        'current_subjects': current_subjects,
    })
    
@login_required
def officer_student_list(request):
    """
    Exams Officer can view all students and update their details.
    """
    if not is_exams_officer(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    students = Student.objects.select_related('class_group').order_by('last_name', 'first_name')
    return render(request, 'staff/officer_student_list.html', {'students': students})


@login_required
def officer_student_edit(request, student_id):
    """
    Exams Officer can edit a student's name and class.
    """
    if not is_exams_officer(request.user):
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'POST':
        form = OfficerStudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.first_name} {student.last_name} updated.')
            return redirect('staff:officer_student_list')
    else:
        form = OfficerStudentForm(instance=student)
    
    return render(request, 'staff/officer_student_form.html', {'form': form, 'student': student})

@login_required
def class_inventory(request):
    """
    Public-facing (or staff-facing) list of all classes.
    Each item links to the class detail page.
    """
    classes = ClassGroup.objects.select_related('class_teacher__user').annotate(
        student_count=Count('students', distinct=True),
    ).order_by('name')
    return render(request, 'staff/class_inventory.html', {'classes': classes})
