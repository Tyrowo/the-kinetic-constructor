from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from main import MainWindow
    from widgets.pictograph.pictograph import Pictograph


class GlyphVisibilityManager:
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        self.visibility_states: dict[str, bool] = {}

    def toggle_visibility(self, glyph_type):
        if glyph_type in self.visibility_states:
            self.visibility_states[glyph_type] = not self.visibility_states[glyph_type]
            self.apply_visibility(glyph_type)

    def apply_visibility(self, glyph_type, pictograph: "Pictograph"):
        if glyph_type == "VTG":
            pictograph.vtg_glyph.setVisible(self.visibility_states[glyph_type])
        elif glyph_type == "TKA":
            pictograph.tka_glyph.setVisible(self.visibility_states[glyph_type])
        elif glyph_type == "Elemental":
            pictograph.elemental_glyph.setVisible(self.visibility_states[glyph_type])

    def apply_current_visibility_settings(self, pictograph: "Pictograph"):
        for glyph_type in ["VTG", "TKA", "Elemental"]:
            visibility = self.get_glyph_visibility(glyph_type)
            self.visibility_states[glyph_type] = visibility
            self.apply_visibility(glyph_type, pictograph)

    def should_glyph_be_visible(self, glyph_type: str) -> bool:
        return self.get_glyph_visibility(glyph_type)

    def get_glyph_visibility(self, glyph_type: str) -> bool:
        self.settings_manager = self.main_window.settings_manager
        self.settings = self.settings_manager.settings
        return self.settings.get("glyph_visibility", {}).get(glyph_type, True)

    def set_glyph_visibility(self, glyph_type: str, visible: bool) -> None:
        if "glyph_visibility" not in self.settings:
            self.settings["glyph_visibility"] = {}
        self.settings["glyph_visibility"][glyph_type] = visible
        self.settings_manager.save_settings()
        self.apply_glyph_visibility()

    def apply_glyph_visibility(self):
        for pictograph_list in self.main_window.main_widget.all_pictographs.values():
            for pictograph in pictograph_list.values():
                if pictograph.view.isVisible():
                    self.apply_current_visibility_settings(pictograph)

        for beat_view in self.main_window.main_widget.sequence_widget.beats:
            if beat_view.is_filled:
                self.apply_current_visibility_settings(beat_view.beat)
                beat_view.beat.updater.update_pictograph()

        start_pos = (
            (
                self.main_window.main_widget.sequence_widget.beat_frame.start_pos_view.start_pos
            )
            if hasattr(
                self.main_window.main_widget.sequence_widget.beat_frame.start_pos_view,
                "start_pos",
            )
            else None
        )
        if start_pos.view.is_filled:
            self.apply_current_visibility_settings(start_pos)
