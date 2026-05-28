# core/views.py — add at the top if not already present:
from django.db.models import Count, Prefetch
from .models import ClassGroup, ClassRelationship, Student, TeacherProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import NewsArticle, Event, ContactMessage, ProspectusRequest, Application
from .forms import ContactForm, ProspectusRequestForm, ApplicationForm
from django.contrib import messages
from django.urls import reverse  # Django's flash message framework
from .forms import ContactForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import NewsArticle, Event
from django.core.mail import send_mail
from django.conf import settings
from exams.models import ExamResult

# Create your views here.



def home(request):
    """
    Homepage view. Fetches published news articles and passes
    them to the template along with static stats data.
    """

    # Fetch only published articles, newest first, limit to 6
    latest_news = NewsArticle.objects.filter(
        status=NewsArticle.STATUS_PUBLISHED
    ).order_by('-published_at')[:6]
    """
    .filter(status='published')  → only show articles marked as published
    .order_by('-published_at')   → newest first (the minus means descending)
    [:6]                          → limit to 6 articles (Django translates
                                     this to SQL LIMIT 6 for efficiency)
    """
    # Upcoming 5 published events, soonest first
    upcoming_events = Event.objects.filter(
        is_published=True,
        start_date__gte=timezone.now().date()
    ).order_by('start_date', 'start_time')[:5]
    """
    start_date__gte=timezone.now().date()
    __gte means "greater than or equal to".
    This filters for events whose start_date is today or later.
    We use timezone.now().date() so we're comparing date-to-date,
    not datetime-to-date, which would exclude today's events.
    """


    context = {
        'stats': [
            {'number': '1:8', 'label': 'Student-Teacher Ratio'},
            {'number': '98%', 'label': 'Exam Pass Rate (A*-C)'},
            {'number': '25+', 'label': 'Years Established'},
            {'number': '40+', 'label': 'Clubs & Activities'},
        ],
        'news': latest_news,     # Now populated from the database
        'events': upcoming_events,
    }
    return render(request, 'core/home.html', context)


# about view remains unchanged...


def about(request):
    """
    About Us page view.
    Currently static content; later leadership team could come from a model.
    """
    context = {
        'leadership': [
            {
                'name': 'Dr. Amina Okafor',
                'title': 'Head of School',
                'bio': 'Dr. Okafor has over 20 years of experience in international education...',
                'image': 'images/leadership/dr_amina_okafor.jpeg',  # relative to static/
            },
            {
                'name': 'Mr. James Adeyemi',
                'title': 'Deputy Head (Academics)',
                'bio': 'James leads curriculum development and teacher professional growth...',
                'image': 'images/leadership/mr_james_adeyemi.png',
            },
            {
                'name': 'Mrs. Chioma Eze',
                'title': 'Deputy Head (Pastoral)',
                'bio': 'Chioma oversees student wellbeing, safeguarding, and the house system...',
                'image': 'images/leadership/mrs_chioma_eze.png',
            },
            {
                'name': 'Mr. David Bello',
                'title': 'Head of Admissions & Communications',
                'bio': 'David ensures every family experiences a warm, informative admissions journey...',

                'image': 'images/leadership/mr_david_bello.png',
            },
        ],
        'values': [
            {'title': 'Excellence', 'description': 'We pursue the highest standards in teaching, learning, and personal conduct.', 'icon': 'bi-star-fill'},
            {'title': 'Integrity', 'description': 'We foster honesty, responsibility, and ethical decision-making in all we do.', 'icon': 'bi-shield-check'},
            {'title': 'Curiosity', 'description': 'We ignite a lifelong love of learning through inquiry and exploration.', 'icon': 'bi-lightbulb-fill'},
            {'title': 'Community', 'description': 'We celebrate diversity and nurture strong, supportive relationships.', 'icon': 'bi-people-fill'},
        ],
        'milestones': [
            {'year': '2001', 'event': 'School founded with 45 students'},
            {'year': '2008', 'event': 'First graduating class'},
            {'year': '2012', 'event': 'Opened new science wing'},
            {'year': '2018', 'event': 'Achieved international accreditation'},
            {'year': '2023', 'event': 'Launched scholarship programme'},
            {'year': '2026', 'event': 'New performing arts centre opens'},
        ],
    }
    return render(request, 'core/about.html', context)
