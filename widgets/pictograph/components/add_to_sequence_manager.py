from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from widgets.sequence_widget.sequence_widget_beat_frame.beat import Beat
    from widgets.pictograph.pictograph import Pictograph
    from widgets.sequence_builder.sequence_builder import SequenceBuilder


class AddToSequenceManager:
    def __init__(self, sequence_builder: "SequenceBuilder") -> None:
        self.sequence_builder = sequence_builder

    def create_new_beat(self, clicked_option: "Pictograph") -> "Beat":
        from widgets.sequence_widget.sequence_widget_beat_frame.beat import Beat

        new_beat = Beat(clicked_option.main_widget)
        new_beat.setSceneRect(clicked_option.sceneRect())
        pictograph_dict = clicked_option.get.pictograph_dict()
        new_beat.updater.update_pictograph(pictograph_dict)
        self.sequence_builder.current_pictograph = new_beat
        return new_beat
