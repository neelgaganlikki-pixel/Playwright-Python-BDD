import base64
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from config.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger("JenkinsManager")


class JenkinsManager:
    """
    Production-grade Jenkins CI/CD REST API Manager.
    Handles authentication, CSRF crumbs, job triggers, queue polling,
    build monitoring, and test result extraction.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        job_name: Optional[str] = None,
    ):
        self.base_url = (base_url or ConfigReader.get_jenkins_url()).rstrip("/")
        self.username = username or ConfigReader.get_jenkins_user()
        self.api_token = api_token or ConfigReader.get_jenkins_api_token()
        self.job_name = job_name or ConfigReader.get_jenkins_job_name()

    def _get_auth_headers(self) -> dict[str, str]:
        """
        Constructs HTTP Basic Authentication headers using Username + API Token.
        """
        headers = {"User-Agent": "Playwright-BDD-Automation-Client"}
        if self.username and self.api_token:
            auth_str = f"{self.username}:{self.api_token}"
            encoded = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {encoded}"
        return headers

    def get_crumb(self) -> dict[str, str]:
        """
        Fetches CSRF crumb if Jenkins CSRF protection is enabled.
        """
        crumb_url = f"{self.base_url}/crumbIssuer/api/json"
        headers = self._get_auth_headers()
        req = urllib.request.Request(crumb_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                crumb_field = data.get("crumbRequestField", "Jenkins-Crumb")
                crumb_val = data.get("crumb", "")
                return {crumb_field: crumb_val}
        except Exception:
            return {}

    def check_connection(self) -> tuple[bool, str]:
        """
        Verifies Jenkins reachability and authentication status.
        """
        headers = self._get_auth_headers()
        req = urllib.request.Request(f"{self.base_url}/api/json", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True, "Connected to Jenkins successfully."
                return False, f"Unexpected response status: {resp.status}"
        except urllib.error.HTTPError as http_err:
            if http_err.code == 401:
                return False, "Authentication failed (HTTP 401): Invalid JENKINS_USER or JENKINS_API_TOKEN."
            elif http_err.code == 403:
                return False, (
                    "Access Forbidden (HTTP 403): Jenkins requires authentication or API Token credentials. "
                    "Ensure JENKINS_USER and JENKINS_API_TOKEN are configured."
                )
            return False, f"HTTP Error {http_err.code}: {http_err.reason}"
        except Exception as err:
            return False, f"Connection failed to {self.base_url}: {err}"

    def trigger_build(
        self,
        parameters: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, str, Optional[str]]:
        """
        Triggers a build for the configured job.
        Returns: (success_bool, message, queue_url)
        """
        is_connected, msg = self.check_connection()
        if not is_connected:
            return False, f"Cannot trigger build: {msg}", None

        headers = self._get_auth_headers()
        headers.update(self.get_crumb())

        if parameters:
            endpoint = f"{self.base_url}/job/{self.job_name}/buildWithParameters"
            data = urllib.parse.urlencode(parameters).encode("utf-8")
        else:
            endpoint = f"{self.base_url}/job/{self.job_name}/build"
            data = b""

        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201):
                    queue_url = resp.headers.get("Location")
                    logger.info("Build triggered. Queue location: %s", queue_url)
                    return True, "Build triggered successfully.", queue_url
                return False, f"Unexpected response code: {resp.status}", None
        except urllib.error.HTTPError as http_err:
            return False, f"Failed to trigger build (HTTP {http_err.code}): {http_err.reason}", None
        except Exception as e:
            return False, f"Failed to trigger build: {e}", None

    def poll_queue_for_build_number(
        self,
        queue_url: str,
        timeout: int = 120,
        poll_interval: int = 3,
    ) -> tuple[Optional[int], Optional[str]]:
        """
        Polls the Jenkins queue until the task is assigned a build number.
        Returns: (build_number, build_url)
        """
        api_queue_url = f"{queue_url.rstrip('/')}/api/json"
        headers = self._get_auth_headers()
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                req = urllib.request.Request(api_queue_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    executable = data.get("executable")
                    if executable and "number" in executable:
                        return executable["number"], executable.get("url")
            except Exception as e:
                logger.debug("Polling queue: %s", e)
            time.sleep(poll_interval)

        return None, None

    def monitor_build(
        self,
        build_number: int,
        poll_interval: int = 5,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """
        Monitors a running build until it reaches a final state.
        Retrieves build status, duration, test counts, and failures.
        """
        build_url = f"{self.base_url}/job/{self.job_name}/{build_number}/api/json"
        headers = self._get_auth_headers()
        start_time = time.time()

        result_data: dict[str, Any] = {
            "build_number": build_number,
            "status": "UNKNOWN",
            "duration": "0s",
            "url": f"{self.base_url}/job/{self.job_name}/{build_number}/",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "failed_tests": [],
            "pipeline_failure": None,
        }

        while time.time() - start_time < timeout:
            try:
                req = urllib.request.Request(build_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    is_building = data.get("building", True)
                    if not is_building:
                        result_data["status"] = data.get("result", "UNKNOWN")
                        duration_ms = data.get("duration", 0)
                        result_data["duration"] = f"{duration_ms / 1000:.2f}s"
                        break
            except Exception as e:
                logger.debug("Error checking build status: %s", e)

            time.sleep(poll_interval)

        # Retrieve test results from Jenkins Test Report API
        test_report_url = f"{self.base_url}/job/{self.job_name}/{build_number}/testReport/api/json"
        try:
            req_tr = urllib.request.Request(test_report_url, headers=headers)
            with urllib.request.urlopen(req_tr, timeout=10) as resp:
                tr_data = json.loads(resp.read().decode("utf-8"))
                result_data["passed"] = tr_data.get("passCount", 0)
                result_data["failed"] = tr_data.get("failCount", 0)
                result_data["skipped"] = tr_data.get("skipCount", 0)
                result_data["total"] = tr_data.get("totalCount", 0)
                for suite in tr_data.get("suites", []):
                    for case in suite.get("cases", []):
                        if case.get("status") in ("FAILED", "REGRESSION"):
                            result_data["failed_tests"].append(case.get("name", "Unknown Test"))
        except Exception:
            # Fallback: parse console output for pytest summary
            self._parse_console_test_counts(build_number, result_data)

        return result_data

    def _parse_console_test_counts(self, build_number: int, result_data: dict[str, Any]) -> None:
        """
        Parses console text for pytest summary if testReport API is not populated.
        """
        console_url = f"{self.base_url}/job/{self.job_name}/{build_number}/consoleText"
        headers = self._get_auth_headers()
        try:
            req = urllib.request.Request(console_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                text = resp.read().decode("utf-8", errors="ignore")

                # Match e.g. "== 12 passed in 35.12s =="
                passed_match = re.search(r"(\d+)\s+passed", text)
                failed_match = re.search(r"(\d+)\s+failed", text)
                skipped_match = re.search(r"(\d+)\s+skipped", text)

                passed = int(passed_match.group(1)) if passed_match else 0
                failed = int(failed_match.group(1)) if failed_match else 0
                skipped = int(skipped_match.group(1)) if skipped_match else 0

                result_data["passed"] = passed
                result_data["failed"] = failed
                result_data["skipped"] = skipped
                result_data["total"] = passed + failed + skipped
        except Exception as e:
            logger.debug("Could not parse console output: %s", e)

    def format_summary(self, result_data: dict[str, Any]) -> str:
        """
        Formats the Jenkins result summary matching master prompt Section 10.
        """
        failed_tests_str = "\n".join(
            f"{i + 1}. {test}" for i, test in enumerate(result_data.get("failed_tests", []))
        ) or "None"

        summary = f"""JENKINS BUILD
Build Number: {result_data.get('build_number', 'N/A')}
Status: {result_data.get('status', 'UNKNOWN')}
Duration: {result_data.get('duration', 'N/A')}
URL: {result_data.get('url', 'N/A')}

TEST RESULTS
Passed: {result_data.get('passed', 0)}
Failed: {result_data.get('failed', 0)}
Skipped: {result_data.get('skipped', 0)}
Total: {result_data.get('total', 0)}

FAILED TESTS
{failed_tests_str}
"""
        if result_data.get("pipeline_failure"):
            summary += f"\nPIPELINE FAILURE\n{result_data['pipeline_failure']}\n"

        return summary
