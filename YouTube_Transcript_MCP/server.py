# ============================================================
# MCP Name      : YouTube_Transcript_MCP
# Author        : ParisNeo (Converted from original lollms function)
# Creation Date : 2025-10-26
# Description   : Provides a tool for LLMs to download the text
#                 transcript of a YouTube video given its ID.
#                 Automatically manages its dependencies.
# ============================================================

import argparse
import sys
import subprocess
from pathlib import Path

# Use pipmaster to ensure dependencies are installed
try:
    import pipmaster as pm
except ImportError:
    print("Pipmaster not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pipmaster"], check=True)
    import pipmaster as pm

from mcp.server.fastmcp import FastMCP
from ascii_colors import ASCIIColors

# --- MCP Tool Dependencies ---
REQUIRED_PACKAGES = [
    "pyyaml",
    "ascii_colors",
    "fastmcp",
    "youtube-transcript-api"
]

def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES, upgrade=True)
    ASCIIColors.green("All dependencies are met.")

# After dependency check, we can import the required library
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="YouTube Transcript MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9628, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()

mcp = FastMCP(
    name="YouTubeTranscriptMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="YouTubeTranscriptMCPServer")

@mcp.tool()
def get_youtube_transcript(video_id: str, language_code: str = "en") -> dict:
    """
    Fetches the transcript for a given YouTube video ID.

    Args:
        video_id: The unique identifier of the YouTube video (e.g., 'dQw4w9WgXcQ').
        language_code: The two-letter language code for the desired transcript (e.g., 'en', 'es', 'de').

    Returns:
        A dictionary containing the transcript text or an error message.
    """
    try:
        # Fetching the transcript for the specified language
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])

        # Combining the transcript parts into a single string
        transcript_text = " ".join([entry['text'] for entry in transcript_list])

        ASCIIColors.green(f"Successfully fetched transcript for video ID: {video_id}")
        return {"status": "success", "transcript": transcript_text}

    except TranscriptsDisabled:
        return {"status": "error", "error": f"Transcripts are disabled for video ID: {video_id}"}
    except NoTranscriptFound:
        return {"status": "error", "error": f"No transcript found for video ID '{video_id}' in the language '{language_code}'. The video may not have captions or support this language."}
    except Exception as e:
        ASCIIColors.red(f"An unexpected error occurred for video ID {video_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("YouTube Transcript MCP Server")
    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)