from decimal import Decimal

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .forms import ProductFilterForm
from .models import Album_image
from .search import parse_terms


class ParserTests(SimpleTestCase):
    def test_year_and_price(self):
        t = parse_terms("forest 2024 150")
        self.assertEqual(t[1]["year"], 2024)
        self.assertEqual(t[2]["number"], Decimal("150"))
        self.assertIsNone(t[2]["year"])

    def test_persian_digits(self):
        self.assertEqual(parse_terms("۲۰۲۴")[0]["year"], 2024)

    def test_huge_number_ignored(self):
        self.assertIsNone(parse_terms("99999999999999999999")[0]["number"])

    def test_term_limit(self):
        self.assertEqual(len(parse_terms("a b c d e f g h")), 6)


class FormTests(SimpleTestCase):
    def test_empty_ok(self):
        self.assertTrue(ProductFilterForm({}).is_valid())


class ViewTests(TestCase):
    """Adjust the required fields in create() to match your model."""

    def setUp(self):
        self.url = reverse("products")
        # Album_image.objects.create(title="Forest", price=100, year=2022, ...)
        # Album_image.objects.create(title="Sunset", price=300, year=2024, ...)

    def test_page_loads_with_bad_input(self):
        r = self.client.get(self.url, {"q": "x" * 500})
        self.assertEqual(r.status_code, 200)
