
import os
import json
from pathlib import Path
from typing import Any

from src.risk_engine import calculate_risk_score

from mcp.server.fastmcp import FastMCP  # type: ignore[reportMissingImports]
from mcp.server.transport_security import (  # type: ignore[reportMissingImports]
    TransportSecuritySettings,
)

APP_HOST = "delivery-risk-mcp-sujal-trivedi-fcfncqehbmfddpac.westus-01.azurewebsites.net"

mcp = FastMCP(
    "Delivery Risk MCP",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "localhost:*",
            "127.0.0.1:*",
            f"{APP_HOST}:*",
            f"{APP_HOST}:443",
        ],
        allowed_origins=[
            "http://localhost:*",
            "https://localhost:*",
            f"https://{APP_HOST}",
            f"https://{APP_HOST}:443",
        ],
    ),
)

mcp = FastMCP(
    "Project Delivery Risk Navigator",
    stateless_http=True,
)

DATA_PATH = Path(__file__).parent / "data" / "projects.json"


def load_projects() -> list[dict[str, Any]]:
    """Load synthetic project data from the JSON file."""
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def find_project(project_id: str) -> dict[str, Any] | None:
    """Find a project by its identifier."""
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id must be a non-empty string")

    return next(
        (
            project for project in load_projects()
            if project["project_id"] == normalized_project_id
        ),
        None,
    )


@mcp.tool()
def get_portfolio_overview() -> dict[str, Any]:
    """Return risk ratings and summary metrics for the project portfolio."""
    assessments = [
        calculate_risk_score(project)
        for project in load_projects()
    ]

    return {
        "project_count": len(assessments),
        "rating_counts": {
            rating: sum(
                assessment["rating"] == rating
                for assessment in assessments
            )
            for rating in ("Red", "Amber", "Green")
        },
        "projects": assessments,
    }
try:
    from src.risk_engine import calculate_risk_score
except ModuleNotFoundError:
    from risk_engine import calculate_risk_score


@mcp.tool()
def analyze_project_risk(project_id: str) -> dict[str, Any]:
    """Analyze one project and explain the evidence behind its rating."""
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id must be a non-empty string")

    project = find_project(normalized_project_id)

    if project is None:
        available_project_ids = [
            item["project_id"] for item in load_projects()
        ]
        raise ValueError(
            f"Project '{normalized_project_id}' was not found. "
            f"Available project IDs: {available_project_ids}"
        )

    return calculate_risk_score(project)


@mcp.tool()
def find_projects_needing_attention(
    minimum_rating: str = "Amber",
) -> list[dict[str, Any]]:
    """Return projects at or above the requested risk threshold."""
    rating_order = {"Green": 0, "Amber": 1, "Red": 2}
    normalized_rating = minimum_rating.strip()

    if normalized_rating not in rating_order:
        raise ValueError(
            "minimum_rating must be one of: Green, Amber, Red"
        )

    return [
        assessment
        for assessment in (
            calculate_risk_score(project)
            for project in load_projects()
        )
        if rating_order[assessment["rating"]]
        >= rating_order[normalized_rating]
    ]


@mcp.resource("project://portfolio/summary")
def portfolio_summary() -> str:
    """Provide a readable portfolio summary as an MCP resource."""
    overview = get_portfolio_overview()
    return json.dumps(overview, indent=2)


@mcp.prompt() # tells LLM How you want LLM to respond
def executive_risk_brief() -> str:
    """Guide an AI assistant in preparing an executive risk brief."""
    return (
        "Review the project portfolio using the available risk tools. "
        "Summarize Red and Amber projects, explain the strongest evidence, "
        "identify business impact, and recommend the next management actions."
    )



app = mcp.streamable_http_app()

if __name__ == "__main__":
    mcp.run(transport="stdio")