"""MCP server exposing the aedifion building IoT & analytics API."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .client import AedifionClient

load_dotenv()

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "aedifion",
    instructions=(
        "MCP server for the aedifion cloud API (https://api.cloud.aedifion.eu). "
        "Provides tools for managing building IoT projects, datapoints, "
        "timeseries data, analytics, alerts, components, controls, tasks, and more. "
        "Requires AEDIFION_USERNAME and AEDIFION_PASSWORD environment variables "
        "(or AEDIFION_TOKEN) for authentication."
    ),
)

_client: AedifionClient | None = None


def _get_client() -> AedifionClient:
    global _client
    if _client is not None:
        return _client

    base_url = os.environ.get("AEDIFION_BASE_URL", "https://api.cloud.aedifion.eu")
    _client = AedifionClient(base_url)

    token = os.environ.get("AEDIFION_TOKEN")
    if token:
        _client.set_token(token)
    else:
        username = os.environ.get("AEDIFION_USERNAME", "")
        password = os.environ.get("AEDIFION_PASSWORD", "")
        if not username or not password:
            raise RuntimeError(
                "Set AEDIFION_USERNAME/AEDIFION_PASSWORD or AEDIFION_TOKEN "
                "environment variables."
            )
        _client.set_credentials(username, password)

    return _client


def _fmt(result: dict | list | str) -> str:
    """Format an API result as a readable string."""
    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2, default=str)


# ===================================================================
# META
# ===================================================================


@mcp.tool()
async def ping() -> str:
    """Ping the aedifion API server to check availability."""
    c = _get_client()
    return _fmt(await c.get("/ping"))


@mcp.tool()
async def get_api_version() -> str:
    """Get the aedifion API version."""
    c = _get_client()
    return _fmt(await c.get("/v2/meta/api_version"))


@mcp.tool()
async def get_endpoints() -> str:
    """List all available API endpoints."""
    c = _get_client()
    return _fmt(await c.get("/v2/meta/endpoints"))


@mcp.tool()
async def get_label_definitions() -> str:
    """Get all label definitions available in aedifion."""
    c = _get_client()
    return _fmt(await c.get("/v2/labels/definitions"))


@mcp.tool()
async def get_label_systems() -> str:
    """Get available label/unit systems (e.g. SI, imperial)."""
    c = _get_client()
    return _fmt(await c.get("/v2/labels/systems"))


# ===================================================================
# USER
# ===================================================================


@mcp.tool()
async def get_user() -> str:
    """Get the currently logged-in user's details."""
    c = _get_client()
    return _fmt(await c.get("/v2/user"))


@mcp.tool()
async def update_user(first_name: str | None = None, last_name: str | None = None) -> str:
    """Update the logged-in user's details.

    Args:
        first_name: New first name.
        last_name: New last name.
    """
    c = _get_client()
    body: dict = {}
    if first_name is not None:
        body["firstName"] = first_name
    if last_name is not None:
        body["lastName"] = last_name
    return _fmt(await c.put("/v2/user", json_body=body))


@mcp.tool()
async def get_user_permissions() -> str:
    """Get the logged-in user's project permissions."""
    c = _get_client()
    return _fmt(await c.get("/v2/user/permissions"))


@mcp.tool()
async def get_user_roles() -> str:
    """Get the logged-in user's roles."""
    c = _get_client()
    return _fmt(await c.get("/v2/user/roles"))


# ===================================================================
# AI
# ===================================================================


@mcp.tool()
async def ai_get_threads(page: int | None = None, per_page: int | None = None) -> str:
    """List all AI conversation threads for the current user.

    Args:
        page: Page number for pagination.
        per_page: Number of items per page.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/user/ai/threads", params={"page": page, "per_page": per_page}))


@mcp.tool()
async def ai_get_thread(thread_id: str) -> str:
    """Get all messages in an AI conversation thread.

    Args:
        thread_id: The thread identifier.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/user/ai/thread/{thread_id}"))


@mcp.tool()
async def ai_chat(thread_id: str, message: str) -> str:
    """Send a chat message to the aedifion AI assistant.

    Args:
        thread_id: The thread identifier (use 'new' for a new thread).
        message: The message to send.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/user/ai/chat/{thread_id}", json_body={"message": message}))


@mcp.tool()
async def ai_delete_thread(thread_id: str) -> str:
    """Delete an AI conversation thread.

    Args:
        thread_id: The thread identifier.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/user/ai/thread/{thread_id}"))


# ===================================================================
# COMPANY
# ===================================================================


@mcp.tool()
async def get_company() -> str:
    """Get the current user's company details including projects and users."""
    c = _get_client()
    return _fmt(await c.get("/v2/company"))


