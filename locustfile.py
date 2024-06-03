import json
from locust import HttpUser, task, between, LoadTestShape

class MyUser(HttpUser):
    wait_time = between(20, 25)

    @task
    def process_question_and_get_answer(self):
        # Step 1: Send a POST request to /preprocess_question
        question = {"text": "T need an actual help please"} 
        headers = {'Content-Type': 'application/json'}
        response = self.client.post("/preprocess_question", data=json.dumps(question), headers=headers)

        # Extract preprocessed_question from response
        preprocessed_question = response.json()["preprocessed_question"]

        # Step 2: Send a POST request to /get_answer with the preprocessed question
        processed_data = {"question": preprocessed_question}
        response = self.client.post("/get_answer", data=json.dumps(processed_data), headers=headers)

        # Optional: You can log/print the answer
        answer = response.json()["answer"]
        print(f"Answer: {answer}")

class StepLoadShape(LoadTestShape):
    """
    A load test shape that:
    1. Starts with two active users.
    2. Spawns two users every 20 seconds, up to a maximum of 20 concurrent users.
    3. Stays at 20 users for 1:30.
    """

    step_time = 30
    step_load = 2
    max_users = 20
    stay_time = 90

    def tick(self):
        run_time = self.get_run_time()

        # Calculate the spawning phase duration
        spawn_duration = ((self.max_users - 2) // self.step_load) * self.step_time

        if run_time < spawn_duration:
            # Spawning phase
            current_step = run_time // self.step_time
            return (2 + current_step * self.step_load, self.step_time)
        elif run_time < spawn_duration + self.stay_time:
            # Stay phase at max users
            return (self.max_users, self.step_time)
        else:
            # Stop the test after stay_time has elapsed
            return None