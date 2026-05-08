"""Scene engine with mandatory environment presets."""

from __future__ import annotations

from typing import Dict

from avatarlm.schemas import ScenePreset


SCENE_PRESETS: Dict[str, ScenePreset] = {
    "beach": ScenePreset(
        scene="beach",
        lighting="warm_sunset",
        sound="ocean_waves",
        camera="slow_dolly_in",
        avatar_spacing="relaxed_medium",
    ),
    "podcast_studio": ScenePreset(
        scene="podcast_studio",
        lighting="soft_indoor_keyfill",
        sound="room_tone_coffee_shop_bed",
        camera="alternating_closeups",
        avatar_spacing="coffee_table_facing",
    ),
    "cliff": ScenePreset(
        scene="cliff",
        lighting="dynamic_wind_light",
        sound="wind_ambience",
        camera="slow_pan",
        avatar_spacing="wide",
    ),
    "jungle": ScenePreset(
        scene="jungle",
        lighting="canopy_dappled",
        sound="insects_and_birds",
        camera="handheld_stabilized",
        avatar_spacing="narrow_path_offset",
    ),
    "lake": ScenePreset(
        scene="lake",
        lighting="blue_hour_reflections",
        sound="gentle_water_and_breeze",
        camera="locked_with_subtle_parallax",
        avatar_spacing="dock_side_by_side",
    ),
    "office": ScenePreset(
        scene="office",
        lighting="neutral_task_lighting",
        sound="low_hvac_room_tone",
        camera="static_presenter_shot",
        avatar_spacing="presentation_distance",
    ),
}


def get_scene_preset(scene: str) -> ScenePreset:
    """Return a scene preset with office as fallback."""
    return SCENE_PRESETS.get(scene.lower(), SCENE_PRESETS["office"])

