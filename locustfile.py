from locust import HttpUser, task, between


class JobPortalUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def view_jobs(self):
        self.client.get("/api/jobs/")