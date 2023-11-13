from PyQt6.QtWidgets import QPushButton, QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout
from objects.arrow import Arrow
from settings.string_constants import ICON_DIR
from settings.styles import (
    ACTION_BUTTON_FONT,
    ACTION_BUTTON_SIZE,
    ACTION_BUTTON_ICON_SIZE,
)


class ActionButtonsFrame(QFrame):
    def __init__(
        self,
        scene,
        json_handler,
        sequence_view,
    ):
        super().__init__()
        self.scene = scene
        self.json_handler = json_handler
        self.sequence_view = sequence_view
        self.action_buttons_layout = QVBoxLayout()
        self.action_buttons_layout.setSpacing(3)
        coordinates = self.scene.get_current_arrow_coordinates()

        buttons_settings = [
            (
                "update_locations.png",
                "Update Optimal Locations",
                lambda: self.json_handler.update_optimal_locations_in_json(coordinates),
            ),
            (
                "delete.png",
                "Delete",
                lambda: self.scene.selectedItems()[0].delete(),
            ),
            (
                "rotate_right.png",
                "Rotate Right",
                lambda: self.scene.selectedItems()[0].rotate(
                    "right",
                ),
            ),
            (
                "rotate_left.png",
                "Rotate Left",
                lambda: self.scene.selectedItems()[0].rotate(
                    "left",
                ),
            ),
            (
                "mirror.png",
                "Mirror",
                lambda: self.scene.selectedItems()[0].mirror(),
            ),
            ("swap.png", "Swap Colors", lambda: self.scene.swap_colors()),
            (
                "select_all.png",
                "Select All",
                lambda: self.scene.select_all_items(),
            ),
            (
                "add_to_sequence.png",
                "Add to Sequence",
                lambda: self.sequence_view.add_to_sequence(self.scene),
            ),
        ]

        # Function to create a congigured button
        def create_and_configure_button(icon_filename, tooltip, on_click):
            icon_path = ICON_DIR + icon_filename
            button = QPushButton(QIcon(icon_path), "")
            button.setToolTip(tooltip)
            button.setFont(ACTION_BUTTON_FONT)
            button.setFixedSize(ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
            button.setIconSize(ACTION_BUTTON_ICON_SIZE)
            button.clicked.connect(on_click)
            return button

        # Create and add buttons to the layout
        for icon_filename, tooltip, action in buttons_settings:
            button = create_and_configure_button(icon_filename, tooltip, action)
            self.action_buttons_layout.addWidget(button)

        self.setLayout(self.action_buttons_layout)

    def get_selected_arrow_color(self):
        selected_items = self.scene.selectedItems()
        if selected_items and isinstance(selected_items[0], Arrow):
            return selected_items[0].color
        return None
