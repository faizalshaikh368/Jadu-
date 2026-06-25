from pydantic import BaseModel
from typing import Any


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str


class InvestigationRequest(BaseModel):
    """Request schema for investigation endpoint."""

    cluster_name: str | None = None


class PodInfo(BaseModel):
    """Pod information schema."""

    name: str
    namespace: str
    status: str
    restarts: int
    node: str


class LogEntry(BaseModel):
    """Log entry schema."""

    pod_name: str
    namespace: str
    logs: str
    error_detected: bool


class EventInfo(BaseModel):
    """Kubernetes event schema."""

    type: str
    reason: str
    message: str
    namespace: str
    involved_object: str


class DeploymentInfo(BaseModel):
    """Deployment information schema."""

    name: str
    namespace: str
    replicas: int
    available_replicas: int
    unavailable_replicas: int
    conditions: list[dict[str, Any]]


class ServiceInfo(BaseModel):
    """Service information schema."""

    name: str
    namespace: str
    type: str
    cluster_ip: str
    ports: list[dict[str, Any]]


class PodsInvestigation(BaseModel):
    """Pod investigation results."""

    healthy: bool
    total_pods: int
    problematic_pods: list[PodInfo]


class LogsInvestigation(BaseModel):
    """Logs investigation results."""

    collected: bool
    entries: list[LogEntry]


class EventsInvestigation(BaseModel):
    """Events investigation results."""

    collected: bool
    events: list[EventInfo]
    warnings: list[str]


class DeploymentsInvestigation(BaseModel):
    """Deployments investigation results."""

    healthy: bool
    deployments: list[DeploymentInfo]


class NetworkInvestigation(BaseModel):
    """Network investigation results."""

    healthy: bool
    services: list[ServiceInfo]
    issues: list[str]


class InvestigationPayload(BaseModel):
    """Complete investigation payload."""

    pods: PodsInvestigation
    logs: LogsInvestigation
    events: EventsInvestigation
    deployments: DeploymentsInvestigation
    network: NetworkInvestigation


class DiagnosisResponse(BaseModel):
    """AI diagnosis response schema."""

    root_cause: str
    explanation: str
    fix: str
    kubectl_command: str
    prevention: str
    confidence: int