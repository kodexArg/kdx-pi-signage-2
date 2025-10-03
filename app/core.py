"""Core domain entities for video signage system."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Video:
    """Video entity representing a video file."""

    id: str
    name: str
    path: Path
    size: int
    modified_time: datetime
    checksum: str
    drive_id: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if video file exists and is accessible."""
        return self.path.exists() and self.path.is_file()


@dataclass
class Playlist:
    """Playlist entity managing video playback order."""

    videos: List[Video]
    current_index: int = 0
    shuffle: bool = False

    def get_next_video(self) -> Optional[Video]:
        """Get next video in playlist."""
        if not self.videos:
            return None

        if self.shuffle:
            import random
            return random.choice(self.videos)

        video = self.videos[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.videos)
        return video

    def add_video(self, video: Video) -> None:
        """Add video to playlist."""
        self.videos.append(video)

    def remove_video(self, video_id: str) -> None:
        """Remove video from playlist."""
        self.videos = [v for v in self.videos if v.id != video_id]

    def get_video_by_id(self, video_id: str) -> Optional[Video]:
        """Get video by ID."""
        return next((v for v in self.videos if v.id == video_id), None)