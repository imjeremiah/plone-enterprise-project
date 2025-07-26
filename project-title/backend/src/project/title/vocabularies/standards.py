"""
Standards Vocabulary for K-12 Educational Platform

This module provides vocabularies for educational standards alignment,
including Common Core State Standards and state-specific standards.
Designed for teachers to easily tag lesson plans and content.
"""

from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
import logging

logger = logging.getLogger(__name__)


# Common Core State Standards - Math (Grade K-12)
CCSS_MATH_STANDARDS = [
    # Kindergarten Math
    ("CCSS.MATH.K.CC.A.1", "K.CC.A.1 - Count to 100 by ones and by tens"),
    ("CCSS.MATH.K.CC.A.2", "K.CC.A.2 - Count forward beginning from a given number"),
    ("CCSS.MATH.K.CC.A.3", "K.CC.A.3 - Write numbers from 0 to 20"),
    (
        "CCSS.MATH.K.CC.B.4",
        "K.CC.B.4 - Understand the relationship between numbers and quantities",
    ),
    ("CCSS.MATH.K.CC.B.5", 'K.CC.B.5 - Count to answer "how many?" questions'),
    (
        "CCSS.MATH.K.OA.A.1",
        "K.OA.A.1 - Represent addition and subtraction with objects",
    ),
    ("CCSS.MATH.K.OA.A.2", "K.OA.A.2 - Solve addition and subtraction word problems"),
    ("CCSS.MATH.K.OA.A.3", "K.OA.A.3 - Decompose numbers less than or equal to 10"),
    ("CCSS.MATH.K.NBT.A.1", "K.NBT.A.1 - Compose and decompose numbers from 11 to 19"),
    ("CCSS.MATH.K.MD.A.1", "K.MD.A.1 - Describe measurable attributes of objects"),
    (
        "CCSS.MATH.K.MD.A.2",
        "K.MD.A.2 - Directly compare two objects with a measurable attribute",
    ),
    ("CCSS.MATH.K.MD.B.3", "K.MD.B.3 - Classify objects into given categories"),
    (
        "CCSS.MATH.K.G.A.1",
        "K.G.A.1 - Describe objects in the environment using names of shapes",
    ),
    (
        "CCSS.MATH.K.G.A.2",
        "K.G.A.2 - Correctly name shapes regardless of their orientations",
    ),
    (
        "CCSS.MATH.K.G.A.3",
        "K.G.A.3 - Identify shapes as two-dimensional or three-dimensional",
    ),
    (
        "CCSS.MATH.K.G.B.4",
        "K.G.B.4 - Analyze and compare two- and three-dimensional shapes",
    ),
    ("CCSS.MATH.K.G.B.6", "K.G.B.6 - Compose simple shapes to form larger shapes"),
    # 1st Grade Math
    (
        "CCSS.MATH.1.OA.A.1",
        "1.OA.A.1 - Use addition and subtraction within 20 to solve problems",
    ),
    (
        "CCSS.MATH.1.OA.A.2",
        "1.OA.A.2 - Solve word problems that call for addition of three whole numbers",
    ),
    (
        "CCSS.MATH.1.OA.B.3",
        "1.OA.B.3 - Apply properties of operations as strategies to add and subtract",
    ),
    (
        "CCSS.MATH.1.OA.B.4",
        "1.OA.B.4 - Understand subtraction as an unknown-addend problem",
    ),
    ("CCSS.MATH.1.OA.C.5", "1.OA.C.5 - Relate counting to addition and subtraction"),
    ("CCSS.MATH.1.OA.C.6", "1.OA.C.6 - Add and subtract within 20"),
    ("CCSS.MATH.1.OA.D.7", "1.OA.D.7 - Understand the meaning of the equal sign"),
    (
        "CCSS.MATH.1.OA.D.8",
        "1.OA.D.8 - Determine the unknown whole number in an addition or subtraction equation",
    ),
    (
        "CCSS.MATH.1.NBT.A.1",
        "1.NBT.A.1 - Count to 120, starting at any number less than 120",
    ),
    (
        "CCSS.MATH.1.NBT.B.2",
        "1.NBT.B.2 - Understand that the two digits of a two-digit number represent amounts of tens and ones",
    ),
    (
        "CCSS.MATH.1.NBT.B.3",
        "1.NBT.B.3 - Compare two two-digit numbers based on meanings of the tens and ones digits",
    ),
    ("CCSS.MATH.1.NBT.C.4", "1.NBT.C.4 - Add within 100"),
    (
        "CCSS.MATH.1.NBT.C.5",
        "1.NBT.C.5 - Given a two-digit number, mentally find 10 more or 10 less",
    ),
    ("CCSS.MATH.1.NBT.C.6", "1.NBT.C.6 - Subtract multiples of 10 in the range 10-90"),
    # 2nd Grade Math (Key Standards)
    (
        "CCSS.MATH.2.OA.A.1",
        "2.OA.A.1 - Use addition and subtraction within 100 to solve one- and two-step word problems",
    ),
    (
        "CCSS.MATH.2.OA.B.2",
        "2.OA.B.2 - Fluently add and subtract within 20 using mental strategies",
    ),
    (
        "CCSS.MATH.2.NBT.A.1",
        "2.NBT.A.1 - Understand that the three digits of a three-digit number represent amounts",
    ),
    (
        "CCSS.MATH.2.NBT.A.2",
        "2.NBT.A.2 - Count within 1000; skip-count by 5s, 10s, and 100s",
    ),
    (
        "CCSS.MATH.2.NBT.B.5",
        "2.NBT.B.5 - Fluently add and subtract within 100 using strategies",
    ),
    (
        "CCSS.MATH.2.MD.A.1",
        "2.MD.A.1 - Measure the length of an object by selecting and using appropriate tools",
    ),
    (
        "CCSS.MATH.2.MD.C.7",
        "2.MD.C.7 - Tell and write time from analog and digital clocks",
    ),
    (
        "CCSS.MATH.2.MD.C.8",
        "2.MD.C.8 - Solve word problems involving dollar bills, quarters, dimes, nickels, and pennies",
    ),
    # 3rd Grade Math (Key Standards)
    (
        "CCSS.MATH.3.OA.A.3",
        "3.OA.A.3 - Use multiplication and division within 100 to solve word problems",
    ),
    ("CCSS.MATH.3.OA.C.7", "3.OA.C.7 - Fluently multiply and divide within 100"),
    ("CCSS.MATH.3.NBT.A.2", "3.NBT.A.2 - Fluently add and subtract within 1000"),
    (
        "CCSS.MATH.3.NBT.A.3",
        "3.NBT.A.3 - Multiply one-digit whole numbers by multiples of 10",
    ),
    (
        "CCSS.MATH.3.NF.A.1",
        "3.NF.A.1 - Understand a fraction 1/b as the quantity formed by 1 part",
    ),
    (
        "CCSS.MATH.3.NF.A.3",
        "3.NF.A.3 - Explain equivalence of fractions in special cases",
    ),
    (
        "CCSS.MATH.3.MD.A.2",
        "3.MD.A.2 - Measure and estimate liquid volumes and masses of objects",
    ),
    (
        "CCSS.MATH.3.MD.C.7",
        "3.MD.C.7 - Relate area to the operations of multiplication and addition",
    ),
    # 4th Grade Math (Key Standards)
    (
        "CCSS.MATH.4.OA.A.3",
        "4.OA.A.3 - Solve multistep word problems with whole numbers",
    ),
    (
        "CCSS.MATH.4.NBT.A.2",
        "4.NBT.A.2 - Read and write multi-digit whole numbers using base-ten numerals",
    ),
    (
        "CCSS.MATH.4.NBT.B.5",
        "4.NBT.B.5 - Multiply a whole number of up to four digits by a one-digit whole number",
    ),
    (
        "CCSS.MATH.4.NBT.B.6",
        "4.NBT.B.6 - Find whole-number quotients and remainders with up to four-digit dividends",
    ),
    (
        "CCSS.MATH.4.NF.A.1",
        "4.NF.A.1 - Explain why a fraction a/b is equivalent to a fraction (n×a)/(n×b)",
    ),
    (
        "CCSS.MATH.4.NF.B.3",
        "4.NF.B.3 - Understand a fraction a/b with a > 1 as a sum of fractions 1/b",
    ),
    (
        "CCSS.MATH.4.NF.C.7",
        "4.NF.C.7 - Compare two decimals to hundredths by reasoning about their size",
    ),
    # 5th Grade Math (Key Standards)
    (
        "CCSS.MATH.5.OA.A.1",
        "5.OA.A.1 - Use parentheses, brackets, or braces in numerical expressions",
    ),
    (
        "CCSS.MATH.5.NBT.A.3",
        "5.NBT.A.3 - Read, write, and compare decimals to thousandths",
    ),
    ("CCSS.MATH.5.NBT.B.5", "5.NBT.B.5 - Fluently multiply multi-digit whole numbers"),
    (
        "CCSS.MATH.5.NBT.B.6",
        "5.NBT.B.6 - Find whole-number quotients of whole numbers with up to four-digit dividends",
    ),
    (
        "CCSS.MATH.5.NF.A.1",
        "5.NF.A.1 - Add and subtract fractions with unlike denominators",
    ),
    (
        "CCSS.MATH.5.NF.B.4",
        "5.NF.B.4 - Apply and extend previous understandings of multiplication",
    ),
    (
        "CCSS.MATH.5.MD.A.1",
        "5.MD.A.1 - Convert among different-sized standard measurement units",
    ),
    # Middle School Math (6th-8th Grade Key Standards)
    (
        "CCSS.MATH.6.RP.A.1",
        "6.RP.A.1 - Understand the concept of a ratio and use ratio language",
    ),
    (
        "CCSS.MATH.6.RP.A.3",
        "6.RP.A.3 - Use ratio and rate reasoning to solve real-world problems",
    ),
    ("CCSS.MATH.6.NS.A.1", "6.NS.A.1 - Interpret and compute quotients of fractions"),
    (
        "CCSS.MATH.6.EE.A.2",
        "6.EE.A.2 - Write, read, and evaluate expressions in which letters stand for numbers",
    ),
    (
        "CCSS.MATH.6.EE.B.5",
        "6.EE.B.5 - Understand solving an equation or inequality as a process",
    ),
    (
        "CCSS.MATH.6.G.A.1",
        "6.G.A.1 - Find the area of right triangles, other triangles, special quadrilaterals",
    ),
    (
        "CCSS.MATH.7.RP.A.2",
        "7.RP.A.2 - Recognize and represent proportional relationships between quantities",
    ),
    (
        "CCSS.MATH.7.NS.A.1",
        "7.NS.A.1 - Apply and extend previous understandings of addition and subtraction",
    ),
    (
        "CCSS.MATH.7.EE.A.1",
        "7.EE.A.1 - Apply properties of operations as strategies to add, subtract, factor",
    ),
    (
        "CCSS.MATH.7.EE.B.4",
        "7.EE.B.4 - Use variables to represent quantities in a real-world problem",
    ),
    (
        "CCSS.MATH.7.G.A.2",
        "7.G.A.2 - Draw (freehand, with ruler and protractor, and with technology) geometric shapes",
    ),
    (
        "CCSS.MATH.8.NS.A.2",
        "8.NS.A.2 - Use rational approximations of irrational numbers",
    ),
    (
        "CCSS.MATH.8.EE.A.1",
        "8.EE.A.1 - Know and apply the properties of integer exponents",
    ),
    (
        "CCSS.MATH.8.EE.B.5",
        "8.EE.B.5 - Graph proportional relationships, interpreting the unit rate",
    ),
    (
        "CCSS.MATH.8.F.A.1",
        "8.F.A.1 - Understand that a function is a rule that assigns to each input exactly one output",
    ),
    (
        "CCSS.MATH.8.G.A.5",
        "8.G.A.5 - Use informal arguments to establish facts about angle sum and exterior angle",
    ),
]

