from typing import TYPE_CHECKING, Union
from Enums.Enums import LetterType

from constants import Type2
from objects.arrow.arrow import Arrow

if TYPE_CHECKING:
    from widgets.pictograph.components.placement_managers.arrow_placement_manager.handlers.turns_tuple_generator.turns_tuple_generator import (
        TurnsTupleGenerator,
    )


class MirroredTurnsTupleGenerator:
    def __init__(self, turns_tuple_generator: "TurnsTupleGenerator"):
        self.turns_tuple_generator = turns_tuple_generator

    def generate(self, arrow: "Arrow") -> Union[str, None]:
        letter = arrow.pictograph.letter
        letter_type = LetterType.get_letter_type(arrow.pictograph.letter)

        if (
            arrow.motion.motion_type
            != arrow.pictograph.get.other_motion(arrow.motion).motion_type
            or letter in ["S", "T"]
            or letter_type == Type2
        ):
            return self.turns_tuple_generator.generate_turns_tuple(arrow.pictograph)

        mirrored_logic = {
            "Type1": self._handle_type1,
            "Type4": self._handle_type4,
            "Type5": self._handle_type56,
            "Type6": self._handle_type56,
        }

        return mirrored_logic.get(letter_type, lambda x: None)(arrow)

    def _handle_type1(self, arrow: Arrow):
        turns_tuple = self.turns_tuple_generator.generate_turns_tuple(arrow.pictograph)
        if (
            arrow.motion.motion_type
            == arrow.pictograph.get.other_motion(arrow.motion).motion_type
        ):
            items = turns_tuple.strip("()").split(", ")
            return f"({items[1]}, {items[0]})"
        return turns_tuple

    def _handle_type4(self, arrow: Arrow):
        turns_tuple = self.turns_tuple_generator.generate_turns_tuple(arrow.pictograph)
        prop_rotation = "cw" if "ccw" in turns_tuple else "ccw"
        turns = turns_tuple[turns_tuple.find(",") + 2 :]
        return (
            f"({prop_rotation}, {turns})"
            if "cw" in turns_tuple or "ccw" in turns_tuple
            else None
        )

    def _handle_type56(self, arrow: Arrow):
        turns_tuple = self.turns_tuple_generator.generate_turns_tuple(arrow.pictograph)
        other_arrow = arrow.pictograph.get.other_arrow(arrow)
        if arrow.motion.turns > 0 and other_arrow.motion.turns > 0:
            items = turns_tuple.strip("()").split(", ")
            return f"({items[0]}, {items[2]}, {items[1]})"
        elif arrow.motion.turns > 0 or other_arrow.motion.turns > 0:
            prop_rotation = "cw" if "ccw" in turns_tuple else "ccw"
            turns = turns_tuple[turns_tuple.find(",") + 2 : -1]
            return f"({prop_rotation}, {turns})"
