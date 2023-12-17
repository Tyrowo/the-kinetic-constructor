from typing import TYPE_CHECKING, List

from PyQt6.QtWidgets import (
    QGridLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from constants.string_constants import BLUE, RED
from widgets.sequence_widget.beat_frame.beat import Beat
from widgets.sequence_widget.beat_frame.start_position import StartPosition
from widgets.sequence_widget.beat_frame.start_position_view import StartPositionView


if TYPE_CHECKING:
    from widgets.main_widget import MainWidget
    from objects.pictograph.pictograph import Pictograph
    from widgets.sequence_widget.sequence_widget import SequenceWidget

from widgets.sequence_widget.beat_frame.beat_view import BeatView


class BeatFrame(QFrame):
    picker_updater: pyqtSignal = pyqtSignal(dict)
    COLUMN_COUNT = 5  # Increased to 5 because of the extra column for StartPosition

    def __init__(
        self,
        main_widget: "MainWidget",
        pictograph: "Pictograph",
        sequence_widget: "SequenceWidget",
    ) -> None:
        super().__init__()
        self.main_widget = main_widget
        self.pictograph = pictograph
        self.sequence_widget = sequence_widget
        self.beats: List[BeatView] = []
        self.layout: QGridLayout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add StartPositionView to the first column of the first row
        self.start_position = StartPosition(main_widget, self)
        self.start_position_view = StartPositionView(self.start_position)
        self.layout.addWidget(
            self.start_position_view, 0, 0
        )  # Occupies the first column

        # Populate the first row with beats from the second to the fifth column
        for i in range(1, self.COLUMN_COUNT):
            self._add_beat_to_layout(0, i)

        # Populate the second to fourth row, starting from the first column
        for j in range(1, 4):  # Starting from the second row
            for i in range(1, self.COLUMN_COUNT):  # Starting from the first column
                self._add_beat_to_layout(j, i)

        self.start_position_view.setMaximumHeight(
            int(self.start_position_view.width() * 90 / 75)
        )  # Maintain aspect ratio

    def _add_beat_to_layout(self, row: int, col: int):
        beat_view = BeatView(self)
        beat = Beat(self.main_widget, self)
        beat_view.beat = beat
        self.layout.addWidget(beat_view, row, col)
        self.beats.append(beat_view)

    def add_start_position(self, start_position: "StartPosition"):
        self.start_position_view.set_start_position(start_position)

    def add_scene_to_sequence(self, copied_scene: "Pictograph") -> None:
        next_beat_index = self.find_next_available_beat()
        if next_beat_index is not None:
            self.beats[next_beat_index].set_pictograph(copied_scene)
        new_motions = {
            "red_motion": copied_scene.motions[RED],
            "blue_motion": copied_scene.motions[BLUE],
        }

        self.picker_updater.emit(new_motions)

    def find_next_available_beat(self) -> int:
        for i, beat in enumerate(self.beats):
            if beat.scene() is None or beat.scene().items() == []:
                return i
        return None

    def get_last_beat(self) -> BeatView:
        for beat in reversed(self.beats):
            if beat.scene() is not None and beat.scene().items() != []:
                return beat
        return self.beats[0]

    def resize_beat_frame(self) -> None:
        beat_width = int(self.width() / 4)
        beat_height = int(beat_width * 90 / 75)

        for beat in self.beats:
            beat.setMaximumHeight(beat_height)
            beat.setMinimumWidth(beat_width)
