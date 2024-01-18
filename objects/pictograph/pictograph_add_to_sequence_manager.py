from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QGraphicsScene

from constants import *

if TYPE_CHECKING:
    from objects.pictograph.pictograph import Pictograph
from ..motion.motion import Motion
from ..prop.prop import Prop
from ..arrow.arrow import Arrow
from ..arrow.ghost_arrow import GhostArrow
from ..prop.ghost_prop import GhostProp


class AddToSequenceManager:
    def __init__(self, pictograph: "Pictograph") -> None:
        self.pictograph = pictograph

    def add_to_sequence_callback(self) -> None:
        new_beat = self.create_new_beat()
        self.pictograph.main_widget.main_sequence_widget.beat_frame.add_scene_to_sequence(
            new_beat
        )

    def create_new_beat(self) -> QGraphicsScene:
        from widgets.sequence_widget.beat_frame.beat import Beat

        new_beat = Beat(self.pictograph.main_widget)
        new_beat.setSceneRect(self.pictograph.sceneRect())
        for motion in self.pictograph.motions.values():
            new_beat.motions[motion.color] = Motion(new_beat, motion.get_attributes())
            new_arrow = Arrow(
                new_beat, motion.arrow.get_attributes(), new_beat.motions[motion.color]
            )

            new_prop = Prop(
                new_beat, motion.prop.get_attributes(), new_beat.motions[motion.color]
            )

            new_ghost_arrow = GhostArrow(
                new_beat, motion.arrow.get_attributes(), new_beat.motions[motion.color]
            )

            new_ghost_prop = GhostProp(
                new_beat, motion.prop.get_attributes(), new_beat.motions[motion.color]
            )

            new_beat.arrows[new_arrow.color] = new_arrow
            new_beat.props[new_prop.color] = new_prop

            new_beat.motions[motion.color].arrow = new_arrow
            new_beat.motions[motion.color].prop = new_prop
            new_beat.motions[motion.color].arrow.ghost = new_ghost_arrow
            new_beat.motions[motion.color].prop.ghost = new_ghost_prop

            new_beat.arrows[motion.color] = new_arrow
            new_beat.props[motion.color] = new_prop
            new_beat.ghost_arrows[motion.color] = new_ghost_arrow
            new_beat.ghost_props[motion.color] = new_ghost_prop

            if new_arrow.loc:
                new_arrow.update_arrow()
                new_ghost_arrow.update_arrow()

            if new_prop.loc:
                new_prop.update_prop()
                new_ghost_prop.update_prop()

            new_arrow.ghost = new_ghost_arrow
            new_prop.ghost = new_ghost_prop

            new_arrow.motion = new_beat.motions[motion.color]
            new_prop.motion = new_beat.motions[motion.color]
            new_ghost_arrow.motion = new_beat.motions[motion.color]
            new_ghost_prop.motion = new_beat.motions[motion.color]

            new_ghost_arrow.hide()
            new_ghost_prop.hide()

            motion_dict = self.pictograph.motions[motion.color].get_attributes()
            motion_dict[ARROW] = new_arrow
            motion_dict[PROP] = new_prop
            motion_dict[MOTION_TYPE] = new_arrow.motion_type
            new_arrow.turns = motion_dict[TURNS]
            new_arrow.motion.update_motion(motion_dict)

            new_arrow.setTransformOriginPoint(new_arrow.boundingRect().center())
            new_arrow.ghost.setTransformOriginPoint(
                new_arrow.ghost.boundingRect().center()
            )
            new_arrow.update_arrow()
        new_beat.state_updater.update_pictograph()

        return new_beat
