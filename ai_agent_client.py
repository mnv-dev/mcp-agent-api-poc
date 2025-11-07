import json
import httpx
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

if not PROJECT_ID or not CLOUD_LOCATION:
    print("FATAL: Missing GOOGLE_PROJECT_ID or GOOGLE_CLOUD_LOCATION in .env file.")
    sys.exit(1)

def extract_text(response) -> str:
    try:
        if not getattr(response, "candidates", None):
            return ""
        cand = response.candidates[0]
        if not getattr(cand, "content", None) or not getattr(cand.content, "parts", None):
            return ""
        parts = cand.content.parts
        texts = []
        for p in parts:
            text_val = getattr(p, "text", None)
            if text_val is None and hasattr(p, "as_dict"):
                d = p.as_dict()
                text_val = d.get("text")
            if text_val:
                texts.append(text_val)
        return "".join(texts).strip()
    except Exception:
        return getattr(response, "text", "")

EMPLOYEE_TOOLS_SCHEMA = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name='list_employees',
                description="Retrieves a list of employees. Can filter using partial matches on name, email, or position.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING, description="Optional partial name filter."),
                        "email": types.Schema(type=types.Type.STRING, description="Optional partial email filter."),
                        "position": types.Schema(type=types.Type.STRING, description="Optional position filter."),
                        "limit": types.Schema(type=types.Type.INTEGER, description="Maximum number of results to return. Default is 100.")
                    },
                )
            ),
            types.FunctionDeclaration(
                name='create_employee_record',
                description="Saves a new employee's name, email, and position to the employee database.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING, description="The full name of the employee."),
                        "email": types.Schema(type=types.Type.STRING, description="The unique email address of the employee."),
                        "position": types.Schema(type=types.Type.STRING, description="The employee's job title or role.")
                    },
                    required=["name", "email", "position"]
                )
            ),
            types.FunctionDeclaration(
                name='get_employee_details',
                description="Retrieves a single employee record by their unique ID.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "employee_id": types.Schema(type=types.Type.INTEGER, description="The unique numerical ID of the employee.")
                    },
                    required=["employee_id"]
                )
            ),
        ]
    )
]

# MCP call via JSON-RPC to the MCP server
def execute_mcp_call(function_call: types.FunctionCall) -> str:
    method_name = function_call.name
    params = dict(function_call.args)
    mcp_request = {"jsonrpc": "2.0", "method": method_name, "params": params, "id": 1234}
    print(f"\n[AGENT] Calling MCP Server with method: **{method_name}**...")
    try:
        response = httpx.post(MCP_SERVER_URL, headers={"Content-Type": "application/json"}, json=mcp_request)
        response.raise_for_status()
        mcp_response = response.json()
        return json.dumps(mcp_response.get('result', mcp_response))
    except httpx.HTTPError as e:
        return json.dumps({"error": f"HTTP error calling MCP: {e}", "details": e.response.text})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

def run_agent_turn(client, conversation_history, prompt):
    conversation_history.append(prompt)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=conversation_history,
        config=types.GenerateContentConfig(tools=EMPLOYEE_TOOLS_SCHEMA),
    )
    if response.function_calls:
        print("[AGENT] Model requested a tool call.")
        tool_contents = []
        for function_call in response.function_calls:
            result_data = execute_mcp_call(function_call)
            tool_contents.append(
                types.Content(
                    role='function',
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={"result": result_data}
                        )
                    ]
                )
            )
        if getattr(response, "candidates", None) and response.candidates and response.candidates[0].content:
            conversation_history.append(response.candidates[0].content)
        conversation_history.extend(tool_contents)
        print("[AGENT] Sending tool results back to the model for final answer...")
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=conversation_history,
            config=types.GenerateContentConfig(tools=EMPLOYEE_TOOLS_SCHEMA),
        )
        if getattr(final_response, "candidates", None) and final_response.candidates and final_response.candidates[0].content:
            conversation_history.append(final_response.candidates[0].content)
        return extract_text(final_response)
    else:
        if getattr(response, "candidates", None) and response.candidates and response.candidates[0].content:
            conversation_history.append(response.candidates[0].content)
        return extract_text(response)

def chat():
    client = genai.Client(project=PROJECT_ID, location=CLOUD_LOCATION)
    conversation_history = []
    print("Welcome to the Conversational MCP Agent! Type 'exit' or 'quit' to end.")
    while True:
        user_input = input("\n[USER] > ")
        if user_input.lower() in ['exit', 'quit']:
            break
        try:
            agent_response = run_agent_turn(client, conversation_history, user_input)
            print("\n[AGENT] **Response**:")
            print(agent_response)
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            break

if __name__ == "__main__":
    print("Initializing Gemini Client for Project...")
    chat()