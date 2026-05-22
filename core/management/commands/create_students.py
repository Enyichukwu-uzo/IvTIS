# core/management/commands/create_students.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import ClassGroup, Student
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    """
    Custom Django management command to generate 10 students 
    for every existing ClassGroup in the database.

    Run with:
        python manage.py create_students
    """

    help = "Populate each class group with 10 dynamically named, age-appropriate students."

    def handle(self, *args, **kwargs):
        # Retrieve all configured class groups from the database
        class_groups = ClassGroup.objects.all()

        if not class_groups.exists():
            self.stdout.write(
                self.style.ERROR("❌ No Class Groups found! Run 'create_class_groups' first.")
            )
            return

        # =========================================================
        # SEED NAME POOLS
        # ---------------------------------------------------------
        # Pools of diverse first and last names. We mix these up
        # algorithmically using the loop indexes to create 220 unique,
        # non-repetitive combinations without hardcoding 220 entries.
        # =========================================================
        first_names = [
            "Chidi", "Blessing", "Amina", "John", "Sarah", "David", "Emeka", "Fatima", 
            "Grace", "Tunde", "Chioma", "Musa", "Daniel", "Joy", "Samuel", "Aisha",
            "Tari", "Kelechi", "Yusuf", "Elizabeth"
        ]
        
        last_names = [
            "Okeke", "Abubakar", "Balogun", "Smith", "Obi", "Adeleke", "Nwachukwu", 
            "Ibrahim", "Williams", "Okon", "Bello", "Eze", "Johnson", "Aliyu", 
            "Umar", "Okafor", "Danjuma", "Sanni", "Mensah", "Adebayo"
        ]

        # Use an atomic transaction block so everything rolls back cleanly if an error occurs
        with transaction.atomic():
            
            # Track total insertions across the system
            total_students_created = 0

            # Enumerate through classes to get an index for structural uniqueness strings
            for class_idx, class_group in enumerate(class_groups, start=1):
                self.stdout.write(self.style.MIGRATE_LABEL(f"\nSeeding students for: {class_group.name}"))

                # -------------------------------------------------
                # DETERMINISTIC AGE LOGIC
                # -------------------------------------------------
                # To prevent generating an SS3 student born in 2023, we infer a realistic 
                # age target based on keyword tokens found inside the class name.
                # -------------------------------------------------
                class_name = class_group.name
                if "Nursery 1" in class_name:   base_age = 3
                elif "Nursery 2" in class_name: base_age = 4
                elif "Kindergarten" in class_name: base_age = 5
                elif "Primary 1" in class_name: base_age = 6
                elif "Primary 2" in class_name: base_age = 7
                elif "Primary 3" in class_name: base_age = 8
                elif "Primary 4" in class_name: base_age = 9
                elif "Primary 5" in class_name: base_age = 10
                elif "Primary 6" in class_name: base_age = 11
                elif "JSS 1" in class_name:base_age = 12
                elif "JSS 2" in class_name:base_age = 13
                elif "JSS 3" in class_name:base_age = 14
                elif "SS 1" in class_name:base_age = 15
                elif "SS 2" in class_name:base_age = 16
                elif "SS 3" in class_name:base_age = 17
                else:base_age = 10  # Standard fallback default
                
                birth_year = 2026 - base_age

                # -------------------------------------------------
                # GENERATE 10 STUDENTS FOR THIS CLASS
                # -------------------------------------------------
                for student_idx in range(1, 11):
                    
                    # Mathematical offsets map varying pairs out of our array matrices
                    f_name = first_names[(student_idx + class_idx) % len(first_names)]
                    l_name = last_names[(student_idx * class_idx) % len(last_names)]
                    
                    # 1. Structural Unique Identity Generation
                    # Combines class index and student number to form deterministic, non-clashing usernames & ID codes
                    unique_slug = f"{class_idx:02d}{student_idx:02d}"
                    username = f"std_{f_name.lower()}_{unique_slug}"
                    admission_num = f"ADM/2026/{unique_slug}"
                    
                    # 2. Setup/Fetch Base User Account
                    # Enforces the specific constraints: role='student'
                    user, user_created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            "email": f"{username}@schoolportal.com",
                            "first_name": f_name,
                            "last_name": l_name,
                            "role": "student"
                        }
                    )
                    
                    if user_created:
                        user.set_password("StudentPassword123")
                        user.save()

                    # 3. Setup/Fetch Student Profile Instance
                    # Ties back to the User and target ClassGroup
                    student, student_created = Student.objects.get_or_create(
                        admission_number=admission_num,
                        defaults={
                            "user": user,
                            "first_name": f_name,
                            "last_name": l_name,
                            "date_of_birth": date(birth_year, 5, student_idx), # Stagger days slightly
                            "class_group": class_group
                        }
                    )

                    if student_created:
                        total_students_created += 1
                        
                self.stdout.write(f"  ✔ Successfully processed 10 students for {class_group.name}.")

        # =========================================================
        # SYSTEM SUMMARY FINALIZATION MESSAGE
        # =========================================================
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Enrollment batch execution complete. Created/Verified {total_students_created} students total."
            )
        )