# Common Core State Standards - English Language Arts (Grade K-12)
CCSS_ELA_STANDARDS = [
    # Kindergarten ELA
    (
        "CCSS.ELA.K.RL.1",
        "K.RL.1 - With prompting and support, ask and answer questions about key details",
    ),
    ("CCSS.ELA.K.RL.2", "K.RL.2 - With prompting and support, retell familiar stories"),
    (
        "CCSS.ELA.K.RL.3",
        "K.RL.3 - With prompting and support, identify characters, settings, and major events",
    ),
    (
        "CCSS.ELA.K.RF.1",
        "K.RF.1 - Demonstrate understanding of the organization and basic features of print",
    ),
    (
        "CCSS.ELA.K.RF.2",
        "K.RF.2 - Demonstrate understanding of spoken words, syllables, and sounds",
    ),
    (
        "CCSS.ELA.K.RF.3",
        "K.RF.3 - Know and apply grade-level phonics and word analysis skills",
    ),
    (
        "CCSS.ELA.K.W.1",
        "K.W.1 - Use a combination of drawing, dictating, and writing to compose opinion pieces",
    ),
    (
        "CCSS.ELA.K.W.2",
        "K.W.2 - Use a combination of drawing, dictating, and writing to compose informative/explanatory texts",
    ),
    (
        "CCSS.ELA.K.SL.1",
        "K.SL.1 - Participate in collaborative conversations with diverse partners",
    ),
    (
        "CCSS.ELA.K.L.1",
        "K.L.1 - Demonstrate command of the conventions of standard English grammar",
    ),
    # 1st Grade ELA
    (
        "CCSS.ELA.1.RL.1",
        "1.RL.1 - Ask and answer questions about key details in a text",
    ),
    (
        "CCSS.ELA.1.RL.2",
        "1.RL.2 - Retell stories, including key details, and demonstrate understanding",
    ),
    (
        "CCSS.ELA.1.RF.1",
        "1.RF.1 - Demonstrate understanding of the organization and basic features of print",
    ),
    (
        "CCSS.ELA.1.RF.2",
        "1.RF.2 - Demonstrate understanding of spoken words, syllables, and sounds",
    ),
    (
        "CCSS.ELA.1.RF.3",
        "1.RF.3 - Know and apply grade-level phonics and word analysis skills",
    ),
    (
        "CCSS.ELA.1.W.1",
        "1.W.1 - Write opinion pieces in which they introduce the topic",
    ),
    (
        "CCSS.ELA.1.W.2",
        "1.W.2 - Write informative/explanatory texts in which they name a topic",
    ),
    (
        "CCSS.ELA.1.SL.1",
        "1.SL.1 - Participate in collaborative conversations with diverse partners",
    ),
    # 2nd Grade ELA
    (
        "CCSS.ELA.2.RL.1",
        "2.RL.1 - Ask and answer such questions as who, what, where, when, why, and how",
    ),
    (
        "CCSS.ELA.2.RL.2",
        "2.RL.2 - Recount stories, including fables and folktales from diverse cultures",
    ),
    (
        "CCSS.ELA.2.RF.3",
        "2.RF.3 - Know and apply grade-level phonics and word analysis skills",
    ),
    (
        "CCSS.ELA.2.RF.4",
        "2.RF.4 - Read with sufficient accuracy and fluency to support comprehension",
    ),
    (
        "CCSS.ELA.2.W.1",
        "2.W.1 - Write opinion pieces in which they introduce the topic or book they are writing about",
    ),
    (
        "CCSS.ELA.2.W.2",
        "2.W.2 - Write informative/explanatory texts in which they introduce a topic",
    ),
    # 3rd Grade ELA
    (
        "CCSS.ELA.3.RL.1",
        "3.RL.1 - Ask and answer questions to demonstrate understanding of a text",
    ),
    (
        "CCSS.ELA.3.RL.2",
        "3.RL.2 - Recount stories, including fables, folktales, and myths from diverse cultures",
    ),
    (
        "CCSS.ELA.3.RF.3",
        "3.RF.3 - Know and apply grade-level phonics and word analysis skills",
    ),
    (
        "CCSS.ELA.3.RF.4",
        "3.RF.4 - Read with sufficient accuracy and fluency to support comprehension",
    ),
    (
        "CCSS.ELA.3.W.1",
        "3.W.1 - Write opinion pieces on topics or texts, supporting a point of view with reasons",
    ),
    (
        "CCSS.ELA.3.W.2",
        "3.W.2 - Write informative/explanatory texts to examine a topic",
    ),
    # 4th Grade ELA
    (
        "CCSS.ELA.4.RL.1",
        "4.RL.1 - Refer to details and examples in a text when explaining what the text says",
    ),
    (
        "CCSS.ELA.4.RL.2",
        "4.RL.2 - Determine a theme of a story, drama, or poem from details in the text",
    ),
    (
        "CCSS.ELA.4.RF.3",
        "4.RF.3 - Know and apply grade-level phonics and word analysis skills",
    ),
    (
        "CCSS.ELA.4.RF.4",
        "4.RF.4 - Read with sufficient accuracy and fluency to support comprehension",
    ),
    (
        "CCSS.ELA.4.W.1",
        "4.W.1 - Write opinion pieces on topics or texts, supporting a point of view",
    ),
    (
        "CCSS.ELA.4.W.2",
        "4.W.2 - Write informative/explanatory texts to examine a topic",
    ),
    # 5th Grade ELA
    (
        "CCSS.ELA.5.RL.1",
        "5.RL.1 - Quote accurately from a text when explaining what the text says explicitly",
    ),
    (
        "CCSS.ELA.5.RL.2",
        "5.RL.2 - Determine a theme of a story, drama, or poem from details in the text",
    ),
    (
        "CCSS.ELA.5.RF.3",
        "5.RF.3 - Know and apply grade-level phonics and word analysis skills",
    ),
    (
        "CCSS.ELA.5.RF.4",
        "5.RF.4 - Read with sufficient accuracy and fluency to support comprehension",
    ),
    (
        "CCSS.ELA.5.W.1",
        "5.W.1 - Write opinion pieces on topics or texts, supporting a point of view",
    ),
    (
        "CCSS.ELA.5.W.2",
        "5.W.2 - Write informative/explanatory texts to examine a topic",
    ),
    # Middle School ELA (6th-8th Grade)
    (
        "CCSS.ELA.6.RL.1",
        "6.RL.1 - Cite textual evidence to support analysis of what the text says explicitly",
    ),
    ("CCSS.ELA.6.RL.2", "6.RL.2 - Determine a theme or central idea of a text"),
    (
        "CCSS.ELA.6.W.1",
        "6.W.1 - Write arguments to support claims with clear reasons and relevant evidence",
    ),
    (
        "CCSS.ELA.6.W.2",
        "6.W.2 - Write informative/explanatory texts to examine a topic",
    ),
    (
        "CCSS.ELA.7.RL.1",
        "7.RL.1 - Cite several pieces of textual evidence to support analysis",
    ),
    ("CCSS.ELA.7.RL.2", "7.RL.2 - Determine a theme or central idea of a text"),
    (
        "CCSS.ELA.7.W.1",
        "7.W.1 - Write arguments to support claims with logical reasoning",
    ),
    (
        "CCSS.ELA.7.W.2",
        "7.W.2 - Write informative/explanatory texts to examine a topic",
    ),
    (
        "CCSS.ELA.8.RL.1",
        "8.RL.1 - Cite the textual evidence that most strongly supports an analysis",
    ),
    ("CCSS.ELA.8.RL.2", "8.RL.2 - Determine a theme or central idea of a text"),
    (
        "CCSS.ELA.8.W.1",
        "8.W.1 - Write arguments to support claims with logical reasoning",
    ),
    (
        "CCSS.ELA.8.W.2",
        "8.W.2 - Write informative/explanatory texts to examine a topic",
    ),
]

