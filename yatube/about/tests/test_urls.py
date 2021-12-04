from django.test import TestCase
from django.urls.base import reverse

from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    def test_static_urls_exists_at_disired_location(self):
        reverse_names = [
            reverse('about:author'),
            reverse('about:tech'),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_correct_template(self):
        reverse_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in reverse_names.items():
            with self.subTest(adress=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
