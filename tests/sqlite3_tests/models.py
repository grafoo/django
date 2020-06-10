from django.contrib.sqlite3.search import FTS5Model, FTSField


class Breakfast(FTS5Model):
    ingredients = FTSField()
