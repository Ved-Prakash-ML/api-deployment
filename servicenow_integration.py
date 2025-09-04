import requests
import json
import base64

class ServiceNowIntegration:
    def __init__(self, instance_url, username, password):
        self.instance_url = instance_url
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_incident(self, short_description, description, priority="3", urgency="3"):
        url = f"{self.instance_url}/api/now/table/incident"
        
        data = {
            "short_description": short_description,
            "description": description,
            "category": "IT Support",
            "subcategory": "Email/Outlook",
            "priority": priority,
            "urgency": urgency,
            "caller_id": "admin",
            "assignment_group": "IT Support"
        }
        
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code == 201:
            result = response.json()
            return {
                "success": True,
                "ticket_number": result['result']['number'],
                "sys_id": result['result']['sys_id']
            }
        else:
            return {
                "success": False,
                "error": response.text
            }
    
    def update_incident(self, ticket_number, update_data):
        get_url = f"{self.instance_url}/api/now/table/incident?sysparm_query=number={ticket_number}"
        get_response = requests.get(get_url, headers=self.headers)
        
        if get_response.status_code == 200:
            tickets = get_response.json()['result']
            if tickets:
                sys_id = tickets[0]['sys_id']
                
                # Update ticket
                update_url = f"{self.instance_url}/api/now/table/incident/{sys_id}"
                response = requests.put(update_url, headers=self.headers, data=json.dumps(update_data))
                
                if response.status_code == 200:
                    return {"success": True, "message": "Ticket updated successfully"}
                else:
                    return {"success": False, "error": response.text}
            else:
                return {"success": False, "error": "Ticket not found"}
        else:
            return {"success": False, "error": "Failed to find ticket"}





