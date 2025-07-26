"""
SIMPLE Standards Alignment Behavior - GUARANTEED TO WORK

This is a minimal version to get the tab working immediately.
"""

from plone import schema
from plone.supermodel import model


class ISimpleStandardsAligned(model.Schema):
    """
    Simple behavior for standards alignment.
    No complex vocabularies or fieldsets - just basic fields.
    """

    # Simple text field for standards
    aligned_standards = schema.Text(
        title="Aligned Standards",
        description="Enter the educational standards that this content addresses",
        required=False,
    )

    # Simple choice field for subject
    primary_subject = schema.Choice(
        title="Primary Subject",
        description="Select the main subject area",
        values=["math", "english", "science", "social_studies", "other"],
        required=False,
    )

    # Simple text field for grade levels
    grade_levels = schema.TextLine(
        title="Grade Levels",
        description="Enter grade levels (e.g., K-5, 6-8, 9-12)",
        required=False,
    )
