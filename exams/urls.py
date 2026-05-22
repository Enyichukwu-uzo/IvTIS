# exams/urls.py
from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('staff/', views.exam_list, name='exam_list'),
    path('staff/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('staff/<int:exam_id>/subject/<int:subject_id>/enrol/', views.manage_enrolment, name='manage_enrolment'),
    path('staff/<int:exam_id>/subject/<int:subject_id>/results/', views.result_entry, name='result_entry'),
    path('student/', views.student_results, name='student_results'),
    path('timetable/<int:exam_id>/', views.exam_timetable, name='exam_timetable'),
    # parent results later
]
urlpatterns += [
    path('officer/dashboard/', views.officer_dashboard, name='officer_dashboard'),
    path('officer/exam/create/', views.officer_create_exam, name='officer_create_exam'),
    path('officer/exam/<int:exam_id>/edit/', views.officer_edit_exam, name='officer_edit_exam'),
    path('officer/exam/<int:exam_id>/subjects/', views.officer_manage_subjects, name='officer_manage_subjects'),
    path('officer/exam/<int:exam_id>/subjects/add/', views.officer_add_subject, name='officer_add_subject'),
    path('officer/exam/<int:exam_id>/timetable/', views.officer_manage_timetable, name='officer_manage_timetable'),
    path('teacher/subjects/', views.teacher_exam_subjects, name='teacher_exam_subjects'),
]