@mcp.tool()
async def update_company(name: str | None = None, description: str | None = None) -> str:
    """Update company details.

    Args:
        name: New company name.
        description: New company description.
    """
    c = _get_client()
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    return _fmt(await c.put("/v2/company", json_body=body))


@mcp.tool()
async def get_company_roles() -> str:
    """Get all roles defined in the company."""
    c = _get_client()
    return _fmt(await c.get("/v2/company/roles"))


@mcp.tool()
async def get_company_permissions() -> str:
    """Get all project permissions granted to the company."""
    c = _get_client()
    return _fmt(await c.get("/v2/company/permissions"))


@mcp.tool()
async def get_company_labels() -> str:
    """Get all labels assigned to the company."""
    c = _get_client()
    return _fmt(await c.get("/v2/company/labels"))


@mcp.tool()
async def create_project(name: str, description: str | None = None) -> str:
    """Create a new project in the company.

    Args:
        name: Project name.
        description: Project description.
    """
    c = _get_client()
    body: dict = {"name": name}
    if description is not None:
        body["description"] = description
    return _fmt(await c.post("/v2/company/project", json_body=body))


@mcp.tool()
async def create_user(email: str, first_name: str, last_name: str, password: str) -> str:
    """Create a new user in the company.

    Args:
        email: User email address.
        first_name: First name.
        last_name: Last name.
        password: Initial password.
    """
    c = _get_client()
    body = {
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "password": password,
    }
    return _fmt(await c.post("/v2/company/user", json_body=body))


@mcp.tool()
async def get_company_user(user_id: int) -> str:
    """Get details of a user within the company.

    Args:
        user_id: The user's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/company/user/{user_id}"))


@mcp.tool()
async def delete_company_user(user_id: int) -> str:
    """Delete a user from the company.

    Args:
        user_id: The user's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/company/user/{user_id}"))


# ===================================================================
# REALM
# ===================================================================


@mcp.tool()
async def get_realm_companies(page: int | None = None, per_page: int | None = None) -> str:
    """Get all companies in the realm.

    Args:
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/realm/companies", params={"page": page, "per_page": per_page}))


@mcp.tool()
async def get_realm_projects(page: int | None = None, per_page: int | None = None) -> str:
    """Get all projects in the realm.

    Args:
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/realm/projects", params={"page": page, "per_page": per_page}))


@mcp.tool()
async def get_realm_users(page: int | None = None, per_page: int | None = None) -> str:
    """Get all users in the realm.

    Args:
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/realm/users", params={"page": page, "per_page": per_page}))


# ===================================================================
# PROJECT
# ===================================================================


@mcp.tool()
async def get_project(project_id: int) -> str:
    """Get a project's details.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}"))


@mcp.tool()
async def update_project(project_id: int, name: str | None = None, description: str | None = None) -> str:
    """Update a project's details.

    Args:
        project_id: The project's numeric ID.
        name: New project name.
        description: New project description.
    """
    c = _get_client()
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    return _fmt(await c.put(f"/v2/project/{project_id}", json_body=body))


@mcp.tool()
async def delete_project(project_id: int, project_name: str) -> str:
    """Delete a project. Requires confirmation via the project name.

    Args:
        project_id: The project's numeric ID.
        project_name: The project name (for confirmation).
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}", params={"project_name": project_name}))


@mcp.tool()
async def get_project_datapoints(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
    filter: str | None = None,
) -> str:
    """Get all datapoints in a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
        filter: Filter string for datapoint names.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/datapoints",
            params={"page": page, "per_page": per_page, "filter": filter},
        )
    )


@mcp.tool()
async def get_project_timeseries(
    project_id: int,
    datapoint_ids: str,
    start: str | None = None,
    end: str | None = None,
    max: int | None = None,
    samplerate: str | None = None,
    interpolation: str | None = None,
    aggregation: str | None = None,
    short: bool | None = None,
    units_system: str | None = None,
    currency_system: str | None = None,
) -> str:
    """Get time series data for one or more datapoints in a project.

    Args:
        project_id: The project's numeric ID.
        datapoint_ids: Comma-separated datapoint IDs (hash keys or alternate keys).
        start: Start time in ISO 8601 format (e.g. '2024-01-01T00:00:00Z').
        end: End time in ISO 8601 format.
        max: Maximum number of observations to return.
        samplerate: Resample interval (e.g. '15min', '1h', '1d').
        interpolation: Interpolation method when resampling (e.g. 'linear', 'pad').
        aggregation: Aggregation method when resampling (e.g. 'mean', 'sum', 'max', 'min').
        short: If true, return short format (timestamps + values only).
        units_system: Unit system (e.g. 'SI', 'imperial').
        currency_system: Currency system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/timeseries",
            params={
                "dataPointIDs": datapoint_ids,
                "start": start,
                "end": end,
                "max": max,
                "samplerate": samplerate,
                "interpolation": interpolation,
                "aggregation": aggregation,
                "short": short,
                "units_system": units_system,
                "currency_system": currency_system,
            },
        )
    )


@mcp.tool()
async def write_project_timeseries(project_id: int, timeseries_data: str) -> str:
    """Write timeseries data to datapoints in a project.

    Args:
        project_id: The project's numeric ID.
        timeseries_data: JSON string with timeseries data (list of objects with dataPointID, value, time).
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/project/{project_id}/timeseries", json_body=json.loads(timeseries_data)))


