"""
test_ieee_compliance.py
------------------------
Pytest test suite for the SIRS IEEE Compliance Checker.

Tests all 5 IEEE standards individually + integration tests.

Run:
    pytest test_ieee_compliance.py -v
"""

import pytest
from tools.ieee_compliance_tool import check_compliance, IEEEComplianceChecker

checker = IEEEComplianceChecker()


# ─────────────────────────────────────────────
#  Sample content strings
# ─────────────────────────────────────────────

RICH_CONTENT = """
SIRS - Secure Offline Intelligence Retrieval System

Scope and Purpose:
SIRS is an offline AI-powered document retrieval system with six-layer architecture.
The system shall provide secure document retrieval with accuracy above 85%.
Performance requirement: query response < 500ms. Reliability: 99.5% uptime.

Requirements (IEEE 830):
REQ-01: The system shall support offline document retrieval.
REQ-02: Authentication and access control shall be enforced.
FR-01: Users must be able to upload and query PDF documents.
NFR-01: System latency must be under 500ms for 95% of queries.

Design (IEEE 1016):
Architecture follows a six-layer design: API, Agent, MCP, Tools, Retrieval, LLM.
FAISS vector index is used for embedding-based document retrieval.
FastAPI exposes REST API endpoints. Interface design documented with UML diagrams.
Design rationale: FAISS chosen for offline speed; Ollama for local LLM inference.

Testing (IEEE 829):
Test Plan covers unit tests, integration tests, and system tests.
TC-01: Test document upload — Expected result: 200 OK, document indexed.
TC-02: Test query retrieval — Expected result: top-3 relevant documents returned.
Test coverage includes edge cases, boundary conditions, and negative tests.
Test environment: Python 3.13, pytest, Postman for API validation.

Quality Assurance (IEEE 730):
Quality metrics: retrieval accuracy > 85%, latency < 500ms, recall > 0.8.
Code review process: all PRs reviewed by guide before merge.
Defect tracking: GitHub issues used for bug and fix management.
Security: offline-only deployment, no external data transmission.
Compliance: system conforms to IEEE 12207 lifecycle standards.

Life Cycle (IEEE 12207):
Requirements phase completed. Design phase completed.
Implementation phase: FastAPI backend + React frontend developed.
Testing phase: 15 test cases defined and executed.
Deployment: local Windows machine, Ollama model running.
Maintenance: version control via Git, documentation updated regularly.
Team roles: developer (Abhi), guide (supervisor), reviewer.
"""

EMPTY_CONTENT = ""

MINIMAL_CONTENT = "This system retrieves documents."

PARTIAL_CONTENT = """
The system uses FAISS for document retrieval.
Architecture has multiple components and layers.
FastAPI provides the REST API interface.
Testing is done with pytest. Unit tests are written.
"""


# ─────────────────────────────────────────────
#  TC-01 to TC-05: Individual Standard Tests (PASS cases)
# ─────────────────────────────────────────────

def test_tc01_ieee_12207_passes_on_rich_content():
    """TC-01: IEEE 12207 should pass when lifecycle phases are all covered."""
    result = checker.check_ieee_12207(RICH_CONTENT)
    assert result.passed is True, f"Expected PASS. Score: {result.score:.2f}. Failures: {result.failures}"
    assert result.score >= 0.5


def test_tc02_ieee_830_passes_on_rich_content():
    """TC-02: IEEE 830 should pass when requirements are complete and measurable."""
    result = checker.check_ieee_830(RICH_CONTENT)
    assert result.passed is True, f"Expected PASS. Score: {result.score:.2f}. Failures: {result.failures}"
    assert result.score >= 0.5


def test_tc03_ieee_829_passes_on_rich_content():
    """TC-03: IEEE 829 should pass when test documentation is structured."""
    result = checker.check_ieee_829(RICH_CONTENT)
    assert result.passed is True, f"Expected PASS. Score: {result.score:.2f}. Failures: {result.failures}"
    assert result.score >= 0.5


def test_tc04_ieee_1016_passes_on_rich_content():
    """TC-04: IEEE 1016 should pass when design is well-documented."""
    result = checker.check_ieee_1016(RICH_CONTENT)
    assert result.passed is True, f"Expected PASS. Score: {result.score:.2f}. Failures: {result.failures}"
    assert result.score >= 0.5


