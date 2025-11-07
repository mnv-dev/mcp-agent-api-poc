# MCP Employee API - Proof of Concept

A proof-of-concept implementation demonstrating the **Model Context Protocol (MCP)** as an intermediary layer between REST API endpoints and AI agents. This project showcases how AI agents can interact with backend services through a standardized MCP interface.

## Architecture Overview

This POC implements a three-layer architecture:

```
┌─────────────────┐
│   AI Agent      │  (Google Gemini)
│  (Conversational│
│    Interface)   │
└────────┬────────┘
         │ JSON-RPC
         ↓
┌─────────────────┐
│   MCP Server    │  (Port 8001)
│  (Translation   │
│     Layer)      │
└────────┬────────┘
         │ REST API
         ↓
┌─────────────────┐
│  REST API       │  (Port 8000)
│  (FastAPI +     │
│   PostgreSQL)   │
└─────────────────┘
```

### Components

1. **REST API Layer** (`main.py`): FastAPI-based CRUD operations for employee management
2. **MCP Server Layer** (`mcp_server.py`): Translates JSON-RPC calls from AI agents to REST API calls
3. **AI Agent Client** (`ai_agent_client.py`): Conversational interface using Google Gemini with function calling

## Features

- **Employee CRUD Operations**: Create, read, and list employee records
- **MCP Protocol Implementation**: JSON-RPC 2.0 compliant interface
- **AI-Powered Interactions**: Natural language queries via Google Gemini
- **Filtering & Pagination**: Search employees by name, email or position
- **PostgreSQL Database**: Robust data persistence

## 🔧 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Google Cloud Project with Vertex AI API enabled
- Google Cloud credentials configured

## 📦 Installation

1. **Clone the repository** (or extract the project files)

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**

```bash
# Create the database
createdb employees_db

# Or using psql
psql -U postgres
CREATE DATABASE employees_db;
\q
```

## ⚙️ Configuration

1. **Create a `.env` file** in the project root with the following variables:

```env
# Google Configuration
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_CLOUD_LOCATION=us-central1
MODEL_NAME=gemini-2.5-flash

# REST API base URL for MCP server to call
REST_API_BASE_URL=http://127.0.0.1:8000

# MCP Server URL
MCP_SERVER_URL=http://127.0.0.1:8001/mcp/

# Database configuration
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=employees_db
```

2. **Configure Google Cloud authentication**

```bash
# Set up application default credentials
gcloud auth application-default login

# Or set the service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## 🚀 Usage

### Step 1: Start the REST API Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

### Step 2: Start the MCP Server

In a new terminal:

```bash
python mcp_server.py
```

The MCP server will be available at `http://localhost:8001`

### Step 3: Run the AI Agent Client

In a new terminal:

```bash
python ai_agent_client.py
```

### Interacting with the AI Agent

Once the agent is running, you can use natural language queries:

```
[USER] > Create an employee named John Doe with email john.doe@company.com as a Software Engineer

[USER] > List all employees

[USER] > Find employees with position Software Engineer

[USER] > Get details for employee with ID 1

[USER] > Show me all employees with "Engineer" in their position
```

Type `exit` or `quit` to end the session.

## API Documentation

### REST API Endpoints

#### Create Employee
```http
POST /employees/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john.doe@company.com",
  "position": "Software Engineer"
}
```

#### List Employees (with filters)
```http
GET /employees/?name=John&position=Engineer&limit=10&skip=0
```

#### Get Employee by ID
```http
GET /employees/{employee_id}
```

### MCP Protocol Endpoints

#### List Available Tools
```json
{
  "jsonrpc": "2.0",
  "method": "mcp/tool/list",
  "params": {},
  "id": 1
}
```

#### Call MCP Tool
Example request for `create_employee_record` tool:
```json
{
  "jsonrpc": "2.0",
  "method": "create_employee_record",
  "params": {
    "name": "John Doe",
    "email": "john.doe@company.com",
    "position": "Software Engineer"
  },
  "id": 1
}
```

## MCP Protocol

The MCP (Model Context Protocol) layer implements three main tools:

### 1. `create_employee_record`
Saves a new employee to the database.

**Parameters:**
- `name` (string, required): Full name of the employee
- `email` (string, required): Unique email address
- `position` (string, required): Job title or role

### 2. `get_employee_details`
Retrieves a single employee by ID.

**Parameters:**
- `employee_id` (integer, required): Unique employee ID

### 3. `list_employees`
Retrieves a list of employees with optional filters.

**Parameters:**
- `name` (string, optional): Partial name filter
- `email` (string, optional): Partial email filter
- `position` (string, optional): Position filter
- `limit` (integer, optional): Maximum results (default: 100)

## How It Works

### Request Flow

1. **User Input**: User types a natural language query
2. **AI Processing**: Gemini interprets the intent and determines which tool to call
3. **Function Call**: AI generates a structured function call
4. **MCP Translation**: MCP server receives JSON-RPC request and translates to REST API call
5. **Database Operation**: REST API performs CRUD operation on PostgreSQL
6. **Response Chain**: Result flows back through MCP server to AI agent
7. **Natural Response**: AI formats the result into natural language for the user

### Example Flow

```
User: "Add Jane Smith as a Data Scientist with email jane@company.com"
  ↓
Gemini: Calls create_employee_record(name="Jane Smith", email="jane@company.com", position="Data Scientist")
  ↓
MCP Server: POST http://localhost:8000/employees/ with JSON body
  ↓
REST API: Inserts record into PostgreSQL
  ↓
Returns: {"id": 1, "name": "Jane Smith", "email": "jane@company.com", "position": "Data Scientist"}
  ↓
Gemini: "I've successfully created a new employee record for Jane Smith as a Data Scientist."
```

## Testing

### Manual Testing - REST API

```bash
# Create an employee
curl -X POST "http://localhost:8000/employees/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","position":"Tester"}'

# List all employees
curl "http://localhost:8000/employees/"

# Get specific employee
curl "http://localhost:8000/employees/1"
```

### Manual Testing - MCP Server

```bash
# List available tools
curl -X POST "http://localhost:8001/mcp/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"mcp/tool/list","params":{},"id":1}'

# Create employee via MCP
curl -X POST "http://localhost:8001/mcp/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"create_employee_record","params":{"name":"MCP Test","email":"mcp@test.com","position":"Engineer"},"id":1}'
```

### Sample Conversation Tests

```
1. "Create an employee with details Carol (carol@co.com, Designer)"
2. "Show me all employees"
3. "Find all developers"
4. "What's the email of employee ID 2?"
5. "List employees whose names start with 'A'"
```

## Troubleshooting

### Google Cloud Authentication Issues

**Problem**: `DefaultCredentialsError: Could not automatically determine credentials`

**Solution**:
```bash
gcloud auth application-default login
# or
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### MCP Server Connection Issues

**Problem**: AI agent can't reach MCP server

**Solution**:
- Verify MCP server is running on port 8001
- Check `MCP_SERVER_URL` in `.env` matches the server address
- Ensure firewall allows local connections