@mcp.tool()
async def delete_project_timeseries(
    project_id: int,
    datapoint_id: str,
    start: str | None = None,
    end: str | None = None,
) -> str:
    """Delete timeseries data for a datapoint.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
    """
    c = _get_client()
    return _fmt(
        await c.delete(
            f"/v2/project/{project_id}/timeseries",
            params={"dataPointID": datapoint_id, "start": start, "end": end},
        )
    )


@mcp.tool()
async def get_project_alerts(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """Get all alerts configured in a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/alerts",
            params={"page": page, "per_page": per_page},
        )
    )


@mcp.tool()
async def get_project_tags(
    project_id: int,
    key: str | None = None,
    keys_only: bool | None = None,
) -> str:
    """Get all datapoint tags in a project.

    Args:
        project_id: The project's numeric ID.
        key: Filter by tag key.
        keys_only: If true, return only tag keys without values.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/tags",
            params={"key": key, "keys_only": keys_only},
        )
    )


@mcp.tool()
async def add_project_tag(project_id: int, tag_id: str, key: str, value: str) -> str:
    """Add or overwrite a tag on a datapoint.

    Args:
        project_id: The project's numeric ID.
        tag_id: The tag identifier.
        key: Tag key.
        value: Tag value.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/project/{project_id}/tag/{tag_id}",
            json_body={"key": key, "value": value},
        )
    )


@mcp.tool()
async def delete_project_tag(project_id: int, tag_id: str) -> str:
    """Delete a tag.

    Args:
        project_id: The project's numeric ID.
        tag_id: The tag identifier.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/tag/{tag_id}"))


@mcp.tool()
async def get_project_components(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """Get all components configured in a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/componentsInProject",
            params={"page": page, "per_page": per_page},
        )
    )


@mcp.tool()
async def get_project_component(project_id: int, cip_id: int) -> str:
    """Get a specific component in a project.

    Args:
        project_id: The project's numeric ID.
        cip_id: The component-in-project ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/componentInProject/{cip_id}"))


@mcp.tool()
async def add_project_component(project_id: int, component_id: int) -> str:
    """Add a component to a project.

    Args:
        project_id: The project's numeric ID.
        component_id: The component definition ID.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/project/{project_id}/componentInProject",
            params={"component_id": component_id},
        )
    )


@mcp.tool()
async def delete_project_component(project_id: int, cip_id: int) -> str:
    """Remove a component from a project.

    Args:
        project_id: The project's numeric ID.
        cip_id: The component-in-project ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/componentInProject/{cip_id}"))


@mcp.tool()
async def get_component_pins(project_id: int, cip_id: int) -> str:
    """Get all pin mappings for a component in a project.

    Args:
        project_id: The project's numeric ID.
        cip_id: The component-in-project ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/componentInProject/{cip_id}/pins"))


@mcp.tool()
async def map_component_pin(project_id: int, cip_id: int, pin_id: int, datapoint_id: str) -> str:
    """Map a component pin to a datapoint.

    Args:
        project_id: The project's numeric ID.
        cip_id: The component-in-project ID.
        pin_id: The pin ID.
        datapoint_id: The datapoint identifier to map to.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/project/{project_id}/componentInProject/{cip_id}/pin/{pin_id}",
            json_body={"dataPointID": datapoint_id},
        )
    )


@mcp.tool()
async def unmap_component_pin(project_id: int, cip_id: int, pin_id: int) -> str:
    """Unmap a pin from a component in a project.

    Args:
        project_id: The project's numeric ID.
        cip_id: The component-in-project ID.
        pin_id: The pin ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/componentInProject/{cip_id}/pin/{pin_id}"))


@mcp.tool()
async def get_component_attributes(project_id: int, cip_id: int) -> str:
    """Get all attributes of a component in a project.

    Args:
        project_id: The project's numeric ID.
        cip_id: The component-in-project ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/componentInProject/{cip_id}/attributes"))


