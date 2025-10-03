"""YouTube video downloader using yt-dlp (bonus feature)."""

import logging
import subprocess
from pathlib import Path
from typing import Optional


class YouTubeDownloader:
    """Service for downloading videos from YouTube using yt-dlp."""

    def __init__(self, download_dir: str = "cache/videos"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def download_video(self, url: str, output_filename: Optional[str] = None) -> Optional[str]:
        """Download video from YouTube URL."""
        try:
            if not output_filename:
                output_filename = self._generate_filename(url)

            output_path = self.download_dir / output_filename

            # yt-dlp command for downloading best quality video
            command = [
                "yt-dlp",
                "--output", str(output_path),
                "--format", "best[height<=1080]",  # Max 1080p for signage
                "--no-playlist",  # Don't download playlists
                "--quiet",  # Reduce output
                "--no-warnings",
                url
            ]

            self.logger.info(f"Downloading YouTube video: {url}")

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode == 0 and output_path.exists():
                file_size = output_path.stat().st_size
                self.logger.info(f"Successfully downloaded: {output_filename} ({file_size} bytes)")
                return str(output_path)
            else:
                self.logger.error(f"Failed to download video: {result.stderr}")
                return None

        except subprocess.CalledProcessError as e:
            self.logger.error(f"yt-dlp error: {e.stderr}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error downloading video: {e}")
            return None

    def _generate_filename(self, url: str) -> str:
        """Generate filename from YouTube URL."""
        # Extract video ID from URL for consistent naming
        import re

        # Match various YouTube URL formats
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return f"youtube_{video_id}.mp4"

        # Fallback: use timestamp
        import time
        return f"youtube_{int(time.time())}.mp4"

    def is_video_available(self, url: str) -> bool:
        """Check if video is available for download."""
        try:
            command = [
                "yt-dlp",
                "--no-download",
                "--quiet",
                "--no-warnings",
                url
            ]

            result = subprocess.run(command, capture_output=True)
            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Error checking video availability: {e}")
            return False


def test_youtube_download():
    """Test function to download the specified YouTube video."""
    downloader = YouTubeDownloader()

    test_url = "https://youtu.be/WOqR_aycESw?si=VtH0hm7rFgcx7vMy"

    if downloader.is_video_available(test_url):
        print("Video is available, starting download...")
        result = downloader.download_video(test_url)

        if result:
            print(f"Download completed successfully: {result}")
        else:
            print("Download failed")
    else:
        print("Video is not available for download")


if __name__ == "__main__":
    test_youtube_download()