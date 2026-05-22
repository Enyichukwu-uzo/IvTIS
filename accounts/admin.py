from django.contrib import admin

# Register your models here.
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from core.models import TeacherProfile, Student  # import your existing models

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    # Only show if user role is staff (handled in get_inlines)

class StudentProfileInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('role',)
    list_filter = UserAdmin.list_filter + ('role',)
    
    # Add role field to the edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    # add to the class
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True, is_active=True)
        self.message_user(request, f"{queryset.count()} staff accounts approved.")
    approve_users.short_description = "Approve selected staff accounts"

    def get_inlines(self, request, obj=None):
        if obj and obj.role == User.Role.STAFF:
            return [TeacherProfileInline]
        elif obj and obj.role == User.Role.STUDENT:
            return [StudentProfileInline]
        return []

admin.site.register(User, CustomUserAdmin)