@mcp.tool()
async def get_project_permissions(project_id: int) -> str:
    """Get permissions configured for a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/permissions"))


@mcp.tool()
async def get_project_labels(project_id: int) -> str:
    """Get all labels assigned to a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/labels"))


@mcp.tool()
async def set_datapoint_renamings(project_id: int, renamings: str) -> str:
    """Set alternate keys (renamings) for datapoints in a project.

    Args:
        project_id: The project's numeric ID.
        renamings: JSON string with renaming mappings (list of {dataPointID, alternateKey}).
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/project/{project_id}/renamings", json_body=json.loads(renamings)))


@mcp.tool()
async def get_project_setpoints(project_id: int) -> str:
    """Get all setpoints in a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/setpoints"))


@mcp.tool()
async def write_setpoint(project_id: int, datapoint_id: str, value: float, priority: int | None = None) -> str:
    """Write a setpoint value to a datapoint.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
        value: The setpoint value.
        priority: BACnet priority (1-16).
    """
    c = _get_client()
    body: dict = {"dataPointID": datapoint_id, "value": value}
    if priority is not None:
        body["priority"] = priority
    return _fmt(await c.post(f"/v2/project/{project_id}/setpoints", json_body=body))


@mcp.tool()
async def delete_setpoint(project_id: int, setpoint_id: int) -> str:
    """Delete a setpoint.

    Args:
        project_id: The project's numeric ID.
        setpoint_id: The setpoint ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/setpoints/{setpoint_id}"))


@mcp.tool()
async def get_setpoint_status(project_id: int, setpoint_id: int) -> str:
    """Get the status of a setpoint.

    Args:
        project_id: The project's numeric ID.
        setpoint_id: The setpoint ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/setpoints/{setpoint_id}"))


@mcp.tool()
async def get_project_weather(project_id: int, units_system: str | None = None) -> str:
    """Get current weather for a project's location.

    Args:
        project_id: The project's numeric ID.
        units_system: Unit system (e.g. 'SI').
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/weather/current", params={"units_system": units_system}))


@mcp.tool()
async def get_project_weather_forecast(project_id: int, units_system: str | None = None) -> str:
    """Get weather forecast for a project's location.

    Args:
        project_id: The project's numeric ID.
        units_system: Unit system (e.g. 'SI').
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/weather/forecast", params={"units_system": units_system}))


@mcp.tool()
async def grant_ai_consent(project_id: int, consent: bool) -> str:
    """Grant or revoke consent for the AI Assistant on a project.

    Args:
        project_id: The project's numeric ID.
        consent: True to grant, False to revoke.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/project/{project_id}/ai/consent", params={"consent": consent}))


# -- Plot Views --------------------------------------------------------


@mcp.tool()
async def get_plot_views(project_id: int) -> str:
    """Get all saved plot views for a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/plotViews"))


@mcp.tool()
async def create_plot_view(project_id: int, plot_config: str) -> str:
    """Create a new plot view.

    Args:
        project_id: The project's numeric ID.
        plot_config: JSON string with the plot configuration.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/project/{project_id}/plotViews", json_body=json.loads(plot_config)))


@mcp.tool()
async def delete_plot_view(project_id: int, plot_view_id: int) -> str:
    """Delete a plot view.

    Args:
        project_id: The project's numeric ID.
        plot_view_id: The plot view ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/plotViews/{plot_view_id}"))


# -- Logbooks ----------------------------------------------------------


@mcp.tool()
async def get_logbooks(project_id: int) -> str:
    """Get all logbooks in a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/logbooks"))


@mcp.tool()
async def create_logbook(project_id: int, name: str, description: str | None = None) -> str:
    """Create a new logbook in a project.

    Args:
        project_id: The project's numeric ID.
        name: Logbook name.
        description: Logbook description.
    """
    c = _get_client()
    body: dict = {"name": name}
    if description is not None:
        body["description"] = description
    return _fmt(await c.post(f"/v2/project/{project_id}/logbooks", json_body=body))


@mcp.tool()
async def get_logbook(project_id: int, logbook_id: int) -> str:
    """Get a specific logbook.

    Args:
        project_id: The project's numeric ID.
        logbook_id: The logbook ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/project/{project_id}/logbooks/{logbook_id}"))


@mcp.tool()
async def delete_logbook(project_id: int, logbook_id: int) -> str:
    """Delete a logbook.

    Args:
        project_id: The project's numeric ID.
        logbook_id: The logbook ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/logbooks/{logbook_id}"))


@mcp.tool()
async def create_logbook_entry(project_id: int, logbook_id: int, title: str, body_text: str) -> str:
    """Create a new entry in a logbook.

    Args:
        project_id: The project's numeric ID.
        logbook_id: The logbook ID.
        title: Entry title.
        body_text: Entry body text.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/project/{project_id}/logbooks/{logbook_id}/entries",
            json_body={"title": title, "body": body_text},
        )
    )


