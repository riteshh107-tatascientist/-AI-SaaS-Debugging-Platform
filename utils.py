import uuid

# ---------------- PROFESSIONAL EXPLANATION ----------------
def explain(cat):
    mapping = {
        "Dependency": "Missing library or package issue",
        "Syntax Error": "Code structure mistake detected",
        "Name Error": "Undefined variable used",
        "Type Error": "Data type mismatch issue",
        "Value Error": "Invalid value passed to function",
        "Index Error": "List index out of range",
        "Key Error": "Dictionary key not found",
        "Runtime Error": "Execution-time failure detected",
        "File Error": "File path or file missing issue",
        "Environment": "System or permission related issue",
        "Build Error": "Project build failure"
    }
    return mapping.get(cat, "Unknown issue type")

# ---------------- TICKET FORMAT ENGINE ----------------
def format_out(log, cat, sol):
    ticket_id = "DBG-" + str(uuid.uuid4())[:8].upper()

    return {
        "ticket_id": ticket_id,
        "log": log,
        "category": cat,
        "explanation": explain(cat),

        # 🔥 PROFESSIONAL STEP-BY-STEP RESPONSE
        "solution_steps": [
            "Step 1: Identify the root cause from error logs",
            f"Step 2: Issue type detected → {cat}",
            f"Step 3: Apply fix → {sol}",
            "Step 4: Restart environment and re-run code",
            "Step 5: Verify if error is resolved"
        ],

        "final_solution": sol,
        "status": "RESOLVED"
    }