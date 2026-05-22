from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# accounts/models.py

class User(AbstractUser):
    """
    Custom User model for all account types (parents, staff, students, etc.).
    Extends Django's AbstractUser to add a 'role' field for future differentiation.
    """
    class Role(models.TextChoices):
        PARENT = 'parent', 'Parent/Guardian'
        STAFF = 'staff', 'Staff'
        STUDENT = 'student', 'Student'
        EXAMS_OFFICER = 'exams_officer', 'Examinations Officer'
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARENT,
        help_text="Designates the type of user account."
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    is_approved = models.BooleanField(
    default=False,
    help_text="Designates whether this staff/student account has been approved by admin."
   )

    def is_parent(self):
        return self.role == self.Role.PARENT

    def is_staff_user(self):
        # Note: is_staff is for admin access, this is for school staff
        return self.role == self.Role.STAFF
    def is_exams_officer(self):
        return self.role == self.Role.EXAMS_OFFICER
    def __str__(self):
        return self.get_full_name() or self.username