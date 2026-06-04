"""
ieee_compliance_tool.py
-----------------------
IEEE Compliance Checker for SIRS RAG Pipeline.

Validates content (RAG responses, documents, or combined text) against
5 IEEE Standards relevant to software engineering projects:

    IEEE 12207 — Software Life Cycle Processes
    IEEE 830   — Software Requirements Specifications
    IEEE 829   — Software Test Documentation
    IEEE 1016  — Software Design Description
    IEEE 730   — Software Quality Assurance

Usage:
    from tools.ieee_compliance_tool import check_compliance

    report = check_compliance("your RAG response text here")
    print(report)  # Returns a dict with scores per standard
"""

import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List
from datetime import datetime


# ─────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────

@dataclass
class StandardResult:
    standard_id: str
    standard_name: str
    passed: bool
    score: float                   # 0.0 – 1.0
    checks: Dict[str, bool]
    failures: List[str]
    suggestions: List[str]


@dataclass
class ComplianceReport:
    timestamp: str
    overall_score: float           # 0.0 – 1.0
    overall_passed: bool
    standards: List[StandardResult]
    summary: str

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dict (for API responses)."""
        return {
            "timestamp": self.timestamp,
            "overall_score_pct": round(self.overall_score * 100, 1),
            "overall_passed": self.overall_passed,
            "verdict": "COMPLIANT ✅" if self.overall_passed else "NEEDS IMPROVEMENT ⚠️",
            "summary": self.summary,
            "standards": [
                {
                    "id": s.standard_id,
                    "name": s.standard_name,
                    "passed": s.passed,
                    "score_pct": round(s.score * 100, 1),
                    "checks": s.checks,
                    "failures": s.failures,
                    "suggestions": s.suggestions,
                }
                for s in self.standards
            ],
        }


# ─────────────────────────────────────────────
#  Checker class
# ─────────────────────────────────────────────

class IEEEComplianceChecker:
    """
    Runs keyword-pattern compliance checks against 5 IEEE standards.

    The checks are designed for SIRS — a document retrieval / RAG system.
    Content passed in can be:
        • A RAG-generated answer
        • The text of a retrieved document
        • Combined context (query + answer + source excerpt)

    PASS_THRESHOLD: fraction of checks that must pass for a standard to
    be considered compliant (default 0.5 = 50 %).
    """

    PASS_THRESHOLD = 0.5

    # ── IEEE 12207 ──────────────────────────────────────────────────────
    def check_ieee_12207(self, content: str) -> StandardResult:
        """
        IEEE 12207: Software Life Cycle Processes
        Verifies that the content covers key phases of the software lifecycle.
        """
        c = content.lower()

        checks: Dict[str, bool] = {
            "covers_requirements_phase": any(kw in c for kw in [
                "requirement", "srs", "specification", "user need", "stakeholder"
            ]),
            "covers_design_phase": any(kw in c for kw in [
                "design", "architecture", "component", "module", "interface", "layer"
            ]),
            "covers_implementation_phase": any(kw in c for kw in [
                "implement", "develop", "code", "build", "program", "source"
            ]),
            "covers_testing_phase": any(kw in c for kw in [
                "test", "validation", "verification", "quality", "review", "assert"
            ]),
            "covers_deployment_or_maintenance": any(kw in c for kw in [
                "deploy", "maintain", "update", "release", "install", "operation", "run"
            ]),
            "defines_process_roles": any(kw in c for kw in [
                "role", "responsibility", "team", "stakeholder", "owner", "developer"
            ]),
        }

        suggestions = []
        if not checks["covers_requirements_phase"]:
            suggestions.append(
                "Add requirements documentation to cover the IEEE 12207 acquisition/supply process."
            )
        if not checks["covers_testing_phase"]:
            suggestions.append(
                "Include a verification/validation process as required by IEEE 12207 §6.4."
            )
        if not checks["covers_deployment_or_maintenance"]:
            suggestions.append(
                "Document the operation and maintenance process per IEEE 12207 §6.7."
            )

        score = sum(checks.values()) / len(checks)
        failures = [k.replace("_", " ").capitalize() for k, v in checks.items() if not v]

        return StandardResult(
            standard_id="IEEE 12207",
            standard_name="Software Life Cycle Processes",
            passed=score >= self.PASS_THRESHOLD,
            score=score,
            checks=checks,
            failures=failures,
            suggestions=suggestions,
        )

    # ── IEEE 830 ────────────────────────────────────────────────────────
    def check_ieee_830(self, content: str) -> StandardResult:
        """
        IEEE 830: Software Requirements Specifications
        Checks SRS quality — completeness, correctness, and measurability.
        """
        c = content.lower()

        checks: Dict[str, bool] = {
            "has_functional_requirements": any(kw in c for kw in [
                "functional", "shall", "must", "should", "feature", "capability"
            ]),
            "has_non_functional_requirements": any(kw in c for kw in [
                "performance", "security", "reliability", "scalability",
                "availability", "offline", "accuracy", "latency"
            ]),
            "has_scope_or_purpose": any(kw in c for kw in [
                "scope", "purpose", "objective", "goal", "overview", "introduction"
            ]),
            "has_measurable_criteria": bool(re.search(
                r"\d+\s*(%|ms|seconds?|users?|requests?|mb|gb|kb|query)", c
            )),
            "has_traceability_indicators": any(kw in c for kw in [
                "req-", "fr-", "nfr-", "traceable", "traceability", "req id", "#req"
            ]),
            "has_constraints_or_assumptions": any(kw in c for kw in [
                "constraint", "assumption", "limitation", "dependency", "prerequisite"
            ]),
        }

        suggestions = []
        if not checks["has_measurable_criteria"]:
            suggestions.append(
                "Add measurable acceptance criteria (e.g., 'response < 200 ms') per IEEE 830 §5.3."
            )
        if not checks["has_traceability_indicators"]:
            suggestions.append(
                "Add requirement IDs (REQ-01, FR-01) for full traceability per IEEE 830 §4.3."
            )
        if not checks["has_constraints_or_assumptions"]:
            suggestions.append(
                "Document constraints and assumptions (e.g., offline-only, Python 3.x) per IEEE 830."
            )

        score = sum(checks.values()) / len(checks)
        failures = [k.replace("_", " ").capitalize() for k, v in checks.items() if not v]

        return StandardResult(
            standard_id="IEEE 830",
            standard_name="Software Requirements Specifications",
            passed=score >= self.PASS_THRESHOLD,
            score=score,
            checks=checks,
            failures=failures,
            suggestions=suggestions,
        )

    # ── IEEE 829 ────────────────────────────────────────────────────────
    def check_ieee_829(self, content: str) -> StandardResult:
        """
        IEEE 829: Software Test Documentation
        Checks if test documentation is structured and complete.
        """
        c = content.lower()

        checks: Dict[str, bool] = {
            "has_test_plan_or_cases": any(kw in c for kw in [
                "test plan", "test case", "test suite", "test script", "tc-", "test id"
            ]),
            "has_expected_results": any(kw in c for kw in [
                "expected", "expected result", "expected output", "pass criteria", "acceptance"
            ]),
            "has_test_types_defined": any(kw in c for kw in [
                "unit test", "integration test", "system test", "regression",
                "smoke test", "load test", "api test", "end-to-end"
            ]),
            "has_pass_fail_criteria": any(kw in c for kw in [
                "pass", "fail", "status", "result", "outcome", "verdict"
            ]),
            "has_test_coverage": any(kw in c for kw in [
                "coverage", "scenario", "edge case", "boundary", "negative test", "corner case"
            ]),
            "has_test_environment_or_tools": any(kw in c for kw in [
                "environment", "pytest", "postman", "tool", "framework", "setup", "ollama"
            ]),
        }

        suggestions = []
        if not checks["has_test_plan_or_cases"]:
            suggestions.append(
                "Add structured test cases with IDs (TC-01, TC-02) per IEEE 829 §5."
            )
        if not checks["has_test_coverage"]:
            suggestions.append(
                "Include edge cases and boundary tests per IEEE 829 §7."
            )
        if not checks["has_test_types_defined"]:
            suggestions.append(
                "Define the types of tests (unit, integration, system) per IEEE 829 §4."
            )

        score = sum(checks.values()) / len(checks)
        failures = [k.replace("_", " ").capitalize() for k, v in checks.items() if not v]

        return StandardResult(
            standard_id="IEEE 829",
            standard_name="Software Test Documentation",
            passed=score >= self.PASS_THRESHOLD,
            score=score,
            checks=checks,
            failures=failures,
            suggestions=suggestions,
        )

    # ── IEEE 1016 ───────────────────────────────────────────────────────
    def check_ieee_1016(self, content: str) -> StandardResult:
        """
        IEEE 1016: Software Design Description
        Checks if design documentation is structurally complete.
        """
        c = content.lower()

        checks: Dict[str, bool] = {
            "has_architecture_description": any(kw in c for kw in [
                "architecture", "system design", "layer", "component", "module", "subsystem"
            ]),
            "has_interface_description": any(kw in c for kw in [
                "interface", "api", "endpoint", "rest", "request", "response", "fastapi"
            ]),
            "has_data_design": any(kw in c for kw in [
                "data", "database", "schema", "model", "entity", "faiss",
                "vector", "index", "embedding"
            ]),
            "has_component_descriptions": any(kw in c for kw in [
                "component", "service", "class", "function", "method", "module",
                "agent", "retrieval", "llm"
            ]),
            "has_design_rationale": any(kw in c for kw in [
                "rationale", "reason", "because", "chosen", "selected",
                "decision", "trade-off", "why"
            ]),
            "has_diagrams_or_models": any(kw in c for kw in [
                "diagram", "uml", "flowchart", "sequence", "er diagram",
                "dfd", "figure", "chart"
            ]),
        }

        suggestions = []
        if not checks["has_diagrams_or_models"]:
            suggestions.append(
                "Include architecture/UML diagrams in design docs per IEEE 1016 §5.4."
            )
        if not checks["has_design_rationale"]:
            suggestions.append(
                "Document design decisions and rationale (why FAISS, why Ollama) per IEEE 1016 §5.5."
            )
        if not checks["has_interface_description"]:
            suggestions.append(
                "Add API/interface descriptions for all endpoints per IEEE 1016 §5.3."
            )

        score = sum(checks.values()) / len(checks)
        failures = [k.replace("_", " ").capitalize() for k, v in checks.items() if not v]

        return StandardResult(
            standard_id="IEEE 1016",
            standard_name="Software Design Description",
            passed=score >= self.PASS_THRESHOLD,
            score=score,
            checks=checks,
            failures=failures,
            suggestions=suggestions,
        )

    # ── IEEE 730 ────────────────────────────────────────────────────────
    def check_ieee_730(self, content: str) -> StandardResult:
        """
        IEEE 730: Software Quality Assurance
        Checks if quality assurance processes are defined and documented.
        """
        c = content.lower()

        checks: Dict[str, bool] = {
            "has_quality_objectives": any(kw in c for kw in [
                "quality", "quality goal", "quality objective", "sqa", "assurance"
            ]),
            "has_review_process": any(kw in c for kw in [
                "review", "inspection", "audit", "walkthrough", "approval", "peer"
            ]),
            "has_metrics_defined": any(kw in c for kw in [
                "metric", "kpi", "measure", "accuracy", "precision", "recall",
                "latency", "throughput", "f1"
            ]),
            "has_defect_tracking": any(kw in c for kw in [
                "defect", "bug", "issue", "error handling", "exception", "fix", "patch"
            ]),
            "has_standards_compliance_mention": any(kw in c for kw in [
                "ieee", "standard", "compliance", "conform", "guideline", "regulation"
            ]),
            "has_security_or_access_control": any(kw in c for kw in [
                "security", "access control", "authentication", "authorization",
                "offline", "encrypt", "secure"
            ]),
        }

        suggestions = []
        if not checks["has_metrics_defined"]:
            suggestions.append(
                "Define quality metrics (retrieval accuracy, latency, recall) per IEEE 730 §4.4."
            )
        if not checks["has_review_process"]:
            suggestions.append(
                "Document the code review and QA process per IEEE 730 §4.2."
            )
        if not checks["has_security_or_access_control"]:
            suggestions.append(
                "Include security/access control documentation per IEEE 730 §4.7."
            )

        score = sum(checks.values()) / len(checks)
        failures = [k.replace("_", " ").capitalize() for k, v in checks.items() if not v]

        return StandardResult(
            standard_id="IEEE 730",
            standard_name="Software Quality Assurance",
            passed=score >= self.PASS_THRESHOLD,
            score=score,
            checks=checks,
            failures=failures,
            suggestions=suggestions,
        )

    # ── Master runner ────────────────────────────────────────────────────
    def run_full_compliance_check(self, content: str) -> ComplianceReport:
        """
        Run all 5 IEEE compliance checks and return a full ComplianceReport.

        Args:
            content (str): Text to validate. Can be a RAG response,
                           a document excerpt, or any project documentation.

        Returns:
            ComplianceReport: Full report with per-standard scores + overall verdict.
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty for IEEE compliance check.")

        results = [
            self.check_ieee_12207(content),
            self.check_ieee_830(content),
            self.check_ieee_829(content),
            self.check_ieee_1016(content),
            self.check_ieee_730(content),
        ]

        overall_score = sum(r.score for r in results) / len(results)
        overall_passed = all(r.passed for r in results)
        passed_count = sum(1 for r in results if r.passed)

        summary = (
            f"{passed_count}/5 IEEE standards passed | "
            f"Overall score: {round(overall_score * 100, 1)}% | "
            f"{'COMPLIANT ✅' if overall_passed else 'NEEDS IMPROVEMENT ⚠️'}"
        )

        return ComplianceReport(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            overall_passed=overall_passed,
            standards=results,
            summary=summary,
        )


# ─────────────────────────────────────────────
#  Public API (import this in your RAG pipeline)
# ─────────────────────────────────────────────

_checker = IEEEComplianceChecker()   # module-level singleton


def check_compliance(content: str) -> dict:
    """
    Run IEEE compliance check on any text content.

    Args:
        content (str): Text to check (RAG response, document, etc.)

    Returns:
        dict: JSON-serializable compliance report with per-standard scores.

    Example:
        from tools.ieee_compliance_tool import check_compliance

        report = check_compliance(rag_answer + " " + source_docs)
        print(report["summary"])
        print(report["standards"])
    """
    report = _checker.run_full_compliance_check(content)
    return report.to_dict()