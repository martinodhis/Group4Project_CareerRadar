import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import requests

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.job import Job
from app.models.user_activity import UserActivity
from app.models.job_alert import JobAlert
from app.models.notification import Notification
from config import Config


class PostmanApiTests(unittest.TestCase):
    password = "Password123!"

    def setUp(self):
        test_config = type(
            "TestConfig",
            (Config,),
            {
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "TESTING": True,
                "JWT_DECODE_LEEWAY": 86400,
            },
        )
        self.app = create_app(test_config)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def admin_headers(self):
        response = self.client.post(
            "/register",
            json={
                "email": "admin@example.com",
                "first_name": "Api",
                "last_name": "Admin",
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 201)

        user = User.query.filter_by(email="admin@example.com").one()
        user.role = "ADMIN"
        db.session.commit()

        response = self.client.post(
            "/login",
            json={"email": "admin@example.com", "password": self.password},
        )
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.get_json()['data']['access_token']}"}

    def test_public_reads_and_protected_writes(self):
        self.assertEqual(self.client.get("/jobs").status_code, 200)
        self.assertEqual(self.client.get("/skills").status_code, 200)
        self.assertEqual(self.client.get("/users").status_code, 401)
        self.assertEqual(
            self.client.post("/jobs", json={"title": "Engineer"}).status_code, 401
        )
        self.assertEqual(
            self.client.post("/skills", json={"name": "Python"}).status_code, 401
        )
        preflight = self.client.options(
            "/applications",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        self.assertEqual(preflight.status_code, 200)
        self.assertEqual(
            preflight.headers["Access-Control-Allow-Origin"], "http://localhost:5173"
        )
        self.assertIn(
            "authorization",
            preflight.headers["Access-Control-Allow-Headers"].lower(),
        )

    def test_registration_creates_user_profile_and_activity_in_one_request(self):
        response = self.client.post(
            "/register",
            json={
                "email": "new-account@example.com",
                "first_name": "New",
                "last_name": "Account",
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 201, response.get_json())
        user = User.query.filter_by(email="new-account@example.com").one()
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.role, "USER")
        self.assertEqual(
            UserActivity.query.filter_by(
                user_id=user.id, action="USER_REGISTERED"
            ).count(),
            1,
        )

    def test_registration_rejects_weak_passwords(self):
        weak_passwords = (
            "short1!",
            "lowercase1!",
            "UPPERCASE1!",
            "NoNumber!!",
            "Password123",
            "Password 123",
        )
        for index, password in enumerate(weak_passwords):
            with self.subTest(password=password):
                response = self.client.post(
                    "/register",
                    json={
                        "email": f"weak-password-{index}@example.com",
                        "first_name": "Weak",
                        "last_name": "Password",
                        "password": password,
                    },
                )
                self.assertEqual(response.status_code, 400, response.get_json())
                self.assertEqual(response.get_json()["error"]["code"], "VALIDATION_ERROR")

    def test_promote_admin_cli_requires_existing_account_and_confirmation(self):
        registered = self.client.post(
            "/register",
            json={
                "email": "first-admin@example.com",
                "first_name": "First",
                "last_name": "Admin",
                "password": self.password,
            },
        )
        self.assertEqual(registered.status_code, 201)
        user = User.query.filter_by(email="first-admin@example.com").one()
        runner = self.app.test_cli_runner()

        cancelled = runner.invoke(
            args=["promote-admin", "first-admin@example.com"],
            input="n\n",
        )
        self.assertEqual(cancelled.exit_code, 0, cancelled.output)
        self.assertEqual(user.role, "USER")

        promoted = runner.invoke(
            args=["promote-admin", "first-admin@example.com"],
            input="y\n",
        )
        self.assertEqual(promoted.exit_code, 0, promoted.output)
        self.assertEqual(user.role, "ADMIN")
        self.assertIn("Sign out and sign in again", promoted.output)

        missing = runner.invoke(
            args=["promote-admin", "missing@example.com"],
            input="y\n",
        )
        self.assertNotEqual(missing.exit_code, 0)
        self.assertIn("No account found", missing.output)

    def test_public_jobs_auto_sync_empty_database_and_keyword_search(self):
        sync_calls = []

        def sync_jobs(count=None, tag=None, **kwargs):
            sync_calls.append({"count": count, "tag": tag})
            title = "Data Engineer" if tag else "Backend Engineer"
            job = Job(
                source="jobicy",
                external_id=f"auto-{len(sync_calls)}",
                title=title,
                company_name="CareerRadar Test",
                last_synced_at=datetime.now(timezone.utc),
            )
            db.session.add(job)
            db.session.commit()
            return {"fetched": 1, "created": 1, "updated": 0}

        with patch("app.routes.jobs.jobicy_service.sync", side_effect=sync_jobs):
            home_response = self.client.get("/jobs?limit=20")
            self.assertEqual(home_response.status_code, 200, home_response.get_json())
            self.assertEqual(
                home_response.get_json()["data"]["jobs"][0]["title"],
                "Backend Engineer",
            )

            search_response = self.client.get("/jobs?keyword=Data&limit=20")
            self.assertEqual(search_response.status_code, 200, search_response.get_json())
            self.assertEqual(
                [job["title"] for job in search_response.get_json()["data"]["jobs"]],
                ["Data Engineer"],
            )

        self.assertEqual(sync_calls[0], {"count": 50, "tag": None})
        self.assertEqual(sync_calls[1], {"count": 50, "tag": "Data"})

    def test_user_job_and_skill_admin_crud(self):
        headers = self.admin_headers()

        self.assertEqual(self.client.get("/users/me", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/profile", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/users", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/users/1", headers=headers).status_code, 200)

        response = self.client.post(
            "/users",
            headers=headers,
            json={
                "email": "new-user@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 201)
        user_id = response.get_json()["data"]["id"]
        promoted = self.client.patch(
            f"/users/{user_id}", headers=headers, json={"role": "ADMIN"}
        )
        self.assertEqual(promoted.status_code, 200, promoted.get_json())
        promoted_login = self.client.post(
            "/login",
            json={"email": "new-user@example.com", "password": self.password},
        )
        promoted_headers = {
            "Authorization": f"Bearer {promoted_login.get_json()['data']['access_token']}"
        }
        self.assertEqual(self.client.get("/dashboard/admin", headers=promoted_headers).status_code, 200)
        self.assertEqual(
            self.client.patch(
                f"/users/{user_id}", headers=headers, json={"first_name": "Updated"}
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/users/{user_id}", headers=headers).status_code, 200
        )

        response = self.client.post(
            "/skills",
            headers=headers,
            json={"name": "Python", "category": "Programming"},
        )
        self.assertEqual(response.status_code, 201)
        skill_id = response.get_json()["data"]["id"]
        self.assertEqual(
            self.client.put(
                f"/skills/{skill_id}", headers=headers, json={"name": "Python 3"}
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/skills/{skill_id}", headers=headers).status_code, 200
        )

        response = self.client.post(
            "/jobs", headers=headers, json={"title": "API Engineer"}
        )
        self.assertEqual(response.status_code, 201)
        job_id = response.get_json()["data"]["id"]
        self.assertEqual(
            self.client.patch(
                f"/jobs/{job_id}", headers=headers, json={"location": "Remote"}
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/jobs/{job_id}", headers=headers).status_code, 200
        )

    def test_admin_dashboard_and_user_activity_history(self):
        admin_headers = self.admin_headers()
        job_response = self.client.post(
            "/jobs",
            headers=admin_headers,
            json={"title": "Backend Engineer", "company_name": "CareerRadar"},
        )
        self.assertEqual(job_response.status_code, 201)
        job_id = job_response.get_json()["data"]["id"]

        register_response = self.client.post(
            "/register",
            json={
                "email": "candidate@example.com",
                "first_name": "Career",
                "last_name": "Candidate",
                "password": self.password,
            },
        )
        self.assertEqual(register_response.status_code, 201)
        login_response = self.client.post(
            "/login",
            json={"email": "candidate@example.com", "password": self.password},
        )
        user_headers = {
            "Authorization": f"Bearer {login_response.get_json()['data']['access_token']}"
        }

        self.assertEqual(
            self.client.get("/jobs?keyword=Backend", headers=user_headers).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                "/jobs?minimum_salary=50000", headers=user_headers
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(f"/jobs/{job_id}", headers=user_headers).status_code, 200
        )
        self.assertEqual(
            self.client.post(
                "/saved-jobs", headers=user_headers, json={"job_id": job_id}
            ).status_code,
            201,
        )
        application_response = self.client.post(
            "/applications",
            headers=user_headers,
            json={"job_id": job_id, "status": "APPLIED"},
        )
        self.assertEqual(application_response.status_code, 201)
        application_id = application_response.get_json()["data"]["id"]
        pending_history_response = self.client.get(
            "/dashboard/admin/activity?application_status=PENDING",
            headers=admin_headers,
        )
        self.assertEqual(pending_history_response.status_code, 200)
        pending_history = pending_history_response.get_json()["data"]
        self.assertEqual(len(pending_history["applications"]), 1)
        self.assertEqual(pending_history["applications"][0]["id"], application_id)
        self.assertEqual(pending_history["application_status"], "PENDING")

        duplicate_application = self.client.post(
            "/applications",
            headers=user_headers,
            json={"job_id": job_id, "status": "APPLIED"},
        )
        self.assertEqual(duplicate_application.status_code, 409)
        self.assertEqual(
            self.client.patch(
                f"/applications/{application_id}",
                headers=user_headers,
                json={"status": "INTERVIEW"},
            ).status_code,
            200,
        )

        self.assertEqual(self.client.get("/dashboard/admin").status_code, 401)
        self.assertEqual(
            self.client.get("/dashboard/admin", headers=user_headers).status_code, 403
        )
        stats_response = self.client.get(
            "/dashboard/admin", headers=admin_headers
        )
        self.assertEqual(stats_response.status_code, 200)
        self.assertEqual(stats_response.get_json()["data"]["applications"], 1)

        history_response = self.client.get(
            "/dashboard/admin/activity?limit=100", headers=admin_headers
        )
        self.assertEqual(history_response.status_code, 200)
        history = history_response.get_json()["data"]
        actions = {activity["action"] for activity in history["activities"]}
        self.assertTrue(
            {
                "LOGIN",
                "JOB_SEARCH",
                "JOB_VIEW",
                "JOB_SAVED",
                "APPLICATION_CREATED",
                "APPLICATION_UPDATED",
            }.issubset(actions)
        )
        application = history["applications"][0]
        self.assertEqual(application["user"]["email"], "candidate@example.com")
        self.assertEqual(application["status"], "INTERVIEW")

    def test_created_user_can_create_and_save_profile_without_existing_profile(self):
        admin_headers = self.admin_headers()
        response = self.client.post(
            "/users",
            headers=admin_headers,
            json={
                "email": "profile-user@example.com",
                "first_name": "Profile",
                "last_name": "User",
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        login = self.client.post(
            "/login",
            json={"email": "profile-user@example.com", "password": self.password},
        )
        self.assertEqual(login.status_code, 200)
        headers = {"Authorization": f"Bearer {login.get_json()['data']['access_token']}"}

        profile_response = self.client.get("/profile", headers=headers)
        self.assertEqual(profile_response.status_code, 200, profile_response.get_json())
        db.session.expire_all()
        created_user = User.query.filter_by(email="profile-user@example.com").one()
        self.assertIsNotNone(created_user.profile)
        update_response = self.client.put(
            "/profile",
            headers=headers,
            json={
                "headline": "Junior analyst",
                "location": "Nairobi",
                "years_of_experience": 1.5,
            },
        )
        self.assertEqual(update_response.status_code, 200, update_response.get_json())
        self.assertEqual(update_response.get_json()["data"]["headline"], "Junior analyst")

        account_response = self.client.patch(
            "/users/me",
            headers=headers,
            json={"first_name": "Updated"},
        )
        self.assertEqual(account_response.status_code, 200, account_response.get_json())
        self.assertEqual(account_response.get_json()["data"]["first_name"], "Updated")

    def test_new_job_sync_notifies_matching_active_alerts(self):
        from app.services.jobicy_service import JobicyService

        response = self.client.post(
            "/register",
            json={
                "email": "alerts-user@example.com",
                "first_name": "Alerts",
                "last_name": "User",
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 201)
        user = User.query.filter_by(email="alerts-user@example.com").one()
        db.session.add(
            JobAlert(
                user_id=user.id,
                keyword="data engineer",
                location="remote",
                job_type="full-time",
            )
        )
        db.session.commit()

        remote_response = Mock()
        remote_response.json.return_value = {
            "jobs": [
                {
                    "id": "alert-job-1",
                    "jobTitle": "Data Engineer",
                    "companyName": "CareerRadar",
                    "jobType": ["Full-time"],
                    "jobGeo": "Remote",
                }
            ]
        }
        with patch("app.services.jobicy_service.requests.get", return_value=remote_response):
            result = JobicyService().sync(count=1)

        self.assertEqual(result["created"], 1)
        notification = Notification.query.filter_by(user_id=user.id).one()
        self.assertEqual(notification.kind, "job_alert")
        self.assertIn("Data Engineer", notification.message)
        login = self.client.post(
            "/login",
            json={"email": "alerts-user@example.com", "password": self.password},
        )
        headers = {"Authorization": f"Bearer {login.get_json()['data']['access_token']}"}
        self.assertEqual(login.status_code, 200, login.get_json())
        missing_auth = self.client.post(
            "/alerts", json={"keyword": "product designer"}
        )
        self.assertEqual(missing_auth.status_code, 401)
        created_alert = self.client.post(
            "/alerts",
            headers=headers,
            json={"keyword": "product designer"},
        )
        self.assertEqual(created_alert.status_code, 201, created_alert.get_json())
        notifications = self.client.get("/notifications", headers=headers)
        self.assertEqual(notifications.status_code, 200)
        self.assertEqual(len(notifications.get_json()["data"]["notifications"]), 1)
        mark_read = self.client.patch(
            f"/notifications/{notification.id}/read", headers=headers
        )
        self.assertEqual(mark_read.status_code, 200, mark_read.get_json())
        self.assertTrue(mark_read.get_json()["data"]["is_read"])

    def test_admin_job_sync_validates_input_and_reports_upstream_errors(self):
        headers = self.admin_headers()
        invalid_response = self.client.post(
            "/jobs/sync", headers=headers, json={"count": "many"}
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(
            invalid_response.get_json()["error"]["code"], "VALIDATION_ERROR"
        )

        with patch(
            "app.routes.jobs.jobicy_service.sync",
            side_effect=requests.ConnectionError("upstream unavailable"),
        ):
            failure_response = self.client.post(
                "/jobs/sync", headers=headers, json={"count": 10}
            )
        self.assertEqual(failure_response.status_code, 502)
        self.assertEqual(
            failure_response.get_json()["error"]["code"], "JOB_SYNC_FAILED"
        )

    def test_jobicy_sync_maps_external_job_fields(self):
        from app.services.jobicy_service import JobicyService

        remote_response = Mock()
        remote_response.json.return_value = {
            "jobs": [
                {
                    "id": "external-1",
                    "jobTitle": "Data Engineer",
                    "companyName": "Remote Co",
                    "jobType": ["Full-Time"],
                    "jobIndustry": ["Technology", "Data"],
                    "jobLevel": "Mid-level",
                    "salaryMin": 90000,
                    "salaryMax": 120000,
                    "salaryCurrency": "USD",
                    "jobExcerpt": "Build data platforms",
                }
            ]
        }
        with patch("app.services.jobicy_service.requests.get", return_value=remote_response):
            summary = JobicyService().sync(count=1)

        self.assertEqual(summary["created"], 1)
        job = self.client.get("/jobs/1").get_json()["data"]
        self.assertEqual(job["employment_type"], "Full-Time")
        self.assertEqual(job["industry"], "Technology, Data")
        self.assertEqual(job["experience_level"], "Mid-level")
        self.assertEqual(job["salary_min"], 90000.0)
        self.assertEqual(job["salary_max"], 120000.0)


if __name__ == "__main__":
    unittest.main()
