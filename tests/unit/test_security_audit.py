from src.security.audit import SecurityAuditor


def test_run_audit_collects_results():
    auditor = SecurityAuditor()
    auditor.checks = [lambda: {"check": 1}, lambda: {"check": 2}]
    results = auditor.run_audit()
    assert results == [{"check": 1}, {"check": 2}]
