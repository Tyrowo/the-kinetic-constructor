from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
from Enums import LetterType
from utilities.TypeChecking.letter_lists import (
    EIGHT_VARIATIONS,
    FOUR_VARIATIONS,
    SIXTEEN_VARIATIONS,
)
from .components.scroll_area_pictograph_factory import ScrollAreaPictographFactory
from .components.section_manager.codex_section_manager import CodexSectionManager
from .components.codex_display_manager import CodexDisplayManager
from utilities.TypeChecking.TypeChecking import Letters
from ..pictograph.pictograph import Pictograph
from PyQt6.QtGui import QWheelEvent

if TYPE_CHECKING:
    from ..codex.codex import Codex


class CodexScrollArea(QScrollArea):
    def __init__(self, codex: "Codex") -> None:
        super().__init__(codex)
        self.main_widget = codex.main_widget
        self.codex = codex
        self.letters = self.main_widget.letters
        self.pictographs: dict[Letters, Pictograph] = {}
        self.stretch_index = -1
        self._setup_ui()
        self._setup_managers()

    def _setup_managers(self) -> None:
        self.display_manager = CodexDisplayManager(self)
        self.sections_manager = CodexSectionManager(self)
        self.pictograph_factory = ScrollAreaPictographFactory(
            self, self.codex.pictograph_cache
        )

    def _setup_ui(self) -> None:
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.layout: QVBoxLayout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container.setStyleSheet("background-color: #f2f2f2;")

        self.setWidget(self.container)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def fix_stretch(self):
        if self.stretch_index >= 0:
            item = self.layout.takeAt(self.stretch_index)
            del item
        self.layout.addStretch(1)
        self.stretch_index = self.layout.count()

    def insert_widget_at_index(self, widget: QWidget, index: int) -> None:
        self.layout.insertWidget(index, widget)

    def update_pictographs(self, letter_type: LetterType = None) -> None:
        deselected_letters = self.pictograph_factory.get_deselected_letters()
        selected_letters = set(self.codex.selected_letters)

        if self._only_deselection_occurred(deselected_letters, selected_letters):
            for letter in deselected_letters:
                self.pictograph_factory.remove_deselected_letter_pictographs(letter)
        else:
            for letter in deselected_letters:
                self.pictograph_factory.remove_deselected_letter_pictographs(letter)
            self.pictograph_factory.process_selected_letters()
        if letter_type:
            self.display_manager.order_and_display_pictographs(letter_type)

    def _only_deselection_occurred(self, deselected_letters, selected_letters) -> bool:
        if not deselected_letters:
            return False
        if not selected_letters:
            return True

        current_pictograph_letters = {key.split("_")[0] for key in self.pictographs}

        return (
            len(deselected_letters) > 0
            and len(selected_letters) == len(current_pictograph_letters) - 1
        )

    def update_arrow_placements(self) -> None:
        for pictograph in self.pictographs.values():
            pictograph.arrow_placement_manager.update_arrow_placements()

    def calculate_section_indices(self, letter_type: str) -> None:
        selected_letters = [
            letter
            for letter in self.codex.selected_letters
            if self.sections_manager.get_pictograph_letter_type(letter) == letter_type
        ]

        total_variations = sum(
            (
                8
                if letter in EIGHT_VARIATIONS
                else (
                    16
                    if letter in SIXTEEN_VARIATIONS
                    else 4 if letter in FOUR_VARIATIONS else 0
                )
            )
            for letter in selected_letters
        )

        self.display_manager.section_indices[letter_type] = (0, 0)
        for i in range(total_variations):
            row, col = divmod(i, self.display_manager.COLUMN_COUNT)
            self.display_manager.section_indices[letter_type] = (row, col)

    def wheelEvent(self, event: QWheelEvent) -> None:
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.change_pictograph_size(increase=True)
            elif delta < 0:
                self.change_pictograph_size(increase=False)
            event.accept()
        else:
            super().wheelEvent(event)  # Call the parent class's wheel event

    def change_pictograph_size(self, increase: bool) -> None:
        MAX_COLUMN_COUNT = 8
        MIN_COLUMN_COUNT = 3
        current_size = self.display_manager.COLUMN_COUNT

        if increase and current_size > MIN_COLUMN_COUNT:
            self.display_manager.COLUMN_COUNT -= 1
        elif not increase and current_size < MAX_COLUMN_COUNT:
            self.display_manager.COLUMN_COUNT += 1

        self.update_all_pictograph_sizes()

    def update_all_pictograph_sizes(self):
        for letter_type in LetterType:
            self.display_manager.order_and_display_pictographs(letter_type)
