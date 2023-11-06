from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtCore import QPointF, Qt
from events.drag.drag_manager import DragManager
import re
from settings.string_constants import *
from utilities.manipulators import Manipulators
from objects.arrow.arrow_positioner import ArrowPositioner
from objects.arrow.arrow_selector import ArrowSelector
from objects.arrow.arrow_state_comparator import ArrowStateComparator
from data.start_end_location_mapping import start_end_location_mapping


class Arrow(QGraphicsSvgItem):
    ARROW_ATTRIBUTES = [
        COLOR,
        MOTION_TYPE,
        ROTATION_DIRECTION,
        QUADRANT,
        START_LOCATION,
        END_LOCATION,
        TURNS,
    ]

    def __init__(self, scene, dict):
        self.svg_file = self.get_svg_file(dict)
        super().__init__(self.svg_file)
        self.initialize_svg_renderer(self.svg_file)
        self.setup_attributes(scene, dict)
        self.initialize_graphics_flags()
        self.setup_handlers()

    def setup_handlers(self):
        self.positioner = ArrowPositioner(self.scene, self)
        self.selector = ArrowSelector(self)
        self.state_comparator = ArrowStateComparator(self)

    def select(self):
        self.setSelected(True)

    def get_svg_file(self, dict):
        motion_type = dict[MOTION_TYPE]
        turns = dict.get(TURNS, None)

        if motion_type in [PRO, ANTI]:
            self.is_shift = True
            return SHIFT_DIR + motion_type + "_" + str(turns) + ".svg"
        elif motion_type in [STATIC]:
            self.is_static = True
            return None

    def setup_attributes(self, scene, dict):
        if scene is not None:
            self.scene = scene
            if hasattr(scene, "infobox"):
                self.infobox = scene.infobox
            self.main_widget = scene.main_widget
            self.in_graphboard = False
            self.drag_offset = QPointF(0, 0)
            self.is_still = False
            self.staff = None
            self.is_mirrored = False
            self.previous_arrow = None
            self.drag_manager = self.main_widget.drag_manager

        self.update_attributes(dict)
        self.update_appearance()
        self.center = self.boundingRect().center()

    def initialize_graphics_flags(self):
        flags = [
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges,
            QGraphicsItem.GraphicsItemFlag.ItemIsFocusable,
            QGraphicsSvgItem.GraphicsItemFlag.ItemIsMovable,
            QGraphicsSvgItem.GraphicsItemFlag.ItemIsSelectable,
        ]

        for flag in flags:
            self.setFlag(flag, True)

        self.setTransformOriginPoint(self.center)

    def initialize_svg_renderer(self, svg_file):
        if getattr(self, "is_shift", False):
            self.renderer = QSvgRenderer(svg_file)
            self.setSharedRenderer(self.renderer)

    ### MOUSE EVENTS ###

    def mousePressEvent(self, event):
        self.drag_start_pos = self.pos()
        self.drag_offset = event.pos()

    def mouseMoveEvent(self, event):
        self.setSelected(True)
        if event.buttons() == Qt.MouseButton.LeftButton:
            from widgets.graph_editor.graphboard.graphboard import Graphboard
            from objects.pictograph.pictograph_view import PictographView

            if isinstance(self.scene, Graphboard):
                self.handle_graphboard_drag(event)
            elif isinstance(self.scene, PictographView):
                self.handle_pictograph_view_drag(event)

    def mouseReleaseEvent(self, event):
        from widgets.graph_editor.graphboard.graphboard import Graphboard
        if isinstance(self.scene, Graphboard):
            self.positioner.update_arrow_position(self.scene)

    def handle_graphboard_drag(self, event):
        """Dragging an arrow that is already in the graphboard"""
        new_pos = self.mapToScene(event.pos()) - self.boundingRect().center()
        self.setPos(new_pos)
        new_quadrant = self.scene.get_graphboard_quadrants(new_pos + self.center)
        if self.quadrant != new_quadrant:
            self.quadrant = new_quadrant
            self.update_appearance()
            (
                self.start_location,
                self.end_location,
            ) = self.attributes.get_start_end_locations(
                self.motion_type, self.rotation_direction, self.quadrant
            )
            self.staff.location = self.end_location
            self.staff.attributes.update_attributes_from_arrow(self)
            self.staff.handler.update_graphboard_staffs(self.scene.graphboard)
            self.scene.graphboard.update()
            self.scene.info_handler.update()

    def handle_pictograph_view_drag(self, event):
        new_pos = self.mapToScene(event.pos()) - self.drag_offset / 2
        self.setPos(new_pos)

    # UPDATE APPEARANCE

    def update_appearance(self):
        self.update_color()
        self.update_rotation()

    def set_svg_color(self, svg_file, new_color):
        color_map = {RED: RED_HEX, BLUE: BLUE_HEX}
        new_hex_color = color_map.get(new_color)

        with open(svg_file, CLOCKWISE) as f:
            svg_data = f.read()

        style_tag_pattern = re.compile(
            r"\.st0{fill\s*:\s*(#[a-fA-F0-9]{6})\s*;}", re.DOTALL
        )
        match = style_tag_pattern.search(svg_data)

        if match:
            old_color = match.group(1)
            svg_data = svg_data.replace(old_color, new_hex_color)
        return svg_data.encode("utf-8")

    def get_svg_data(self, svg_file):
        with open(svg_file, CLOCKWISE) as f:
            svg_data = f.read()
        return svg_data.encode("utf-8")

    def update_color(self):
        if self.motion_type in [PRO, ANTI]:
            new_svg_data = self.set_svg_color(self.svg_file, self.color)

            self.renderer.load(new_svg_data)
            self.setSharedRenderer(self.renderer)

    def update_rotation(self):
        angle = self.get_rotation_angle(
            self.quadrant, self.motion_type, self.rotation_direction
        )
        self.setRotation(angle)

    def get_rotation_angle(self, quadrant, motion_type, rotation_direction):
        quadrant_to_angle = self.get_quadrant_to_angle_map(
            motion_type, rotation_direction
        )
        return quadrant_to_angle.get(quadrant, 0)

    def get_quadrant_to_angle_map(self, motion_type, rotation_direction):
        if motion_type == PRO:
            return {
                CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 270,
                    SOUTHEAST: 180,
                    SOUTHWEST: 90,
                    NORTHWEST: 0,
                },
            }.get(rotation_direction, {})
        elif motion_type == ANTI:
            return {
                CLOCKWISE: {
                    NORTHEAST: 270,
                    SOUTHEAST: 180,
                    SOUTHWEST: 90,
                    NORTHWEST: 0,
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },
            }.get(rotation_direction, {})
        elif motion_type == STATIC:
            return {
                CLOCKWISE: {NORTHEAST: 0, SOUTHEAST: 0, SOUTHWEST: 0, NORTHWEST: 0},
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 0,
                    SOUTHWEST: 0,
                    NORTHWEST: 0,
                },
            }.get(rotation_direction, {})

    def mirror_self(self):
        self.is_mirrored = not self.is_mirrored
        self.setScale(-self.scale())

    def increment_turns(self):
        self.turns += 1
        if self.turns > 2:
            self.turns = 0
        self.update_arrow_svg()
        self.finalize_manipulation()

    def decrement_turns(self):
        self.turns -= 1
        if self.turns < 0:
            self.turns = 2
        self.update_arrow_svg()
        self.finalize_manipulation()

    def set_turns(self, turns):
        self.turns = turns
        self.update_arrow_svg()
        self.finalize_manipulation()

    def update_arrow_svg(self):
        self.svg_file = f"{SHIFT_DIR}{self.motion_type}_{self.turns}.svg"
        self.initialize_svg_renderer(self.svg_file)
        self.update_appearance()

    def finalize_manipulation(self):
        self.arrow_manager.positioner.update_arrow_position(
            self.arrow_manager.graphboard
        )
        self.update_appearance()
        self.infobox.update()
        self.scene.update_staffs(self.scene)
        self.scene.info_handler.update()

    def update_attributes(self, dict):
        for attr in self.ARROW_ATTRIBUTES:
            value = dict.get(attr)
            if attr == TURNS:
                value = int(value)
            setattr(self, attr, value)

        self.attributes = {
            COLOR: dict.get(COLOR, None),
            MOTION_TYPE: dict.get(MOTION_TYPE, None),
            ROTATION_DIRECTION: dict.get(ROTATION_DIRECTION, None),
            QUADRANT: dict.get(QUADRANT, None),
            START_LOCATION: dict.get(START_LOCATION, None),
            END_LOCATION: dict.get(END_LOCATION, None),
            TURNS: dict.get(TURNS, None),
        }

    def create_dict_from_arrow(self, arrow):
        if arrow.motion_type in [PRO, ANTI]:
            start_location, end_location = self.get_start_end_locations(
                arrow.motion_type, arrow.rotation_direction, arrow.quadrant
            )
        elif arrow.motion_type == STATIC:
            start_location, end_location = arrow.start_location, arrow.end_location

        dict = {
            COLOR: arrow.color,
            MOTION_TYPE: arrow.motion_type,
            ROTATION_DIRECTION: arrow.rotation_direction,
            QUADRANT: arrow.quadrant,
            START_LOCATION: start_location,
            END_LOCATION: end_location,
            TURNS: arrow.turns,
        }
        return dict

    def get_attributes(self):
        return {attr: getattr(self, attr) for attr in self.ARROW_ATTRIBUTES}

    def get_start_end_locations(self, motion_type, rotation_direction, quadrant):
        return (
            start_end_location_mapping.get(quadrant, {})
            .get(rotation_direction, {})
            .get(motion_type, (None, None))
        )

    def finalize_manipulation(self):
        self.positioner.update_arrow_position(self.scene)
        self.update_appearance()
        self.scene.update_staffs()
        self.scene.update()
