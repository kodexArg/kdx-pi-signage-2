#!/usr/bin/env python3
"""Individual VLC component tests using system VLC libraries."""

import os
import sys
from pathlib import Path

def get_vlc_dir():
    """Get VLC directory from environment variable set by uv."""
    # Try to get VLC_DIR from environment (set by uv based on pyproject.toml)
    vlc_dir = os.environ.get('VLC_DIR')

    if vlc_dir:
        print(f"Using VLC_DIR from environment: {vlc_dir}")
        return vlc_dir
    else:
        # Fallback to default if environment variable not set
        default_vlc_dir = r"C:\Users\Kodex\scoop\apps\vlc\current"
        print(f"⚠️  VLC_DIR environment variable not found, using default: {default_vlc_dir}")
        return default_vlc_dir

def test_vlc_import():
    """Test 1: VLC Python module import."""
    try:
        print("=== Test 1: VLC Import ===")

        # Get VLC directory from environment variable (set by uv)
        vlc_dir = get_vlc_dir()
        plugin_dir = os.path.join(vlc_dir, "plugins")

        print(f"VLC directory: {vlc_dir}")
        print(f"Plugin directory: {plugin_dir}")

        # Set environment variables for system VLC
        os.environ['VLC_PLUGIN_PATH'] = plugin_dir
        os.environ['PATH'] = vlc_dir + os.pathsep + os.environ['PATH']

        import vlc
        print("✅ VLC imported successfully")
        return True
    except ImportError as e:
        print(f"❌ VLC import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ VLC import error: {e}")
        return False

def test_vlc_instance():
    """Test 2: VLC instance creation."""
    try:
        print("\n=== Test 2: VLC Instance Creation ===")
        import vlc

        # Try basic instance creation
        instance = vlc.Instance()
        if instance is None:
            print("❌ VLC instance creation returned None")
            return False

        print("✅ VLC instance created successfully")
        return instance

    except Exception as e:
        print(f"❌ VLC instance creation failed: {e}")
        return False

def test_media_player():
    """Test 3: Media player creation."""
    try:
        print("\n=== Test 3: Media Player Creation ===")
        import vlc

        instance = vlc.Instance()
        if instance is None:
            print("❌ Cannot test media player - no VLC instance")
            return False

        player = instance.media_player_new()
        if player is None:
            print("❌ Media player creation returned None")
            return False

        print("✅ Media player created successfully")
        player.release()
        return True

    except Exception as e:
        print(f"❌ Media player creation failed: {e}")
        return False

def test_video_files():
    """Test 4: Video files detection."""
    try:
        print("\n=== Test 4: Video Files Detection ===")
        videos_dir = Path("videos")
        if not videos_dir.exists():
            print(f"❌ Videos directory {videos_dir} does not exist")
            return False

        video_files = []
        for ext in ['.webm', '.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend(videos_dir.glob(f"*{ext}"))
            video_files.extend(videos_dir.glob(f"*{ext.upper()}"))

        if not video_files:
            print(f"❌ No video files found in {videos_dir}")
            return False

        print(f"✅ Found {len(video_files)} video files:")
        for video_file in video_files:
            size_mb = video_file.stat().st_size / (1024 * 1024)
            print(f"  - {video_file.name} ({size_mb:.1f} MB)")

        return True

    except Exception as e:
        print(f"❌ Video files detection failed: {e}")
        return False

def test_video_loading():
    """Test 5: Video loading into VLC."""
    try:
        print("\n=== Test 5: Video Loading ===")
        import vlc

        # Get first video file
        videos_dir = Path("videos")
        video_files = []
        for ext in ['.webm', '.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend(videos_dir.glob(f"*{ext}"))
            video_files.extend(videos_dir.glob(f"*{ext.upper()}"))

        if not video_files:
            print("❌ No video files available for loading test")
            return False

        first_video = video_files[0]
        print(f"Testing with video: {first_video.name}")

        # Create VLC instance and player
        instance = vlc.Instance()
        if instance is None:
            print("❌ Cannot test video loading - no VLC instance")
            return False

        player = instance.media_player_new()
        if player is None:
            print("❌ Cannot test video loading - no media player")
            return False

        # Load media
        media = instance.media_new(str(first_video))
        if media is None:
            print("❌ Media creation returned None")
            player.release()
            return False

        player.set_media(media)
        print("✅ Video loaded successfully")

        # Cleanup
        player.release()
        return True

    except Exception as e:
        print(f"❌ Video loading failed: {e}")
        return False

def test_basic_playback():
    """Test 6: Basic playback (3 seconds)."""
    try:
        print("\n=== Test 6: Basic Playback ===")
        import vlc

        # Get first video file
        videos_dir = Path("videos")
        video_files = []
        for ext in ['.webm', '.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend(videos_dir.glob(f"*{ext}"))
            video_files.extend(videos_dir.glob(f"*{ext.upper()}"))

        if not video_files:
            print("❌ No video files available for playback test")
            return False

        first_video = video_files[0]
        print(f"Testing playback with: {first_video.name}")

        # Create VLC instance and player
        instance = vlc.Instance()
        if instance is None:
            print("❌ Cannot test playback - no VLC instance")
            return False

        player = instance.media_player_new()
        if player is None:
            print("❌ Cannot test playback - no media player")
            return False

        # Load and play media
        media = instance.media_new(str(first_video))
        if media is None:
            print("❌ Cannot test playback - media creation failed")
            player.release()
            return False

        player.set_media(media)

        # Play for 3 seconds
        print("Playing for 3 seconds...")
        player.play()

        # Wait a bit
        import time
        time.sleep(3)

        # Stop and cleanup
        player.stop()
        player.release()

        print("✅ Basic playback test completed")
        return True

    except Exception as e:
        print(f"❌ Basic playback test failed: {e}")
        return False

def run_all_tests():
    """Run all VLC tests in order."""
    print("Starting VLC component tests using system libraries...")
    print("=" * 60)

    tests = [
        ("VLC Import", test_vlc_import),
        ("VLC Instance", test_vlc_instance),
        ("Media Player", test_media_player),
        ("Video Files", test_video_files),
        ("Video Loading", test_video_loading),
        ("Basic Playback", test_basic_playback),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    all_passed = True

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:15} {status}")
        if not result:
            all_passed = False

    print("-" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")

    return all_passed

def main():
    """Main function."""
    success = run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)