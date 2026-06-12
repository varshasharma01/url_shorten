"""
Load Test for Webvory Analytics API.

Simulates concurrent users hitting the analytics endpoints to verify
response times stay under 2 seconds under load.

Run:
    locust -f load_test/locustfile.py --host=http://localhost:8000

Then open http://localhost:8089, set:
    - Number of users (e.g. 100)
    - Spawn rate (e.g. 10 users/second)
    - Click "Start"

For a headless run (no web UI), useful for CI / report generation:
    locust -f load_test/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 60s --headless \
           --csv=load_test/results
"""

from locust import HttpUser, task, between


class AnalyticsUser(HttpUser):
    """
    Simulates a user/dashboard repeatedly querying the analytics API.

    wait_time: each virtual user pauses 1-2s between requests,
    mimicking a dashboard auto-refreshing or a human browsing.
    """

    wait_time = between(1, 2)

    @task(3)
    def get_summary(self):
        """
        Most frequently hit - the main dashboard summary card.
        Weight 3 = called 3x as often as other tasks.
        """
        self.client.get("/analytics/summary")

    @task(2)
    def get_revenue_trends(self):
        """Revenue trend chart on dashboard."""
        self.client.get("/analytics/revenue-trends")

    @task(1)
    def get_top_customers_10(self):
        """Top 10 customers widget."""
        self.client.get("/analytics/top-customers?limit=10")

    @task(1)
    def get_top_customers_50(self):
        """Larger top-customers request (less common)."""
        self.client.get("/analytics/top-customers?limit=50")