"""Main entry point for video signage system."""

import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.application import PlaybackService
from app.infrastructure import GoogleDriveRepository, VLCPlayer


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

    def _load_configuration(self) -> dict:
        """Load configuration from environment variables."""
        return {
            "google_drive_folder_id": os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
            "google_credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
            "videos_dir": os.getenv("VIDEOS_DIR", "videos"),  # Main Google Drive sync folder
            "cache_dir": os.getenv("CACHE_DIR", "cache"),
            "logs_dir": os.getenv("LOGS_DIR", "logs"),
            "sync_interval": int(os.getenv("SYNC_INTERVAL", "30")),
            "vlc_verbose": os.getenv("VLC_VERBOSE_LEVEL", "0"),
        }

    def _create_dependencies(self, config: dict):
        """Create and wire dependencies using dependency injection."""
        # Create infrastructure services
        google_drive_repo = GoogleDriveRepository(
            folder_id=config["google_drive_folder_id"],
            credentials_path=config["google_credentials_path"],
            videos_dir=config["videos_dir"]  # Main Google Drive sync folder
        )

        vlc_player = VLCPlayer()

        # Create application service
        self.playback_service = PlaybackService(
            video_repository=google_drive_repo,
            video_player=vlc_player,
            videos_dir=config.get("videos_dir", "videos"),  # Main Google Drive sync folder
            cache_dir=config["cache_dir"],
            sync_interval=config["sync_interval"]
        )

    def start(self) -> None:
        """Start the application."""
        try:
            self.logger.info("Starting KDX Pi Signage System")

            # Load configuration
            config = self._load_configuration()

            # Validate required configuration
            if not config["google_drive_folder_id"]:
                raise ValueError("GOOGLE_DRIVE_FOLDER_ID environment variable is required")
            if not config["google_credentials_path"]:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required")

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

        # Keep main thread alive
        while True:
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