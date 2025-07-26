"""
Hall Pass Vocabularies for Classroom Management

Provides choice vocabularies for hall pass destinations and related features.
"""

from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@implementer(IVocabularyFactory)
class HallPassDestinationsVocabulary(object):
    """Vocabulary of common hall pass destinations"""

    def __call__(self, context):
        """Generate vocabulary terms for hall pass destinations"""
        terms = [
            SimpleTerm(value="Restroom", token="restroom", title="Restroom"),
            SimpleTerm(value="Office", token="office", title="Main Office"),
            SimpleTerm(value="Nurse", token="nurse", title="Nurse's Office"),
            SimpleTerm(value="Library", token="library", title="Library"),
            SimpleTerm(value="Guidance", token="guidance", title="Guidance Counselor"),
            SimpleTerm(
                value="Principal", token="principal", title="Principal's Office"
            ),
            SimpleTerm(value="Locker", token="locker", title="Locker"),
            SimpleTerm(value="Water", token="water", title="Water Fountain"),
            SimpleTerm(
                value="Technology", token="technology", title="Technology Support"
            ),
            SimpleTerm(value="Other", token="other", title="Other (see notes)"),
        ]
        return SimpleVocabulary(terms)


# Factory instances
hall_pass_destinations_vocabulary_factory = HallPassDestinationsVocabulary()
