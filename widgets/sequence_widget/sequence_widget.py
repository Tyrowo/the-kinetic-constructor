from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QHBoxLayout

from widgets.sequence_widget.my_sequence_label import MySequenceLabel
from widgets.sequence_widget.sequence_modifier import SequenceModifier
from ..indicator_label import IndicatorLabel
from ..scroll_area.components.sequence_widget_pictograph_factory import (
    SequenceWidgetPictographFactory,
)
from .sequence_widget_beat_frame.beat import Beat
from .sequence_widget_beat_frame.sequence_widget_beat_frame import (
    SequenceWidgetBeatFrame,
)
from .sequence_widget_button_frame import SequenceWidgetButtonFrame
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from widgets.main_widget.main_widget import MainWidget
    from widgets.main_widget.top_builder_widget import TopBuilderWidget


class SequenceWidget(QWidget):
    def __init__(self, top_builder_widget: "TopBuilderWidget") -> None:
        super().__init__()
        self.top_builder_widget = top_builder_widget
        self.main_widget = top_builder_widget.main_widget
        self._setup_cache()
        self._setup_components()
        self._setup_beat_frame_layout()
        self._setup_indicator_label_layout()
        self._setup_layout()

    def _setup_cache(self):
        self.sequence_widget_pictograph_cache: dict[str, Beat] = {}

    def _setup_components(self):
        self.indicator_label = IndicatorLabel(self)
        self.beat_frame = SequenceWidgetBeatFrame(self)
        self.sequence_modifier = SequenceModifier(self)
        self.button_frame = SequenceWidgetButtonFrame(self)
        self.pictograph_factory = SequenceWidgetPictographFactory(self)
        self.my_sequence_label = MySequenceLabel(self)

    def _setup_beat_frame_layout(self) -> None:
        # hbox with two vboxes inside - beat frame on the left and button frame on the right
        self.beat_frame_layout = QHBoxLayout()
        self.beat_frame_layout.addWidget(self.beat_frame)
        self.beat_frame_layout.addWidget(self.button_frame)

    def _setup_layout(self) -> None:
        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.my_sequence_label,1)
        self.layout.addLayout(self.beat_frame_layout, 19)
        self.layout.addLayout(self.indicator_label_layout, 1)
        self.layout.addWidget(self.sequence_modifier, 10)
        # self.layout.addStretch(1)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _setup_indicator_label_layout(self):
        self.indicator_label_layout = QHBoxLayout()
        self.indicator_label_layout.addStretch(1)
        self.indicator_label_layout.addWidget(self.indicator_label)
        self.indicator_label_layout.addStretch(1)

    def populate_sequence(self, pictograph_dict: dict) -> None:
        pictograph = Beat(self.main_widget)
        pictograph.updater.update_pictograph(pictograph_dict)
        self.beat_frame.add_scene_to_sequence(pictograph)
        pictograph_key = (
            pictograph.main_widget.pictograph_key_generator.generate_pictograph_key(
                pictograph_dict
            )
        )
        self.sequence_widget_pictograph_cache[pictograph_key] = pictograph

    def resize_sequence_widget(self) -> None:
        self.my_sequence_label.resize_my_sequence_label()
        self.beat_frame.resize_beat_frame()
        self.sequence_modifier.resize_sequence_modifier()
        self.indicator_label.resize_indicator_label()
        self.button_frame.resize_button_frame()
