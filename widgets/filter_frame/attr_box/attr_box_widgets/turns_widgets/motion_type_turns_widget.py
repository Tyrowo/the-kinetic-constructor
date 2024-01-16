from typing import TYPE_CHECKING
from objects.pictograph.pictograph import Pictograph
from widgets.filter_frame.attr_box.attr_box_widgets.turns_widgets.base_turns_widget.base_turns_widget import (
    TurnsWidget,
)

if TYPE_CHECKING:
    from widgets.filter_frame.attr_box.motion_type_attr_box import MotionTypeAttrBox


class MotionTypeTurnsWidget(TurnsWidget):
    def __init__(self, attr_box: "MotionTypeAttrBox") -> None:
        """Initialize the IGMotionTypeTurnsWidget."""
        super().__init__(attr_box)
        self.attr_box = attr_box

    def update_turns_display_for_pictograph(self, pictograph: Pictograph) -> None:
        """Update the turnbox display based on the latest turns value of the pictograph."""
        for motion in pictograph.get_motions_by_type(self.attr_box.motion_type):
            self.turn_display_manager.update_turns_display(motion.turns)
            break

    def _update_turns_directly_by_motion_type(self, turns: str) -> None:
        turns = self._convert_turns_from_str_to_num(turns)
        self.turn_direct_set_manager._directly_set_turns(turns)

    def resize_turns_widget(self) -> None:
        self.turn_display_manager.update_turnbox_size()
        self.turn_display_manager.update_adjust_turns_button_size()
