

from typing import TYPE_CHECKING

from objects.prop.prop_placement_manager.beta_prop_direction_calculator import (
    BetaPropDirectionCalculator,
)
from objects.prop.prop_placement_manager.beta_prop_positioner import BetaPropPositioner
from objects.prop.prop_placement_manager.default_prop_positioner import (
    DefaultPropPositioner,
)
from objects.prop.prop_placement_manager.prop_offset_calculator import (
    PropOffsetCalculator,
)


if TYPE_CHECKING:
    from widgets.pictograph.pictograph import Pictograph


class PropPlacementManager:
    def __init__(self, pictograph: "Pictograph") -> None:
        self.pictograph = pictograph
        
        # Positioners
        self.default_positioner = DefaultPropPositioner(self)
        self.beta_positioner = BetaPropPositioner(self)
        
        # Calculators
        self.offset_calculator = PropOffsetCalculator(self)
        self.dir_calculator = BetaPropDirectionCalculator(self)

    def update_prop_positions(self) -> None:
        for prop, ghost_prop in zip(
            self.pictograph.props.values(), self.pictograph.ghost_props.values()
        ):
            self.default_positioner.set_prop_to_default_loc(prop)
            self.default_positioner.set_prop_to_default_loc(ghost_prop)
            
        if self.pictograph.has_props_in_beta():
            self.beta_positioner.reposition_beta_props()
