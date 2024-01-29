from typing import TYPE_CHECKING
from objects.prop.prop import Prop
from utilities.TypeChecking.TypeChecking import Directions
from .big_prop_positioner import BigPropPositioner
from .prop_classifier import PropClassifier
from .reposition_beta_props_by_letter_manager import RepositionBetaPropsByLetterManager
from .small_prop_positioner import SmallPropPositioner
from .swap_beta_handler import SwapBetaHandler

if TYPE_CHECKING:
    from widgets.pictograph.pictograph import Pictograph
    from ..prop_placement_manager import PropPlacementManager


class BetaPropPositioner:
    def __init__(self, ppm: "PropPlacementManager") -> None:
        self.pictograph: "Pictograph" = ppm.pictograph
        self.ppm = ppm

        self.reposition_beta_props_by_letter_manager = (
            RepositionBetaPropsByLetterManager(self)
        )
        self.small_prop_positioner = SmallPropPositioner(self)
        self.big_prop_positioner = BigPropPositioner(self)
        self.swap_beta_handler = SwapBetaHandler(self)
        self.classifier = PropClassifier(self.pictograph)

    def reposition_beta_props(self) -> None:
        if len(self.classifier.big_props) == 2:
            self.big_prop_positioner.reposition()
        elif len(self.classifier.small_props) == 2:
            self.small_prop_positioner.reposition()
        self.swap_beta_handler.swap_beta_if_needed()

    def move_prop(self, prop: Prop, direction: Directions) -> None:
        offset = self.ppm.offset_calculator.calculate_new_position_with_offset(
            prop.pos(), direction
        )
        prop.setPos(offset)
