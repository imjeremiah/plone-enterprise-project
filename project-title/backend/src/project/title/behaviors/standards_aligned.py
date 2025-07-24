"""
Standards Alignment Behavior for Educational Content

This behavior allows teachers to align any content (lessons, activities, resources)
with educational standards including Common Core, NGSS, and state standards.
Designed to be teacher-friendly with search and filtering capabilities.
"""

from plone import schema
from plone.autoform import directives
from plone.supermodel import model
from zope import interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory, IVocabularyFactory
import logging

logger = logging.getLogger(__name__)


@provider(IContextAwareDefaultFactory)
def default_grade_levels(context):
    """
    Provide reasonable default grade levels based on context.
    This helps teachers by pre-selecting common grade ranges.
    """
    # Default to elementary grades - most common in K-12
    return ['K', '1', '2', '3', '4', '5']


class IStandardsAligned(model.Schema):
    """
    Behavior for aligning educational content with standards.
    
    This behavior can be applied to any content type to allow teachers
    to tag lessons, activities, and resources with relevant educational standards.
    Supports multiple standard types and grade levels for maximum flexibility.
    """
    
    model.fieldset(
        'standards',
        label='Standards Alignment',
        description='Align this content with educational standards for lesson planning and reporting.',
        fields=['aligned_standards', 'primary_subject', 'grade_levels', 'alignment_notes', 'difficulty_level']
    )
    
    # Primary standards alignment - comprehensive list
    aligned_standards = schema.List(
        title="Aligned Standards",
        description="Select the educational standards that this content addresses. "
                   "You can choose from Common Core (Math & ELA), NGSS (Science), "
                   "and NCSS (Social Studies) standards.",
        value_type=schema.Choice(
            vocabulary="project.title.vocabularies.Standards"
        ),
        required=False,
        missing_value=[],
    )
    
    # Primary subject area for easier organization
    primary_subject = schema.Choice(
        title="Primary Subject Area",
        description="Select the main subject area for this content. "
                   "This helps with organization and filtering.",
        vocabulary="project.title.vocabularies.SubjectAreas",
        required=False,
    )
    
    # Grade levels this content is appropriate for
    grade_levels = schema.List(
        title="Grade Levels",
        description="Select all grade levels where this content is appropriate. "
                   "This helps teachers find age-appropriate materials.",
        value_type=schema.Choice(
            vocabulary="project.title.vocabularies.GradeLevels"
        ),
        required=False,
        defaultFactory=default_grade_levels,
        missing_value=[],
    )
    
    # Additional alignment notes for teacher context
    alignment_notes = schema.Text(
        title="Alignment Notes",
        description="Add any additional notes about how this content aligns with standards. "
                   "This is helpful for other teachers using your materials.",
        required=False,
        missing_value="",
    )
    
    # Difficulty level for differentiation
    difficulty_level = schema.Choice(
        title="Difficulty Level",
        description="Indicate the difficulty level to help with differentiation and scaffolding.",
        vocabulary="project.title.vocabularies.DifficultyLevels",
        required=False,
    )
    
    # Widget customizations for better teacher experience
    directives.widget(
        'aligned_standards',
        pattern_options={
            'multiple': True,
            'placeholder': 'Search for standards (e.g., "CCSS.MATH.3.OA.A.1" or "3rd grade addition")',
            'allow_clear': True,
        }
    )
    
    directives.widget(
        'grade_levels',
        pattern_options={
            'multiple': True,
            'placeholder': 'Select grade levels',
            'allow_clear': True,
        }
    )


class ISubjectAreas(interface.Interface):
    """Marker interface for subject areas vocabulary."""
    pass


class IGradeLevels(interface.Interface):
    """Marker interface for grade levels vocabulary."""
    pass


class IDifficultyLevels(interface.Interface):
    """Marker interface for difficulty levels vocabulary."""
    pass


# Additional vocabularies for the behavior
SUBJECT_AREAS = [
    ('mathematics', 'Mathematics'),
    ('english_language_arts', 'English Language Arts'),
    ('science', 'Science'),
    ('social_studies', 'Social Studies'),
    ('art', 'Art'),
    ('music', 'Music'),
    ('physical_education', 'Physical Education'),
    ('technology', 'Technology/Computer Science'),
    ('world_languages', 'World Languages'),
    ('health', 'Health'),
    ('career_technical', 'Career & Technical Education'),
    ('special_education', 'Special Education'),
    ('interdisciplinary', 'Interdisciplinary'),
]

GRADE_LEVELS = [
    ('PK', 'Pre-Kindergarten'),
    ('K', 'Kindergarten'),
    ('1', '1st Grade'),
    ('2', '2nd Grade'),
    ('3', '3rd Grade'),
    ('4', '4th Grade'),
    ('5', '5th Grade'),
    ('6', '6th Grade'),
    ('7', '7th Grade'),
    ('8', '8th Grade'),
    ('9', '9th Grade'),
    ('10', '10th Grade'),
    ('11', '11th Grade'),
    ('12', '12th Grade'),
]

DIFFICULTY_LEVELS = [
    ('beginner', 'Beginner - Introduction to concept'),
    ('developing', 'Developing - Building understanding'),
    ('proficient', 'Proficient - Meets grade level expectations'),
    ('advanced', 'Advanced - Exceeds expectations'),
    ('remedial', 'Remedial - Below grade level support'),
    ('enrichment', 'Enrichment - Extended learning'),
]


@interface.implementer(IVocabularyFactory)
class SubjectAreasVocabularyFactory:
    """Factory for subject areas vocabulary."""
    
    def __call__(self, context=None):
        """Create and return the subject areas vocabulary."""
        from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
        
        terms = []
        for value, title in SUBJECT_AREAS:
            term = SimpleTerm(value=value, token=value, title=title)
            terms.append(term)
        
        return SimpleVocabulary(terms)


@interface.implementer(IVocabularyFactory)
class GradeLevelsVocabularyFactory:
    """Factory for grade levels vocabulary."""
    
    def __call__(self, context=None):
        """Create and return the grade levels vocabulary."""
        from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
        
        terms = []
        for value, title in GRADE_LEVELS:
            term = SimpleTerm(value=value, token=value, title=title)
            terms.append(term)
        
        return SimpleVocabulary(terms)


@interface.implementer(IVocabularyFactory)
class DifficultyLevelsVocabularyFactory:
    """Factory for difficulty levels vocabulary."""
    
    def __call__(self, context=None):
        """Create and return the difficulty levels vocabulary."""
        from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
        
        terms = []
        for value, title in DIFFICULTY_LEVELS:
            term = SimpleTerm(value=value, token=value, title=title)
            terms.append(term)
        
        return SimpleVocabulary(terms)


# Factory instances
subject_areas_vocabulary_factory = SubjectAreasVocabularyFactory()
grade_levels_vocabulary_factory = GradeLevelsVocabularyFactory()
difficulty_levels_vocabulary_factory = DifficultyLevelsVocabularyFactory() 