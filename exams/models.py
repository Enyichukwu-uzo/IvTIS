from django.db import models

# Create your models here.
# exams/models.py
from django.db import models
from django.conf import settings
from core.models import Student, Subject, ClassGroup, TeacherProfile


class Exam(models.Model):
    """A major exam period, e.g. 'First Term 2026/2027', 'Mid‑Year Assessments'."""
    name = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20, default='2026/2027')
    EXAM_TYPE_CHOICES = [
        ('midterm', 'Mid‑Term'),
        ('final', 'Final'),
        ('mock', 'Mock'),
        ('entrance', 'Entrance'),
    ]
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['-academic_year', '-start_date']

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class ExamSubject(models.Model):
    """
    A subject scheduled for a particular exam, per class.
    Defines max marks, passing marks, etc.
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=40)
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exam_subjects',
        help_text='Teacher responsible for this exam paper'
    )
    # exams/models.py — add to ExamSubject

    supervisor = models.ForeignKey(
    TeacherProfile,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='supervised_exams',
    help_text='Invigilator/supervisor for this exam paper (can be different from the subject teacher).'
)

    class Meta:
        unique_together = ('exam', 'class_group', 'subject')

    def __str__(self):
        return f"{self.exam.name} - {self.class_group.name} - {self.subject.name}"


class ExamTimetable(models.Model):
    """Date and time for an exam subject."""
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='timetable_entries')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.exam_subject} on {self.date} {self.start_time}-{self.end_time}"


class StudentEnrolment(models.Model):
    """Records which students are taking which exam subjects."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_enrolments')
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='enrolments')
    is_confirmed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'exam_subject')

    def __str__(self):
        return f"{self.student} - {self.exam_subject}"


class ExamResult(models.Model):
    """Individual result for one student in one exam subject."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True, help_text='A*, A, B, etc.')
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exam_results_entered'
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'exam_subject')

    def __str__(self):
        return f"{self.student} - {self.exam_subject}: {self.marks_obtained or 'N/A'}"
    
class ResultBulkUpload(models.Model):
    """
    Records a bulk result upload by a teacher for their assigned exam subject.
    Stores the original CSV file for audit purposes.
    """
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='bulk_uploads')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='result_uploads')
    csv_file = models.FileField(upload_to='results/bulk_uploads/%Y/%m/')
    results_created = models.PositiveIntegerField(default=0)
    results_updated = models.PositiveIntegerField(default=0)
    errors = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Bulk upload for {self.exam_subject} by {self.uploaded_by} on {self.uploaded_at:%d %b %Y}"