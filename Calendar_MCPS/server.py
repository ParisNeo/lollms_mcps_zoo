# ============================================================
# MCP Name      : Calendar_MCP
# Author        : ParisNeo
# Creation Date : 2025-08-07
# Description   : Provides calendar management services for LOLLMS.
#                 Supports adding, listing, removing, and updating calendar events using .ics format.
#
#                 WARNING: This MCP performs actions on calendar data. Ensure backups are maintained to prevent accidental loss.
#
#                 Configuration options:
#                 - calendar_path (string): Path to the .ics calendar file (default: calendar.ics).
#                 - Additional configuration fields can be defined in schema.config.json.
#                 - Environment variable mapping is supported via schema metadata.
# ============================================================

from mcp.server.fastmcp import FastMCP
from ascii_colors import ASCIIColors
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
import yaml
import json
import os
import datetime
from icalendar import Calendar, Event
from dateutil.parser import parse as date_parse

class MCPConfig:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.schema = {}
        self.config = {}
        self._load_schema()
        self._load_config()
        self._apply_env_vars()

    def _load_schema(self):
        schema_path = self.base_path / "schema.config.json"
        if schema_path.exists():
            with schema_path.open("r", encoding="utf-8") as f:
                self.schema = json.load(f)

    def _load_config(self):
        config_path = self.base_path / "config.yaml"
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        for key, meta in self.schema.get("properties", {}).items():
            if key not in self.config and "default" in meta:
                self.config[key] = meta["default"]

    def _apply_env_vars(self):
        for key, meta in self.schema.get("properties", {}).items():
            env_var = meta.get("envVar")
            if env_var and env_var in os.environ:
                self.config[key] = os.environ[env_var]

    def get(self, key, default=None):
        return self.config.get(key, default)


def parse_args():
    parser = argparse.ArgumentParser(description="Calendar MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname")
    parser.add_argument("--port", type=int, default=9630, help="Port number")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http")
    return parser.parse_args()


args = parse_args()
config = MCPConfig()
calendar_path = Path(config.get("calendar_path"))
if not calendar_path.exists():
    calendar_path.write_text("BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR")

mcp = FastMCP(name="CalendarMCP", host=args.host, port=args.port, log_level=args.log_level)

def load_calendar() -> Calendar:
    with open(calendar_path, "rb") as f:
        return Calendar.from_ical(f.read())

def save_calendar(cal: Calendar):
    with open(calendar_path, "wb") as f:
        f.write(cal.to_ical())

@mcp.tool(name="add_event", description="Adds an event to the calendar.")
async def add_event(title: str, start: str, end: str, location: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    cal = load_calendar()
    event = Event()
    event.add("summary", title)
    event.add("dtstart", date_parse(start))
    event.add("dtend", date_parse(end))
    if location:
        event.add("location", location)
    if description:
        event.add("description", description)
    cal.add_component(event)
    save_calendar(cal)
    return {"status": "Event added successfully"}

@mcp.tool(name="list_events", description="Lists all upcoming events.")
async def list_events() -> Dict[str, Any]:
    cal = load_calendar()
    now = datetime.datetime.now(datetime.timezone.utc)
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get("dtstart").dt
            if isinstance(dtstart, datetime.datetime) and dtstart > now:
                events.append({
                    "title": str(component.get("summary")),
                    "start": dtstart.isoformat(),
                    "end": component.get("dtend").dt.isoformat(),
                    "location": str(component.get("location", "")),
                    "description": str(component.get("description", ""))
                })
    return {"events": events}

@mcp.tool(name="remove_events_by_title", description="Removes all events matching a given title.")
async def remove_events_by_title(title: str) -> Dict[str, Any]:
    cal = load_calendar()
    new_cal = Calendar()
    for attr in cal.property_items():
        new_cal.add(*attr)
    removed = 0
    for component in cal.walk():
        if component.name == "VEVENT" and str(component.get("summary")).strip() != title.strip():
            new_cal.add_component(component)
        else:
            removed += 1
    save_calendar(new_cal)
    return {"removed_count": removed}

@mcp.tool(name="update_event_time", description="Updates the time of an event matching the title.")
async def update_event_time(title: str, new_start: str, new_end: str) -> Dict[str, Any]:
    cal = load_calendar()
    updated = 0
    for component in cal.walk():
        if component.name == "VEVENT" and str(component.get("summary")).strip() == title.strip():
            component["dtstart"] = date_parse(new_start)
            component["dtend"] = date_parse(new_end)
            updated += 1
    save_calendar(cal)
    return {"updated_count": updated}

if __name__ == "__main__":
    ASCIIColors.cyan("Calendar MCP is starting...")
    ASCIIColors.cyan(f"Listening for MCP messages on {mcp.run(transport=args.transport)}...")
    mcp.run(transport=args.transport)
