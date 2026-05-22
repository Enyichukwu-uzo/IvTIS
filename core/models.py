from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from config import settings

# Create your models here.
# core/models.py


class NewsArticle(models.Model):
    """
    Represents a single news article or blog post for the school website.

    We use a custom model rather than relying on a third-party blog app
    so that we have full control over the fields, appearance, and
    integration with the rest of the site (calendar, class manager, etc.).
    """

    # Status choices — a tuple of (database_value, human_readable_label)
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    # --- Core fields ---
    title = models.CharField(max_length=200)
    """
    The article headline. max_length=200 gives enough room for a meaningful
    title without being unwieldy in card layouts.
    """

    slug = models.SlugField(max_length=250, unique=True, blank=True)
    """
    A URL-friendly version of the title. Example:
        Title:  "Science Fair Winners 2026"
        Slug:   "science-fair-winners-2026"

    unique=True ensures no two articles can have the same slug.
    blank=True means the field is optional on the form — we'll auto-generate it.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_articles'
    )#why not one to one?
    """
    Links each article to a Django User account.
    on_delete=models.SET_NULL: if the author's account is deleted, the article
        remains but the author field becomes NULL (rather than deleting the article).
    related_name='news_articles': allows us to do user.news_articles.all()
        to get all articles written by a specific user.
    """

    image = models.ImageField(
        upload_to='news/images/%Y/%m/',
        blank=True,
        null=True
    )
    """
    Optional featured image for the article.
    upload_to='news/images/%Y/%m/' organises files by year and month,
        so the media folder doesn't become a single giant directory.
    Example path: media/news/images/2026/05/science-fair.jpg
    """

    summary = models.TextField(max_length=500)
    """
    A short preview shown on cards and the homepage.
    max_length=500 gives enough space for 3-4 sentences.
    """

    body = models.TextField()
    """
    The full article content. Using TextField (not CharField) because
    articles can be long. We'll add a rich text editor later if needed.
    """

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    """
    Controls visibility. Only articles with status='published' will appear
    on the public website. Draft articles are only visible in the admin.
    """

    published_at = models.DateTimeField(default=timezone.now)
    """
    The date/time the article was (or will be) published.
    default=timezone.now sets it to the current time when first created,
    but staff can set a future date to schedule posts.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    """
    Set automatically when the article is first created. Never changes.
    Useful for audit trails and sorting by creation order.
    """

    updated_at = models.DateTimeField(auto_now=True)
    """
    Updates automatically every time the article is saved.
    Useful for showing "last updated" information.
    """

    class Meta:
        """
        Meta options control model-level behaviour, not field-level.
        """
        ordering = ['-published_at']
        """
        Orders articles by published_at descending (newest first) by default.
        The minus sign means descending order.
        """
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'

    def save(self, *args, **kwargs):
        """
        Override the save() method to auto-generate the slug from the title.
        This runs every time the article is saved, including updates.
        """
        if not self.slug:
            # Only generate a slug if one doesn't already exist.
            # This prevents the slug from changing every time the title is edited.
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        """
        super() calls the parent class's save() method.
        This is essential — without it, the article wouldn't actually be saved.
        """

    def __str__(self):
        """
        String representation of the object.
        This is what appears in the admin list view and in shell queries.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the canonical URL for this article.
        Used in admin ("View on site" link) and in templates.
        We'll create this URL pattern later.
        """
        return reverse('core:news_detail', args=[self.slug])#What is the role of self.slug?
    
# core/models.py — add this below the NewsArticle class


