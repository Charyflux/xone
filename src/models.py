"""Pydantic models for X-ONE API"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Finding(BaseModel):
    """Security Finding/Vulnerability"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    vuln_type: str = Field(..., description="Type of vulnerability (XSS, SQLi, SSRF, etc)")
    url: str = Field(..., description="Target URL where vulnerability was found")
    payload: str = Field(..., description="Actual payload or PoC code")
    severity: Literal["Critical", "High", "Medium", "Low", "Info"] = Field(
        ..., description="CVSS severity classification"
    )
    param: Optional[str] = Field(default=None, description="Parameter name if applicable")
    context: str = Field(..., description="Context/explanation of the vulnerability")
    evidence: Optional[str] = Field(default=None, description="Evidence/screenshot/output")
    tool: str = Field(..., description="Tool that discovered this finding (scanner name)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cvss_score: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    cvss_vector: Optional[str] = Field(default=None, description="CVSS v3.1 vector string")

    class Config:
        json_schema_extra = {
            "example": {
                "vuln_type": "XSS Reflected",
                "url": "https://target.com/search?q=",
                "payload": "<script>alert(1)</script>",
                "severity": "High",
                "param": "q",
                "context": "User input reflected without sanitization in HTML body",
                "tool": "context_xss_scanner.py",
                "cvss_score": 7.1,
                "cvss_vector": "AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N"
            }
        }


class ChatMessage(BaseModel):
    """Single chat message in conversation"""
    role: Literal["user", "assistant"]
    content: str
    model: str = Field(default="dolphin-llama3")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to X-ONE for chat/analysis"""
    message: str = Field(..., description="User question or request")
    model: str = Field(default="dolphin-llama3", description="Ollama model to use")
    stream: bool = Field(default=True, description="Enable streaming response")


class ChatResponse(BaseModel):
    """Response from X-ONE"""
    content: str = Field(..., description="Response content")
    model: str
    tokens: int = Field(default=0, description="Tokens generated")


class AnalyzeRequest(BaseModel):
    """Request to analyze a vulnerability"""
    vuln_type: str
    url: str
    payload: str
    severity: Optional[str] = None
    param: Optional[str] = None
    context: Optional[str] = None


class ReportRequest(BaseModel):
    """Request to generate security report"""
    format: Literal["markdown", "html", "json"] = "markdown"
    include_findings: bool = True
    include_analysis: bool = True


class HealthResponse(BaseModel):
    """Server health status"""
    status: Literal["online", "offline"]
    ollama_available: bool
    models_loaded: list[str]
    port: int
    version: str = "4.0.0"


class ModelsResponse(BaseModel):
    """Available Ollama models"""
    models: list[str]
    current: str


class FindingsListResponse(BaseModel):
    """List of all findings"""
    findings: list[Finding]
    total: int
    by_severity: dict[str, int]


class SessionInfo(BaseModel):
    """Current session information"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    findings_count: int