@mcp.tool()
async def delete_logbook_entry(project_id: int, logbook_id: int, entry_id: int) -> str:
    """Delete a logbook entry.

    Args:
        project_id: The project's numeric ID.
        logbook_id: The logbook ID.
        entry_id: The entry ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/logbooks/{logbook_id}/entries/{entry_id}"))


# -- Comments ----------------------------------------------------------


@mcp.tool()
async def get_project_comments(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """Get all comments for a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/comments",
            params={"page": page, "per_page": per_page},
        )
    )


@mcp.tool()
async def add_project_comment(project_id: int, text: str) -> str:
    """Add a comment to a project.

    Args:
        project_id: The project's numeric ID.
        text: Comment text.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/project/{project_id}/comments", json_body={"text": text}))


@mcp.tool()
async def delete_project_comment(project_id: int, comment_id: int) -> str:
    """Delete a project comment.

    Args:
        project_id: The project's numeric ID.
        comment_id: The comment ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/project/{project_id}/comments/{comment_id}"))


# ===================================================================
# DATAPOINT
# ===================================================================


@mcp.tool()
async def get_datapoint(project_id: int, datapoint_id: str) -> str:
    """Get details about a specific datapoint.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier (hash key or alternate key).
    """
    c = _get_client()
    return _fmt(
        await c.get(
            "/v2/datapoint",
            params={"project_id": project_id, "dataPointID": datapoint_id},
        )
    )


@mcp.tool()
async def update_datapoint(
    project_id: int,
    datapoint_id: str,
    description: str | None = None,
    unit: str | None = None,
) -> str:
    """Update datapoint details.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
        description: New description.
        unit: New unit string.
    """
    c = _get_client()
    body: dict = {}
    if description is not None:
        body["description"] = description
    if unit is not None:
        body["unit"] = unit
    return _fmt(
        await c.put(
            "/v2/datapoint",
            params={"project_id": project_id, "dataPointID": datapoint_id},
            json_body=body,
        )
    )


@mcp.tool()
async def delete_datapoint(project_id: int, datapoint_id: str) -> str:
    """Delete a datapoint.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
    """
    c = _get_client()
    return _fmt(
        await c.delete(
            "/v2/datapoint",
            params={"project_id": project_id, "dataPointID": datapoint_id},
        )
    )


@mcp.tool()
async def get_datapoint_timeseries(
    project_id: int,
    datapoint_id: str,
    start: str | None = None,
    end: str | None = None,
    max: int | None = None,
    samplerate: str | None = None,
    interpolation: str | None = None,
    aggregation: str | None = None,
    short: bool | None = None,
    units_system: str | None = None,
) -> str:
    """Get timeseries data for a single datapoint.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        max: Maximum number of observations.
        samplerate: Resample interval (e.g. '15min', '1h').
        interpolation: Interpolation method (e.g. 'linear', 'pad').
        aggregation: Aggregation method (e.g. 'mean', 'sum').
        short: Return short format.
        units_system: Unit system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            "/v2/datapoint/timeseries",
            params={
                "project_id": project_id,
                "dataPointID": datapoint_id,
                "start": start,
                "end": end,
                "max": max,
                "samplerate": samplerate,
                "interpolation": interpolation,
                "aggregation": aggregation,
                "short": short,
                "units_system": units_system,
            },
        )
    )


@mcp.tool()
async def get_datapoint_usage(project_id: int, datapoint_id: str) -> str:
    """Get usage information for a datapoint (where it's referenced).

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            "/v2/datapoint/usage",
            params={"project_id": project_id, "dataPointID": datapoint_id},
        )
    )


@mcp.tool()
async def get_favorite_datapoints(project_id: int) -> str:
    """Get all personal favorite datapoints.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/datapoint/favorites", params={"project_id": project_id}))


@mcp.tool()
async def set_favorite_datapoint(project_id: int, datapoint_id: str) -> str:
    """Mark a datapoint as a personal favorite.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            "/v2/datapoint/favorite",
            params={"project_id": project_id, "dataPointID": datapoint_id},
        )
    )


@mcp.tool()
async def remove_favorite_datapoint(project_id: int, datapoint_id: str) -> str:
    """Remove a datapoint from personal favorites.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
    """
    c = _get_client()
    return _fmt(
        await c.delete(
            "/v2/datapoint/favorite",
            params={"project_id": project_id, "dataPointID": datapoint_id},
        )
    )


