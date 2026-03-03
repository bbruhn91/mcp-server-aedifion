# mcp-server-aedifion

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that provides tools for interacting with the [aedifion](https://www.aedifion.com/) cloud API. This server enables AI assistants (Claude, etc.) to manage building IoT data, analytics, controls, and more through the aedifion platform.

## What is aedifion?

aedifion provides a cloud platform for building performance optimization. Their API offers access to:

- **Building IoT data** &mdash; datapoints, timeseries, setpoints
- **Analytics** &mdash; automated analysis functions, KPI tracking, energy efficiency monitoring
- **Controls** &mdash; remote building control apps
- **Project management** &mdash; components, tags, labels, logbooks, tasks, alerts
- **Weather data** &mdash; current conditions and forecasts for building locations

API documentation: https://api.cloud.aedifion.eu/ui/

## Installation

### Using `uv` (recommended)

```bash
uv pip install git+https://github.com/tookta/mcp-server-aedifion.git
```

### Using `pip`

```bash
pip install git+https://github.com/tookta/mcp-server-aedifion.git
```

### From source

```bash
git clone https://github.com/tookta/mcp-server-aedifion.git
cd mcp-server-aedifion
uv pip install -e .
```

## Configuration

### Environment variables

The server requires aedifion API credentials. Create a `.env` file in your working directory (see `.env.example`):

```bash
cp .env.example .env
# Edit .env with your credentials
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `AEDIFION_USERNAME` | Yes* | &mdash; | Your aedifion account email |
| `AEDIFION_PASSWORD` | Yes* | &mdash; | Your aedifion account password |
| `AEDIFION_TOKEN` | No | &mdash; | Pre-obtained bearer token (alternative to username/password) |
| `AEDIFION_BASE_URL` | No | `https://api.cloud.aedifion.eu` | API base URL |

\* Required unless `AEDIFION_TOKEN` is set.

### Claude Desktop

Add the server to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aedifion": {
      "command": "mcp-server-aedifion",
      "env": {
        "AEDIFION_USERNAME": "your-email@example.com",
        "AEDIFION_PASSWORD": "your-password"
      }
    }
  }
}
```

Or if running from source with `uv`:

```json
{
  "mcpServers": {
    "aedifion": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/mcp-server-aedifion",
        "run", "mcp-server-aedifion"
      ],
      "env": {
        "AEDIFION_USERNAME": "your-email@example.com",
        "AEDIFION_PASSWORD": "your-password"
      }
    }
  }
}
```

### Claude Code

Add the server to your Claude Code settings:

```bash
claude mcp add aedifion -- mcp-server-aedifion
```

Or with environment variables:

```bash
claude mcp add aedifion --env AEDIFION_USERNAME=your-email --env AEDIFION_PASSWORD=your-password -- mcp-server-aedifion
```

## Available tools

The server exposes **95+ tools** organized by category, covering all major areas of the aedifion API.

### Meta

| Tool | Description |
|---|---|
| `ping` | Check API server availability |
| `get_api_version` | Get the aedifion API version |
| `get_endpoints` | List all available API endpoints |
| `get_label_definitions` | Get all label definitions |
| `get_label_systems` | Get available unit/label systems (SI, imperial, etc.) |

### User

| Tool | Description |
|---|---|
| `get_user` | Get current user details |
| `update_user` | Update user profile (first name, last name) |
| `get_user_permissions` | Get user's project permissions |
| `get_user_roles` | Get user's assigned roles |

### AI assistant

| Tool | Description |
|---|---|
| `ai_get_threads` | List AI conversation threads |
| `ai_get_thread` | Get messages in a thread |
| `ai_chat` | Send a message to the aedifion AI assistant |
| `ai_delete_thread` | Delete a conversation thread |

### Company

| Tool | Description |
|---|---|
| `get_company` | Get company details with projects and users |
| `update_company` | Update company name/description |
| `get_company_roles` | List company roles |
| `get_company_permissions` | List company project permissions |
| `get_company_labels` | List company labels |
| `create_project` | Create a new project |
| `create_user` | Create a new user |
| `get_company_user` | Get user details |
| `delete_company_user` | Delete a user |

### Realm

| Tool | Description |
|---|---|
| `get_realm_companies` | List all companies in the realm |
| `get_realm_projects` | List all projects in the realm |
| `get_realm_users` | List all users in the realm |

### Project

| Tool | Description |
|---|---|
| `get_project` | Get project details |
| `update_project` | Update project name/description |
| `delete_project` | Delete a project (requires name confirmation) |
| `get_project_datapoints` | List datapoints with optional filtering |
| `get_project_timeseries` | Get timeseries data for multiple datapoints |
| `write_project_timeseries` | Write timeseries data |
| `delete_project_timeseries` | Delete timeseries data |
| `get_project_alerts` | List project alerts |
| `get_project_tags` | List datapoint tags |
| `add_project_tag` | Add/overwrite a tag |
| `delete_project_tag` | Delete a tag |
| `get_project_components` | List project components |
| `get_project_component` | Get component details |
| `add_project_component` | Add a component to a project |
| `delete_project_component` | Remove a component |
| `get_component_pins` | Get pin mappings for a component |
| `map_component_pin` | Map a pin to a datapoint |
| `unmap_component_pin` | Unmap a pin |
| `get_component_attributes` | Get component attributes |
| `get_project_permissions` | Get project permissions |
| `get_project_labels` | Get project labels |
| `set_datapoint_renamings` | Set alternate keys for datapoints |
| `get_project_setpoints` | List setpoints |
| `write_setpoint` | Write a setpoint value |
| `delete_setpoint` | Delete a setpoint |
| `get_setpoint_status` | Get setpoint status |
| `get_project_weather` | Get current weather |
| `get_project_weather_forecast` | Get weather forecast |
| `grant_ai_consent` | Grant/revoke AI assistant consent |
| `get_plot_views` | List saved plot views |
| `create_plot_view` | Create a plot view |
| `delete_plot_view` | Delete a plot view |
| `get_logbooks` | List project logbooks |
| `create_logbook` | Create a logbook |
| `get_logbook` | Get logbook details |
| `delete_logbook` | Delete a logbook |
| `create_logbook_entry` | Create a logbook entry |
| `delete_logbook_entry` | Delete a logbook entry |
| `get_project_comments` | List project comments |
| `add_project_comment` | Add a comment |
| `delete_project_comment` | Delete a comment |

### Datapoint

| Tool | Description |
|---|---|
| `get_datapoint` | Get datapoint details |
| `update_datapoint` | Update datapoint description/unit |
| `delete_datapoint` | Delete a datapoint |
| `get_datapoint_timeseries` | Get timeseries for a single datapoint |
| `get_datapoint_usage` | Get usage information (where referenced) |
| `get_favorite_datapoints` | List favorite datapoints |
| `set_favorite_datapoint` | Mark as favorite |
| `remove_favorite_datapoint` | Remove from favorites |
| `get_datapoint_labels` | Get datapoint labels |

### Alerts

| Tool | Description |
|---|---|
| `create_threshold_alert` | Create a threshold-based alert |
| `update_threshold_alert` | Update alert configuration |
| `enable_alert` | Enable an alert |
| `disable_alert` | Disable an alert |
| `delete_alert` | Delete an alert |

### Tasks

| Tool | Description |
|---|---|
| `get_project_tasks` | List project tasks |
| `create_task` | Create a task |
| `get_task` | Get task details |
| `update_task` | Update a task |
| `delete_task` | Delete a task |
| `assign_task` | Assign a task to a user |
| `unassign_task` | Unassign a task |
| `add_task_comment` | Add a comment to a task |
| `delete_task_comment` | Delete a task comment |

### Components (global catalog)

| Tool | Description |
|---|---|
| `get_components` | List all component definitions |
| `get_component_attribute_definitions` | Get attribute definitions for a component type |
| `get_component_pin_definitions` | Get pin definitions for a component type |

### Analytics

| Tool | Description |
|---|---|
| `get_analytics_functions` | List available analysis functions |
| `get_analytics_function` | Get analysis function details |
| `get_analytics_instances` | List analytics instances in a project |
| `create_analytics_instance` | Create an analytics instance |
| `get_analytics_instance` | Get instance details |
| `update_analytics_instance` | Update an instance |
| `delete_analytics_instance` | Delete an instance |
| `enable_analytics_instance` | Enable an instance |
| `disable_analytics_instance` | Disable an instance |
| `trigger_analytics_instance` | Manually trigger execution |
| `get_analytics_instance_result` | Get instance results |
| `get_analytics_instance_status` | Get instance status |
| `get_analytics_kpi_aggregation` | Get aggregated KPIs for a project |
| `get_analytics_components_kpi` | Get per-component KPI aggregation |
| `get_analytics_kpi_overview` | High-level KPI overview |
| `get_analytics_status` | Analytics status overview |
| `get_technical_monitoring` | Technical monitoring data |
| `get_energy_efficiency` | Energy efficiency analysis |
| `get_operational_optimization` | Operational optimization data |
| `get_compliance` | Compliance data |
| `get_component_results` | Component-specific analytics results |

### Controls

| Tool | Description |
|---|---|
| `get_controls_apps` | List available controls apps |
| `get_controls_app` | Get controls app details |
| `get_controls_instances` | List controls instances |
| `create_controls_instance` | Create a controls instance |
| `get_controls_instance` | Get instance details |
| `update_controls_instance` | Update an instance |
| `delete_controls_instance` | Delete an instance |
| `enable_controls_instance` | Enable an instance |
| `disable_controls_instance` | Disable an instance |
| `get_controls_instance_status` | Get instance status |

## Usage examples

### Check API connectivity

> "Ping the aedifion API to check if it's available."

### Browse projects and data

> "Show me all projects in my company."
>
> "List all datapoints in project 42 that contain 'temperature' in their name."

### Query timeseries data

> "Get the temperature readings for datapoint 'bacnet500-4120-External-Air-Temperature' in project 42 from the last 24 hours, resampled to 15-minute intervals."

### Analytics

> "What analysis functions are available? Show me the KPI overview for project 42."
>
> "Get the energy efficiency analysis for project 42 for the last month."

### Alerts

> "Create a threshold alert on the room temperature datapoint in project 42 that warns at 26C and goes critical at 30C."

### Building controls

> "List all active controls instances in project 42 and show their current status."

### Weather

> "What's the current weather at the building location for project 42?"

## Development

### Setup

```bash
git clone https://github.com/tookta/mcp-server-aedifion.git
cd mcp-server-aedifion
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Running locally