# Science Standards (Next Generation Science Standards - NGSS)
NGSS_STANDARDS = [
    # Elementary Science
    (
        "NGSS.K.PS2.1",
        "K-PS2-1 - Plan and conduct an investigation to compare the effects of different strengths",
    ),
    (
        "NGSS.K.PS2.2",
        "K-PS2-2 - Analyze data to determine if a design solution works as intended",
    ),
    (
        "NGSS.K.LS1.1",
        "K-LS1-1 - Use observations to describe patterns of what plants and animals need to survive",
    ),
    (
        "NGSS.K.ESS2.1",
        "K-ESS2-1 - Use and share observations of local weather conditions",
    ),
    (
        "NGSS.K.ESS3.1",
        "K-ESS3-1 - Use a model to represent the relationship between the needs of different plants",
    ),
    (
        "NGSS.1.PS4.1",
        "1-PS4-1 - Plan and conduct investigations to provide evidence that vibrating materials can make sound",
    ),
    (
        "NGSS.1.LS1.1",
        "1-LS1-1 - Use materials to design a solution to a human problem by mimicking how plants",
    ),
    (
        "NGSS.1.ESS1.1",
        "1-ESS1-1 - Use observations of the sun, moon, and stars to describe patterns",
    ),
    (
        "NGSS.2.PS1.1",
        "2-PS1-1 - Plan and conduct an investigation to describe and classify different kinds of materials",
    ),
    (
        "NGSS.2.LS2.1",
        "2-LS2-1 - Plan and conduct an investigation to determine if plants need sunlight and water to grow",
    ),
    (
        "NGSS.2.ESS1.1",
        "2-ESS1-1 - Use information from several sources to provide evidence",
    ),
    (
        "NGSS.3.PS2.1",
        "3-PS2-1 - Plan and conduct an investigation to provide evidence of the effects of balanced",
    ),
    (
        "NGSS.3.LS1.1",
        "3-LS1-1 - Develop models to describe that organisms have unique and diverse life cycles",
    ),
    (
        "NGSS.3.ESS2.1",
        "3-ESS2-1 - Represent data in tables and graphical displays to describe typical weather conditions",
    ),
    (
        "NGSS.4.PS3.1",
        "4-PS3-1 - Use evidence to construct an explanation relating the speed of an object",
    ),
    (
        "NGSS.4.LS1.1",
        "4-LS1-1 - Construct an argument that plants and animals have internal and external structures",
    ),
    (
        "NGSS.4.ESS1.1",
        "4-ESS1-1 - Identify evidence from patterns in rock formations and fossils in rock layers",
    ),
    (
        "NGSS.5.PS1.1",
        "5-PS1-1 - Develop a model to describe that matter is made of particles too small to be seen",
    ),
    (
        "NGSS.5.LS1.1",
        "5-LS1-1 - Support an argument that plants get the materials they need for growth",
    ),
    (
        "NGSS.5.ESS1.1",
        "5-ESS1-1 - Develop a model using an example to describe ways the geosphere, biosphere",
    ),
    # Middle School Science
    (
        "NGSS.MS.PS1.1",
        "MS-PS1-1 - Develop models to describe the atomic composition of simple molecules and extended structures",
    ),
    (
        "NGSS.MS.LS1.1",
        "MS-LS1-1 - Conduct an investigation to provide evidence that living things are made of cells",
    ),
    (
        "NGSS.MS.ESS1.1",
        "MS-ESS1-1 - Develop and use a model of the Earth-sun-moon system",
    ),
    (
        "NGSS.MS.ETS1.1",
        "MS-ETS1-1 - Define the criteria and constraints of a design problem",
    ),
]

