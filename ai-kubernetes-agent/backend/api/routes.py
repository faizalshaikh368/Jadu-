from fastapi import APIRouter, HTTPException
from loguru import logger

from ..models.schemas import HealthResponse, InvestigationRequest
from ..services.diagnosis_service import DiagnosisService
from ..core.config import settings

router = APIRouter()

# Initialize diagnosis service
diagnosis_service = DiagnosisService(settings.kubeconfig_path)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status of the service
    """
    logger.info("Health check requested")
    return HealthResponse(status="healthy", service="ai-kubernetes-agent")


@router.post("/investigate")
async def investigate(request: InvestigationRequest):
    """
    Investigate Kubernetes cluster and return diagnosis.

    Args:
        request: Investigation request with optional cluster name

    Returns:
        Investigation results with AI diagnosis
    """
    cluster_name = request.cluster_name or "default"
    logger.info(f"Investigation requested for cluster: {cluster_name}")

    try:
        # Run diagnosis with selected cluster context
        result = await diagnosis_service.diagnose(context=request.cluster_name)

        # Check for errors
        if result.get("status") == "error":
            logger.error(f"Investigation failed: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Investigation failed"),
            )

        logger.info("Investigation completed successfully")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during investigation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/clusters")
async def get_clusters():
    """
    Get list of available Kubernetes clusters.

    Returns:
        List of cluster contexts
    """
    logger.info("Fetching available clusters")

    try:
        from ..kubernetes.kubectl_executor import KubectlExecutor

        executor = KubectlExecutor(settings.kubeconfig_path)
        result = executor.get_contexts()

        if result["success"]:
            # Get current context
            current_result = executor.get_current_context()
            current_context = current_result.get("context") if current_result["success"] else None

            return {
                "success": True,
                "clusters": result["contexts"],
                "current": current_context,
            }
        else:
            logger.warning(f"Failed to fetch clusters: {result.get('error')}")
            return {
                "success": False,
                "clusters": [],
                "error": result.get("error", "Failed to fetch clusters"),
            }

    except Exception as e:
        logger.error(f"Error fetching clusters: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch clusters: {str(e)}",
        )