```bash
# With environment variables
AEDIFION_USERNAME=user@example.com AEDIFION_PASSWORD=pass mcp-server-aedifion

# Or with a .env file
cp .env.example .env
# Edit .env with your credentials
mcp-server-aedifion
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector mcp-server-aedifion
```

## Authentication

The server supports two authentication methods:

1. **Username/Password** (recommended): Set `AEDIFION_USERNAME` and `AEDIFION_PASSWORD`. The server automatically obtains and refreshes bearer tokens via `POST /v2/user/token`.

2. **Pre-obtained token**: Set `AEDIFION_TOKEN` with a valid bearer token. Useful for short-lived sessions or when credentials shouldn't be stored.

Token refresh happens automatically when a `401 Unauthorized` response is received.

## Architecture

```
src/mcp_server_aedifion/
  __init__.py       # Package init
  client.py         # HTTP client with auth handling
  server.py         # MCP server with tool definitions
```

- **`client.py`** &mdash; Async HTTP client built on `httpx`. Handles Basic Auth -> bearer token exchange, automatic token refresh, and provides `get`/`post`/`put`/`delete` helpers.
- **`server.py`** &mdash; MCP server built with `FastMCP`. Registers 95+ tools covering all 12 API categories. Each tool maps to one or more aedifion API endpoints.

## License

MIT &mdash; see [LICENSE](LICENSE).
