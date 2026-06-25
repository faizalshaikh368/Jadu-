from typing import Any
from loguru import logger

from .kubectl_executor import KubectlExecutor


class DeploymentInspector:
    """Inspect deployments and detect issues."""

    def __init__(self, executor: KubectlExecutor):
        """
        Initialize deployment inspector.

        Args:
            executor: KubectlExecutor instance
        """
        self.executor = executor

    def inspect(self, namespace: str = "all-namespaces") -> dict[str, Any]:
        """
        Inspect deployments and identify unhealthy ones.

        Args:
            namespace: Kubernetes namespace to inspect

        Returns:
            Dictionary with deployment investigation results
        """
        logger.info(f"Inspecting deployments in namespace: {namespace}")

        deployments_data = self.executor.get_deployments(namespace)
        if not deployments_data:
            logger.warning("Failed to fetch deployments data")
            return {
                "healthy": False,
                "deployments": [],
                "error": "Failed to fetch deployments",
            }

        items = deployments_data.get("items", [])
        deployments = []
        healthy = True

        for item in items:
            metadata = item.get("metadata", {})
            spec = item.get("spec", {})
            status = item.get("status", {})

            name = metadata.get("name", "unknown")
            dep_namespace = metadata.get("namespace", "unknown")
            replicas = spec.get("replicas", 0)
            available_replicas = status.get("availableReplicas", 0)
            unavailable_replicas = status.get("unavailableReplicas", 0)

            # Check conditions
            conditions = status.get("conditions", [])
            condition_list = []
            for condition in conditions:
                condition_list.append({
                    "type": condition.get("type", "Unknown"),
                    "status": condition.get("status", "Unknown"),
                    "reason": condition.get("reason", ""),
                    "message": condition.get("message", ""),
                })

            # Check if deployment is unhealthy
            is_healthy = (
                available_replicas == replicas
                and unavailable_replicas == 0
            )

            if not is_healthy:
                healthy = False

            deployments.append({
                "name": name,
                "namespace": dep_namespace,
                "replicas": replicas,
                "available_replicas": available_replicas,
                "unavailable_replicas": unavailable_replicas,
                "conditions": condition_list,
                "healthy": is_healthy,
            })

        logger.info(
            f"Deployment inspection complete: {len(deployments)} deployments, "
            f"healthy={healthy}"
        )

        return {
            "healthy": healthy,
            "deployments": deployments,
        }