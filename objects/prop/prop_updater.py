from typing import TYPE_CHECKING, Union

from Enums.MotionAttributes import Colors, Locations, Orientations

if TYPE_CHECKING:
    from objects.prop.prop import Prop


class PropUpdater:
    def __init__(self, prop: "Prop") -> None:
        self.prop = prop
        self.svg_file = self.prop.pictograph.main_widget.svg_manager.get_svg_file(prop)

    def update_prop(
        self, prop_dict: dict[str, Union[Colors, Locations, Orientations]] = None
    ) -> None:

        if prop_dict:
            self.prop.attr_manager.update_attributes(prop_dict)
        self.prop.pictograph.main_widget.svg_manager.update_svg(self.prop)
        self.prop.pictograph.main_widget.svg_manager.update_color(self.prop)
        self.prop.rot_angle_manager.update_prop_rot_angle()
