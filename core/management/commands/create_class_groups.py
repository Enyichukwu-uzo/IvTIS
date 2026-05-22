# # core/management/commands/create_class_groups.py

# from django.core.management.base import BaseCommand
# from core.models import ClassGroup, Subject, ClassRelationship


# class Command(BaseCommand):
#     """
#     Custom Django management command for creating Class Groups
#     and linking them to their respective existing subjects.

#     Run with:
#         python manage.py create_class_groups
#     """

#     help = "Populate the database with Class Groups and assign their subjects."

#     def handle(self, *args, **kwargs):

#         # =========================================================
#         # SUBJECT MAPPING GROUPS
#         # ---------------------------------------------------------
#         # Defining sets of subject codes based on academic levels.
#         # This avoids repeating codes manually for every single class.
#         # =========================================================
        
#         # Nursery levels focus heavily on foundational literacy and rhymes
#         nursery_codes = ["MATH", "ENG", "BSC", "CMP", "PHE", "CCA", "HDW", "PHN", "NRY", "MOR", "RLS"]
        
#         # Kindergarten introduces early logic processing (Reasoning)
#         kindergarten_codes = nursery_codes + ["SOS", "CVE", "VRB", "QTR"]
        
#         # Primary levels introduce technical skills like Agriculture and Home Economics
#         primary_codes = [
#             "MATH", "ENG", "BSC", "SOS", "CVE", "CMP", "PHE", "CCA", 
#             "AGR", "HME", "RLS", "FRN", "VRB", "QTR", "HDW", "MOR"
#         ]

#         # =========================================================
#         # CLASS GROUPS DATA CONFIGURATION
#         # ---------------------------------------------------------
#         # A list of tuples containing:
#         #   1. Class Name
#         #   2. List of relevant subject codes
#         # =========================================================
#         class_groups = [
#             ("Nursery 1", nursery_codes),
#             ("Nursery 2", nursery_codes),
#             ("Kindergarten", kindergarten_codes),
#             ("Primary 1", primary_codes),
#             ("Primary 2", primary_codes),
#             ("Primary 3", primary_codes),
#             ("Primary 4", primary_codes),
#             ("Primary 5", primary_codes),
#             ("Primary 6", primary_codes),
#         ]

#         # =========================================================
#         # PROCESSING AND LINKING
#         # =========================================================
#         for class_name, subject_codes in class_groups:
            
#             # 1. Safely create or fetch the ClassGroup
#             # Using get_or_create ensures we don't crash if the class exists.
#             class_group, class_created = ClassGroup.objects.get_or_create(
#                 name=class_name,
#                 defaults={'academic_year': '2026/2027'}
#             )

#             if class_created:
#                 self.stdout.write(self.style.SUCCESS(f"\n🏫 Class Group created: {class_group.name}"))
#             else:
#                 self.stdout.write(self.style.WARNING(f"\n🏫 Class Group already exists: {class_group.name}"))

#             # 2. Loop through the assigned subject codes for this class
#             for code in subject_codes:
                
#                 # ANSWER TO YOUR QUESTION: "Isn't there a way to just check if the subject exists?"
#                 # Yes! We use .filter().first() or .get() to fetch the existing row. 
#                 # Using .filter(code=code).first() is safer here because if a code is 
#                 # accidentally missing from your DB, it returns None instead of crashing the script.
#                 subject = Subject.objects.filter(code=code).first()

#                 if subject:
#                     # BECAUSE OF THE 'through' TABLE:
#                     # When a ManyToMany field has a custom intermediate table, you cannot 
#                     # use standard syntax like class_group.subjects.add(subject).
#                     # Instead, we perform a get_or_create directly on the ClassRelationship table.
#                     _, link_created = ClassRelationship.objects.get_or_create(
#                         class_group=class_group,
#                         subject=subject
#                     )

#                     if link_created:
#                         self.stdout.write(f"  🔗 Linked subject: {subject.name} ({code})")
#                 else:
#                     # Alert the developer if they forgot to run the first command
#                     self.stdout.write(
#                         self.style.ERROR(f"  ❌ Subject with code '{code}' not found! Run create_primary_subjects first.")
#                     )

#         # =========================================================
#         # FINAL SUCCESS MESSAGE
#         # =========================================================
#         self.stdout.write(
#             self.style.SUCCESS(
#                 "\n🎉 Class Groups setup and subject mapping completed successfully."
#             )
#         )

# core/management/commands/create_class_groups.py

from django.core.management.base import BaseCommand
from core.models import ClassGroup, Subject, ClassRelationship


