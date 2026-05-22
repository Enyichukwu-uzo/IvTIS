# # core/management/commands/create_teachers.py

# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from django.db import transaction
# from core.models import TeacherProfile, ClassGroup, ClassRelationship
# from datetime import date

# User = get_user_model()

# class Command(BaseCommand):
#     """
#     Custom Django management command to generate teacher users,
#     profiles, and assign them to maximum 3 class groups via ClassRelationship.

#     Run with:
#         python manage.py create_teachers
#     """

#     help = "Populate database with teachers and assign them to classes/subjects."

#     def handle(self, *args, **kwargs):
        
#         # =========================================================
#         # TEACHER SEED DATA
#         # ---------------------------------------------------------
#         # We define a structured list of teachers. To stay within your 
#         # rule of "no more than 3 class groups per teacher", we explicitly 
#         # map each teacher to an array of up to 3 class names.
#         # =========================================================
#         teachers_manifest = [
#             {
#                 "username": "jsmith",
#                 "email": "j.smith@school.com",
#                 "first_name": "James",
#                 "last_name": "Smith",
#                 "title": "Mr",
#                 "employee_id": "EMP202601",
#                 "primary_class": "Nursery 1",          # Assigned to class_taught field
#                 "assigned_classes": ["Nursery 1", "Nursery 2", "Kindergarten"] # Max 3 classes
#             },
#             {
#                 "username": "ljones",
#                 "email": "l.jones@school.com",
#                 "first_name": "Linda",
#                 "last_name": "Jones",
#                 "title": "Mrs",
#                 "employee_id": "EMP202602",
#                 "primary_class": "Primary 1",          # Assigned to class_taught field
#                 "assigned_classes": ["Primary 1", "Primary 2", "Primary 3"] # Max 3 classes
#             },
#             {
#                 "username": "dvance",
#                 "email": "d.vance@school.com",
#                 "first_name": "David",
#                 "last_name": "Vance",
#                 "title": "Dr",
#                 "employee_id": "EMP202603",
#                 "primary_class": "Primary 4",          # Assigned to class_taught field
#                 "assigned_classes": ["Primary 4", "Primary 5", "Primary 6"] # Max 3 classes
#             }
#         ]

#         # Using an atomic transaction ensures that if one creation step fails, 
#         # the database rolls back completely to prevent partial/corrupt data setup.
#         with transaction.atomic():
            
#             for data in teachers_manifest:
#                 self.stdout.write(self.style.MIGRATE_LABEL(f"\nProcessing: {data['title']} {data['first_name']} {data['last_name']}"))

#                 # -------------------------------------------------
#                 # STEP 1: CREATE / FETCH THE USER
#                 # -------------------------------------------------
#                 # TeacherProfile depends on a OneToOne relation with User.
#                 # We enforce role='staff' as dictated by your model constraints.
#                 # -------------------------------------------------
#                 user, user_created = User.objects.get_or_create(
#                     username=data["username"],
#                     defaults={
#                         "email": data["email"],
#                         "first_name": data["first_name"],
#                         "last_name": data["last_name"],
#                         "role": "staff"  # Critical for limit_choices_to validation rule
#                     }
#                 )
                
#                 if user_created:
#                     user.set_password("SecurePassword123")
#                     user.save()
#                     self.stdout.write(f"  ✔ User account '{data['username']}' created.")
#                 else:
#                     self.stdout.write(f"  ⚠ User account '{data['username']}' already exists.")

#                 # -------------------------------------------------
#                 # STEP 2: RESOLVE THE PRIMARY FORM CLASS
#                 # -------------------------------------------------
#                 # TeacherProfile has a class_taught field linking to ClassGroup.
#                 # -------------------------------------------------
#                 primary_class_group = ClassGroup.objects.filter(name=data["primary_class"]).first()

