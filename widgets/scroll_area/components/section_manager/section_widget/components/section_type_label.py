from typing import TYPE_CHECKING
from PyQt6.QtGui import QEnterEvent, QFontMetrics
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from Enums.Enums import LetterType
from PyQt6.QtCore import pyqtSignal


if TYPE_CHECKING:
    from widgets.sequence_builder.components.option_picker.option_picker_section_widget import OptionPickerSectionWidget
    from ..letterbook_section_widget import LetterBookSectionWidget


class SectionTypeLabel(QLabel):
    clicked = pyqtSignal()

    TYPE_MAP = {
        LetterType.Type1: "Dual-Shift",
        LetterType.Type2: "Shift",
        LetterType.Type3: "Cross-Shift",
        LetterType.Type4: "Dash",
        LetterType.Type5: "Dual-Dash",
        LetterType.Type6: "Static",
    }

    COLORS = {
        "Shift": "#6F2DA8",  # purple
        "Dual": "#00b3ff",  # cyan
        "Dash": "#26e600",  # green
        "Cross": "#26e600",  # green
        "Static": "#eb7d00",  # orange
        "-": "#000000",  # black
    }

    def __init__(self, section_widget: "OptionPickerSectionWidget") -> None:
        super().__init__()
        self.section_widget = section_widget
        self.setContentsMargins(0, 0, 0, 0)
        self.set_styled_text(section_widget.letter_type)

    def set_styled_text(self, letter_type: LetterType) -> None:
        type_words = self.TYPE_MAP.get(letter_type, "").split("-")
        letter_type_str = letter_type.name
        styled_words = [
            f"<span style='color: {self.COLORS.get(word, 'black')};'>{word}</span>"
            for word in type_words
        ]

        styled_type_name = (
            "-".join(styled_words)
            if "-" in self.TYPE_MAP.get(letter_type, "")
            else "".join(styled_words)
        )

        styled_text = f"{letter_type_str[0:4]} {letter_type_str[4]}: {styled_type_name}"
        self.setText(styled_text)
        self.resize_section_type_label()

    def font_size(self):
        scroll_area = self.section_widget.scroll_area
        base_class_name = type(scroll_area).__name__

        if base_class_name == "LetterBookScrollArea":
            font_size = scroll_area.width() // 40
        elif base_class_name == "OptionPickerScrollArea":
            font_size = scroll_area.width() // 50
        else:
            font_size = 12
        return font_size

    def set_label_style(self, outline=False):
        oval_height = self.font_size() * 2
        self.setFixedHeight(oval_height)
        border_style = "2px solid black" if outline else "none"
        self.setStyleSheet(
            f"QLabel {{"
            f"  background-color: white;"
            f"  border-radius: {oval_height // 2}px;"  # This creates the oval shape
            f"  font-size: {self.font_size()}px;"
            f"  font-weight: bold;"
            f"  border: {border_style};"
            f"}}"
        )

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_label_style(outline=True)

    def leaveEvent(self, event: QEnterEvent) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.set_label_style()

    def resize_section_type_label(self) -> None:
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add a buffer for padding/margins that may not be accounted for by QFontMetrics
        padding = 10

        label_height = self.font_size() * 2
        label_width = label_height * 5

        self.setFixedSize(label_width, label_height)
        self.setStyleSheet(
            f"QLabel {{"
            f"  background-color: white;"
            f"  border-radius: {label_height // 2}px;"  # Adjust radius to maintain an oval shape
            f"  font-size: {self.font_size()}px;"
            f"  font-weight: bold;"
            f"  padding-left: {padding}px;"
            f"  padding-right: {padding}px;"
            f"}}"
        )