# Social Studies Standards (National Council for Social Studies - NCSS Thematic Standards)
NCSS_STANDARDS = [
    ("NCSS.1", "NCSS.1 - Culture: How human beings create, learn, and adapt culture"),
    (
        "NCSS.2",
        "NCSS.2 - Time, Continuity, and Change: How human beings view themselves in and over time",
    ),
    (
        "NCSS.3",
        "NCSS.3 - People, Places, and Environments: The study of people, places, and human-environment interactions",
    ),
    (
        "NCSS.4",
        "NCSS.4 - Individual Development and Identity: Personal identity shaped by culture, groups, and institutions",
    ),
    (
        "NCSS.5",
        "NCSS.5 - Individuals, Groups, and Institutions: How institutions are formed, maintained, and changed",
    ),
    (
        "NCSS.6",
        "NCSS.6 - Power, Authority, and Governance: How people create and change structures of power, authority, and governance",
    ),
    (
        "NCSS.7",
        "NCSS.7 - Production, Distribution, and Consumption: How people organize for the production, distribution, and consumption of goods and services",
    ),
    (
        "NCSS.8",
        "NCSS.8 - Science, Technology, and Society: How science and technology affect our lives",
    ),
    (
        "NCSS.9",
        "NCSS.9 - Global Connections: How societies, cultures, and civilizations are connected globally",
    ),
    (
        "NCSS.10",
        "NCSS.10 - Civic Ideals and Practices: How citizens preserve and improve the democratic way of life",
    ),
]