#                 # -------------------------------------------------
#                 # STEP 3: CREATE / UPDATE TEACHER PROFILE
#                 # -------------------------------------------------
#                 # We use update_or_create here so if the command runs again,
#                 # it safely modifies changing parameters without throwing uniqueness errors.
#                 # -------------------------------------------------
#                 profile, profile_created = TeacherProfile.objects.update_or_create(
#                     user=user,
#                     defaults={
#                         "title": data["title"],
#                         "employee_id": data["employee_id"],
#                         "class_taught": primary_class_group,
#                         "hire_date": date(2026, 1, 1)
#                     }
#                 )
                
#                 status_msg = "created" if profile_created else "updated"
#                 self.stdout.write(self.style.SUCCESS(f"  ✔ Teacher Profile {status_msg} (ID: {profile.employee_id})."))

#                 # -------------------------------------------------
#                 # STEP 4: ASSIGN TEACHER TO CLASS-SUBJECTS
#                 # -------------------------------------------------
#                 # Here we find the custom intermediate 'through' tables rows.
#                 # We find all ClassRelationship rows belonging to the assigned classes 
#                 # list (max 3) and update their optional 'teacher' field.
#                 # -------------------------------------------------
#                 target_classes = ClassGroup.objects.filter(name__in=data["assigned_classes"])
                
#                 # Fetching the ClassRelationship link entries matching these specific classes
#                 class_subjects_to_update = ClassRelationship.objects.filter(class_group__in=target_classes)
                
#                 if class_subjects_to_update.exists():
#                     # Mass updates all matching rows efficiently in a single query
#                     updated_count = class_subjects_to_update.update(teacher=profile)
                    
#                     self.stdout.write(
#                         f"  🔗 Assigned as subject teacher to {updated_count} subjects across "
#                         f"these classes: {', '.join(data['assigned_classes'])}"
#                     )
#                 else:
#                     self.stdout.write(
#                         self.style.WARNING(
#                             f"  ⚠ No ClassRelationship records found for {data['assigned_classes']}. "
#                             "Make sure to run your class groups management command first!"
#                         )
#                     )

#         self.stdout.write(
#             self.style.SUCCESS("\n👩‍🏫 Teacher initialization and mapping complete.")
#         )