class Command(BaseCommand):
    """
    Custom Django management command for creating Class Groups
    stretching from Nursery 1 up to SS3 (with varied arms)
    and linking them to their level-appropriate subjects.

    Run with:
        python manage.py create_class_groups
    """

    help = "Populate the database with comprehensive Class Groups (Nursery to SS3) with selective arms."

    def handle(self, *args, **kwargs):

        # =========================================================
        # SUBJECT MAPPING GROUPS (UPDATED)
        # ---------------------------------------------------------
        # We categorize subject codes into five distinct blocks to 
        # reflect the progression from early years to senior secondary.
        # =========================================================
        
        # 1. Early Childhood Foundation
        nursery_codes = ["MATH", "ENG", "BSC", "CMP", "PHE", "CCA", "HDW", "PHN", "NRY", "MOR", "RLS"]
        
        # 2. Advanced Pre-School Logic
        kindergarten_codes = nursery_codes + ["SOS", "CVE", "VRB", "QTR"]
        
        # 3. Comprehensive Primary Education
        primary_codes = [
            "MATH", "ENG", "BSC", "SOS", "CVE", "CMP", "PHE", "CCA", 
            "AGR", "HME", "RLS", "FRN", "VRB", "QTR", "HDW", "MOR"
        ]

        # 4. Junior Secondary School (JSS)
        # Drops early-childhood elements like rhymes/handwriting, retains core academic subsets
        jss_codes = ["MATH", "ENG", "BSC", "SOS", "CVE", "CMP", "PHE", "CCA", "AGR", "HME", "RLS", "FRN"]

        # 5. Senior Secondary School (SSS)
        # Strips out integrated basic tracks; targets specialized foundational blocks from your vault
        sss_codes = ["MATH", "ENG", "CVE", "CMP", "PHE", "AGR", "RLS", "FRN"]

        # =========================================================
        # CLASS GROUPS DATA CONFIGURATION (UPDATED FOR 10+ TEACHERS)
        # ---------------------------------------------------------
        # To facilitate a roster of 10+ teachers, we generate a massive 
        # variety of classes. Notice how some tracks split into A/B arms 
        # while others remain consolidated single arms.
        # =========================================================
        class_groups = [
            # Early Years (Single tracks)
            ("Nursery 1", nursery_codes),
            ("Nursery 2", nursery_codes),
            ("Kindergarten", kindergarten_codes),

            # Primary Tier (Mixed Double/Single Arms)
            ("Primary 1A", primary_codes),
            ("Primary 1B", primary_codes),
            ("Primary 2A", primary_codes),
            ("Primary 2B", primary_codes),
            ("Primary 3", primary_codes),   # Single Arm
            ("Primary 4A", primary_codes),
            ("Primary 4B", primary_codes),
            ("Primary 5", primary_codes),   # Single Arm
            ("Primary 6", primary_codes),   # Single Arm

            # Junior Secondary Tier (Mixed Double/Single Arms)
            ("JSS 1A", jss_codes),
            ("JSS 1B", jss_codes),
            ("JSS 2A", jss_codes),
            ("JSS 2B", jss_codes),
            ("JSS 3", jss_codes),           # Single Arm

            # Senior Secondary Tier (Mixed Double/Single Arms)
            ("SS 1A", sss_codes),
            ("SS 1B", sss_codes),
            ("SS 2A", sss_codes),
            ("SS 2B", sss_codes),
            ("SS 3", sss_codes),             # Single Arm
        ]

        # =========================================================
        # PROCESSING AND LINKING
        # =========================================================
        for class_name, subject_codes in class_groups:
            
            # 1. Safely create or fetch the ClassGroup
            # Using get_or_create guarantees idempotency across your custom structural configuration.
            class_group, class_created = ClassGroup.objects.get_or_create(
                name=class_name,
                defaults={'academic_year': '2026/2027'}
            )

            if class_created:
                self.stdout.write(self.style.SUCCESS(f"\n🏫 Class Group created: {class_group.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"\n🏫 Class Group already exists: {class_group.name}"))

            # 2. Loop through and establish connections with existing subject entries
            for code in subject_codes:
                
                # We perform a read lookup matching the subject shortcode string safely.
                subject = Subject.objects.filter(code=code).first()

                if subject:
                    # Write execution directly into the Many-to-Many 'through' model table instance
                    _, link_created = ClassRelationship.objects.get_or_create(
                        class_group=class_group,
                        subject=subject
                    )

                    if link_created:
                        self.stdout.write(f"  🔗 Linked subject: {subject.name} ({code})")
                else:
                    # Logs clean diagnostic errors in case the seed vault missing secondary specifications
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ Subject with code '{code}' not found! Run create_primary_subjects first.")
                    )

        # =========================================================
        # FINAL SUCCESS SUMMARY MESSAGE
        # =========================================================
        self.stdout.write(
            self.style.SUCCESS(
                "\n🎉 Complete K-12 Class Groups layout setup successfully synchronized."
            )
        )
