from .models import Subject, TeacherProfile, ClassGroup, ClassRelationship, Student
from .models import NewsArticle, Event, ContactMessage, ProspectusRequest, Application
from django.contrib import admin


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """
    Customises how NewsArticle appears in the Django admin interface.
    """

    # Columns shown in the list view
    list_display = [
        'title','author','status','published_at','created_at',
    ]
    """
    These fields appear as columns in the admin table.
    Staff can click column headers to sort by that field.
    """

    # Filters shown in the right sidebar
    list_filter = [
        'status', 'published_at', 'author',
    ]
    """
    Allows staff to quickly filter to "only published articles" or
    "articles by a specific author" or "articles from this year".
    """

    # Searchable fields (uses database LIKE query)
    search_fields = [
        'title',
        'summary',
        'body',
    ]
    """
    The search bar at the top of the admin list will look in these fields.
    """

    # Fields that are auto-populated as you type (in the admin form)
    prepopulated_fields = {
        'slug': ('title',)
    }
    """
    When typing a title, the slug field automatically fills with the
    URL-friendly version. Staff can still edit it manually if needed.
    This is an admin-only convenience — our model's save() method
    also handles slug generation as a backup.
    """

    # Organise fields in the add/edit form
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'image', 'summary', 'body'),
            'classes': ('collapse',),
        }),
        ('Publishing', {
            'fields': ('status', 'published_at'),
            'classes': ('collapse',),  # Collapsible section — less clutter
        }),
    )
    """
    fieldsets organise the form into logical groups.
    The 'collapse' class makes the Publishing section collapsible,
    which is useful because those fields are changed less often.
    """

    # Default values for new articles
    def get_changeform_initial_data(self, request):
        """
        Pre-fill the author field with the current logged-in user
        when creating a new article.
        """
        return {
            'author': request.user,
            'status': 'draft',
        }
        
        
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'start_date',
        'end_date',
        'is_published',
    ]
    list_filter = [
        'category',
        'is_published',
        'start_date',
    ]
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    """
    date_hierarchy adds a date-based drilldown navigation at the top
    of the admin list view. Staff can click through year → month → day
    to find events quickly.
    """

    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'slug', 'category', 'description', 'location')
        }),
        ('Date & Time', {
            'fields': (('start_date', 'end_date'), ('start_time', 'end_time')),
        }),
        ('Visibility', {
            'fields': ('is_published',),
        }),
    )
    """
    Grouping related fields with parentheses — ('start_date', 'end_date') —
    puts them on the same row in the admin form, which is logical since
    they are related values.
    """
    # core/admin.py — update the import line at the top


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Customises the admin interface for contact form submissions.

    Features:
        - Colour-coded status indicators
        - Quick filters by type and status
        - Read-only fields to prevent accidental editing of messages
        - Staff notes field for internal communication
    """

    list_display = [
        'name',
        'email',
        'enquiry_type',
        'subject',
        'status_badge',  # Custom method below
        'submitted_at',
    ]
    """
    status_badge is a custom method that returns a coloured HTML badge.
    We'll define it below.
    """

    list_filter = [
        'enquiry_type',
        'status',
        'submitted_at',
    ]

    search_fields = [
        'name',
        'email',
        'subject',
        'message',
    ]

    readonly_fields = [
        'name',
        'email',
        'phone',
        'enquiry_type',
        'subject',
        'message',
        'submitted_at',
    ]
    """
    Read-only fields prevent accidental editing of the original message.
    Staff can only change 'status' and 'staff_notes' — not the message itself.
    """

    fieldsets = (
        ('Message Details', {
            'fields': (
                'name',
                'email',
                'phone',
                'enquiry_type',
                'subject',
                'message',
            ),
            'classes': ('wide',),
        }),
        ('Internal Tracking', {
            'fields': (
                'status',
                'staff_notes',
                'submitted_at',
            ),
        }),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        """
        Returns a coloured HTML badge based on the message status.
        This appears in the admin list view.

        We use format_html() to safely render HTML in the admin.
        Never use mark_safe() on user-supplied data — format_html()
        escapes content automatically.
        """
        from django.utils.html import format_html

        colours = {
            'new': '#0d6efd',      # Blue
            'read': '#6c757d',     # Gray
            'replied': '#198754',  # Green
            'closed': '#dc3545',   # Red
        }
        colour = colours.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:white; padding:2px 8px; '
            'border-radius:10px; font-size:0.8em;">{}</span>',
            colour,
            obj.get_status_display()
        )
    # status_badge.short_description = 'Status'  # Column header in admin
    # core/admin.py — update import


@admin.register(ProspectusRequest)
class ProspectusRequestAdmin(admin.ModelAdmin):
    list_display = ['parent_name', 'parent_email', 'child_name', 'child_age_group', 'requested_at', 'fulfilled']
    list_filter = ['child_age_group', 'fulfilled', 'requested_at']
    search_fields = ['parent_name', 'parent_email', 'child_name']
    actions = ['mark_fulfilled']

    def mark_fulfilled(self, request, queryset):
        queryset.update(fulfilled=True)
    mark_fulfilled.short_description = "Mark selected as fulfilled"


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'student_full_name',
        'parent_name',
        'parent_email',
        'proposed_entry_year',
        'status',
        'submitted_at',
    ]
    list_filter = ['status', 'proposed_entry_year', 'submitted_at']
    search_fields = ['student_first_name', 'student_last_name', 'parent_name', 'parent_email']
    readonly_fields = ['submitted_at', 'updated_at']
    fieldsets = (
        ('Student Information', {
            'fields': (
                ('student_first_name', 'student_last_name'),
                'student_date_of_birth',
                'student_gender',
                'proposed_entry_year',
                'current_school',
                'current_grade',
            )
        }),
        ('Parent/Guardian', {
            'fields': (
                'parent_name',
                'parent_email',
                'parent_phone',
                'parent_address',
                'how_heard',
            )
        }),
        ('Documents', {
            'fields': (
                'birth_certificate',
                'last_report_card',
                'additional_document',
            )
        }),
        ('Application Status', {
            'fields': (
                'status',
                'staff_notes',
                'submitted_at',
                'updated_at',
            )
        }),
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name']

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'hire_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']

class ClassRelationshipInline(admin.TabularInline):
    model = ClassRelationship
    extra = 1

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year']
    inlines = [ClassRelationshipInline]

    def get_queryset(self, request):
        """Teachers only see their own class group."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For staff users, filter by the class they teach
        if hasattr(request.user, 'teacher_profile') and request.user.teacher_profile:
            return qs.filter(id=request.user.teacher_profile.class_taught_id)
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and hasattr(request.user, 'teacher_profile'):
            return obj.id == request.user.teacher_profile.class_taught_id
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            # Allow viewing the list (filtered by get_queryset)
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete class groups
        return request.user.is_superuser
    # You can also add a student inline later

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'admission_number', 'class_group', 'is_active']
    list_filter = ['class_group', 'is_active']
    search_fields = ['first_name', 'last_name', 'admission_number']
from .models import SchoolDocument

@admin.register(SchoolDocument)
class SchoolDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'uploaded_at']
    list_filter = ['document_type']