"""Interface definitions for hexagonal architecture."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from .core import Video


class VideoRepository(ABC):
    """Interface for video repository operations."""

    @abstractmethod
    def get_videos(self) -> List[Video]:
        """Get list of available videos."""
        pass

    @abstractmethod
    def sync_videos(self) -> None:
        """Synchronize videos with remote source."""
        pass

    @abstractmethod
    def download_video(self, video_id: str, local_path: Path) -> bool:
        """Download video to local path."""
        pass

    @abstractmethod
    def delete_video(self, video_id: str) -> bool:
        """Delete video from repository."""
        pass


class VideoPlayer(ABC):
    """Interface for video player operations."""

    @abstractmethod
    def play(self, video_path: str) -> bool:
        """Play video file."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop video playback."""
        pass

    @abstractmethod
    def is_playing(self) -> bool:
        """Check if video is playing."""
        pass

    @abstractmethod
    def get_position(self) -> float:
        """Get playback position (0.0 to 1.0)."""
        pass

    @abstractmethod
    def set_position(self, position: float) -> None:
        """Set playback position (0.0 to 1.0)."""
        pass


class Logger(ABC):
    """Interface for logging operations."""

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message."""
        pass