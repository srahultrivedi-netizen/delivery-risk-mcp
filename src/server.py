import json
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

try:
    from src.risk_engine import calculate_risk_score
except ModuleNotFoundError:
    from risk_engine import calculate_risk_score


def normalize_host(value: str) -> str:
    host = value.strip()
    host = host.replace("https://", "").replace("http://", "")
    host = host.split("/", 1)[0]
    host = host.split(":", 1)[0]
    return host


app_service_host = normalize_host(
    os.getenv("APP_SERVICE_HOST")
    or os.getenv("WEBSITE_HOSTNAME", "")
)

allowed_hosts = [
    "localhost",
    "localhost:8000",
    "127.0.0.1",
    "127.0.0.1:8000",
]

allowed_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

if app_service_host:
    allowed_hosts.extend(
        [
            app_service_host,
            f"{app_service_host}:80",
            f"{app_service_host}:443",
            f"{app_service_host}:8000",
        ]
    )
    allowed_origins.extend(
        [
            f"https://{app_service_host}",
            f"https://{app_service_host}:443",
        ]
    )


mcp = FastMCP(
    "Project Delivery Risk Navigator",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    ),
)


DATA_PATH = Path(__file__).parent / "data" / "projects.json"


def load_projects() -> list[dict[str, Any]]:
    """Load synthetic project data."""
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def find_project(project_id: str) -> dict[str, Any] | None:
    """Find a project by identifier."""
    normalized_project_id = project_id.strip()

    if not normalized_project_id:
        raise ValueError("project_id must be a non-empty string")

    return next(
        (
            project
            for project in load_projects()
            if project["project_id"] == normalized_project_id
        ),
        None,
    )


@mcp.tool()
def get_portfolio_overview() -> dict[str, Any]:
    """Return risk ratings and summary metrics for the portfolio."""
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


@mcp.tool()
def analyze_project_risk(project_id: str) -> dict[str, Any]:
    """Analyze one project and explain its risk rating."""
    normalized_project_id = project_id.strip()

    if not normalized_project_id:
        raise ValueError("project_id must be a non-empty string")

    project = find_project(normalized_project_id)

    if project is None:
        available_ids = [
            item["project_id"]
            for item in load_projects()
        ]
        raise ValueError(
            f"Project '{normalized_project_id}' was not found. "
            f"Available project IDs: {available_ids}"
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
        for project in load_projects()
        for assessment in [calculate_risk_score(project)]
        if rating_order[assessment["rating"]]
        >= rating_order[normalized_rating]
    ]


@mcp.resource("project://portfolio/summary")
def portfolio_summary() -> str:
    """Provide a readable portfolio summary."""
    return json.dumps(get_portfolio_overview(), indent=2)


@mcp.prompt()
def executive_risk_brief() -> str:
    """Guide the assistant in preparing an executive risk brief."""
    return (
        "Review the project portfolio using the available risk tools. "
        "Summarize Red and Amber projects, explain the strongest evidence, "
        "identify business impact, and recommend management actions."
    )


app = mcp.streamable_http_app()


if __name__ == "__main__":
    if os.getenv("MCP_TRANSPORT", "stdio") == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