@mcp.tool()
async def get_datapoint_labels(project_id: int, datapoint_id: str) -> str:
    """Get all labels assigned to a datapoint.

    Args:
        project_id: The project's numeric ID.
        datapoint_id: The datapoint identifier.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            "/v2/datapoint/labels",
            params={"project_id": project_id, "dataPointID": datapoint_id},
        )
    )


# ===================================================================
# ALERTS
# ===================================================================


@mcp.tool()
async def create_threshold_alert(
    project_id: int,
    name: str,
    datapoint_id: str,
    info_threshold: float | None = None,
    warn_threshold: float | None = None,
    crit_threshold: float | None = None,
    email: str | None = None,
    telegram_chatid: str | None = None,
    period: int | None = None,
) -> str:
    """Create a new threshold-based alert.

    Args:
        project_id: The project's numeric ID.
        name: Alert name.
        datapoint_id: The datapoint to monitor.
        info_threshold: Info-level threshold value.
        warn_threshold: Warning-level threshold value.
        crit_threshold: Critical-level threshold value.
        email: Email address for notifications.
        telegram_chatid: Telegram chat ID for notifications.
        period: Evaluation period in seconds.
    """
    c = _get_client()
    body: dict = {"name": name, "dataPointID": datapoint_id}
    if info_threshold is not None:
        body["info_threshold"] = info_threshold
    if warn_threshold is not None:
        body["warn_threshold"] = warn_threshold
    if crit_threshold is not None:
        body["crit_threshold"] = crit_threshold
    if email is not None:
        body["email"] = email
    if telegram_chatid is not None:
        body["telegram_chatid"] = telegram_chatid
    if period is not None:
        body["period"] = period
    return _fmt(await c.post("/v2/alert/threshold", params={"project_id": project_id}, json_body=body))


@mcp.tool()
async def update_threshold_alert(alert_id: int, alert_details: str) -> str:
    """Update a threshold alert's configuration.

    Args:
        alert_id: The alert ID.
        alert_details: JSON string with fields to update.
    """
    c = _get_client()
    return _fmt(await c.put(f"/v2/alert/threshold/{alert_id}", json_body=json.loads(alert_details)))


@mcp.tool()
async def enable_alert(alert_id: int) -> str:
    """Enable an alert.

    Args:
        alert_id: The alert ID.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/alert/{alert_id}/enable"))


@mcp.tool()
async def disable_alert(alert_id: int) -> str:
    """Disable an alert.

    Args:
        alert_id: The alert ID.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/alert/{alert_id}/disable"))


@mcp.tool()
async def delete_alert(alert_id: int) -> str:
    """Delete an alert.

    Args:
        alert_id: The alert ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/alert/{alert_id}"))


# ===================================================================
# TASKS
# ===================================================================