# core/views.py — add this function


# ... existing home and about views ...

def news_detail(request, slug):
    """
    Displays a single news article by its slug.
    get_object_or_404 returns the article or raises a 404 page
    if no published article with that slug exists.
    """
    article = get_object_or_404(
        NewsArticle,
        slug=slug,
        status=NewsArticle.STATUS_PUBLISHED
    )
    """
    We filter by both slug AND status=published.
    This prevents anyone from viewing draft articles by guessing the slug.
    """
    return render(request, 'core/news_detail.html', {'article': article})
# core/views.py — add this function

def news_events(request):
    """
    Combined News & Events page with two tabs:
        Tab 1: All news articles (paginated later)
        Tab 2: Events calendar (list view + calendar placeholder)
    """
    # All published news articles, newest first
    all_news = NewsArticle.objects.filter(
        status=NewsArticle.STATUS_PUBLISHED
    ).order_by('-published_at')

    # All published upcoming events, soonest first
    all_events = Event.objects.filter(
        is_published=True,
        start_date__gte=timezone.now().date()
    ).order_by('start_date', 'start_time')

    # We also fetch past events (for the "Past Events" section potential)
    past_events = Event.objects.filter(
        is_published=True,
        start_date__lt=timezone.now().date()
    ).order_by('-start_date')[:10]

    context = {
        'all_news': all_news,
        'all_events': all_events,
        'past_events': past_events,
    }
    return render(request, 'core/news_events_page.html', context)
# core/views.py — add these imports at the top if not already present