# core/management/commands/create_teachers.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import TeacherProfile, ClassGroup, ClassRelationship
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    """
    Custom Django management command to generate teacher users,
    profiles, and assign them to maximum 3 class groups via ClassRelationship.

    Run with:
        python manage.py create_teachers
    """

    help = "Populate database with a large roster of 15 teachers mapped across 22 classes."

    def handle(self, *args, **kwargs):
        
        # =========================================================
        # ROBUST TEACHER SEED DATA (15 Teachers Manifest)
        # ---------------------------------------------------------
        # Spanning Early Years, Primary Arms, JSS Arms, and SS Tracks.
        # Enforces the constraint: "No more than 3 assigned classes per teacher".
        # =========================================================
        teachers_manifest = [
            # --- Early Years Tier ---
            {
                "username": "abrown",
                "email": "a.brown@school.com",
                "first_name": "Alice",
                "last_name": "Brown",
                "title": "Mrs",
                "employee_id": "EMP202601",
                "primary_class": "Nursery 1",
                "assigned_classes": ["Nursery 1", "Nursery 2"]
            },
            {
                "username": "cgreen",
                "email": "c.green@school.com",
                "first_name": "Charles",
                "last_name": "Green",
                "title": "Mr",
                "employee_id": "EMP202602",
                "primary_class": "Kindergarten",
                "assigned_classes": ["Kindergarten"]
            },
            
            # --- Lower Primary Tier (Arms A & B) ---
            {
                "username": "mwhite",
                "email": "m.white@school.com",
                "first_name": "Mary",
                "last_name": "White",
                "title": "Miss",
                "employee_id": "EMP202603",
                "primary_class": "Primary 1A",
                "assigned_classes": ["Primary 1A", "Primary 1B"]
            },
            {
                "username": "rblack",
                "email": "r.black@school.com",
                "first_name": "Robert",
                "last_name": "Black",
                "title": "Mr",
                "employee_id": "EMP202604",
                "primary_class": "Primary 1B",
                "assigned_classes": ["Primary 1B", "Primary 2A"]
            },
            {
                "username": "sgrey",
                "email": "s.grey@school.com",
                "first_name": "Susan",
                "last_name": "Grey",
                "title": "Dr",
                "employee_id": "EMP202605",
                "primary_class": "Primary 2A",
                "assigned_classes": ["Primary 2A", "Primary 2B"]
            },
            {
                "username": "jdoe",
                "email": "j.doe@school.com",
                "first_name": "John",
                "last_name": "Doe",
                "title": "Mr",
                "employee_id": "EMP202606",
                "primary_class": "Primary 2B",
                "assigned_classes": ["Primary 2B", "Primary 3"]
            },

            # --- Upper Primary Tier ---
            {
                "username": "esmith",
                "email": "e.smith@school.com",
                "first_name": "Emily",
                "last_name": "Smith",
                "title": "Mrs",
                "employee_id": "EMP202607",
                "primary_class": "Primary 3",
                "assigned_classes": ["Primary 3", "Primary 4A", "Primary 4B"]
            },
            {
                "username": "wjohnson",
                "email": "w.johnson@school.com",
                "first_name": "William",
                "last_name": "Johnson",
                "title": "Mr",
                "employee_id": "EMP202608",
                "primary_class": "Primary 4A",
                "assigned_classes": ["Primary 4A", "Primary 5"]
            },
            {
                "username": "hwright",
                "email": "h.wright@school.com",
                "first_name": "Hope",
                "last_name": "Wright",
                "title": "Miss",
                "employee_id": "EMP202609",
                "primary_class": "Primary 4B",
                "assigned_classes": ["Primary 4A", "Primary 5", "Primary 6"]
            },
            {
                "username": "awright",
                "email": "a.wright@school.com",
                "first_name": "Anna",
                "last_name": "Wright",
                "title": "Mrs",
                "employee_id": "EMP202610",
                "primary_class": "Primary 5",
                "assigned_classes": ["Primary 4B", "Primary 5", "Primary 6"]
            },

            # --- Junior Secondary Tier (JSS) ---
            {
                "username": "kadi",
                "email": "k.adi@school.com",
                "first_name": "Kevin",
                "last_name": "Adi",
                "title": "Mr",
                "employee_id": "EMP202611",
                "primary_class": "Primary 6",
                "assigned_classes": ["Primary 6", "JSS 1A", "JSS 1B"]
            },
            {
                "username": "kade",
                "email": "k.ade@school.com",
                "first_name": "Kehinde",
                "last_name": "Ade",
                "title": "Miss",
                "employee_id": "EMP202612",
                "primary_class": "JSS 1B",
                "assigned_classes": ["Primary 6", "JSS 1A", "JSS 2B"]
            },
            {
                "username": "oojo",
                "email": "o.ojo@school.com",
                "first_name": "Olumide",
                "last_name": "Ojo",
                "title": "Mr",
                "employee_id": "EMP202613",
                "primary_class": "JSS 1A",
                "assigned_classes": ["JSS 1A", "JSS 2A", "JSS 3"]
            },
            {
                "username": "asani",
                "email": "a.sani@school.com",
                "first_name": "Amina",
                "last_name": "Sani",
                "title": "Miss",
                "employee_id": "EMP202614",
                "primary_class": "JSS 2A",
                "assigned_classes": ["JSS 1B", "JSS 2A", "JSS 2B"]
            },

            # --- Senior Secondary Tier (SS) ---
            {
                "username": "nnwosu",
                "email": "n.nwosu@school.com",
                "first_name": "Nneka",
                "last_name": "Nwosu",
                "title": "Mrs",
                "employee_id": "EMP202615",
                "primary_class": "JSS 2B",
                "assigned_classes": ["JSS 2B", "JSS 3", "SS 1A"]
            },
            {
                "username": "tbell",
                "email": "t.bell@school.com",
                "first_name": "Thomas",
                "last_name": "Bell",
                "title": "Dr",
                "employee_id": "EMP202616",
                "primary_class": "SS 1A",
                "assigned_classes": ["SS 1A", "SS 1B", "SS 2A"]
            },
            {
                "username": "fdupont",
                "email": "f.dupont@school.com",
                "first_name": "Francois",
                "last_name": "Dupont",
                "title": "Mr",
                "employee_id": "EMP202617",
                "primary_class": "SS 3",
                "assigned_classes": ["SS 2A", "SS 2B", "SS 3"]
            },
            {
                "username": "uagu",
                "email": "u.agu@school.com",
                "first_name": "Ugo",
                "last_name": "Agu",
                "title": "Mr",
                "employee_id": "EMP202618",
                "primary_class": "SS 2B",
                "assigned_classes": ["SS 2A", "SS 2B", "SS 3"]
            }
        ]

        # Use an atomic transaction block so database writes roll back cleanly on errors
        with transaction.atomic():
            
            for data in teachers_manifest:
                self.stdout.write(self.style.MIGRATE_LABEL(f"\nProcessing Staff: {data['title']} {data['first_name']} {data['last_name']}"))

                # -------------------------------------------------
                # STEP 1: CREATE OR FETCH BASE AUTH USER
                # -------------------------------------------------
                user, user_created = User.objects.get_or_create(
                    username=data["username"],
                    defaults={
                        "email": data["email"],
                        "first_name": data["first_name"],
                        "last_name": data["last_name"],
                        "role": "staff"
                    }
                )
                
                if user_created:
                    user.set_password("SecurePassword123")
                    user.save()
                    self.stdout.write(f"  ✔ Auth user account '{data['username']}' created.")
                else:
                    self.stdout.write(f"  ⚠ Auth user account '{data['username']}' already exists.")

                # -------------------------------------------------
                # STEP 2: RESOLVE THE FORM CLASS OBJECT
                # -------------------------------------------------
                primary_class_group = ClassGroup.objects.filter(name=data["primary_class"]).first()

                # -------------------------------------------------
                # STEP 3: CREATE OR UPDATE EXTENDED PROFILE
                # -------------------------------------------------
                profile, profile_created = TeacherProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "title": data["title"],
                        "employee_id": data["employee_id"],
                        "class_taught": primary_class_group,
                        "hire_date": date(2026, 1, 1)
                    }
                )
                
                status_msg = "created" if profile_created else "updated"
                self.stdout.write(self.style.SUCCESS(f"  ✔ Profile instance {status_msg} (ID: {profile.employee_id})."))

                # -------------------------------------------------
                # STEP 4: ASSIGN TEACHER FIELD IN INTERMEDIATE MODEL
                # -------------------------------------------------
                # Select ClassGroup database objects matching the assigned array strings
                target_classes = ClassGroup.objects.filter(name__in=data["assigned_classes"])
                
                # Fetch only ClassRelationship table rows belonging to those targeted groups
                class_subjects_to_update = ClassRelationship.objects.filter(class_group__in=target_classes)
                
                if class_subjects_to_update.exists():
                    # Efficient single-query mass assignment update
                    updated_count = class_subjects_to_update.update(teacher=profile)
                    
                    self.stdout.write(
                        f"  🔗 Assigned to {updated_count} course subjects throughout: "
                        f"{', '.join(data['assigned_classes'])}"
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ No ClassRelationship rows available for classes {data['assigned_classes']}. "
                            "Ensure 'create_class_groups' runs first!"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS("\n🎉 Massive K-12 school infrastructure successfully mapped with 18 teachers.")
        )
