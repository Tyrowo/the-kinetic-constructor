import logging
from Enums import (
    Color,
    Letter,
    Location,
    MotionAttributesDicts,
    MotionTypeCombination,
    Position,
    RotationDirection,
    SpecificPosition,
    SpecificStartEndPositionsDicts,
)

from data.letter_engine_data import (
    motion_type_combinations,
    motion_type_letter_groups,
    parallel_combinations,
)
from data.positions_map import get_specific_start_end_positions
from objects.motion import Motion
from constants.string_constants import (
    BLUE,
    RED,
    CLOCKWISE,
    COUNTER_CLOCKWISE,
    EAST,
    NORTH,
    SOUTH,
    WEST,
)

from utilities.TypeChecking.Letters import GammaEndingLetters
from utilities.TypeChecking.TypeChecking import LetterGroupsByMotionType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
from typing import TYPE_CHECKING, Dict, Literal, Set, Tuple

if TYPE_CHECKING:
    from objects.pictograph.pictograph import Pictograph


class LetterEngine:
    def __init__(self, pictograph: "Pictograph") -> None:
        self.pictograph = pictograph
        self.letters = pictograph.main_widget.letters
        self.parallel_combinations: Set[
            Tuple[str, str, str, str]
        ] = parallel_combinations
        self.cached_parallel = None
        self.cached_handpath = None

    def get_current_letter(self) -> Letter | None:
        self.red_motion = self.get_motion(RED)
        self.blue_motion = self.get_motion(BLUE)

        state = self.pictograph.get_state()

        specific_position: Dict[
            str, SpecificPosition
        ] = get_specific_start_end_positions(
            self.get_motion(RED), self.get_motion(BLUE)
        )
        if specific_position:
            overall_position: Dict[str, Position] = self.get_overall_position(
                specific_position
            )
            motion_letter_group = self.get_motion_type_letter_group()

            motion_letter_set = set(motion_letter_group)
            filtered_letter_group = {letter.value for letter in Letter}
            filtered_letter_group = {
                letter
                for letter in filtered_letter_group
                if letter in motion_letter_set
            }

            if len(filtered_letter_group) != 1:
                if "gamma" in overall_position.get("end_position", "").lower():
                    filtered_letter_group = self.get_gamma_letter(filtered_letter_group)

            if len(filtered_letter_group) == 1:
                current_letter = filtered_letter_group.pop()
                return current_letter
            else:
                logging.debug(
                    "Multiple letters returned by get_current_letter: %s",
                    filtered_letter_group,
                )
                return None
        else:
            return None

    def get_motion(self, color: Color) -> Motion | None:
        return next(
            (
                motion
                for motion in self.pictograph.motions.values()
                if motion.color == color
            ),
            None,
        )

    def get_motion_type_letter_group(self) -> LetterGroupsByMotionType:
        red_motion_type = self.red_motion.motion_type
        blue_motion_type = self.blue_motion.motion_type

        motion_type_combination: MotionTypeCombination = motion_type_combinations.get(
            (red_motion_type, blue_motion_type)
        )
        motion_type_letter_group: LetterGroupsByMotionType = (
            motion_type_letter_groups.get(motion_type_combination, "")
        )

        self.motion_type_combination = motion_type_combination
        self.motion_letter_group = motion_type_letter_group

        return motion_type_letter_group

    def is_parallel(self) -> bool:
        red_start = self.red_motion.start_location
        red_end = self.red_motion.end_location

        blue_start = self.blue_motion.start_location
        blue_end = self.blue_motion.end_location

        parallel_check_result = (
            red_start,
            red_end,
            blue_start,
            blue_end,
        ) in self.parallel_combinations

        return parallel_check_result

    def determine_handpath_direction_relationship(self) -> Literal["same", "opp", None]:
        clockwise = ["n", "e", "s", "w"]

        # Function to calculate direction
        def calculate_direction(start, end) -> RotationDirection:
            return (clockwise.index(end) - clockwise.index(start)) % len(clockwise)

        # Check if all arrow locations are valid
        arrow_locations = [
            self.red_motion.start_location,
            self.red_motion.end_location,
            self.blue_motion.start_location,
            self.blue_motion.end_location,
        ]
        if not all(location in clockwise for location in arrow_locations):
            return None

        # Calculate directions for red and blue arrows
        red_direction = calculate_direction(
            self.red_motion.start_location, self.red_motion.end_location
        )
        blue_direction = calculate_direction(
            self.blue_motion.start_location, self.blue_motion.end_location
        )

        # Determine handpath direction relationship
        handpath_direction_relationship = (
            "same" if red_direction == blue_direction else "opp"
        )
        self.handpath_direction_relationship = handpath_direction_relationship
        return handpath_direction_relationship

    def get_gamma_handpath_group(self) -> Literal["MNOPQR", "STUV"]:
        gamma_handpath_group = {
            "opp": "MNOPQR",
            "same": "STUV",
        }
        handpath_type = self.determine_handpath_direction_relationship()
        return gamma_handpath_group.get(handpath_type, "")

    def get_gamma_opp_handpath_letter_group(self) -> Literal["MNO", "PQR"]:
        if self.is_parallel():
            return "MNO"  # Return parallel group
        else:
            return "PQR"  # Return antiparallel group

    def get_gamma_letter(self, letter_group) -> GammaEndingLetters:
        gamma_handpath_letters = set(self.get_gamma_handpath_group())
        filtered_letter_group = {
            letter for letter in letter_group if letter in gamma_handpath_letters
        }

        # Opp/same handpath logic
        if any(letter in "MNOPQR" for letter in filtered_letter_group):
            gamma_opp_handpath_letters = set(self.get_gamma_opp_handpath_letter_group())
            filtered_letter_group = {
                letter
                for letter in filtered_letter_group
                if letter in gamma_opp_handpath_letters
            }

        if any(letter in "STUV" for letter in filtered_letter_group):
            if self.motion_type_combination == "pro_vs_anti":
                self.pro_motion = (
                    self.red_motion
                    if self.red_motion.motion_type == "pro"
                    else self.blue_motion
                )
                self.anti_motion = (
                    self.red_motion
                    if self.red_motion.motion_type == "ANTI"
                    else self.blue_motion
                )
                gamma_same_handpath_hybrid_letter = (
                    self.get_gamma_same_handpath_hybrid_letter()
                )
                filtered_letter_group = {
                    letter
                    for letter in filtered_letter_group
                    if letter == gamma_same_handpath_hybrid_letter
                }

        return filtered_letter_group

    def get_overall_position(
        self, specific_positions: SpecificStartEndPositionsDicts
    ) -> Position:
        return {position: value[:-1] for position, value in specific_positions.items()}

    def get_handpath_rotation_direction(
        self, start, end
    ) -> Literal["ccw", "cw"] | None:
        """Returns COUNTER_CLOCKWISE if the handpath direction is counter-clockwise, CLOCKWISE otherwise."""
        ccw_positions = [NORTH, WEST, SOUTH, EAST]
        start_index = ccw_positions.index(start)
        end_index = ccw_positions.index(end)
        if start_index == 3 and end_index == 0:
            return COUNTER_CLOCKWISE
        elif start_index == 0 and end_index == 3:
            return CLOCKWISE
        elif start_index < end_index:
            return COUNTER_CLOCKWISE
        elif start_index > end_index:
            return CLOCKWISE

    def determine_leader_and_same_handpath_hybrid(
        self,
    ) -> Literal["leading_pro", "leading_ANTI"] | None:
        """Determine the leading arrow and whether the handpath is a hybrid of same-direction motion."""
        pro_handpath_direction = self.get_handpath_rotation_direction(
            self.pro_motion.start_location, self.pro_motion.end_location
        )
        anti_handpath_direction = self.get_handpath_rotation_direction(
            self.anti_motion.start_location,
            self.anti_motion.end_location,
        )

        if pro_handpath_direction != anti_handpath_direction:
            logging.ERROR(
                "Cannot disambiguate U and V. Handpath directions aren't the same."
            )
            return None, ""
        else:
            handpath_direction = pro_handpath_direction

        ccw_positions = [NORTH, WEST, SOUTH, EAST]
        pro_start_index = ccw_positions.index(self.pro_motion.start_location)
        anti_start_index = ccw_positions.index(self.anti_motion.start_location)

        if (
            handpath_direction == CLOCKWISE
            and (anti_start_index - pro_start_index) % len(ccw_positions) == 1
        ):
            return "leading_pro"
        elif (
            handpath_direction == CLOCKWISE
            and (pro_start_index - anti_start_index) % len(ccw_positions) == 1
        ):
            return "leading_anti"
        elif (
            handpath_direction == COUNTER_CLOCKWISE
            and (pro_start_index - anti_start_index) % len(ccw_positions) == 1
        ):
            return "leading_pro"
        elif (
            handpath_direction == COUNTER_CLOCKWISE
            and (anti_start_index - pro_start_index) % len(ccw_positions) == 1
        ):
            return "leading_ANTI"

    def get_gamma_same_handpath_hybrid_letter(self) -> Literal["U", "V"]:
        gamma_same_handpath_hybrid_group = {
            "leading_pro": "U",
            "leading_ANTI": "V",
        }
        same_handpath_hybrid_type = self.determine_leader_and_same_handpath_hybrid()

        gamma_same_handpath_hybrid_letter: Literal[
            "U", "V"
        ] = gamma_same_handpath_hybrid_group.get(same_handpath_hybrid_type, "")
        return gamma_same_handpath_hybrid_letter
