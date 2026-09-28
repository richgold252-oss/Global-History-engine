"""Tests for media manifest generation."""

import json
from pathlib import Path
from src.media.manifest import MediaManifest, build_manifest_from_script


def test_media_manifest_init():
    """Test media manifest initialization."""
    manifest = MediaManifest(
        title="Test Video",
        duration_seconds=60,
        narration="Test narration",
    )
    assert manifest.title == "Test Video"
    assert manifest.duration_seconds == 60
    assert len(manifest.scenes) == 0


def test_media_manifest_add_scene():
    """Test adding scenes to manifest."""
    manifest = MediaManifest(title="Test Video", duration_seconds=60)

    manifest.add_scene(
        scene_number=1,
        duration=12,
        narration="Scene 1 narration",
        visual_description="Visual for scene 1",
        image_prompt="Image prompt",
        video_prompt="Video prompt",
        subtitle_text="Subtitle",
        transition="fade",
    )

    assert len(manifest.scenes) == 1
    assert manifest.scenes[0]["scene_number"] == 1


def test_media_manifest_to_dict():
    """Test manifest conversion to dictionary."""
    manifest = MediaManifest(
        title="Test Video",
        duration_seconds=60,
        narration="Test narration",
    )

    manifest.add_scene(
        scene_number=1,
        duration=60,
        narration="Narration",
        visual_description="Visual",
        image_prompt="Image",
        video_prompt="Video",
        subtitle_text="Subtitle",
        transition="fade",
    )

    result = manifest.to_dict()
    assert isinstance(result, dict)
    assert result["title"] == "Test Video"
    assert result["duration_seconds"] == 60
    assert len(result["scenes"]) == 1


def test_build_manifest_from_script():
    """Test building manifest from script data."""
    script_data = {
        "title": "Test Script",
        "narration": "First sentence. Second sentence. Third sentence.",
        "duration_seconds": 60,
        "sources": [
            {
                "title": "Source 1",
                "publisher": "Pub 1",
                "credibility_score": 90,
            }
        ],
    }

    manifest = build_manifest_from_script("Test Script", script_data)
    assert manifest.title == "Test Script"
    assert len(manifest.scenes) > 0
