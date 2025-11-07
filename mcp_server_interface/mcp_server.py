from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import httpx
import os
from mcp_metadata import EMPLOYEE_TOOL_METADATA

REST_API_BASE_URL = os.environ.get("REST_API_BASE_URL",
                                   "http://127.0.0.1:8000")

app = FastAPI(title="MCP Server Interface")
http_client = httpx.AsyncClient(base_url=REST_API_BASE_URL)

# REST POST /employees/
async def call_create_employee(params):
    data = {
        "name": params.get("name"),
        "email": params.get("email"),
        "position": params.get("position")
    }
    response = await http_client.post("/employees/", json=data)
    response.raise_for_status()
    return response.json()

# REST GET /employees/{id}
async def call_get_employee(params):
    employee_id = params.get("employee_id")
    response = await http_client.get(f"/employees/{employee_id}")
    response.raise_for_status()
    return response.json()

# REST GET /employees/?filters
async def call_list_employees(params: dict):
    query_params = {k: v for k, v in params.items() if v is not None and v != ""}
    response = await http_client.get("/employees/", params=query_params)
    response.raise_for_status()
    return response.json()

MCP_TOOL_MAP = {
    "create_employee_record": call_create_employee,
    "get_employee_details": call_get_employee,
    "list_employees": call_list_employees,
}

# Handle MCP JSON-RPC requests
@app.post("/mcp/")
async def mcp_handler(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})

    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    if method == "mcp/tool/list":
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "result": EMPLOYEE_TOOL_METADATA["result"]["tools"],
            "id": request_id
        })

    if method in MCP_TOOL_MAP:
        try:
            result = await MCP_TOOL_MAP[method](params)
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })
        except httpx.HTTPError as e:
            return JSONResponse(status_code=500, content={
                "jsonrpc": "2.0",
                "error": {"code": 500, "message": f"Backend API Error: {e.response.status_code} - {e.response.text}"},
                "id": request_id
            })

    return JSONResponse(status_code=404, content={
        "jsonrpc": "2.0",
        "error": {"code": 404, "message": f"Method not found: {method}"},
        "id": request_id
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8001, reload=True)