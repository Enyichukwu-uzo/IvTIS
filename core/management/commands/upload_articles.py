import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import NewsArticle

class Command(BaseCommand):
    help = 'Uploads 10 unique articles authored by the first superuser'

    def handle(self, *args, **options):
        # Find the first available superuser
        author = User.objects.filter(is_superuser=True).first()
        
        if not author:
            self.stdout.write(self.style.ERROR("No superuser found. Create one first!"))
            return

        articles_data = [
            {
                'title': 'Grand Opening of the New Science Wing',
                'summary': 'The school unveils its state-of-the-art laboratory facilities.',
                'body': 'After two years of construction, the Excellence Science Wing is finally open. It features four biology labs, three chemistry stations, and a dedicated robotics workshop to help our students excel in STEM fields.',
                'image_name': 'img1.jpg'
            },
            {
                'title': 'Inter-House Sports Festival 2026',
                'summary': 'A day of record-breaking performances on the field.',
                'body': 'Blue House took home the trophy this year in a stunning display of athletics. Notable highlights included the 100m sprint where a 10-year record was broken by David Smith from Year 11.',
                'image_name': 'img2.jpg'
            },
            {
                'title': 'National Debating Championship Victory',
                'summary': 'Our debating team brings home the regional gold medal.',
                'body': 'The team argued their way to the top last Friday at the Regional Finals. The topic focused on the ethics of AI in education, and our students were praised for their critical thinking and eloquence.',
                'image_name': 'img3.jpg'
            },
            {
                'title': 'Annual Art Exhibition: Creative Minds',
                'summary': 'Student artwork on display at the city gallery.',
                'body': 'From oil paintings to digital sculptures, the Creative Minds exhibition showcased the immense talent of our senior art students. Over 200 visitors attended the opening night gala.',
                'image_name': 'img4.jpg'
            },
            {
                'title': 'New Computer Literacy Program Launched',
                'summary': 'Every student to receive specialized coding training.',
                'body': 'Starting next term, the school is introducing Python and Web Development into the core curriculum for all junior students to prepare them for a digital future.',
                'image_name': 'img5.jpg'
            },
            {
                'title': 'Sustainability Initiative: Solar Campus',
                'summary': 'School transitions to 60% renewable energy.',
                'body': 'We have successfully installed 120 solar panels across the roof of the main hall. This project will not only reduce our carbon footprint but also serve as a live learning tool for environmental science students.',
                'image_name': 'img6.jpg'
            },
            {
                'title': 'Music Department Spring Concert',
                'summary': 'A night of orchestral magic and modern jazz.',
                'body': 'The school orchestra, joined by the jazz ensemble, performed to a sold-out crowd. The highlight of the evening was a solo violin performance of Vivaldi’s Winter by Sarah Jenkins.',
                'image_name': 'img7.jpg'
            },
            {
                'title': 'Community Volunteer Day Success',
                'summary': 'Students and staff partner with local charities.',
                'body': 'Over 300 volunteers participated in our annual community day, helping to renovate the local park and organize a food drive that collected over 500kg of supplies for families in need.',
                'image_name': 'img8.jpg'
            },
            {
                'title': 'Global Exchange Program Returns',
                'summary': 'Students prepare for a semester in France and Japan.',
                'body': 'After a brief hiatus, our international exchange program is back. Twelve students have been selected to travel abroad, fostering cultural understanding and language immersion.',
                'image_name': 'img9.jpg'
            },
            {
                'title': 'Library Upgrade: The Digital Commons',
                'summary': 'Traditional reading meets modern technology.',
                'body': 'The library has been renovated to include "The Digital Commons," a space equipped with VR headsets for historical tours and high-speed research pods for collaborative projects.',
                'image_name': 'img10.jpg'
            }
        ]

        for item in articles_data:
            article, created = NewsArticle.objects.get_or_create(
                title=item['title'],
                defaults={
                    'summary': item['summary'],
                    'body': item['body'],
                    'author': author,
                    'status': 'published',
                }
            )

            if created:
                img_path = f'setup_assets/{item["image_name"]}'
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        article.image.save(item['image_name'], File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f"Created: {article.title}"))
            else:
                self.stdout.write(f"Skipped: {article.title}")