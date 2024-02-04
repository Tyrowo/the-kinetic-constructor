from typing import TYPE_CHECKING

from ..graphical_object.graphical_object import GraphicalObject
from .prop_attr_manager import PropAttrManager
from .prop_checker import PropChecker
from .prop_mouse_event_handler import PropMouseEventHandler
from .prop_offset_calculator import PropOffsetCalculator
from .prop_rot_angle_manager import PropRotAngleManager
from .prop_updater import PropUpdater
from utilities.TypeChecking.MotionAttributes import Locations, Orientations
from utilities.TypeChecking.TypeChecking import Axes
from utilities.TypeChecking.prop_types import PropTypes


if TYPE_CHECKING:
    from objects.arrow.arrow import Arrow
    from widgets.pictograph.pictograph import Pictograph
    from objects.motion.motion import Motion


class Prop(GraphicalObject):
    loc: Locations
    ori: Orientations = None
    axis: Axes
    prop_type: PropTypes

    def __init__(self, pictograph, prop_dict: dict, motion: "Motion") -> None:
        super().__init__(pictograph)
        self.motion = motion
        self.scene: Pictograph = pictograph
        self.arrow: Arrow
        self.previous_location: Locations
        self.prop_dict = prop_dict
        self.attr_manager = PropAttrManager(self)
        self.rot_angle_manager = PropRotAngleManager(self)
        self.mouse_event_handler = PropMouseEventHandler(self)
        self.prop_updater = PropUpdater(self)
        self.check = PropChecker(self)
        self.offest_calculator = PropOffsetCalculator(self)
        self.updater = PropUpdater(self)

    ### MOUSE EVENTS ###

    def mousePressEvent(self, event) -> None:
        self.mouse_event_handler.handle_mouse_press()

    def mouseMoveEvent(self, event) -> None:
        self.mouse_event_handler.handle_mouse_move(event)

    def mouseReleaseEvent(self, event) -> None:
        self.mouse_event_handler.handle_mouse_release(event)
