"""Only run against your own LOCAL DormMate server, not GitHub Pages/public hosts."""
from locust import HttpUser, between, task


class DormMateUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def students(self):
        self.client.get('/students', name='GET /students')

    @task(3)
    def rooms(self):
        self.client.get('/rooms', name='GET /rooms')

    @task(2)
    def applications(self):
        self.client.get('/applications', name='GET /applications')

    @task(1)
    def home(self):
        self.client.get('/', name='GET /')
