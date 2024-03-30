from typing import TYPE_CHECKING

from custom_tab_bar import CustomTabBar
from styles.get_tab_stylesheet import get_tab_stylesheet
from widgets.dictionary.dictionary_widget import DictionaryWidget
from widgets.sequence_builder.sequence_builder import SequenceBuilder
from widgets.turn_pattern_widget import TurnPatternWidget
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from ..main_widget.main_widget import MainWidget


class BuilderToolbar(QTabWidget):
    def __init__(self, main_widget: "MainWidget") -> None:
        super().__init__(main_widget)
        self.main_widget = main_widget
        self.sequence_builder = SequenceBuilder(main_widget)
        self.dictionary = DictionaryWidget(main_widget)
        self.turn_pattern_widget = TurnPatternWidget(self)

        self.setTabBar(CustomTabBar())
        self.addTab(self.sequence_builder, "Builder")
        self.addTab(self.dictionary, "Dictionary")
        self.addTab(self.turn_pattern_widget, "Turn Patterns")
        self.currentChanged.connect(self.on_tab_changed)
        self.setStyleSheet(get_tab_stylesheet())

        # Set custom tab bar for handling hover events specifically on tabs

        self.setTabShape(QTabWidget.TabShape.Rounded)
        self.setTabPosition(QTabWidget.TabPosition.North)

    def on_tab_changed(self) -> None:
        current_tab = self.currentWidget()
        beat_frame = self.main_widget.sequence_widget.beat_frame
        if current_tab == self.sequence_builder:
            if beat_frame.start_pos_view.scene():
                if not self.sequence_builder.option_picker.isVisible():
                    self.sequence_builder.transition_to_sequence_building()
        self.resize_current_tab()

    def resize_current_tab(self) -> None:
        current_tab = self.currentWidget()
        if current_tab == self.sequence_builder:
            self.sequence_builder.resize_sequence_builder()
        elif current_tab == self.dictionary:
            self.dictionary.resize_dictionary()
        elif current_tab == self.turn_pattern_widget:
            self.turn_pattern_widget.resize_turn_pattern_widget()
