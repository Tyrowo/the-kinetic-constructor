from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QTabWidget
from main_window.main_widget.top_builder_widget.sequence_builder.auto_builder.auto_builder import (
    AutoBuilder,
)
from main_window.main_widget.top_builder_widget.sequence_builder.manual_builder import (
    ManualBuilder,
)

if TYPE_CHECKING:
    from main_window.main_widget.top_builder_widget.top_builder_widget import (
        TopBuilderWidget,
    )


class SequenceBuilder(QTabWidget):
    def __init__(self, top_builder_widget: "TopBuilderWidget") -> None:
        super().__init__(top_builder_widget)
        self.top_builder_widget = top_builder_widget
        self.main_widget = top_builder_widget.main_widget

        # Create instances of ManualBuilder and AutoBuilder
        self.manual_builder = ManualBuilder(self)
        self.auto_builder = AutoBuilder(self)

        # Add tabs for both builders
        self.addTab(self.manual_builder, "Manual Builder")
        self.addTab(self.auto_builder, "Auto Builder")

        # Set initial tab to manual builder
        self.load_last_used_builder()

        # resize on tab change
        self.currentChanged.connect(self.on_tab_change)

    def load_last_used_builder(self):
        """Set the last used builder as the current tab."""
        last_used_builder = (
            self.main_widget.settings_manager.builder_settings.get_last_used_builder()
        )

        if last_used_builder == "manual":
            self.setCurrentWidget(self.manual_builder)
        else:
            self.setCurrentWidget(self.auto_builder)
            last_used_auto_builder = (
                self.main_widget.settings_manager.builder_settings.auto_builder.get_current_auto_builder()
            )
            self.auto_builder.load_last_used_auto_builder(last_used_auto_builder)

    def on_tab_change(self):
        """Save the currently selected tab."""
        if self.currentWidget() == self.manual_builder:
            self.main_widget.settings_manager.builder_settings.set_last_used_builder(
                "manual"
            )
        elif self.currentWidget() == self.auto_builder:
            self.main_widget.settings_manager.builder_settings.set_last_used_builder(
                "auto"
            )
            # Save which auto builder is open

        self.resize_current_tab()

    def resize_sequence_builder_tab_widget(self):
        self.manual_builder.resize_manual_builder()
        self.auto_builder.resize_auto_builder()

    def resize_current_tab(self):
        if self.currentWidget() == self.manual_builder:
            self.manual_builder.resize_manual_builder()
        elif self.currentWidget() == self.auto_builder:
            self.auto_builder.resize_auto_builder()
