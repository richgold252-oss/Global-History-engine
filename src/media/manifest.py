"""Media manifest generation for video production."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logging import get_logger

logger = get_logger(__name__)


class MediaManifest:
    """Represents a production manifest for a video story."""

    def __init__(
        self,
        title: str,
        duration_seconds: int = 60,
        narration: str = "",
        sources: Optional[List[Dict[str, Any]]] = None,
    ):
        """Initialize manifest."""
        self.title = title
        self.duration_seconds = duration_seconds
        self.narration = narration
        self.sources = sources or []
        self.scenes: List[Dict[str, Any]] = []

    def add_scene(
        self,
        scene_number: int,
        duration: int,
        narration: str,
        visual_description: str,
        image_prompt: str,
        video_prompt: str,
        subtitle_text: str,
        transition: str,
        source_references: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add a scene to the manifest."""
        self.scenes.append(
            {
                "scene_number": scene_number,
                "duration": duration,
                "narration": narration,
                "visual_description": visual_description,
                "image_prompt": image_prompt,
                "video_prompt": video_prompt,
                "subtitle_text": subtitle_text,
                "transition": transition,
                "source_references": source_references or [],
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        return {
            "title": self.title,
            "duration_seconds": self.duration_seconds,
            "narration": self.narration,
            "scenes": self.scenes,
            "source_references": self.sources,
        }

    def save(self, output_dir: str = "data/media") -> Path:
        """Save manifest to disk as JSON."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        file_path = path / f"{self.title.lower().replace(' ', '_')}_manifest.json"
        with file_path.open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)

        logger.info(f"Saved media manifest to {file_path}")
        return file_path


def build_manifest_from_script(title: str, script: Dict[str, Any]) -> MediaManifest:
    """Build production manifest from script data."""
    manifest = MediaManifest(
        title=title,
        duration_seconds=script.get("duration_seconds", 60),
        narration=script.get("narration", ""),
        sources=script.get("sources", []),
    )

    narration_segments = script.get("narration", "").split(". ")
    for idx, segment in enumerate(narration_segments[:5], start=1):
        clean_segment = segment.strip()
        if not clean_segment:
            continue

        manifest.add_scene(
            scene_number=idx,
            duration=max(8, int(manifest.duration_seconds / max(len(narration_segments[:5]), 1))),
            narration=clean_segment,
            visual_description=f"Historical illustration depicting {title}",
            image_prompt=f"Documentary style visual for {title}, historical accuracy focus",
            video_prompt=f"Cinematic historical sequence for {title}, educational pacing",
            subtitle_text=clean_segment,
            transition="fade",
            source_references=script.get("sources", [])[:2],
        )

    return manifest