def contact(request):
    """
    Contact page view.

    Handles both:
        GET  → displays the empty form
        POST → validates and saves the form, shows success message

    Uses Django's messages framework to show a one-time success banner
    after form submission. The messages are stored in the session and
    displayed on the next rendered page (or the same page after redirect).
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            contact_message = form.save()
            """
            form.save() creates the ContactMessage record.
            We could also send an email notification here using
            Django's send_mail() — we'll add that later.
            """

            # Flash a success message to the user
            messages.success(
                request,
                'Thank you for your message. We will get back to you shortly.'
            )

            # Redirect to the same page to prevent form re-submission
            # (the Post/Redirect/Get pattern)
            return redirect('core:contact')
            """
            Redirecting after POST is important:
            - Prevents "Confirm form resubmission" browser warnings
            - Clears the form fields
            - Ensures the success message appears on the fresh GET request
            """
        else:
            messages.error(
                request,
                'There were errors in the form. Please correct them and try again.'
            )
            return redirect(f"{reverse('core:contact')}#form")
    else:
        form = ContactForm()
        """
        On GET requests, instantiate an empty form.
        We don't pass any data, so all fields are blank.
        """

    context = {
        'form': form,
        # Contact details can be pulled from a SiteSettings model later.
        # For now, we hardcode them in the template or pass them here.
    }
    return render(request, 'core/contact.html', context)


def admissions_overview(request):
    """
    Admissions landing page showing the process, fees, and links to the forms.
    No forms on this page — just marketing content and CTAs.
    """
    return render(request, 'core/admissions_overview.html')


def admissions_prospectus(request):
    """
    Dedicated prospectus request page.
    Same look as admissions, but only the prospectus form.
    """
    form = ProspectusRequestForm()
    if request.method == 'POST':
        form = ProspectusRequestForm(request.POST)
        if form.is_valid():
            prospectus = form.save()
            messages.success(
                request,
                'Thank you! Your prospectus request has been received. '
                'We will email you shortly with a link to download the prospectus.'
            )
            send_mail(
                'Prospectus Request Received',
                f"Dear {prospectus.parent_name},\n\nThank you for requesting a prospectus for {prospectus.child_name}. "
                f"We will email you the PDF shortly.\n\nBest regards,\nIvory Tower Admissions",
                settings.DEFAULT_FROM_EMAIL,
                [prospectus.parent_email],
                fail_silently=True,
            )
            return redirect('core:admissions_prospectus')
    return render(request, 'core/admissions_prospectus.html', {'form': form})


def admissions_apply(request):
    """
    Dedicated application page.
    Same look as admissions, but only the application form.
    """
    form = ApplicationForm()
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            if request.user.is_authenticated:
                application.user = request.user
            application.save()
            messages.success(
                request,
                'Your application has been submitted successfully. '
                'Our admissions team will contact you within 5 working days.'
            )
            send_mail(
                'Application Received',
                f"Dear {application.parent_name},\n\nYour application for {application.student_full_name} "
                f"has been received. Our admissions team will contact you within 5 working days.\n\n"
                f"Regards,\nIvory Tower",
                settings.DEFAULT_FROM_EMAIL,
                [application.parent_email],
                fail_silently=True,
            )
            send_mail(
                'New Application Submitted',
                f"A new application has been submitted for {application.student_full_name}.",
                settings.DEFAULT_FROM_EMAIL,
                ['admissions@ivorytower.edu.ng'],
                fail_silently=True,
            )
            if not request.user.is_authenticated:
                messages.info(
                    request,
                    'To track your application, please <a href="%s">create an account</a>.' % reverse('accounts:register')
                )
            return redirect('core:admissions_apply')
    return render(request, 'core/admissions_apply.html', {'form': form})

from django.db.models import Prefetch
from .models import ClassGroup, Student

def academics(request):
    classes = ClassGroup.objects.select_related(
        'class_teacher__user',
    ).prefetch_related(
        Prefetch(
            'class_relationships',
            queryset=ClassRelationship.objects.select_related('subject', 'teacher__user')
        ),
        Prefetch(
            'students',
            queryset=Student.objects.filter(is_active=True).order_by('last_name', 'first_name')
        ),
    ).annotate(
        student_count=Count('students', distinct=True),
    )
    
    return render(request, 'core/academics.html', {'classes': classes})

from .models import SchoolDocument

def parent_hub(request):
    documents = {
        'policies': SchoolDocument.objects.filter(document_type='policy'),
        'menus': SchoolDocument.objects.filter(document_type='menu'),
        'uniforms': SchoolDocument.objects.filter(document_type='uniform'),
    }
    
    # Fetch children with results for logged-in parent
    children = None
    if request.user.is_authenticated and request.user.role == 'parent':
        children = Student.objects.filter(
            guardians__guardian=request.user
        ).prefetch_related(
            Prefetch(
                'exam_results',
                queryset=ExamResult.objects.select_related(
                    'exam_subject__exam',
                    'exam_subject__subject'
                ).order_by('-exam_subject__exam__start_date')
            )
        ).distinct()
    
    return render(request, 'core/parent_hub.html', {
        'documents': documents,
        'children': children,
    })
def pastoral(request):
    # Static content; houses could be a model later
    houses = [
        {'name': 'Sapphire', 'colour': 'Blue', 'motto': 'Strength and Wisdom'},
        {'name': 'Ruby', 'colour': 'Red', 'motto': 'Courage and Passion'},
        {'name': 'Emerald', 'colour': 'Green', 'motto': 'Growth and Harmony'},
        {'name': 'Topaz', 'colour': 'Gold', 'motto': 'Excellence and Integrity'},
    ]
    return render(request, 'core/pastoral.html', {'houses': houses})

# core/views.py — add this function

def class_detail_public(request, class_id):
    """
    Public view of a single class: shows teacher, subjects, and student list.
    """
    class_group = get_object_or_404(
        ClassGroup.objects.select_related('class_teacher__user').prefetch_related(
            Prefetch(
                'class_relationships',
                queryset=ClassRelationship.objects.select_related('subject', 'teacher__user')
            ),
            Prefetch(
                'students',
                queryset=Student.objects.filter(is_active=True).order_by('last_name', 'first_name')
            ),
        ),
        pk=class_id
    )
    
    return render(request, 'core/class_detail_public.html', {
        'class_group': class_group,
    })