@implementer(IVocabularyFactory)
class StandardsVocabularyFactory:
    """
    Factory for creating educational standards vocabulary.

    Combines Common Core State Standards for Math and ELA,
    Next Generation Science Standards (NGSS), and
    National Council for Social Studies (NCSS) thematic standards.

    This provides teachers with a comprehensive, searchable list
    of standards for lesson planning and content alignment.
    """

    def __call__(self, context=None):
        """Create and return the standards vocabulary."""

        # Combine all standards into one comprehensive list
        all_standards = []
        all_standards.extend(CCSS_MATH_STANDARDS)
        all_standards.extend(CCSS_ELA_STANDARDS)
        all_standards.extend(NGSS_STANDARDS)
        all_standards.extend(NCSS_STANDARDS)

        # Create vocabulary terms
        terms = []
        for standard_id, standard_title in all_standards:
            term = SimpleTerm(
                value=standard_id, token=standard_id, title=standard_title
            )
            terms.append(term)

        # Sort terms by ID for better organization
        terms.sort(key=lambda term: term.value)

        logger.info(f"Created standards vocabulary with {len(terms)} standards")

        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class MathStandardsVocabularyFactory:
    """Factory for creating Math-only standards vocabulary."""

    def __call__(self, context=None):
        """Create and return the math standards vocabulary."""
        terms = []
        for standard_id, standard_title in CCSS_MATH_STANDARDS:
            term = SimpleTerm(
                value=standard_id, token=standard_id, title=standard_title
            )
            terms.append(term)

        terms.sort(key=lambda term: term.value)
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class ELAStandardsVocabularyFactory:
    """Factory for creating ELA-only standards vocabulary."""

    def __call__(self, context=None):
        """Create and return the ELA standards vocabulary."""
        terms = []
        for standard_id, standard_title in CCSS_ELA_STANDARDS:
            term = SimpleTerm(
                value=standard_id, token=standard_id, title=standard_title
            )
            terms.append(term)

        terms.sort(key=lambda term: term.value)
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class ScienceStandardsVocabularyFactory:
    """Factory for creating Science-only standards vocabulary."""

    def __call__(self, context=None):
        """Create and return the science standards vocabulary."""
        terms = []
        for standard_id, standard_title in NGSS_STANDARDS:
            term = SimpleTerm(
                value=standard_id, token=standard_id, title=standard_title
            )
            terms.append(term)

        terms.sort(key=lambda term: term.value)
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class SocialStudiesStandardsVocabularyFactory:
    """Factory for creating Social Studies-only standards vocabulary."""

    def __call__(self, context=None):
        """Create and return the social studies standards vocabulary."""
        terms = []
        for standard_id, standard_title in NCSS_STANDARDS:
            term = SimpleTerm(
                value=standard_id, token=standard_id, title=standard_title
            )
            terms.append(term)

        terms.sort(key=lambda term: term.value)
        return SimpleVocabulary(terms)


# Convenience factory instances
standards_vocabulary_factory = StandardsVocabularyFactory()
math_standards_vocabulary_factory = MathStandardsVocabularyFactory()
ela_standards_vocabulary_factory = ELAStandardsVocabularyFactory()
science_standards_vocabulary_factory = ScienceStandardsVocabularyFactory()
social_studies_standards_vocabulary_factory = SocialStudiesStandardsVocabularyFactory()
