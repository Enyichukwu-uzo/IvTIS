# # core/management/commands/create_primary_subjects.py

# from django.core.management.base import BaseCommand
# from core.models import Subject


# class Command(BaseCommand):
#     """
#     Custom Django management command for creating
#     common subjects studied from Nursery 1 to Primary 6.

#     Run with:
#         python manage.py create_primary_subjects
#     """

#     help = "Populate the database with Nursery and Primary school subjects."

#     def handle(self, *args, **kwargs):
#         subjects = [

#             (
#                 "Mathematics",
#                 "MATH",
#                 "Basic arithmetic, numbers, shapes, measurements, and problem solving."
#             ),

#             (
#                 "English Language",
#                 "ENG",
#                 "Reading, writing, spelling, grammar, and communication skills."
#             ),

#             (
#                 "Basic Science",
#                 "BSC",
#                 "Introduction to science concepts, nature, health, and environment."
#             ),

#             (
#                 "Social Studies",
#                 "SOS",
#                 "Study of society, culture, relationships, and civic life."
#             ),

#             (
#                 "Civic Education",
#                 "CVE",
#                 "Teaching citizenship, rights, duties, and national values."
#             ),

#             (
#                 "Computer Studies",
#                 "CMP",
#                 "Introduction to computers, digital devices, and basic ICT skills."
#             ),

#             (
#                 "Physical and Health Education",
#                 "PHE",
#                 "Exercise, sports, hygiene, safety, and healthy living."
#             ),

#             (
#                 "Cultural and Creative Arts",
#                 "CCA",
#                 "Music, drawing, drama, crafts, and creative expression."
#             ),

#             (
#                 "Agricultural Science",
#                 "AGR",
#                 "Basic farming, plants, animals, and food production."
#             ),(
#                 "Home Economics",
#                 "HME",
#                 "Basic home management, nutrition, and life skills."
#             ), (
#                 "Religious Studies",
#                 "RLS",
#                 "Moral and religious teachings for character development."
#             ), (
#                 "French Language",
#                 "FRN",
#                 "Introduction to basic French vocabulary and communication."), (
#                 "Verbal Reasoning",
#                 "VRB",
#                 "Development of language logic and comprehension skills."
#             ), (
#                 "Quantitative Reasoning", "QTR", "Logical thinking using numbers, patterns, and sequences."
#             ), ( "Handwriting",
#                 "HDW",
#                 "Development of neat and legible writing skills."
#             ),

#             (
#                 "Phonics",
#                 "PHN",
#                 "Learning letter sounds and pronunciation for early literacy."
#             ),

#             (
#                 "Nursery Rhymes",
#                 "NRY",
#                 "Songs and rhymes used in early childhood learning."
#             ),

#             (
#                 "Moral Instruction",
#                 "MOR",
#                 "Teaching discipline, honesty, kindness, and good behavior."
#             ),
#         ]
#         for name, code, description in subjects:

#             subject, created = Subject.objects.get_or_create(

#                 # Fields used to check uniqueness
#                 name=name,

#                 # Values to insert if object does not exist
#                 defaults={
#                     'code': code,
#                     'description': description
#                 }
#             )
#             if created:

#                 self.stdout.write(
#                     self.style.SUCCESS(
#                         f"✔ Subject created: {subject.name}"
#                     )
#                 )

#             else:

#                 self.stdout.write(
#                     self.style.WARNING(
#                         f"⚠ Subject already exists: {subject.name}"
#                     )
#                 )
#         self.stdout.write(self.style.SUCCESS("\n🎓 Primary and Nursery subjects setup completed successfully."))
# core/management/commands/create_primary_subjects.py

from django.core.management.base import BaseCommand
from core.models import Subject