def test_tc05_ieee_730_passes_on_rich_content():
    """TC-05: IEEE 730 should pass when QA processes are documented."""
    result = checker.check_ieee_730(RICH_CONTENT)
    assert result.passed is True, f"Expected PASS. Score: {result.score:.2f}. Failures: {result.failures}"
    assert result.score >= 0.5


# ─────────────────────────────────────────────
#  TC-06 to TC-10: FAIL cases (minimal/empty content)
# ─────────────────────────────────────────────

def test_tc06_ieee_12207_fails_on_minimal_content():
    """TC-06: IEEE 12207 should fail when lifecycle phases are missing."""
    result = checker.check_ieee_12207(MINIMAL_CONTENT)
    assert result.passed is False, "Expected FAIL on minimal content."
    assert result.score < 0.5


def test_tc07_ieee_830_fails_on_minimal_content():
    """TC-07: IEEE 830 should fail when no requirements structure is present."""
    result = checker.check_ieee_830(MINIMAL_CONTENT)
    assert result.passed is False, "Expected FAIL on minimal content."


def test_tc08_ieee_829_fails_on_minimal_content():
    """TC-08: IEEE 829 should fail when no test documentation is present."""
    result = checker.check_ieee_829(MINIMAL_CONTENT)
    assert result.passed is False, "Expected FAIL on minimal content."


def test_tc09_empty_content_raises_value_error():
    """TC-09: Empty content should raise ValueError, not crash silently."""
    with pytest.raises(ValueError, match="Content cannot be empty"):
        checker.run_full_compliance_check(EMPTY_CONTENT)


def test_tc10_overall_report_fails_on_minimal_content():
    """TC-10: Full report should return overall_passed=False for minimal content."""
    report = checker.run_full_compliance_check(MINIMAL_CONTENT)
    assert report.overall_passed is False
    assert report.overall_score < 0.5


# ─────────────────────────────────────────────
#  TC-11 to TC-13: Report structure tests
# ─────────────────────────────────────────────

def test_tc11_full_report_has_five_standards():
    """TC-11: Full compliance report must contain exactly 5 IEEE standards."""
    report = checker.run_full_compliance_check(RICH_CONTENT)
    assert len(report.standards) == 5
    ids = [s.standard_id for s in report.standards]
    assert "IEEE 12207" in ids
    assert "IEEE 830"   in ids
    assert "IEEE 829"   in ids
    assert "IEEE 1016"  in ids
    assert "IEEE 730"   in ids


def test_tc12_to_dict_is_json_serializable():
    """TC-12: to_dict() output must be JSON-serializable with correct keys."""
    report = checker.run_full_compliance_check(RICH_CONTENT)
    d = report.to_dict()

    assert "overall_score_pct" in d
    assert "overall_passed"    in d
    assert "summary"           in d
    assert "standards"         in d
    assert "timestamp"         in d
    assert isinstance(d["overall_score_pct"], float)
    assert isinstance(d["standards"], list)
    assert len(d["standards"]) == 5


def test_tc13_check_compliance_public_function():
    """TC-13: Public check_compliance() function should return a valid report dict."""
    result = check_compliance(RICH_CONTENT)
    assert isinstance(result, dict)
    assert "overall_score_pct" in result
    assert result["overall_score_pct"] > 0


# ─────────────────────────────────────────────
#  TC-14 to TC-15: Suggestions + score range
# ─────────────────────────────────────────────

def test_tc14_suggestions_given_for_failing_checks():
    """TC-14: Standards that fail checks should provide actionable suggestions."""
    result = checker.check_ieee_830(MINIMAL_CONTENT)
    assert len(result.suggestions) > 0, "Failing standard should have suggestions."


def test_tc15_scores_are_within_valid_range():
    """TC-15: All standard scores must be between 0.0 and 1.0 (inclusive)."""
    report = checker.run_full_compliance_check(PARTIAL_CONTENT)
    for standard in report.standards:
        assert 0.0 <= standard.score <= 1.0, (
            f"{standard.standard_id} score {standard.score} is out of range [0.0, 1.0]"
        )
    assert 0.0 <= report.overall_score <= 1.0