@mcp.tool()
async def get_project_tasks(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """Get all tasks in a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/project/{project_id}/tasks",
            params={"page": page, "per_page": per_page},
        )
    )


@mcp.tool()
async def create_task(project_id: int, title: str, description: str | None = None) -> str:
    """Create a new task in a project.

    Args:
        project_id: The project's numeric ID.
        title: Task title.
        description: Task description.
    """
    c = _get_client()
    body: dict = {"title": title}
    if description is not None:
        body["description"] = description
    return _fmt(await c.post("/v2/task", params={"project_id": project_id}, json_body=body))


@mcp.tool()
async def get_task(task_id: int) -> str:
    """Get details of a task.

    Args:
        task_id: The task ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/task/{task_id}"))


@mcp.tool()
async def update_task(task_id: int, task_data: str) -> str:
    """Update a task.

    Args:
        task_id: The task ID.
        task_data: JSON string with fields to update (title, description, status, etc.).
    """
    c = _get_client()
    return _fmt(await c.put(f"/v2/task/{task_id}", json_body=json.loads(task_data)))


@mcp.tool()
async def delete_task(task_id: int) -> str:
    """Delete a task.

    Args:
        task_id: The task ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/task/{task_id}"))


@mcp.tool()
async def assign_task(task_id: int, user_id: int) -> str:
    """Assign a task to a user.

    Args:
        task_id: The task ID.
        user_id: The user ID to assign.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/task/{task_id}/assignee/{user_id}"))


@mcp.tool()
async def unassign_task(task_id: int, user_id: int) -> str:
    """Unassign a task from a user.

    Args:
        task_id: The task ID.
        user_id: The user ID to unassign.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/task/{task_id}/assignee/{user_id}"))


@mcp.tool()
async def add_task_comment(task_id: int, text: str) -> str:
    """Add a comment to a task.

    Args:
        task_id: The task ID.
        text: Comment text.
    """
    c = _get_client()
    return _fmt(await c.post(f"/v2/task/{task_id}/comments", json_body={"text": text}))


@mcp.tool()
async def delete_task_comment(task_id: int, comment_id: int) -> str:
    """Delete a comment from a task.

    Args:
        task_id: The task ID.
        comment_id: The comment ID.
    """
    c = _get_client()
    return _fmt(await c.delete(f"/v2/task/{task_id}/comments/{comment_id}"))


# ===================================================================
# COMPONENTS (global catalog)
# ===================================================================


@mcp.tool()
async def get_components() -> str:
    """Get all available component definitions."""
    c = _get_client()
    return _fmt(await c.get("/v2/components"))


@mcp.tool()
async def get_component_attribute_definitions(component_id: int) -> str:
    """Get all attribute definitions for a component type.

    Args:
        component_id: The component definition ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/component/{component_id}/attributeDefinitions"))


@mcp.tool()
async def get_component_pin_definitions(component_id: int) -> str:
    """Get all pins and their attributes for a component type.

    Args:
        component_id: The component definition ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/component/{component_id}/pins"))


# ===================================================================
# ANALYTICS
# ===================================================================


@mcp.tool()
async def get_analytics_functions() -> str:
    """Get all available analysis functions."""
    c = _get_client()
    return _fmt(await c.get("/v2/analytics/functions"))


@mcp.tool()
async def get_analytics_function(function_id: str) -> str:
    """Get details of a specific analysis function.

    Args:
        function_id: The analysis function identifier.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/analytics/functions/{function_id}"))


@mcp.tool()
async def get_analytics_instances(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """Get all analytics instances in a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            "/v2/analytics/instances",
            params={"project_id": project_id, "page": page, "per_page": per_page},
        )
    )


@mcp.tool()
async def create_analytics_instance(project_id: int, instance_config: str) -> str:
    """Create a new analytics instance.

    Args:
        project_id: The project's numeric ID.
        instance_config: JSON string with the instance configuration.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            "/v2/analytics/instance",
            params={"project_id": project_id},
            json_body=json.loads(instance_config),
        )
    )


@mcp.tool()
async def get_analytics_instance(instance_id: int, project_id: int) -> str:
    """Get an analytics instance's details.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/instance/{instance_id}",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def update_analytics_instance(instance_id: int, project_id: int, instance_config: str) -> str:
    """Update an analytics instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
        instance_config: JSON string with fields to update.
    """
    c = _get_client()
    return _fmt(
        await c.put(
            f"/v2/analytics/instance/{instance_id}",
            params={"project_id": project_id},
            json_body=json.loads(instance_config),
        )
    )


@mcp.tool()
async def delete_analytics_instance(instance_id: int, project_id: int) -> str:
    """Delete an analytics instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.delete(
            f"/v2/analytics/instance/{instance_id}",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def enable_analytics_instance(instance_id: int, project_id: int) -> str:
    """Enable an analytics instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/analytics/instance/{instance_id}/enable",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def disable_analytics_instance(instance_id: int, project_id: int) -> str:
    """Disable an analytics instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/analytics/instance/{instance_id}/disable",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def trigger_analytics_instance(instance_id: int, project_id: int) -> str:
    """Manually trigger an analytics instance to run.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/analytics/instance/{instance_id}/trigger",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def get_analytics_instance_result(
    instance_id: int,
    project_id: int,
    start: str | None = None,
    end: str | None = None,
    units_system: str | None = None,
    currency_system: str | None = None,
) -> str:
    """Get results for an analytics instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        units_system: Unit system.
        currency_system: Currency system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/instance/{instance_id}/result",
            params={
                "project_id": project_id,
                "start": start,
                "end": end,
                "units_system": units_system,
                "currency_system": currency_system,
            },
        )
    )


@mcp.tool()
async def get_analytics_instance_status(instance_id: int, project_id: int) -> str:
    """Get the status of an analytics instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/instance/{instance_id}/status",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def get_analytics_kpi_aggregation(project_id: int) -> str:
    """Get aggregated KPI results across a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/analytics/kpi_aggregation", params={"project_id": project_id}))


@mcp.tool()
async def get_analytics_components_kpi(project_id: int) -> str:
    """Get aggregated KPI results per component.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get("/v2/analytics/components/kpi_aggregation", params={"project_id": project_id}))


@mcp.tool()
async def get_analytics_kpi_overview(project_id: int) -> str:
    """Get a high-level KPI overview for a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/analytics/project/{project_id}/kpi_overview"))


