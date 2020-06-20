"""
Implements Full-text search using the FTS{3,4,5} Extensions.
See https://www.sqlite.org/fts5.html or https://www.sqlite.org/fts3.html for
further details.

SQLite version 3.5.0 >= FTS3
SQLite version 3.7.4 >= FTS4
SQLite version 3.9.0 >= FTS5
"""
from django.db import models


class _FTSModel(models.Model):
    rowid = models.AutoField(primary_key=True)
    rank = models.FloatField()  # TODO: Decide on FloatField vs. DecimalField

    class Meta:
        abstract = True
        required_db_vendor = "sqlite"


class FTS3Model(_FTSModel):
    class Meta(_FTSModel.Meta):
        abstract = True
        required_db_features = ["fts3_enabled"]


class FTS4Model(_FTSModel):
    class Meta(_FTSModel.Meta):
        abstract = True
        required_db_features = ["fts4_enabled"]


class FTS5Model(_FTSModel):
    class Meta(_FTSModel.Meta):
        abstract = True
        required_db_features = ["fts5_enabled"]


class FTSField(models.TextField):
    description = "Full-text search"


@FTSField.register_lookup  # TODO: Move to apps.ready
class Match(models.Lookup):
    lookup_name = "match"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s MATCH %s" % (lhs, rhs), params


@FTSField.register_lookup  # TODO: Move to apps.ready
class MatchStartswith(Match):
    """
    Creates "Initial Token Queries" where the search string will be converted
    from `foo` to `^foo`.
    """

    lookup_name = "match_startswith"

    def __init__(self, lhs, rhs):
        if rhs.startswith("^"):
            super().__init__(lhs, rhs)
        else:
            super().__init__(lhs, "^" + rhs)


@FTSField.register_lookup  # TODO: Move to apps.ready
class MatchNear(Match):
    """
    Creates "NEAR queries" e.g. `NEAR("SPAM SPAM" "bacon")`.
    """

    lookup_name = "match_near"

    def __init__(self, lhs, rhs):
        if isinstance(rhs, tuple):
            super().__init__(
                lhs, "NEAR(%s)" % " ".join('"%s"' % term for term in rhs)
            )
        else:
            super().__init__(lhs, "NEAR(%s)" % rhs)


class OrOperator:
    def __init__(self, *terms):
        self.terms = terms

    def __str__(self):
        return " OR ".join('"%s"' % term for term in self.terms)


class FTSTokenizerOptionField(models.Field):
    description = "Configure the specific tokenizer used by the FTS5 table"
    # TODO: Add check for tokenizer options
    # https://www.sqlite.org/fts5.html#tokenizers
    def __init__(self, tokenizer=""):
        supported_tokenizers = ["unicode61", "ascii", "porter"]
        if not tokenizer in supported_tokenizers:
            raise ValueError(
                "tokenizer must be one of " + ",".join(supported_tokenizers)
            )
        self.tokenizer = tokenizer
        super().__init__()
