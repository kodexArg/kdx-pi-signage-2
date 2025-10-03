"""Application layer with use cases for video signage system."""

import logging
import threading
import time
from pathlib import Path
from typing import List, Optional

from .core import Video, Playlist
from .interfaces import VideoPlayer, VideoRepository


class PlaybackService:
    """Service orchestrating video playback and synchronization."""

    def __init__(
        self,
        video_repository: VideoRepository,
        video_player: VideoPlayer,
        videos_dir: str = "videos",
        cache_dir: str = "cache",
        sync_interval: int = 30
    ):
        self.video_repository = video_repository
        self.video_player = video_player
        self.videos_dir = Path(videos_dir)  # Main Google Drive sync folder
        self.cache_dir = Path(cache_dir)    # Metadata and temp files
        self.sync_interval = sync_interval
        self.playlist = Playlist([])
        self._sync_thread = None
        self._playback_thread = None
        self._running = False
        self.logger = logging.getLogger(__name__)

    def start(self) -> None:
        """Start the playback service."""
        self._running = True
        self._initialize_cache()
        self._load_videos()
        self._start_sync_thread()
        self._start_playback_thread()

    def stop(self) -> None:
        """Stop the playback service."""
        self._running = False
        self.video_player.stop()

        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5)

        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=5)

    def _initialize_cache(self) -> None:
        """Initialize cache and video directories."""
        # Main videos directory for Google Drive sync
        self.videos_dir.mkdir(exist_ok=True)

        # Cache directory for metadata and temporary files
        self.cache_dir.mkdir(exist_ok=True)
        (self.cache_dir / "metadata").mkdir(exist_ok=True)
        (self.cache_dir / "temp").mkdir(exist_ok=True)

    def _load_videos(self) -> None:
        """Load videos from repository."""
        try:
            videos = self.video_repository.get_videos()
            self.playlist = Playlist(videos)
            self.logger.info(f"Loaded {len(videos)} videos into playlist")
        except Exception as e:
            self.logger.error(f"Failed to load videos: {e}")

    def _sync_videos(self) -> None:
        """Synchronize videos with remote repository."""
        while self._running:
            try:
                self.logger.info("Starting video synchronization")
                self.video_repository.sync_videos()
                self._load_videos()  # Reload playlist after sync
                self.logger.info("Video synchronization completed")
            except Exception as e:
                self.logger.error(f"Video synchronization failed: {e}")
            finally:
                time.sleep(self.sync_interval)

    def _playback_loop(self) -> None:
        """Main playback loop."""
        while self._running:
            try:
                video = self.playlist.get_next_video()
                if video and video.is_valid():
                    self.logger.info(f"Playing video: {video.name}")
                    self.video_player.play(str(video.path))

                    # Wait for video to complete or check periodically
                    while (
                        self._running
                        and self.video_player.is_playing()
                        and video.is_valid()
                    ):
                        time.sleep(1)

                elif not video:
                    self.logger.warning("No videos available in playlist")
                    time.sleep(5)
                else:
                    self.logger.error(f"Invalid video file: {video.path}")
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Playback error: {e}")
                time.sleep(1)

    def _start_sync_thread(self) -> None:
        """Start background synchronization thread."""
        self._sync_thread = threading.Thread(
            target=self._sync_videos,
            daemon=True,
            name="VideoSync"
        )
        self._sync_thread.start()
        self.logger.info("Video synchronization thread started")

    def _start_playback_thread(self) -> None:
        """Start video playback thread."""
        self._playback_thread = threading.Thread(
            target=self._playback_loop,
            daemon=True,
            name="VideoPlayback"
        )
        self._playback_thread.start()
        self.logger.info("Video playback thread started")

    def get_status(self) -> dict:
        """Get current service status."""
        return {
            "running": self._running,
            "playlist_size": len(self.playlist.videos),
            "current_video": getattr(self.playlist, 'current_video', None),
            "sync_thread_alive": self._sync_thread.is_alive() if self._sync_thread else False,
            "playback_thread_alive": self._playback_thread.is_alive() if self._playback_thread else False,
        }