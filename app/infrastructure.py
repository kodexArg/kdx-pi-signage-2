"""Infrastructure adapters for video signage system."""

import hashlib
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import os
import platform
import sys
from pathlib import Path

def _get_vlc_paths():
    """Get VLC installation paths based on platform and environment configuration."""
    system = platform.system().lower()

    # First priority: Environment variable VLC_DIR (from pyproject.toml via uv)
    vlc_dir = os.environ.get('VLC_DIR')

    if vlc_dir and os.path.exists(vlc_dir):
        return {
            'base_dir': vlc_dir,
            'plugins_dir': os.path.join(vlc_dir, 'plugins'),
            'source': 'environment'
        }

    # Second priority: Platform-specific default paths
    if system == "windows":
        # Common Windows VLC installation paths
        common_paths = [
            r"C:\Program Files\VideoLAN\VLC",
            r"C:\Program Files (x86)\VideoLAN\VLC",
            r"C:\Users\Kodex\scoop\apps\vlc\current",  # Scoop installation
        ]

        for path in common_paths:
            if os.path.exists(path):
                return {
                    'base_dir': path,
                    'plugins_dir': os.path.join(path, 'plugins'),
                    'source': 'windows_default'
                }

    elif system == "linux":
        # Common Linux VLC installation paths
        common_paths = [
            "/usr/lib/x86_64-linux-gnu/vlc",  # Ubuntu/Debian standard
            "/usr/lib/vlc",                   # Alternative path
            "/usr/local/lib/vlc",             # Local installation
            "/usr/bin/vlc",                   # Raspberry Pi / standard binary location
        ]

        for path in common_paths:
            if os.path.exists(path):
                return {
                    'base_dir': path,
                    'plugins_dir': os.path.join(path, 'plugins'),
                    'source': 'linux_default'
                }

    # If no valid path found, return None
    return None

def _configure_vlc_paths():
    """Configure VLC paths for cross-platform compatibility."""
    vlc_paths = _get_vlc_paths()

    if not vlc_paths:
        print("Warning: No valid VLC installation found")
        return

    base_dir = vlc_paths['base_dir']
    plugins_dir = vlc_paths['plugins_dir']
    source = vlc_paths['source']

    print(f"Using VLC from {source}: {base_dir}")

    # Set environment variables for VLC
    if os.path.exists(plugins_dir):
        os.environ['VLC_PLUGIN_PATH'] = plugins_dir
        print(f"VLC plugins path: {plugins_dir}")
    else:
        print(f"Warning: VLC plugins directory not found: {plugins_dir}")

    # Platform-specific path configuration
    system = platform.system().lower()

    if system == "windows":
        # Add VLC directory to PATH for DLL loading
        os.environ['PATH'] = base_dir + os.pathsep + os.environ.get('PATH', '')

    elif system == "linux":
        # Add to LD_LIBRARY_PATH for Linux
        os.environ['LD_LIBRARY_PATH'] = base_dir + os.pathsep + os.environ.get('LD_LIBRARY_PATH', '')

# Configure VLC paths before importing
_configure_vlc_paths()

import vlc

from .core import Video
from .interfaces import VideoPlayer, VideoRepository


