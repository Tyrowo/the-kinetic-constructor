from typing import TYPE_CHECKING, Union
from Enums.MotionAttributes import Turns
from Enums.letters import LetterType
from constants import Type2, Type3

if TYPE_CHECKING:
    from ...pictograph.pictograph import Pictograph
    from widgets.graph_editor.components.GE_turns_widget import GE_TurnsWidget


class GE_TurnsAdjustmentManager:
    def __init__(self, turns_widget: "GE_TurnsWidget") -> None:
        self.turns_widget = turns_widget
        self.graph_editor = self.turns_widget.turns_box.graph_editor

    def adjust_turns(self, adjustment: Turns) -> None:
        self.pictograph = self.graph_editor.GE_pictograph_view.get_current_pictograph()
        turns = self._get_turns()
        turns = self._clamp_turns(turns + adjustment)
        turns = self.convert_turn_floats_to_ints(turns)
        self._update_turns_display(turns)
        self._adjust_turns_for_pictograph(self.pictograph, adjustment)

    def set_turns(self, new_turns: Turns) -> None:
        self.pictograph = self.graph_editor.GE_pictograph_view.get_current_pictograph()
        self._update_motion_properties(new_turns)
        turns = self._get_turns()
        turns = self.convert_turn_floats_to_ints(turns)

        self._update_turns_display(new_turns)

    def get_current_turns_value(self) -> Turns:
        return self._get_turns()

    # Private methods

    def _get_turns(self) -> Turns:
        turns = self.turns_widget.display_manager.turns_display.text()
        turns = self.convert_turns_from_str_to_num(turns)
        turns = self.convert_turn_floats_to_ints(turns)
        return turns

    def convert_turns_from_str_to_num(self, turns) -> Union[int, float]:
        return int(turns) if turns in ["0", "1", "2", "3"] else float(turns)

    def convert_turn_floats_to_ints(self, turns: Turns) -> Turns:
        if turns in [0.0, 1.0, 2.0, 3.0]:
            return int(turns)
        else:
            return turns

    def _clamp_turns(self, turns: Turns) -> Turns:
        return self.turns_widget.updater._clamp_turns(turns)

    def _update_turns_display(self, turns: Turns) -> None:
        self.turns_widget.display_manager.update_turns_display(str(turns))

    def _adjust_turns_for_pictograph(self, pictograph, adjustment) -> None:
        self.turns_widget.updater._adjust_turns_for_pictograph(pictograph, adjustment)

    def _update_motion_properties(self, new_turns) -> None:
        self.pictograph = (
            self.graph_editor.GE_pictograph_view.get_current_pictograph()
        )
        for motion in self.pictograph.motions.values():
            if motion.color == self.turns_widget.turns_box.color:
                self.turns_widget.updater.set_motion_turns(motion, new_turns)