class Event(models.Model):
    """
    Represents a school event: open days, parent conferences, sports day,
    exam periods, holidays, etc.

    Events appear on:
        - Homepage sidebar (upcoming, limited to 5)
        - News & Events page (full calendar + list view)
        - Academic calendar downloads (future feature)
    """

    # Event type choices — helps with filtering and colour-coding
    CATEGORY_ACADEMIC = 'academic'
    CATEGORY_SPORTS = 'sports'
    CATEGORY_ARTS = 'arts'
    CATEGORY_ADMISSIONS = 'admissions'
    CATEGORY_PARENT = 'parent'
    CATEGORY_HOLIDAY = 'holiday'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_ACADEMIC, 'Academic'),
        (CATEGORY_SPORTS, 'Sports & Activities'),
        (CATEGORY_ARTS, 'Arts & Culture'),
        (CATEGORY_ADMISSIONS, 'Admissions & Open Days'),
        (CATEGORY_PARENT, 'Parent Events'),
        (CATEGORY_HOLIDAY, 'Holidays & Closures'),
        (CATEGORY_OTHER, 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_OTHER
    )
    description = models.TextField(blank=True)
    """
    Optional longer description. For simple events like "Bank Holiday",
    the title alone may be sufficient.
    """

    location = models.CharField(max_length=300, blank=True)
    """
    E.g., "Main Hall", "Sports Field", "Online (Zoom)", or blank for
    whole-school events.
    """

    start_date = models.DateField()
    """
    The date the event begins. For single-day events, this is the only date.
    """

    end_date = models.DateField(blank=True, null=True)
    """
    Optional end date for multi-day events (e.g., "Exam Week: 12-16 May").
    If null, the event is treated as a single-day event.
    """

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    """
    Optional time range. If null, the event is treated as "all day".
    Example display: "9:00 AM – 11:30 AM" or "All Day".
    """

    is_published = models.BooleanField(default=False)
    """
    Simple boolean for visibility control. We use a boolean rather than
    a status field because events don't need the complexity of draft/published.
    Either it's visible or it's not.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'start_time']
        """
        Orders by date first, then by time within the same date.
        This way morning events appear before afternoon events.
        """
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.start_date:%d %b %Y})"
        """
        Example output: "Open Morning (05 May 2026)"
        """

    @property
    def is_multiday(self):
        """
        Returns True if the event spans multiple days.
        The @property decorator means we can call event.is_multiday
        without parentheses — it behaves like an attribute.
        """
        return self.end_date is not None and self.end_date != self.start_date

    @property
    def is_upcoming(self):
        """
        Returns True if the event date is today or in the future.
        Used for filtering the homepage sidebar.
        """
        from django.utils import timezone
        return self.start_date >= timezone.now().date()

    @property
    def date_range_display(self):
        """
        Returns a human-readable date range string.
        Single day:  "5 May 2026"
        Multi-day:   "12–16 May 2026"
        """
        if self.is_multiday:
            return f"{self.start_date:%d}–{self.end_date:%d %b %Y}"
        return f"{self.start_date:%d %b %Y}"

    @property
    def time_display(self):
        """
        Returns a human-readable time string.
        With times:  "9:00 AM – 11:30 AM"
        All day:     "All Day"
        """
        if self.start_time and self.end_time:
            return f"{self.start_time:%I:%M %p} – {self.end_time:%I:%M %p}"
        return "All Day"
    
class ContactMessage(models.Model):
    """
    Stores messages submitted via the public contact form.

    We save enquiries in the database so that:
        - No message is lost (email can fail)
        - Staff can view all enquiries in the admin panel
        - We can add status tracking (new, replied, closed) later
        - The school can analyse enquiry types over time
    """

    # Enquiry type choices — maps to the dropdown on the form
    ENQUIRY_GENERAL = 'general'
    ENQUIRY_ADMISSIONS = 'admissions'
    ENQUIRY_ACADEMICS = 'academics'
    ENQUIRY_PASTORAL = 'pastoral'
    ENQUIRY_ABSENCE = 'absence'
    ENQUIRY_OTHER = 'other'

    ENQUIRY_CHOICES = [
        (ENQUIRY_GENERAL, 'General Enquiry'),
        (ENQUIRY_ADMISSIONS, 'Admissions'),
        (ENQUIRY_ACADEMICS, 'Academics'),
        (ENQUIRY_PASTORAL, 'Pastoral / Wellbeing'),
        (ENQUIRY_ABSENCE, 'Report an Absence'),
        (ENQUIRY_OTHER, 'Other'),
    ]

    # Status choices for internal tracking
    STATUS_NEW = 'new'
    STATUS_READ = 'read'
    STATUS_REPLIED = 'replied'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_READ, 'Read'),
        (STATUS_REPLIED, 'Replied'),
        (STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    enquiry_type = models.CharField(
        max_length=20,
        choices=ENQUIRY_CHOICES,
        default=ENQUIRY_GENERAL
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    """
    auto_now_add=True sets the timestamp once on creation.
    It doesn't change when the record is updated.
    """

    # Staff notes (internal, not visible to the public)
    staff_notes = models.TextField(blank=True)
    """
    Admin staff can add internal notes (e.g., "Called back on 5 May,
    left voicemail. Follow up on 8 May."). This field never appears
    on the public form — it's admin-only.
    """

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.get_enquiry_type_display()})"
    

class ProspectusRequest(models.Model):
    """
    Records requests for the school prospectus (digital or printed).

    Separate from ContactMessage because:
        - We can track conversion: prospectus request → application
        - Simpler fields tailored to the admissions enquiry
        - Can trigger automated email with PDF prospectus link
    """

    # Age group choices
    AGE_EARLY_YEARS = 'early_years'
    AGE_PRIMARY = 'primary'
    AGE_MIDDLE = 'middle'
    AGE_SENIOR = 'senior'

    AGE_CHOICES = [
        (AGE_EARLY_YEARS, 'Early Years (Ages 3–5)'),
        (AGE_PRIMARY, 'Primary (Ages 5–11)'),
        (AGE_MIDDLE, 'Middle School (Ages 11–14)'),
        (AGE_SENIOR, 'Senior School (Ages 14–18)'),
    ]

    parent_name = models.CharField(max_length=150)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=20, blank=True)
    child_name = models.CharField(max_length=150)
    child_age_group = models.CharField(
        max_length=20,
        choices=AGE_CHOICES,
    )
    message = models.TextField(blank=True, help_text="Any specific questions or interests.")
    requested_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)
    """
    Staff can toggle this in admin after sending the prospectus.
    Acts as a simple CRM tick.
    """

    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Prospectus Request'
        verbose_name_plural = 'Prospectus Requests'

    def __str__(self):
        return f"{self.parent_name} – Prospectus for {self.child_name} ({self.get_child_age_group_display()})"


class Application(models.Model):
    """
    A formal application for admission.

    This model represents the online "Apply Now" form.
    It stores all information needed for the admissions team to begin
    the enrolment process. Supporting documents are uploaded as files.
    """

    # Status pipeline
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_INTERVIEW = 'interview'
    STATUS_OFFERED = 'offered'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_WITHDRAWN = 'withdrawn'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_INTERVIEW, 'Interview Scheduled'),
        (STATUS_OFFERED, 'Offer Made'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    # Year of entry choices (simplified; could be dynamic)
    # current_year = timezone.now().year
    #
    # YEAR_CHOICES = [
    #     (
    #         f"{year}/{year+1}",
    #         f"{year}/{year+1} Academic Year"
    #     )
    #     for year in range(current_year, current_year + 5)
    # ]
    YEAR_CHOICES = [
        ('2026/2027', '2026/2027 Academic Year'),
        ('2027/2028', '2027/2028 Academic Year'),
    ]

    # Student details
    student_first_name = models.CharField(max_length=100)
    student_last_name = models.CharField(max_length=100)
    student_date_of_birth = models.DateField()
    student_gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'), ('female', 'Female'), ('other', 'Prefer not to say')],
        default='other'
    )
    proposed_entry_year = models.CharField(max_length=10, choices=YEAR_CHOICES)
    current_school = models.CharField(max_length=200, blank=True)
    current_grade = models.CharField(max_length=50, blank=True,
        help_text="E.g., Year 4, Grade 3, etc.")

    # Parent/Guardian details (primary contact)
    parent_name = models.CharField(max_length=150)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=20)
    parent_address = models.TextField(blank=True)

    # How they heard about us
    HOW_HEARD_CHOICES = [
        ('website', 'School Website'),
        ('social_media', 'Social Media'),
        ('referral', 'Friend/Family Referral'),
        ('event', 'Open Day/Event'),
        ('advert', 'Advertisement'),
        ('other', 'Other'),
    ]
    how_heard = models.CharField(max_length=20, choices=HOW_HEARD_CHOICES, blank=True)

    # Supporting documents
    birth_certificate = models.FileField(
        upload_to='applications/birth_certificates/%Y/%m/',
        blank=True, null=True,
        help_text="Upload a scan or photo of the student's birth certificate or passport."
    )
    last_report_card = models.FileField(
        upload_to='applications/report_cards/%Y/%m/',
        blank=True, null=True,
        help_text="Upload the most recent school report (if applicable)."
    )
    additional_document = models.FileField(
        upload_to='applications/additional/%Y/%m/',
        blank=True, null=True,
        help_text="Any additional document (e.g., recommendation letter)."
    )

    # Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    staff_notes = models.TextField(blank=True)
     # NEW: Link to user account
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications'
    )
    # NEW: Offer and response fields
    offer_date = models.DateField(null=True, blank=True)
    offer_response = models.CharField(
        max_length=10,
        choices=[('accept', 'Accept'), ('decline', 'Decline')],
        null=True,
        blank=True
    )
    offer_response_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f"Application: {self.student_first_name} {self.student_last_name} ({self.proposed_entry_year})"

    @property
    def student_full_name(self):
        return f"{self.student_first_name} {self.student_last_name}"
    
# core/models.py – add after the Application model, before any final class

class Subject(models.Model):
    """A subject offered at the school (e.g., Mathematics, English, Physics)."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code e.g. MATH, ENG")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class ClassGroup(models.Model):
    """A class/year group, e.g. Year 5, Primary 3, Early Years A."""
    name = models.CharField(max_length=100, unique=True, help_text="e.g. Year 5, Primary 2B")
    academic_year = models.CharField(max_length=20, default="2026/2027")
    # subjects will be managed through a through table
    subjects = models.ManyToManyField(Subject, through='ClassRelationship')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
    
