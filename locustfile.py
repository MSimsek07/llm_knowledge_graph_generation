from locust import HttpUser, task, between
import json

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # Simulate user waiting time between tasks

    @task
    def generate_graph(self):
        payload = {
            "input_text": "Sample input text for generating graph"
        }
        headers = {
            "Content-Type": "application/json"
        }
        self.client.post("/generate_graph", data=json.dumps(payload), headers=headers)
