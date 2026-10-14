"""MCP server "interview-guides": serves the markdown guides in resources/.

Run it (stdio transport, which is what Claude Code uses):
    python mcp/server.py

Deliberately no __init__.py in this folder: as a plain directory it can never
shadow the installed `mcp` package that FastMCP itself imports.
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

# resources/ sits next to mcp/, at the project root.
RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"

mcp = FastMCP("interview-guides")


def guide_paths() -> dict[str, Path]:
    """Map each guide name (file name without .md) to its path."""
    return {path.stem: path for path in sorted(RESOURCES_DIR.glob("*.md"))}


@mcp.tool
def list_guides() -> list[str]:
    """List the available interview guides by name."""
    return list(guide_paths())


@mcp.tool
def get_guide(name: str) -> str:
    """Return the full markdown of one guide, e.g. get_guide("decomposition-guide")."""
    guides = guide_paths()
    # Look the name up instead of building a path from it, so "../.env" and
    # friends can never escape resources/.
    if name not in guides:
        available = ", ".join(guides) or "(none)"
        raise ValueError(f"No guide named '{name}'. Available guides: {available}")
    return guides[name].read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
