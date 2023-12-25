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
    alpha_ending_letters,
    beta_ending_letters,
    gamma_ending_letters,
    alpha_starting_letters,
    beta_starting_letters,
    gamma_starting_letters,
)

from data.letter_engine_data import (
    motion_type_combinations,
    motion_type_letter_groups,
    parallel_combinations,
)
from data.positions_map import get_specific_start_end_positions
from objects.motion import Motion
from constants.string_constants import (
    ALPHA,
    BETA,
    BLUE,
    END_POSITION,
    GAMMA,
    PRO,
    RED,
    CLOCKWISE,
    COUNTER_CLOCKWISE,
    EAST,
    NORTH,
    SOUTH,
    START_POSITION,
    WEST,
)

from utilities.TypeChecking.Letters import (
    AlphaEndingLetters,
    BetaEndingLetters,
    GammaEndingLetters,
)
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

        self.pro_motion = self.pictograph.motions[RED] if self.red_motion.motion_type == PRO else self.pictograph.motions[BLUE]
        self.anti_motion = self.pictograph.motions[BLUE] if self.red_motion.motion_type == PRO else self.pictograph.motions[RED]
        
        specific_position: Dict[
            str, SpecificPosition
        ] = get_specific_start_end_positions(
            self.get_motion(RED), self.get_motion(BLUE)
        )
        if specific_position:
            overall_position: Dict[str, Position] = self.get_overall_position(
                specific_position
            )
            start_position = overall_position[START_POSITION]
            end_position = overall_position[END_POSITION]
            motion_letter_group = self.get_motion_type_letter_group()

            filtered_letter_group = self.filter_by_end_position(
                end_position, motion_letter_group
            )

            if not len(filtered_letter_group) == 1:
                filtered_letter_group = self.filter_by_start_position(
                    start_position, filtered_letter_group
                )

            if not len(filtered_letter_group) == 1:
                filtered_letter_group = self.filter_gamma_letters(filtered_letter_group)

            if len(filtered_letter_group) == 1:
                return filtered_letter_group.pop()
            else:
                logging.debug(
                    "Multiple letters returned by get_current_letter: %s",
                    filtered_letter_group,
                )
                return None

    def filter_by_start_position(
        self, start_position: Position, motion_letter_set: Set[Letter]
    ) -> Set[Letter]:
        if start_position == ALPHA:
            filtered_letter_group = list(alpha_starting_letters)
        elif start_position == BETA:
            filtered_letter_group = list(beta_starting_letters)
        elif start_position == GAMMA:
            filtered_letter_group = list(gamma_starting_letters)

        filtered_letter_group_values = [
            letter.value for letter in filtered_letter_group
        ]
        motion_letter_set_values = [letter for letter in motion_letter_set]

        filtered_letter_group = set(filtered_letter_group_values).intersection(
            motion_letter_set_values
        )

        return filtered_letter_group

    def filter_by_end_position(self, end_position, motion_letter_set) -> Set[Letter]:
        if end_position == ALPHA:
            filtered_letter_group = list(alpha_ending_letters)
        elif end_position == BETA:
            filtered_letter_group = list(beta_ending_letters)
        elif end_position == GAMMA:
            filtered_letter_group = list(gamma_ending_letters)

        filtered_letter_group_values = [
            letter.value for letter in filtered_letter_group
        ]
        motion_letter_set_values = [letter for letter in motion_letter_set]

        filtered_letter_group = set(filtered_letter_group_values).intersection(
            motion_letter_set_values
        )

        return filtered_letter_group

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

    def filter_gamma_non_hybrid(self) -> Literal["MNO", "PQR"]:
        if self.is_parallel():
            return "MNO"  # Return parallel group
        else:
            return "PQR"  # Return antiparallel group

    def filter_gamma_letters(self, letter_group) -> GammaEndingLetters:
        gamma_handpath_letters = set(self.get_gamma_handpath_group())
        filtered_letter_group = {
            letter for letter in letter_group if letter in gamma_handpath_letters
        }

        # Opp/same handpath logic
        if any(letter in "MNOPQR" for letter in filtered_letter_group):
            gamma_opp_handpath_letters = set(self.filter_gamma_non_hybrid())
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
                    if self.red_motion.motion_type == "anti"
                    else self.blue_motion
                )
                filtered_letter_group = {self.filter_for_U_or_V()}

        return filtered_letter_group

    def get_overall_position(
        self, specific_positions: SpecificStartEndPositionsDicts
    ) -> Position:
        return {position: value[:-1] for position, value in specific_positions.items()}



    def determine_leading_motion(self, pro_start, pro_end, anti_start, anti_end):
        """Determines which motion is leading in the rotation sequence."""
        # If the start location of one motion is the same as the end location of the other, it's leading
        if pro_start == anti_end:
            return "pro"
        elif anti_start == pro_end:
            return "anti"
        return None  # Leading motion cannot be determined

    def filter_for_U_or_V(self):
        """Determines if the pictograph represents 'U' or 'V'."""
        leading_motion = self.determine_leading_motion(
            self.pro_motion.start_location,
            self.pro_motion.end_location,
            self.anti_motion.start_location,
            self.anti_motion.end_location,
        )

        if leading_motion == "pro":
            return "U"
        elif leading_motion == "anti":
            return "V"
        return None  # Letter cannot be determined
