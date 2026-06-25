from typing import Any
from loguru import logger

from .kubectl_executor import KubectlExecutor


class PodInspector:
    """Inspect pods and detect unhealthy states."""

    UNHEALTHY_STATUSES = {
        "CrashLoopBackOff",
        "ImagePullBackOff",
        "ErrImagePull",
        "Pending",
        "Error",
        "OOMKilled",
        "Failed",
    }

    def __init__(self, executor: KubectlExecutor):
        """
        Initialize pod inspector.

        Args:
            executor: KubectlExecutor instance
        """
        self.executor = executor

    def inspect(self, namespace: str = "all-namespaces") -> dict[str, Any]:
        """
        Inspect pods and identify problematic ones.

        Args:
            namespace: Kubernetes namespace to inspect

        Returns:
            Dictionary with pod investigation results
        """
        logger.info(f"Inspecting pods in namespace: {namespace}")

        pods_data = self.executor.get_pods(namespace)
        if not pods_data:
            logger.warning("Failed to fetch pods data")
            return {
                "healthy": False,
                "total_pods": 0,
                "problematic_pods": [],
                "error": "Failed to fetch pods",
            }

        items = pods_data.get("items", [])
        total_pods = len(items)
        problematic_pods = []

        for item in items:
            metadata = item.get("metadata", {})
            status = item.get("status", {})
            spec = item.get("spec", {})

            pod_name = metadata.get("name", "unknown")
            pod_namespace = metadata.get("namespace", "unknown")
            pod_status = status.get("phase", "Unknown")

            # Check container statuses for more detailed issues
            container_statuses = status.get("containerStatuses", [])
            restarts = sum(cs.get("restartCount", 0) for cs in container_statuses)

            # Check for waiting/terminated states
            detailed_status = pod_status
            for cs in container_statuses:
                state = cs.get("state", {})
                if "waiting" in state:
                    waiting = state["waiting"]
                    reason = waiting.get("reason", "")
                    if reason in self.UNHEALTHY_STATUSES:
                        detailed_status = reason
                        break
                elif "terminated" in state:
                    terminated = state["terminated"]
                    reason = terminated.get("reason", "")
                    if reason in self.UNHEALTHY_STATUSES:
                        detailed_status = reason
                        break

            # Check if pod is problematic
            is_problematic = (
                detailed_status in self.UNHEALTHY_STATUSES
                or restarts > 5
            )

            if is_problematic:
                node = spec.get("nodeName", "unknown")
                problematic_pods.append({
                    "name": pod_name,
                    "namespace": pod_namespace,
                    "status": detailed_status,
                    "restarts": restarts,
                    "node": node,
                })

        healthy = len(problematic_pods) == 0

        logger.info(
            f"Pod inspection complete: {total_pods} total, "
            f"{len(problematic_pods)} problematic"
        )

        return {
            "healthy": healthy,
            "total_pods": total_pods,
            "problematic_pods": problematic_pods,
        }