class Command(BaseCommand):
    """
    Custom Django management command for creating 
    common subjects studied from Nursery 1 to Senior Secondary 3 (SS3).

    Run with:
        python manage.py create_primary_subjects
    """

    help = "Populate the database with Nursery, Primary, and Secondary school subjects."

    def handle(self, *args, **kwargs):

        # =========================================================
        # MASTER LIST OF SUBJECTS (K-12 Spectrum)
        # ---------------------------------------------------------
        # Each tuple contains:
        #   1. Subject name
        #   2. Subject code (Unique identifier string)
        #   3. Description
        # =========================================================
        subjects = [
            # --- CORE GENERAL SUBJECTS (All Levels) ---
            (
                "Mathematics",
                "MATH",
                "Basic arithmetic, algebra, geometry, trigonometry, and problem solving."
            ),
            (
                "English Language",
                "ENG",
                "Reading, writing, spelling, grammar, and advanced communication skills."
            ),
            (
                "Civic Education",
                "CVE",
                "Teaching citizenship, human rights, social duties, and national values."
            ),
            (
                "Computer Studies",
                "CMP",
                "Introduction to computing, information technology, and digital literacy."
            ),
            (
                "Physical and Health Education",
                "PHE",
                "Physical fitness, sports, personal hygiene, anatomy, and healthy living."
            ),
            (
                "Religious Studies",
                "RLS",
                "Moral, ethical, and spiritual teachings for character development."
            ),
            (
                "French Language",
                "FRN",
                "Introduction to basic and intermediate French vocabulary and phonetics."
            ),
            (
                "Moral Instruction",
                "MOR",
                "Teaching discipline, integrity, kindness, and value-based behavior."
            ),

            # --- EARLY YEARS & PRIMARY SPECIALTIES ---
            (
                "Phonics",
                "PHN",
                "Learning letter sounds and blend pronunciation for early literacy."
            ),
            (
                "Nursery Rhymes",
                "NRY",
                "Melodic songs and rhymes used for cognitive development in early years."
            ),
            (
                "Handwriting",
                "HDW",
                "Development of neat, cursive, and legible fine motor writing skills."
            ),
            (
                "Verbal Reasoning",
                "VRB",
                "Development of language logic, vocabulary patterns, and comprehension."
            ),
            (
                "Quantitative Reasoning", 
                "QTR", 
                "Logical thinking using mathematical patterns, puzzles, and sequences."
            ),

            # --- PRIMARY & JUNIOR SECONDARY INTEGRATED SCIENCES ---
            (
                "Basic Science",
                "BSC",
                "Integrated introduction to biology, chemistry, physics, and ecology."
            ),
            (
                "Social Studies",
                "SOS",
                "Study of human societies, environments, cultures, and relationships."
            ),
            (
                "Cultural and Creative Arts",
                "CCA",
                "Exploration of fine arts, music, local crafts, drama, and performance."
            ),
            (
                "Agricultural Science",
                "AGR",
                "Foundations of farming, crop management, soil science, and livestock care."
            ),
            (
                "Home Economics",
                "HME",
                "Basic hospitality management, food processing, nutrition, and tailoring."
            ),

            # --- NEW: SENIOR SECONDARY SPECIALIZED SUBJECTS (SS1 - SS3) ---
            (
                "Biology",
                "BIO",
                "The scientific study of living organisms, plant life, and human anatomy."
            ),
            (
                "Chemistry",
                "CHM",
                "The study of chemical matter, atomic structures, elements, and laboratory reactions."
            ),
            (
                "Physics",
                "PHY",
                "The study of matter, energy, mechanics, light, electricity, and universal forces."
            ),
            (
                "Economics",
                "ECN",
                "Analysis of production, supply and demand, financial markets, and macroeconomics."
            ),
            (
                "Government",
                "GOV",
                "Study of political systems, state structures, governance, and international relations."
            ),
            (
                "Literature in English",
                "LIT",
                "Critical analysis of classic and contemporary prose, drama, and poetic anthologies."
            ),
            (
                "Further Mathematics",
                "FMA",
                "Advanced mathematics covering calculus, vectors, matrices, and mechanics."
            ),
        ]

        # =========================================================
        # DB SYNCHRONIZATION LOOP
        # =========================================================
        for name, code, description in subjects:

            # Look up existing subjects using the name attribute
            subject, created = Subject.objects.get_or_create(
                name=name,
                defaults={
                    'code': code,
                    'description': description
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✔ Subject created: {subject.name} [{code}]")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Subject already exists: {subject.name}")
                )

        # =========================================================
        # TERMINAL FINALIZATION MSG
        # =========================================================
        self.stdout.write(
            self.style.SUCCESS(
                "\n🎓 Complete K-12 Academic Subjects setup completed successfully."
            )
        )