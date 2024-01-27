from typing import TYPE_CHECKING
from objects.grid import GridPoint
from objects.prop.prop import Prop


if TYPE_CHECKING:
    from ..prop_placement_manager import PropPlacementManager


class DefaultPropPositioner:
    def __init__(self, prop_placement_manager: "PropPlacementManager") -> None:
        self.pictograph = prop_placement_manager.pictograph
        self.prop_placement_manager = prop_placement_manager
        self.location_points_cache = {}

    def set_prop_to_default_loc(self, prop: Prop, strict: bool = False) -> None:
        position_offsets = (
            self.prop_placement_manager.offset_calculator.get_or_calculate_offsets(prop)
        )
        key = (prop.ori, prop.loc)
        offset = position_offsets.get(key)
        prop.setTransformOriginPoint(0, 0)
        location_points = self.get_location_points(strict)

        for location, location_point in location_points.items():
            if prop.loc == location[0]:
                new_position = location_point.coordinates + offset
                prop.setPos(new_position)
                return

    def get_location_points(self, strict: bool) -> dict[str, GridPoint]:
        location_points = (
            self.pictograph.grid.grid_data.hand_points_strict
            if strict
            else self.pictograph.grid.grid_data.hand_points_normal
        )
        return location_points.points
