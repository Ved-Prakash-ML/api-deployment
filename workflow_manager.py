import time
import json
from servicenow_integration import ServiceNowIntegration
class AutoGenWorkflowManager:
    
    def __init__(self, project_client, classification_agent_id, troubleshooting_agent_id, ticketing_agent_id):
        self.project_client = project_client
        self.classification_agent_id = classification_agent_id
        self.troubleshooting_agent_id = troubleshooting_agent_id
        self.ticketing_agent_id = ticketing_agent_id
        self.tasks = {}
        self.results = {}
        self.completed_tasks = set()

    def add_task(self, task_id, description, dependencies=None):
        """Adds a new task to the workflow."""
        self.tasks[task_id] = {
            "description": description,
            "status": "pending",
            "dependencies": dependencies or []
        }

    def get_ready_tasks(self):
        """Identifies tasks whose dependencies have been met."""
        return [
            task_id for task_id, task in self.tasks.items()
            if task["status"] == "pending" and all(dep in self.completed_tasks for dep in task["dependencies"])
        ]

    def execute_task(self, task_id, thread_id):
        """Executes a single task by invoking the appropriate Azure AI agent."""
        task = self.tasks[task_id]
        print(f"\n--- Executing: {task_id} ---")

        agent_map = {
            "classify_issue": self.classification_agent_id,
            "troubleshoot_issue": self.troubleshooting_agent_id,
            "ticketing": self.ticketing_agent_id
        }

        agent_id = agent_map.get(task_id)
        if not agent_id:
            print(f"[FAIL] Failed: {task_id} | Error: No agent configured for this task.")
            task["status"] = "failed"
            return None

        try:
            self.project_client.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=task["description"]
            )
            
            self.project_client.agents.runs.create_and_process(
                thread_id=thread_id,
                agent_id=agent_id
            )
            
            messages = list(self.project_client.agents.messages.list(thread_id=thread_id, order="desc"))
            response = messages[0].content if messages else None
            
            self.results[task_id] = response
            self.completed_tasks.add(task_id)
            task["status"] = "completed"
            print(f"[OK] Completed: {task_id}")
            return response
            
        except Exception as e:
            task["status"] = "failed"
            print(f"[FAIL] Failed: {task_id} | Error: {e}")
            return None