class TeacherProfile(models.Model):
    """
    Extended profile for staff members.
    Links to the custom User model (role='staff').
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'staff'},
        related_name='teacher_profile'
    )
    title = models.CharField(max_length=10, blank=True, help_text="e.g. Mr, Mrs, Dr")
    
    class_taught = models.OneToOneField(
        ClassGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher'
    )
    employee_id = models.CharField(max_length=20, unique=True)
    hire_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} {self.user.get_full_name()}" if self.title else self.user.get_full_name()

    def display_name(self):
        return f"{self.title} {self.user.last_name}" if self.title else self.user.get_full_name()




class Student(models.Model):
    """
    A student enrolled at the school.
    Initially populated from accepted applications (or manually).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile',
        limit_choices_to={'role': 'student'},
        help_text="Link to a user account for the student portal (optional)"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    admission_number = models.CharField(max_length=20, unique=True)
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"

    def display_name(self):
        # Public display: first name + last initial for privacy
        return f"{self.first_name} {self.last_name[0]}." if self.last_name else self.first_name
class ClassRelationship(models.Model):
    """Intermediate table linking a class to a subject with an optional teacher."""
    name_of_class = models.CharField(max_length=100, blank=True, help_text="Optional custom name for this class (e.g. 'Year 5')")
    academic_year = models.CharField(max_length=20, default="2026/2027")
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name='class_relationships'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects_taught'
    )

    class Meta:
        unique_together = ('class_group', 'subject')  # each subject once per class

    def __str__(self):
        return f"{self.class_group.name} - {self.subject.name}"

    def display_teacher_name(self):
        return self.teacher.display_name() if self.teacher else "Not assigned"
class SchoolDocument(models.Model):
    """Uploadable documents for parents: policies, menus, uniform lists, etc."""
    DOC_TYPES = [
        ('policy', 'Policy'),
        ('menu', 'Lunch Menu'),
        ('uniform', 'Uniform List'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOC_TYPES, default='other')
    file = models.FileField(upload_to='documents/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title