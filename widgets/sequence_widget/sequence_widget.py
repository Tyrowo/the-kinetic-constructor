import json
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from widgets.sequence_widget.my_sequence_label import MySequenceLabel
from ..indicator_label import IndicatorLabel
from ..pictograph.pictograph import Pictograph
from ..scroll_area.components.sequence_widget_pictograph_factory import (
    SequenceWidgetPictographFactory,
)
from .sequence_beat_frame.beat import Beat
from .sequence_beat_frame.sequence_beat_frame import SequenceBeatFrame
from .sequence_beat_frame.beat_selection_overlay import BeatSelectionManager
from .button_frame import SequenceButtonFrame
from .sequence_modifier_tab_widget import SequenceModifier
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from widgets.main_widget.main_widget import MainWidget


class SequenceWidget(QWidget):
    def __init__(self, main_widget: "MainWidget") -> None:
        super().__init__()
        self.main_widget = main_widget
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.pictograph_cache: dict[str, Pictograph] = {}
        self.indicator_label = IndicatorLabel(self)
        self.sequence_modifier = SequenceModifier(self)
        self.beat_frame = SequenceBeatFrame(self.main_widget, self)
        self.button_frame = SequenceButtonFrame(self)
        self.pictograph_factory = SequenceWidgetPictographFactory(
            self, self.pictograph_cache
        )
        self.my_sequence_label = MySequenceLabel(self)
        self.beats = self.beat_frame.beats
        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.my_sequence_label)
        self.layout.addWidget(self.beat_frame)
        self.layout.addWidget(self.button_frame)
        self.layout.addWidget(self.indicator_label)
        self.layout.addWidget(self.sequence_modifier)
        # add a stretch
        self.layout.addStretch(1)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def save_sequence(sequence: list[Pictograph], filename: str) -> None:
        sequence_data = [pictograph.get.pictograph_dict() for pictograph in sequence]
        with open(filename, "w") as file:
            json.dump(sequence_data, file, indent=4)

    def populate_sequence(self, pictograph_dict: dict) -> None:
        pictograph = Beat(self.main_widget)
        pictograph.updater.update_pictograph(pictograph_dict)
        self.beat_frame.add_scene_to_sequence(pictograph)
        pictograph_key = (
            pictograph.main_widget.pictograph_key_generator.generate_pictograph_key(
                pictograph_dict
            )
        )
        self.pictograph_cache[pictograph_key] = pictograph

    def resize_sequence_widget(self) -> None:
        self.my_sequence_label.resize_my_sequence_label()
        self.beat_frame.resize_beat_frame()
        self.sequence_modifier.resize_sequence_modifier()
