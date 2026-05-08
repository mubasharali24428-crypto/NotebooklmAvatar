import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient

from avatarlm.backend.app import app


class BackendApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "avatarlm-backend")

    def test_explainer_endpoint(self):
        response = self.client.post(
            "/api/v1/explainer",
            json={"topic": "Transformers", "emotion": "heartbroken", "scene": "cliff"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metadata"]["mode"], "video_explainer")
        self.assertEqual(payload["render"]["voice"]["rate"], "slow")

    def test_infographic_endpoint(self):
        response = self.client.post(
            "/api/v1/infographic",
            json={"topic": "Diffusion models", "emotion": "confident", "scene": "office"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metadata"]["mode"], "infographic")
        self.assertEqual(len(payload["infographic"]["elements"]), 3)

    def test_quiz_endpoint_alias_fields(self):
        response = self.client.post(
            "/api/v1/quiz",
            json={
                "topicText": "Photosynthesis converts light into chemical energy.",
                "durationSeconds": 300,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metadata"]["mode"], "quiz")
        self.assertEqual(payload["supervisor"]["timer_seconds"], 300)

    def test_validation_error_for_short_topic(self):
        response = self.client.post("/api/v1/explainer", json={"topic": "AI", "emotion": "confident", "scene": "office"})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

