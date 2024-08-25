from typing import TYPE_CHECKING
from data.constants import CLOCKWISE, COUNTER_CLOCKWISE, OPP, SAME

from PyQt6.QtWidgets import QFrame, QVBoxLayout

from widgets.graph_editor.ori_picker_box.ori_picker_widget.GE_ori_picker_widget import (
    GE_OriPickerWidget,
)


from .GE_ori_picker_header import GE_OriPickerHeader

if TYPE_CHECKING:
    from widgets.graph_editor.adjustment_panel.GE_adjustment_panel import (
        GE_AdjustmentPanel,
    )
    from widgets.pictograph.pictograph import Pictograph


class GE_OriPickerBox(QFrame):
    def __init__(
        self,
        adjustment_panel: "GE_AdjustmentPanel",
        start_pos: "Pictograph",
        color: str,
    ) -> None:
        super().__init__(adjustment_panel)
        self.adjustment_panel = adjustment_panel
        self.color = color
        self.start_pos = start_pos
        self.graph_editor = self.adjustment_panel.graph_editor
        self.border_width = self.graph_editor.width() // 100

        self.vtg_dir_btn_state: dict[str, bool] = {SAME: False, OPP: False}
        self.prop_rot_dir_btn_state: dict[str, bool] = {
            CLOCKWISE: False,
            COUNTER_CLOCKWISE: False,
        }
        self._setup_widgets()
        self._setup_layout()

    def _setup_widgets(self) -> None:
        self.header = GE_OriPickerHeader(self)
        self.ori_picker_widget = GE_OriPickerWidget(self)

    def _setup_layout(self) -> None:
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.addWidget(self.header)
        layout.addWidget(self.ori_picker_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_styled_border(self) -> None:
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet(
            f"#GE_OriPickerBox {{ border: {self.border_width}px solid {self.color}; }}"
        )

    def resize_ori_picker_box(self) -> None:
        self.header.resize_ori_picker_header()
        self.ori_picker_widget.resize_ori_picker_widget()
