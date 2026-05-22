from django.contrib import admin

# Register your models here.
# exams/admin.py
from django.contrib import admin
from .models import Exam, ExamSubject, ExamTimetable, StudentEnrolment, ExamResult


class ExamSubjectInline(admin.TabularInline):
    model = ExamSubject
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'exam_type', 'start_date', 'end_date']
    inlines = [ExamSubjectInline]


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ['exam', 'class_group', 'subject', 'max_marks', 'passing_marks', 'teacher']
    list_filter = ['exam', 'class_group']


@admin.register(ExamTimetable)
class ExamTimetableAdmin(admin.ModelAdmin):
    list_display = ['exam_subject', 'date', 'start_time', 'end_time', 'room']
    list_filter = ['exam_subject__exam']


@admin.register(StudentEnrolment)
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_subject', 'is_confirmed']
    list_filter = ['exam_subject__exam', 'exam_subject__class_group']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_subject', 'marks_obtained', 'grade', 'last_updated']
    list_filter = ['exam_subject__exam', 'exam_subject__class_group']
    search_fields = ['student__first_name', 'student__last_name']