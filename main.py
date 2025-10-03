"""Main entry point for video signage system."""

import logging
import os
import platform
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.application import PlaybackService
from app.infrastructure import GoogleDriveRepository, VLCPlayer
from app.core import Video


class Application:
    """Main application class handling startup and shutdown."""

    def __init__(self):
        self.playback_service: Optional[PlaybackService] = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("kdx_pi_signage")
        logger.setLevel(logging.INFO)

        # Create logs directory structure
        logs_dir = Path("logs")
        today = Path(datetime.now().strftime("%Y/%m/%d.log"))
        log_file = logs_dir / today

        # Create directories if they don't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _get_local_videos(self, test_videos_dir: str) -> List[Video]:
        """Get list of local videos from test_videos directory."""
        videos = []
        test_videos_path = Path(test_videos_dir)

        self.logger.info(f"Current working directory: {Path.cwd().absolute()}")
        self.logger.info(f"Looking for videos in: {test_videos_path.absolute()}")

        if not test_videos_path.exists():
            self.logger.warning(f"Test videos directory {test_videos_dir} does not exist")
            return videos

        # Supported video extensions
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

        # Debug: List all files in directory
        all_files = list(test_videos_path.iterdir())
        self.logger.info(f"Found {len(all_files)} files/directories in {test_videos_dir}")

        for video_file in all_files:
            self.logger.info(f"Processing file: {video_file.name} (is_file: {video_file.is_file()}, suffix: '{video_file.suffix.lower()}')")

            if video_file.is_file() and video_file.suffix.lower() in video_extensions:
                try:
                    stat = video_file.stat()
                    video = Video(
                        id=f"local_{video_file.stem}",
                        name=video_file.name,
                        path=video_file,
                        size=stat.st_size,
                        modified_time=datetime.fromtimestamp(stat.st_mtime),
                        checksum=f"local_{hash(str(video_file.name))}"  # Simple checksum for local files
                    )
                    videos.append(video)
                    self.logger.info(f"Added video: {video_file.name}")
                except Exception as e:
                    self.logger.warning(f"Error processing local video {video_file}: {e}")
            else:
                self.logger.info(f"Skipped file: {video_file.name} (not a video file)")

        self.logger.info(f"Found {len(videos)} local videos in {test_videos_dir}")
        return videos

    def _load_configuration(self) -> dict:
        """Load configuration from environment variables provided by uv."""
        return {
            "google_drive_folder_id": os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
            "google_credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
            "google_drive_sync_enabled": os.getenv("GOOGLE_DRIVE_SYNC_ENABLED", "false").lower() == "true",
            "videos_dir": os.getenv("VIDEOS_DIR", "videos"),
            "test_videos_dir": os.getenv("TEST_VIDEOS_DIR", "test_videos"),
            "cache_dir": os.getenv("CACHE_DIR", "cache"),
            "logs_dir": os.getenv("LOGS_DIR", "logs"),
            "sync_interval": int(os.getenv("SYNC_INTERVAL", "30")),
            "vlc_verbose": os.getenv("VLC_VERBOSE_LEVEL", "0"),
        }

    def _create_dependencies(self, config: dict):
        """Create and wire dependencies using dependency injection."""
        vlc_player = VLCPlayer()

        # Choose video repository based on sync configuration
        if config["google_drive_sync_enabled"]:
            # Use Google Drive repository for sync
            if not config["google_drive_folder_id"]:
                raise ValueError("GOOGLE_DRIVE_FOLDER_ID environment variable is required when GOOGLE_DRIVE_SYNC_ENABLED=true")
            if not config["google_credentials_path"]:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required when GOOGLE_DRIVE_SYNC_ENABLED=true")

            video_repository = GoogleDriveRepository(
                folder_id=config["google_drive_folder_id"],
                credentials_path=config["google_credentials_path"],
                videos_dir=config["videos_dir"]
            )

            videos_dir = config.get("videos_dir", "videos")
            self.logger.info("Using Google Drive synchronization")
        else:
            # Use local test videos without sync
            local_videos = self._get_local_videos(config["test_videos_dir"])

            # Create a simple repository that returns local videos
            class LocalVideoRepository:
                def __init__(self, videos):
                    self.videos = videos

                def get_videos(self):
                    return self.videos

                def sync_videos(self):
                    # No sync needed for local videos
                    pass

            video_repository = LocalVideoRepository(local_videos)
            videos_dir = config["test_videos_dir"]
            self.logger.info(f"Using local videos from {config['test_videos_dir']} (Google Drive sync disabled)")

        # Create application service
        self.playback_service = PlaybackService(
            video_repository=video_repository,
            video_player=vlc_player,
            videos_dir=videos_dir,
            cache_dir=config["cache_dir"],
            sync_interval=config["sync_interval"]
        )

    def start(self) -> None:
        """Start the application."""
        try:
            self.logger.info("Starting KDX Pi Signage System")

            # Load configuration
            config = self._load_configuration()

            # Validate required configuration based on sync mode
            if config["google_drive_sync_enabled"]:
                if not config["google_drive_folder_id"]:
                    raise ValueError("GOOGLE_DRIVE_FOLDER_ID environment variable is required when GOOGLE_DRIVE_SYNC_ENABLED=true")
                if not config["google_credentials_path"]:
                    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required when GOOGLE_DRIVE_SYNC_ENABLED=true")

            # Create dependencies
            self._create_dependencies(config)

            # Start playback service
            self.playback_service.start()

            self.logger.info("KDX Pi Signage System started successfully")
            self.logger.info(f"Configuration: {config}")

        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            raise

    def stop(self) -> None:
        """Stop the application."""
        try:
            self.logger.info("Stopping KDX Pi Signage System")

            if self.playback_service:
                self.playback_service.stop()

            self.logger.info("KDX Pi Signage System stopped successfully")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    def handle_signal(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point function."""
    app = Application()

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, app.handle_signal)
    signal.signal(signal.SIGINT, app.handle_signal)

    try:
        # Start the application
        app.start()

        # Keep main thread alive (cross-platform)
        while True:
            if platform.system() == "Windows":
                # On Windows, signal.pause() doesn't exist, so we use a simple sleep loop
                # The signal handlers will still work to break out of this loop
                time.sleep(1)
            else:
                # On Unix-like systems, use signal.pause()
                signal.pause()

    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"Application error: {e}")
        app.logger.error(f"Application error: {e}")
    finally:
        app.stop()


if __name__ == "__main__":
    main()