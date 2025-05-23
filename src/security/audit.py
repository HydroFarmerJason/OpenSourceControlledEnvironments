"""Basic security auditing utilities."""
from __future__ import annotations

from typing import Callable, List, Any


class SecurityReport:
    """Collect and generate results from security checks."""

    def __init__(self) -> None:
        self.results: List[Any] = []

    def add_result(self, result: Any) -> None:
        self.results.append(result)

    def generate(self) -> List[Any]:
        return self.results


class SecurityAuditor:
    """Run a series of security checks and compile a report."""

    def __init__(self) -> None:
        self.checks: List[Callable[[], Any]] = [
            self.check_ssl_certificates,
            self.check_user_permissions,
            self.check_system_updates,
            self.check_intrusion_attempts,
            self.check_backup_integrity,
        ]

    def run_audit(self) -> List[Any]:
        """Execute all checks and return the report results."""
        report = SecurityReport()
        for check in self.checks:
            result = check()
            report.add_result(result)
        return report.generate()

    # ---- Example check implementations ----
    def check_ssl_certificates(self) -> dict:
        return {"ssl": "ok"}

    def check_user_permissions(self) -> dict:
        return {"permissions": "ok"}

    def check_system_updates(self) -> dict:
        return {"updates": "ok"}

    def check_intrusion_attempts(self) -> dict:
        return {"intrusions": "none"}

    def check_backup_integrity(self) -> dict:
        return {"backups": "valid"}
