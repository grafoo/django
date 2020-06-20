from django.test import TestCase, modify_settings
from .models import Breakfast
from django.contrib.sqlite3.search import OrOperator as Or


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(clazz):
        _data = [
            "Egg and SPAM",
            "Egg, bacon and SPAM",
            "Egg, bacon, sausage and SPAM",
            "SPAM, bacon, sausage and SPAM",
            "SPAM, egg, SPAM, SPAM, bacon and SPAM",
            "SPAM, SPAM, SPAM, egg and SPAM",
            "SPAM, SPAM, SPAM, SPAM, SPAM, SPAM, baked beans, SPAM, SPAM, SPAM"
            " and SPAM",
            "Lobster Thermidor aux crevettes with a Mornay sauce, garnished"
            " with truffle pâté, brandy and a fried egg on top, and Spam",
        ]
        clazz.breakfast_menu = [
            Breakfast.objects.create(ingredients=ingredients)
            for ingredients in _data
        ]

    def test_match(self):
        expected = self.breakfast_menu
        searched = Breakfast.objects.filter(ingredients__match="spam")
        self.assertSequenceEqual(searched, expected)

    def test_match_with_or_operator(self):
        expected = self.breakfast_menu[-2:]
        searched = Breakfast.objects.filter(
            ingredients__match=Or("baked beans", "lobster",)
        )
        self.assertSequenceEqual(searched, expected)

    def test_match_near_with_tuple(self):
        expected = self.breakfast_menu[4]
        searched = Breakfast.objects.get(
            ingredients__match_near=("SPAM SPAM", "bacon",)
        )
        self.assertEqual(searched, expected)

    def test_match_near_with_string(self):
        expected = self.breakfast_menu[4]
        searched = Breakfast.objects.get(
            ingredients__match_near='"SPAM SPAM" "bacon"'
        )
        self.assertEqual(searched, expected)

    def test_default_tokenizer_removes_diacritics(self):
        expected = self.breakfast_menu[-1]
        searched = Breakfast.objects.get(ingredients__match="pate")
        self.assertEqual(searched, expected)

    def test_match_first_token(self):
        expected = self.breakfast_menu[:3]
        searched = Breakfast.objects.filter(
            ingredients__match_startswith="egg"
        )
        self.assertSequenceEqual(searched, expected)

    def test_match_prefix_token(self):
        expected = 5
        searched = len(Breakfast.objects.filter(ingredients__match="ba*"))
        self.assertEqual(searched, expected)
