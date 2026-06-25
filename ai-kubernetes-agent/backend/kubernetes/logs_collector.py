from typing import Any
from loguru import logger

from .kubectl_executor import KubectlExecutor


class LogsCollector:
    """Collect logs from problematic pods."""

    ERROR_PATTERNS = [
        "Exception",
        "Error",
        "FATAL",
        "connection refused",
        "connection reset",
        "timeout",
        "not found",
        "missing",
        "failed",
        "panic",
        "OOM",
        "killed",
        "permission denied",
        "no such file",
        "cannot",
        "unable",
    ]

    def __init__(self, executor: KubectlExecutor, max_lines: int = 100):
        """
        Initialize logs collector.

        Args:
            executor: KubectlExecutor instance
            max_lines: Maximum lines to collect per pod
        """
        self.executor = executor
        self.max_lines = max_lines

    def collect(self, problematic_pods: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Collect logs from problematic pods.

        Args:
            problematic_pods: List of problematic pod dictionaries

        Returns:
            Dictionary with collected logs
        """
        logger.info(f"Collecting logs from {len(problematic_pods)} problematic pods")

        entries = []

        for pod in problematic_pods:
            pod_name = pod.get("name", "unknown")
            namespace = pod.get("namespace", "unknown")

            logger.info(f"Collecting logs for pod: {pod_name} in {namespace}")

            result = self.executor.get_logs(
                pod_name=pod_name,
                namespace=namespace,
                tail_lines=self.max_lines,
            )

            if result["success"]:
                logs = result["stdout"]
                error_detected = self._detect_errors(logs)

                entries.append({
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "logs": logs,
                    "error_detected": error_detected,
                })
            else:
                logger.warning(
                    f"Failed to collect logs for {pod_name}: {result['stderr']}"
                )
                entries.append({
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "logs": f"Failed to collect logs: {result['stderr']}",
                    "error_detected": True,
                })

        logger.info(f"Log collection complete: {len(entries)} entries collected")

        return {
            "collected": True,
            "entries": entries,
        }

    def _detect_errors(self, logs: str) -> bool:
        """
        Detect if logs contain error patterns.

        Args:
            logs: Log content

        Returns:
            True if errors detected, False otherwise
        """
        logs_lower = logs.lower()
        for pattern in self.ERROR_PATTERNS:
            if pattern.lower() in logs_lower:
                return True
        return False