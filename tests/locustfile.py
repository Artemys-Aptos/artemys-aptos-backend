import random
from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def get_public_prompts(self):
        """
        Test for fetching public prompts with pagination.
        """
        page = random.randint(1, 10)
        page_size = random.choice([5, 10, 20])
        self.client.get(f"/prompts/get-public-prompts/?page={page}&page_size={page_size}")

    @task(2)
    def get_premium_prompts(self):
        """
        Test for fetching premium prompts.
        """
        page = random.randint(1, 10)
        page_size = random.choice([5, 10, 20])
        self.client.get(f"/marketplace/get-premium-prompts/?page={page}&page_size={page_size}")

    @task(1)
    def filter_public_prompts(self):
        """
        Test for filtering public prompts.
        """
        payload = {
            "prompt_tag": random.choice(["3D Art", "Anime", "all"]),
            "public": random.choice([True]),
            "page": random.randint(1, 5),
            "page_size": random.choice([5, 10, 20])
        }
        self.client.post("/prompts/filter-public-prompts/", json=payload)

class APIUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Simulate wait time between tasks (1 to 5 seconds)
