EMPLOYEE_TOOL_METADATA = {
    "jsonrpc": "2.0",
    "result": {
        "tools": [
            {
                "name": "create_employee_record",
                "description": "Saves a new employee's name, email, and position to the employee database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The full name of the employee."},
                        "email": {"type": "string", "description": "The unique email address of the employee."},
                        "position": {"type": "string", "description": "The employee's job title or role."}
                    },
                    "required": ["name", "email", "position"]
                }
            },
            {
                "name": "get_employee_details",
                "description": "Retrieves a single employee record by their unique ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {"type": "integer", "description": "The unique numerical ID of the employee."}
                    },
                    "required": ["employee_id"]
                }
            },
            {
                "name": "list_employees",
                "description": "Retrieves a list of employees. Can filter using partial matches on name, email, or position.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Optional partial name filter."},
                        "email": {"type": "string", "description": "Optional partial email filter."},
                        "position": {"type": "string", "description": "Optional position filter."},
                        "limit": {"type": "integer", "description": "Maximum number of results to return. Default is 100."}
                    },
                    "required": []
                }
            }
        ]
    }
}