class GoogleDriveRepository(VideoRepository):
    """Repository for managing videos in Google Drive."""

    def __init__(self, folder_id: str, credentials_path: str, videos_dir: str = "videos"):
        self.folder_id = folder_id
        self.credentials_path = credentials_path
        self.videos_dir = Path(videos_dir)  # Main Google Drive sync folder
        self.cache_dir = Path("cache")      # Metadata and temp files
        self.logger = logging.getLogger(__name__)

        # Initialize Google Drive client (placeholder)
        self._drive_service = None

    def _initialize_drive_service(self):
        """Initialize Google Drive service client."""
        # TODO: Implement Google Drive API client initialization
        # This would use google-api-python-client and google-auth
        pass

    def get_videos(self) -> List[Video]:
        """Get list of videos from Google Drive."""
        try:
            # TODO: Implement actual Google Drive API call
            # This should return a list of video files from the specified folder
            return []
        except Exception as e:
            self.logger.error(f"Failed to get videos from Google Drive: {e}")
            return []

    def download_video(self, video_id: str, local_path: Path) -> bool:
        """Download video from Google Drive to local path."""
        try:
            # TODO: Implement actual download logic
            # This should download the file and return success status
            self.logger.info(f"Downloading video {video_id} to {local_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download video {video_id}: {e}")
            return False

    def delete_video(self, video_id: str) -> bool:
        """Delete video from local cache."""
        try:
            # TODO: Implement logic to mark file for deletion in Google Drive
            # For now, just remove from local cache
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete video {video_id}: {e}")
            return False

    def sync_videos(self) -> None:
        """Synchronize local cache with Google Drive."""
        try:
            # Get remote videos
            remote_videos = self.get_videos()

            # Get local videos
            local_videos = self._get_local_videos()

            # Find videos to download
            videos_to_download = []
            for remote_video in remote_videos:
                local_match = next(
                    (lv for lv in local_videos if lv.drive_id == remote_video.get("id")),
                    None
                )

                if not local_match or self._needs_update(remote_video, local_match):
                    videos_to_download.append(remote_video)

            # Find videos to delete
            videos_to_delete = []
            for local_video in local_videos:
                remote_match = next(
                    (rv for rv in remote_videos if rv.get("id") == local_video.drive_id),
                    None
                )
                if not remote_match:
                    videos_to_delete.append(local_video)

            # Download new/changed videos
            for video_data in videos_to_download:
                self._download_single_video(video_data)

            # Delete removed videos
            for video in videos_to_delete:
                self._delete_local_video(video)

        except Exception as e:
            self.logger.error(f"Sync failed: {e}")

    def _get_local_videos(self) -> List[dict]:
        """Get list of locally cached videos."""
        local_videos = []
        metadata_dir = self.cache_dir / "metadata"

        if not metadata_dir.exists():
            return local_videos

        for metadata_file in metadata_dir.glob("*.json"):
            try:
                # TODO: Load metadata from JSON file
                # This should return video metadata including drive_id, checksum, etc.
                pass
            except Exception as e:
                self.logger.warning(f"Failed to load metadata {metadata_file}: {e}")

        return local_videos

    def _needs_update(self, remote_video: dict, local_video: dict) -> bool:
        """Check if remote video needs to be downloaded."""
        # Compare modification times and checksums
        return True  # Placeholder

    def _download_single_video(self, video_data: dict) -> None:
        """Download a single video file."""
        video_id = video_data.get("id")
        filename = video_data.get("name")

        if not video_id or not filename:
            return

        local_path = self.videos_dir / filename

        # Download file
        if self.download_video(video_id, local_path):
            # Calculate checksum
            checksum = self._calculate_checksum(local_path)

            # Save metadata
            self._save_metadata(video_data, local_path, checksum)

    def _delete_local_video(self, video: Video) -> None:
        """Delete video from local cache."""
        try:
            if video.path.exists():
                video.path.unlink()
                self.logger.info(f"Deleted local video: {video.path}")
        except Exception as e:
            self.logger.error(f"Failed to delete local video {video.path}: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""

    def _save_metadata(self, video_data: dict, local_path: Path, checksum: str) -> None:
        """Save video metadata to JSON file."""
        metadata = {
            "id": video_data.get("id"),
            "name": video_data.get("name"),
            "size": video_data.get("size", 0),
            "modified_time": video_data.get("modifiedTime"),
            "local_path": str(local_path),
            "checksum": checksum,
            "drive_id": video_data.get("id")
        }

        metadata_file = self.cache_dir / "metadata" / f"{video_data.get('id')}.json"

        try:
            # TODO: Save metadata as JSON
            # import json
            # with open(metadata_file, 'w') as f:
            #     json.dump(metadata, f, indent=2)
            pass
        except Exception as e:
            self.logger.error(f"Failed to save metadata for {video_data.get('name')}: {e}")


class VLCPlayer(VideoPlayer):
    """VLC-based video player for headless playback."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.player = None
        self.instance = None
        self._initialize_player()

    def _initialize_player(self) -> None:
        """Initialize VLC player with appropriate options."""
        try:
            # VLC options for fullscreen, headless playback
            vlc_args = [
                '--fullscreen',           # Start in fullscreen
                '--no-video-title-show',  # Hide video title
                '--mouse-hide-timeout=0', # Hide mouse immediately
                '--quiet',                # Reduce VLC verbosity
            ]

            self.instance = vlc.Instance(vlc_args)
            self.player = self.instance.media_player_new()

            self.logger.info("VLC player initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize VLC player: {e}")
            raise

    def play(self, video_path: str) -> bool:
        """Play video file."""
        try:
            if not os.path.exists(video_path):
                self.logger.error(f"Video file not found: {video_path}")
                return False

            media = self.instance.media_new(video_path)
            self.player.set_media(media)

            if self.player.play() == -1:
                self.logger.error(f"Failed to play video: {video_path}")
                return False

            self.logger.info(f"Started playing: {video_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error playing video {video_path}: {e}")
            return False

    def stop(self) -> None:
        """Stop video playback."""
        try:
            if self.player:
                self.player.stop()
                self.logger.info("Video playback stopped")
        except Exception as e:
            self.logger.error(f"Error stopping playback: {e}")

    def is_playing(self) -> bool:
        """Check if video is currently playing."""
        try:
            if self.player:
                state = self.player.get_state()
                # VLC states: NothingSpecial=0, Opening=1, Buffering=2, Playing=3, Paused=4, Stopped=5, Ended=6, Error=7
                # Return True only for actively playing states, False for ended/stopped/error
                return state in [1, 2, 3]  # Opening, Buffering, or Playing
            return False
        except Exception as e:
            self.logger.error(f"Error checking playback state: {e}")
            return False

    def get_state(self) -> int:
        """Get the current VLC player state."""
        try:
            if self.player:
                return self.player.get_state()
            return 0  # NothingSpecial
        except Exception as e:
            self.logger.error(f"Error getting player state: {e}")
            return 0

    def get_position(self) -> float:
        """Get current playback position (0.0 to 1.0)."""
        try:
            if self.player:
                return self.player.get_position()
        except Exception as e:
            self.logger.error(f"Error getting position: {e}")
        return 0.0

    def set_position(self, position: float) -> None:
        """Set playback position (0.0 to 1.0)."""
        try:
            if self.player:
                self.player.set_position(max(0.0, min(1.0, position)))
        except Exception as e:
            self.logger.error(f"Error setting position: {e}")