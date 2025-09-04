from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import json
from config import (
    project_client,
    CLASSIFICATION_AGENT_ID,
    TROUBLESHOOTING_AGENT_ID,
    TICKETING_AGENT_ID
)
from workflow_manager import AutoGenWorkflowManager

app = FastAPI(title="Outlook Issue Resolution API")

class OutlookIssue(BaseModel):
    issue_description: str

class WorkflowResponse(BaseModel):
    thread_id: str
    trace_id: str
    status: str
    classification_result: str = None
    troubleshooting_result: str = None
    ticket_details: str = None

@app.post("/api/outlook/resolve", response_model=WorkflowResponse)
async def resolve_outlook_issue(issue: OutlookIssue):
    try:
        workflow = AutoGenWorkflowManager(
            project_client,
            classification_agent_id=CLASSIFICATION_AGENT_ID,
            troubleshooting_agent_id=TROUBLESHOOTING_AGENT_ID,
            ticketing_agent_id=TICKETING_AGENT_ID
        )
        
        thread = project_client.agents.threads.create()
        thread_id = thread.id
        trace_id = str(uuid.uuid4())
        
        # Classification
        workflow.add_task("classify_issue", f"Classify this Outlook issue: {issue.issue_description}")
        workflow.execute_task("classify_issue", thread_id)
        classi_output = workflow.results.get("classify_issue")
        
        classification_result = ""
        troubleshooting_result = ""
        ticket_details = ""
        
        if classi_output and isinstance(classi_output, list):
            classification_result = classi_output[0]['text']['value']
        
        # Check if in scope
        if classi_output and "out of scope" not in str(classi_output).lower():
            # Troubleshooting
            workflow.add_task("troubleshoot_issue", f"Provide PowerShell script for: {classification_result}")
            workflow.execute_task("troubleshoot_issue", thread_id)
            
            troubleshoot_output = workflow.results.get("troubleshoot_issue")
            if troubleshoot_output and isinstance(troubleshoot_output, list):
                troubleshooting_result = troubleshoot_output[0]['text']['value']
                
                # Create resolution ticket
                workflow.add_task("ticketing", f"Issue resolved. Original: {issue.issue_description}")
                workflow.execute_task("ticketing", thread_id)
            else:
                # Troubleshooting failed - create ticket
                workflow.add_task("ticketing", f"Troubleshooting failed for: {issue.issue_description}")
                workflow.execute_task("ticketing", thread_id)
        else:
            # Out of scope - create ticket
            workflow.add_task("ticketing", f"Out of scope issue: {issue.issue_description}")
            workflow.execute_task("ticketing", thread_id)
        
        # Get ticket details
        ticketing_result = workflow.results.get("ticketing")
        if ticketing_result and isinstance(ticketing_result, list):
            ticket_details = ticketing_result[0]['text']['value']
        
        return WorkflowResponse(
            thread_id=thread_id,
            trace_id=trace_id,
            status="completed",
            classification_result=classification_result,
            troubleshooting_result=troubleshooting_result,
            ticket_details=ticket_details
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
