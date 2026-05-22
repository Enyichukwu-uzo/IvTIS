from django.test import TestCase


class HomePageTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ivory Tower International School')

    def test_home_page_uses_partial_templates(self):
        response = self.client.get('/')

        self.assertContains(response, 'Welcome from the Head')
        self.assertContains(response, 'Latest News')
