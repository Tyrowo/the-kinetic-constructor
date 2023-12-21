from PyQt6.QtCore import QPointF
import pandas as pd
from constants.numerical_constants import DISTANCE
from constants.string_constants import *
from objects.arrow.arrow import Arrow
from typing import TYPE_CHECKING, Dict, Callable

if TYPE_CHECKING:
    from objects.pictograph.pictograph import Pictograph

from utilities.TypeChecking.TypeChecking import Colors, MotionTypes


class ArrowPositioner:
    ### SETUP ###
    def __init__(self, pictograph: "Pictograph") -> None:
        self.letters = pictograph.main_widget.letters
        self.pictograph = pictograph

    ### PUBLIC METHODS ###
    def update_arrow_positions(self) -> None:
        current_letter = self.pictograph.current_letter
        state_dict = self.pictograph.get_state()
        self.set_optimal_or_default_positions(current_letter, state_dict)

    ### POSITIONING LOGIC ###
    def set_optimal_or_default_positions(self, current_letter, state_dict):
        reposition_method = self.get_reposition_method(current_letter)
        reposition_method()

    def get_reposition_method(self, current_letter) -> Callable:
        positioning_methods = {
            "G": self.reposition_GH,
            "H": self.reposition_GH,
            "I": self.reposition_I,
            "P": self.reposition_P,
            "Q": self.reposition_Q,
            "R": self.reposition_R,
        }
        return positioning_methods.get(current_letter, self.set_arrows_by_motion_type)

    def set_arrows_by_motion_type(self) -> None:
        for arrow in self.pictograph.arrows.values():
            if self.is_arrow_movable(arrow):
                self.set_arrow_to_default_loc(arrow)
        for ghost_arrow in self.pictograph.ghost_arrows.values():
            if self.is_arrow_movable(ghost_arrow):
                self.set_arrow_to_default_loc(ghost_arrow)

    ### HELPERS ###
    def is_arrow_movable(self, arrow: Arrow) -> bool:
        return (
            not arrow.is_dragging
            and arrow.motion
            and arrow.motion.motion_type != STATIC
        )

    def find_optimal_locations(self, current_letter) -> Dict | None:
        if not current_letter:
            return None
        current_state = self.pictograph.get_state()
        candidate_states = self.letters.get(current_letter, [])
        for candidate_state in candidate_states:
            if self.compare_states(current_state, candidate_state):
                return candidate_state.get("optimal_locations")
        return None

    def compare_states(self, current_state: Dict, candidate_state: Dict) -> bool:
        relevant_keys = [
            "letter",
            "start_position",
            "end_position",
            "blue_motion_type",
            "blue_rotation_direction",
            "blue_turns",
            "blue_start_location",
            "blue_end_location",
            "red_motion_type",
            "red_rotation_direction",
            "red_turns",
            "red_start_location",
            "red_end_location",
        ]
        return all(
            current_state.get(key) == candidate_state.get(key) for key in relevant_keys
        )

    ### POSITIONING METHODS ###
    def reposition_GH(self) -> None:
        for arrow in [
            self.pictograph.arrows.get(RED),
            self.pictograph.arrows.get(BLUE),
        ]:
            adjustment = self.calculate_GH_adjustment(arrow)
            self.apply_adjustment(arrow, adjustment)

    def reposition_I(self) -> None:
        for arrow in [
            self.pictograph.arrows.get(RED),
            self.pictograph.arrows.get(BLUE),
        ]:
            state = self.pictograph.get_state()
            motion_type = state[f"{arrow.color}_motion_type"]
            adjustment = self.calculate_I_adjustment(arrow, motion_type)
            self.apply_adjustment(arrow, adjustment)

    def reposition_P(self) -> None:
        for arrow in [
            self.pictograph.arrows.get(RED),
            self.pictograph.arrows.get(BLUE),
        ]:
            adjustment = self.calculate_P_adjustment(arrow)
            self.apply_adjustment(arrow, adjustment)

    def reposition_Q(self) -> None:
        for arrow in [
            self.pictograph.arrows.get(RED),
            self.pictograph.arrows.get(BLUE),
        ]:
            adjustment = self.calculate_Q_adjustment(arrow)
            self.apply_adjustment(arrow, adjustment)

    def reposition_R(self) -> None:
        for arrow in [
            self.pictograph.arrows.get(RED),
            self.pictograph.arrows.get(BLUE),
        ]:
            adjustment = self.calculate_R_adjustment(arrow)
            self.apply_adjustment(arrow, adjustment)

    ### ADJUSTMENT CALCULATIONS ###
    def calculate_GH_adjustment(self, arrow: Arrow) -> QPointF:
        distance = 105 if arrow.color == RED else 50
        return self.calculate_adjustment(arrow.location, distance)

    def calculate_I_adjustment(self, arrow: Arrow, motion_type: MotionTypes) -> QPointF:
        distance = 100 if motion_type == PRO else 55
        return self.calculate_adjustment(arrow.location, distance)

    def calculate_P_adjustment(self, arrow: Arrow) -> QPointF:
        distance = 90 if arrow.color == RED else 35
        return self.calculate_adjustment(arrow.location, distance)

    def calculate_Q_adjustment(self, arrow: Arrow) -> QPointF:
        adjustment_dict = {
            RED: {
                CLOCKWISE: {
                    NORTHEAST: QPointF(70, -110),
                    SOUTHEAST: QPointF(110, 70),
                    SOUTHWEST: QPointF(-70, 110),
                    NORTHWEST: QPointF(-110, -70),
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: QPointF(110, -70),
                    SOUTHEAST: QPointF(70, 110),
                    SOUTHWEST: QPointF(-110, 70),
                    NORTHWEST: QPointF(-70, -110),
                },
            },
            BLUE: {
                CLOCKWISE: {
                    NORTHEAST: QPointF(30, -30),
                    SOUTHEAST: QPointF(30, 30),
                    SOUTHWEST: QPointF(-30, 30),
                    NORTHWEST: QPointF(-30, -30),
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: QPointF(30, -30),
                    SOUTHEAST: QPointF(30, 30),
                    SOUTHWEST: QPointF(-30, 30),
                    NORTHWEST: QPointF(-30, -30),
                },
            },
        }
        color_adjustments = adjustment_dict.get(arrow.color, {})
        rotation_adjustments = color_adjustments.get(
            arrow.motion.rotation_direction, {}
        )
        return rotation_adjustments.get(arrow.location, QPointF(0, 0))

    def calculate_R_adjustment(self, arrow: Arrow) -> QPointF:
        adjustment_dict = {
            PRO: {
                CLOCKWISE: {
                    NORTHEAST: QPointF(75, -60),
                    SOUTHEAST: QPointF(60, 75),
                    SOUTHWEST: QPointF(-75, 60),
                    NORTHWEST: QPointF(-60, -75),
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: QPointF(60, -75),
                    SOUTHEAST: QPointF(75, 60),
                    SOUTHWEST: QPointF(-60, 75),
                    NORTHWEST: QPointF(-75, -60),
                },
            },
            ANTI: {
                CLOCKWISE: {
                    NORTHEAST: QPointF(30, -30),
                    SOUTHEAST: QPointF(30, 30),
                    SOUTHWEST: QPointF(-30, 30),
                    NORTHWEST: QPointF(-30, -30),
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: QPointF(35, -25),
                    SOUTHEAST: QPointF(25, 35),
                    SOUTHWEST: QPointF(-35, 25),
                    NORTHWEST: QPointF(-25, -35),
                },
            },
        }
        motion_type_adjustments = adjustment_dict.get(arrow.motion_type, {})
        rotation_adjustments = motion_type_adjustments.get(
            arrow.motion.rotation_direction, {}
        )
        return rotation_adjustments.get(arrow.location, QPointF(0, 0))

    ### UNIVERSAL METHODS ###
    def calculate_adjustment(self, location: str, distance: int) -> QPointF:
        location_adjustments = {
            NORTHEAST: QPointF(distance, -distance),
            SOUTHEAST: QPointF(distance, distance),
            SOUTHWEST: QPointF(-distance, distance),
            NORTHWEST: QPointF(-distance, -distance),
        }
        return location_adjustments.get(location, QPointF(0, 0))

    def apply_adjustment(self, arrow: Arrow, adjustment: QPointF) -> None:
        default_pos = self.get_default_position(arrow)
        arrow_center = arrow.boundingRect().center()
        new_pos = default_pos - arrow_center + adjustment
        arrow.setPos(new_pos)

    ### GETTERS ###
    def get_default_position(self, arrow: Arrow) -> QPointF:
        layer2_points = self.pictograph.grid.get_layer2_points()
        return layer2_points.get(arrow.location, QPointF(0, 0))

    def get_layer2_points(self, grid_mode) -> Dict[str, QPointF]:
        if grid_mode == DIAMOND:
            return self.pictograph.grid.diamond_layer2_points
        elif grid_mode == BOX:
            return self.pictograph.grid.box_layer2_points
        return {}

    ### SETTERS ###
    def set_arrow_to_optimal_loc(self, arrow: Arrow, optimal_locations: Dict) -> None:
        optimal_location = optimal_locations.get(f"optimal_{arrow.color}_location")
        if optimal_location:
            arrow.setPos(optimal_location - arrow.boundingRect().center())

    def set_arrow_to_default_loc(self, arrow: Arrow, _: Dict = None) -> None:
        default_pos = self.get_default_position(arrow)
        adjustment = self.calculate_adjustment(arrow.location, DISTANCE)
        new_pos = default_pos + adjustment - arrow.boundingRect().center()
        arrow.setPos(new_pos)