@mcp.tool()
async def get_analytics_status(project_id: int) -> str:
    """Get the analytics status overview for a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/analytics/project/{project_id}/status"))


@mcp.tool()
async def get_technical_monitoring(
    project_id: int,
    start: str | None = None,
    end: str | None = None,
    units_system: str | None = None,
) -> str:
    """Get technical monitoring data for a project.

    Args:
        project_id: The project's numeric ID.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        units_system: Unit system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/project/{project_id}/technical_monitoring",
            params={"start": start, "end": end, "units_system": units_system},
        )
    )


@mcp.tool()
async def get_energy_efficiency(
    project_id: int,
    start: str | None = None,
    end: str | None = None,
    units_system: str | None = None,
) -> str:
    """Get energy efficiency analysis data for a project.

    Args:
        project_id: The project's numeric ID.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        units_system: Unit system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/project/{project_id}/energy_efficiency",
            params={"start": start, "end": end, "units_system": units_system},
        )
    )


@mcp.tool()
async def get_operational_optimization(
    project_id: int,
    start: str | None = None,
    end: str | None = None,
    units_system: str | None = None,
) -> str:
    """Get operational optimization data for a project.

    Args:
        project_id: The project's numeric ID.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        units_system: Unit system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/project/{project_id}/operational_optimization",
            params={"start": start, "end": end, "units_system": units_system},
        )
    )


@mcp.tool()
async def get_compliance(project_id: int) -> str:
    """Get compliance data for a project.

    Args:
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/analytics/project/{project_id}/compliance"))


@mcp.tool()
async def get_component_results(
    cip_id: int,
    project_id: int,
    units_system: str | None = None,
    currency_system: str | None = None,
) -> str:
    """Get analytics results for a specific component in a project.

    Args:
        cip_id: The component-in-project ID.
        project_id: The project's numeric ID.
        units_system: Unit system.
        currency_system: Currency system.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/analytics/componentInProject/{cip_id}/results",
            params={
                "project_id": project_id,
                "units_system": units_system,
                "currency_system": currency_system,
            },
        )
    )


# ===================================================================
# CONTROLS
# ===================================================================


@mcp.tool()
async def get_controls_apps() -> str:
    """Get all available controls apps."""
    c = _get_client()
    return _fmt(await c.get("/v2/controls/apps"))


@mcp.tool()
async def get_controls_app(app_id: str) -> str:
    """Get details of a specific controls app.

    Args:
        app_id: The controls app identifier.
    """
    c = _get_client()
    return _fmt(await c.get(f"/v2/controls/apps/{app_id}"))


@mcp.tool()
async def get_controls_instances(
    project_id: int,
    page: int | None = None,
    per_page: int | None = None,
) -> str:
    """Get all controls instances in a project.

    Args:
        project_id: The project's numeric ID.
        page: Page number.
        per_page: Items per page.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            "/v2/controls/instances",
            params={"project_id": project_id, "page": page, "per_page": per_page},
        )
    )


@mcp.tool()
async def create_controls_instance(project_id: int, instance_config: str) -> str:
    """Create a new controls instance.

    Args:
        project_id: The project's numeric ID.
        instance_config: JSON string with the controls instance configuration.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            "/v2/controls/instance",
            params={"project_id": project_id},
            json_body=json.loads(instance_config),
        )
    )


@mcp.tool()
async def get_controls_instance(instance_id: int, project_id: int) -> str:
    """Get a controls instance's details.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/controls/instance/{instance_id}",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def update_controls_instance(instance_id: int, project_id: int, instance_config: str) -> str:
    """Update a controls instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
        instance_config: JSON string with fields to update.
    """
    c = _get_client()
    return _fmt(
        await c.put(
            f"/v2/controls/instance/{instance_id}",
            params={"project_id": project_id},
            json_body=json.loads(instance_config),
        )
    )


@mcp.tool()
async def delete_controls_instance(instance_id: int, project_id: int) -> str:
    """Delete a controls instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.delete(
            f"/v2/controls/instance/{instance_id}",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def enable_controls_instance(instance_id: int, project_id: int) -> str:
    """Enable a controls instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/controls/instance/{instance_id}/enable",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def disable_controls_instance(instance_id: int, project_id: int) -> str:
    """Disable a controls instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.post(
            f"/v2/controls/instance/{instance_id}/disable",
            params={"project_id": project_id},
        )
    )


@mcp.tool()
async def get_controls_instance_status(instance_id: int, project_id: int) -> str:
    """Get the status of a controls instance.

    Args:
        instance_id: The instance ID.
        project_id: The project's numeric ID.
    """
    c = _get_client()
    return _fmt(
        await c.get(
            f"/v2/controls/instance/{instance_id}/status",
            params={"project_id": project_id},
        )
    )


# ===================================================================
# Entrypoint
# ===================================================================


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
