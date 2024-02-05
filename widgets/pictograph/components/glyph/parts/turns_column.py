from PyQt6.QtWidgets import QGraphicsItemGroup
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtSvg import QSvgRenderer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from widgets.pictograph.components.glyph.glyph import Glyph


class TurnsColumn(QGraphicsItemGroup):
    def __init__(self, glyph: "Glyph"):
        super().__init__()
        self.glyph = glyph
        self.top_number_item = None
        self.bottom_number_item = None
        self.svg_path_prefix = "images/numbers/"
        self.blank_svg_path = "images/blank.svg"  # Use for zero turns

    def load_number_svg(self, number: float) -> QGraphicsSvgItem:
        svg_path = (
            self.blank_svg_path
            if number == 0
            else f"{self.svg_path_prefix}{number}.svg"
        )
        renderer = QSvgRenderer(svg_path)
        if renderer.isValid():
            number_item = QGraphicsSvgItem()
            number_item.setSharedRenderer(renderer)
            return number_item
        return None

    def set_number(self, number: float, is_top: bool):
        new_item = self.load_number_svg(number)
        old_item = self.top_number_item if is_top else self.bottom_number_item

        if old_item:
            self.removeFromGroup(old_item)
            old_item.hide()

        if new_item:
            self.addToGroup(new_item)
            if is_top:
                self.top_number_item = new_item
            else:
                self.bottom_number_item = new_item

    def position_turns(self):
        reference_rect = (
            self.glyph.dash.dash_item.sceneBoundingRect()
            if self.glyph.dash.dash_item
            else self.glyph.letter.letter_item.sceneBoundingRect()
        )
        letter_scene_rect = self.glyph.letter.letter_item.sceneBoundingRect()

        base_pos_x = (
            reference_rect.right() + 15
        )  # Fixed padding from the reference point

        # Specific high and low Y positions
        high_pos_y = letter_scene_rect.top() - 5  # Move high number up by 10 pixels
        low_pos_y = (
            letter_scene_rect.bottom()
            - (
                self.bottom_number_item.boundingRect().height()
                if self.bottom_number_item
                else 0
            )
            + 5
        )  # Move low number down by 10 pixels

        if self.top_number_item:
            self.top_number_item.setPos(base_pos_x, high_pos_y)

        if self.bottom_number_item:
            # Adjust low position based on the presence of a top number to maintain vertical spacing
            adjusted_low_pos_y = (
                low_pos_y if self.top_number_item else high_pos_y + 20
            )  # Example spacing if only one number
            self.bottom_number_item.setPos(base_pos_x, adjusted_low_pos_y)

    def update_turns(self, top_turn: float, bottom_turn: float):
        self.set_number(top_turn, is_top=True)
        self.set_number(bottom_turn, is_top=False)
        self.position_turns()
