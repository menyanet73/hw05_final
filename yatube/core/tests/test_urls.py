from django.test import TestCase


class ErrorPageTest(TestCase):
    
    def test_404_custom_page(self):
        response = self.client.get('/not_existing_page/')
        self.assertTemplateUsed(response, 'core/404.html')