"""
Custom Events for Classroom Management Integration

Events enable loose coupling between features while maintaining
backward compatibility with existing functionality.
"""

from zope.interface import Interface, implementer
from zope.lifecycleevent import ObjectEvent
from datetime import datetime


# Base Object Event Interface (define our own)
class IObjectEvent(Interface):
    """An event related to an object."""


# Event Interfaces
class IHallPassEvent(IObjectEvent):
    """Base interface for hall pass events"""


class IHallPassIssuedEvent(IHallPassEvent):
    """Fired when a hall pass is issued"""


class IHallPassReturnedEvent(IHallPassEvent):
    """Fired when a hall pass is returned"""


class IHallPassWarningEvent(IHallPassEvent):
    """Fired when a hall pass exceeds warning threshold"""


class ISeatingChartUpdatedEvent(IObjectEvent):
    """Fired when seating chart is modified"""


class ITimerCompletedEvent(Interface):
    """Fired when a timer reaches zero"""

    def get_timer_data():
        """Return timer completion data"""


class ISubstituteFolderGeneratedEvent(IObjectEvent):
    """Fired when substitute folder is created"""


# Event Implementations
@implementer(IHallPassIssuedEvent)
class HallPassIssuedEvent(ObjectEvent):
    """Hall pass issued event"""

    def __init__(self, obj, student_name=None, destination=None):
        super(HallPassIssuedEvent, self).__init__(obj)
        self.student_name = student_name
        self.destination = destination


@implementer(IHallPassReturnedEvent)
class HallPassReturnedEvent(ObjectEvent):
    """Hall pass returned event"""

    def __init__(self, obj, duration=None):
        super(HallPassReturnedEvent, self).__init__(obj)
        self.duration = duration


@implementer(IHallPassWarningEvent)
class HallPassWarningEvent(ObjectEvent):
    """Hall pass warning event"""

    def __init__(self, obj, duration=None, alert_level=None):
        super(HallPassWarningEvent, self).__init__(obj)
        self.duration = duration
        self.alert_level = alert_level


@implementer(ISeatingChartUpdatedEvent)
class SeatingChartUpdatedEvent(ObjectEvent):
    """Seating chart updated event"""

    def __init__(self, obj, student_count=None):
        super(SeatingChartUpdatedEvent, self).__init__(obj)
        self.student_count = student_count


@implementer(ITimerCompletedEvent)
class TimerCompletedEvent(object):
    """Timer completed event"""

    def __init__(self, duration=None, timer_type=None, context=None):
        self.duration = duration
        self.timer_type = timer_type
        self.context = context

    def get_timer_data(self):
        return {
            "duration": self.duration,
            "timer_type": self.timer_type,
            "completion_time": str(datetime.now()),
        }


@implementer(ISubstituteFolderGeneratedEvent)
class SubstituteFolderGeneratedEvent(ObjectEvent):
    """Substitute folder generated event"""

    def __init__(self, obj, folder_items=None):
        super(SubstituteFolderGeneratedEvent, self).__init__(obj)
        self.folder_items = folder_items or []
