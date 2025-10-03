# Project Overview

## Mission

Creation of a multiplatform Python service (`uv run ...`) for cyclically displaying advertising videos.

## Problem Solved

This system permanently displays updated videos on a monitor using a Raspberry Pi (Lite version, no desktop), without interruption.

A Google Drive folder with videos changes permanently, and these must be displayed on a TV connected to the Raspberry Pi where this application runs as a service.

The system is 100% multiplatform and works with VLC, displaying videos directly on the screen, monitoring changes, and updating its own video cache, also removing videos that disappear from Google Drive, without stopping.

The system runs anywhere with 'uv run main.py' (even on Windows).

## Architecture

Simple hexagonal architecture based on files, not folders. The important thing is the separation of responsibilities.

## File Structure

```
├── kdx-pi-signage-2/
│   ├── core.py                         # Contains Video, Playlist classes (Domain)
│   ├── application.py                  # Contains PlaybackService (Use Cases)
│   ├── infrastructure.py               # Contains GoogleDriveRepository, VLCPlayer
│   └── docs/*                           # Markdown files with documentation
├── main.py                             # Entry point that wires everything together
├── .env + pyproject.toml
└── README.md
```

## Existing Infrastructure

You already have the Raspberry Pi and the service running ~/kdx-pi-signage-2/main.py, and you don't need to worry about any of this or even installing packages on the Raspberry Pi (Linux); but you should be careful with dependencies in pyproject.toml.

## System Operation

### Cache

Videos are kept locally in a folder in this project (e.g., 'cache'), and synchronized with Google Drive.

Cache review occurs in the background without affecting video viewing, and here we can use different threads from the start (main.py) and it must recover from transfer errors or lack of connection.

### Variables and Secrets

Environment configuration variables in pyproject.toml and secrets (like Google Drive) in .env

### Logging and Errors

Precise logs required and saved in /logs folder by date, each day, saving terminal output in this folder. Auditing and knowing each video shown is very important. No cycle or anything like that, simply log lines with terminal output, but organized by year, month and day (folders).

### Video Display

We already trust the quality of Google Drive videos, so we can trigger the video with VLC directly on the screen, and remember you don't have desktop, it's a Lite Raspberry Pi system (and also works in development on Windows)

### API: Future (in progress)

DO NOT create a FastAPI API yet, but you can already add the dependencies. The API, very humble, serves to trigger commands with curl (or however) and will be used as an interface. But this functionality is EMPTY for now, will not be implemented.

## Steps to Create the System

1. Specifications and Clear Architecture: create in /docs/ the files that explain these same instructions, precisely, curated and organized

2. Create all empty files, then we will fill them.

3. Then create a file with TASK or TODO with the required steps, and here we write very clear class and function names.

4. DO NOT USE COMMENTS and barely a phrase is enough for docstring. Documentation will be separate

5. Document what you need in docs, keeping README very simple. The license for this is MIT and the text is in Spanish (variables and classes always in English, even docstring, only markdown documents allow Spanish)

6. Bonus with yt-dlp, install this library so in the future we can download and show YouTube videos. To check it works, download these videos to the video folder, and these will be the original files that move with the project:

https://youtu.be/WOqR_aycESw?si=VtH0hm7rFgcx7vMy

7. .gitignore! and you must ignore the entire cache folder (e.g., the video above).