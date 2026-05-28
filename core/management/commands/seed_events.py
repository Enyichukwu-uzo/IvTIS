from datetime import date, time
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import Event  # ⚠️ Replace 'your_app_name' with your actual app name


class Command(BaseCommand):
    help = "Seeds the database with 7 diverse school events for testing."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seeding for Events..."))

        # 1. Define 7 mock events matching the Category Choices
        events_data = [
            {
                "title": "Autumn Term Open Morning",
                "category": Event.CATEGORY_ADMISSIONS,
                "description": "Welcome session for prospective families. Includes a tour of the campus and a Q&A with the Headteacher.",
                "location": "Main Hall & Campus",
                "start_date": date(2026, 9, 12),
                "start_time": time(9, 0),
                "end_time": time(12, 30),
                "is_published": True,
            },
            {
                "title": "Annual Sports Day",
                "category": Event.CATEGORY_SPORTS,
                "description": "Inter-house track and field competitions. Parents are highly encouraged to attend and cheer!",
                "location": "Sports Field",
                "start_date": date(2026, 6, 18),
                "start_time": time(10, 0),
                "end_time": time(16, 0),
                "is_published": True,
            },
            {
                "title": "Year 11 Parents Evening",
                "category": Event.CATEGORY_PARENT,
                "description": "One-on-one consultations regarding mock exam results and graduation pathways.",
                "location": "Online (Zoom)",
                "start_date": date(2026, 11, 5),
                "start_time": time(16, 30),
                "end_time": time(20, 0),
                "is_published": True,
            },
            {
                "title": "Half-Term Break",
                "category": Event.CATEGORY_HOLIDAY,
                "description": "School closed for the autumn half-term holiday.",
                "location": "",
                "start_date": date(2026, 10, 26),
                "end_date": date(2026, 10, 30),
                "start_time": None,  # All day event
                "end_time": None,
                "is_published": True,
            },
            {
                "title": "Summer Art & Music Showcase",
                "category": Event.CATEGORY_ARTS,
                "description": "An evening celebrating student gallery displays and live orchestral performances.",
                "location": "Arts Centre Theater",
                "start_date": date(2026, 7, 2),
                "start_time": time(18, 0),
                "end_time": time(21, 0),
                "is_published": True,
            },
            {
                "title": "GCSE Final Exam Period",
                "category": Event.CATEGORY_ACADEMIC,
                "description": "Main exam hall is strictly off-limits to non-exam students. Good luck to all cohorts!",
                "location": "Main Examination Hall",
                "start_date": date(2026, 5, 11),
                "end_date": date(2026, 5, 22),
                "start_time": None,
                "end_time": None,
                "is_published": True,
            },
            {
                "title": "Staff Professional Development Day",
                "category": Event.CATEGORY_OTHER,
                "description": "In-service training day for faculty. No school for students.",
                "location": "Staff Lounge",
                "start_date": date(2026, 9, 1),
                "start_time": time(8, 30),
                "end_time": time(15, 30),
                "is_published": False,  # Draft status example
            },
        ]

        # 2. Iterate and create records
        created_count = 0
        for data in events_data:
            # Using update_or_create preventing duplicate records if you run this multiple times
            # It uses unique slug generation based on the title
            generated_slug = slugify(data["title"])
            
            obj, created = Event.objects.update_or_create(
                slug=generated_slug,
                defaults=data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f" Successfully created event: '{obj.title}'")
            else:
                self.stdout.write(self.style.NOTICE(f" Updated existing event: '{obj.title}'"))

        # 3. Success feedback message
        self.stdout.write(
            self.style.SUCCESS(f"\nSeeding complete! Added {created_count} new events.")
        )