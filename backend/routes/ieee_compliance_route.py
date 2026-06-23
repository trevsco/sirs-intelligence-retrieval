"""
routes/ieee_compliance_route.py
---------------------------------
FastAPI route for the IEEE Compliance Check feature in SIRS.

Endpoints:
    POST /compliance/check   — Check any text against all 5 IEEE standards
    GET  /compliance/info    — Get info about the 5 supported standards

Add to your main.py:
    from routes.ieee_compliance_route import router as compliance_router
    app.include_router(compliance_router, prefix="/compliance", tags=["IEEE Compliance"])
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# Adjust import path to match your project structure
from tools.ieee_compliance_tool import check_compliance

router = APIRouter()


# ─────────────────────────────────────────────
#  Request / Response schemas
# ─────────────────────────────────────────────

class ComplianceCheckRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=10,
        description="Text to validate (RAG response, document, or any project text).",
        example="The system shall retrieve documents with accuracy above 85%. "
                "Unit tests and integration tests are defined for all modules. "
                "Architecture follows a six-layer design with FAISS and Ollama.",
    )
    label: Optional[str] = Field(
        None,
        description="Optional label for this check (e.g., 'Query Response #42').",
    )


class ComplianceCheckResponse(BaseModel):
    label: Optional[str]
    compliance_report: dict


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@router.post("/check", response_model=ComplianceCheckResponse, summary="Run IEEE Compliance Check")
async def run_ieee_compliance_check(request: ComplianceCheckRequest):
    """
    Run a compliance check on the provided text against all 5 IEEE standards:
    - IEEE 12207 (Life Cycle Processes)
    - IEEE 830  (Requirements Specifications)
    - IEEE 829  (Test Documentation)
    - IEEE 1016 (Design Description)
    - IEEE 730  (Quality Assurance)

    Returns a full compliance report with per-standard scores,
    individual check results, failures, and improvement suggestions.
    """
    try:
        report = await check_compliance(request.content)
        return ComplianceCheckResponse(
            label=request.label,
            compliance_report=report,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")


@router.get("/info", summary="List Supported IEEE Standards")
async def get_standards_info():
    """
    Returns metadata about the 5 IEEE standards used in SIRS compliance checks.
    """
    return {
        "supported_standards": [
            {
                "id": "IEEE 12207",
                "name": "Software Life Cycle Processes",
                "focus": "Requirements, design, implementation, testing, deployment phases",
                "relevance_to_sirs": "Ensures SIRS follows a complete software development lifecycle",
            },
            {
                "id": "IEEE 830",
                "name": "Software Requirements Specifications",
                "focus": "Functional & non-functional requirements, traceability, measurability",
                "relevance_to_sirs": "Validates SIRS requirements are complete and well-defined",
            },
            {
                "id": "IEEE 829",
                "name": "Software Test Documentation",
                "focus": "Test plans, test cases, expected results, test coverage",
                "relevance_to_sirs": "Validates SIRS test documentation quality",
            },
            {
                "id": "IEEE 1016",
                "name": "Software Design Description",
                "focus": "Architecture, interfaces, data design, design rationale",
                "relevance_to_sirs": "Validates SIRS six-layer architecture documentation",
            },
            {
                "id": "IEEE 730",
                "name": "Software Quality Assurance",
                "focus": "Quality metrics, review processes, defect tracking, security",
                "relevance_to_sirs": "Ensures SIRS meets quality standards for offline AI systems",
            },
        ],
        "pass_threshold": "50% of checks per standard must pass",
        "overall_compliant": "All 5 standards must individually pass",
    }
