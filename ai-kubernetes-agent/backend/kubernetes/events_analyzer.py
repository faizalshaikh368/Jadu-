from typing import Any
from loguru import logger

from .kubectl_executor import KubectlExecutor


class EventsAnalyzer:
    """Analyze Kubernetes events and detect warnings."""

    WARNING_REASONS = {
        "FailedScheduling",
        "BackOff",
        "FailedMount",
        "FailedPull",
        "ErrImagePull",
        "Unhealthy",
        "FailedCreate",
        "Failed",
        "Killing",
        "Preempting",
    }

    def __init__(self, executor: KubectlExecutor):
        """
        Initialize events analyzer.

        Args:
            executor: KubectlExecutor instance
        """
        self.executor = executor

    def analyze(self, namespace: str = "all-namespaces") -> dict[str, Any]:
        """
        Analyze Kubernetes events and identify warnings.

        Args:
            namespace: Kubernetes namespace to analyze

        Returns:
            Dictionary with event analysis results
        """
        logger.info(f"Analyzing events in namespace: {namespace}")

        events_data = self.executor.get_events(namespace)
        if not events_data:
            logger.warning("Failed to fetch events data")
            return {
                "collected": False,
                "events": [],
                "warnings": ["Failed to fetch events"],
            }

        items = events_data.get("items", [])
        events = []
        warnings = []

        for item in items:
            metadata = item.get("metadata", {})
            spec = item.get("involvedObject", {})

            event_type = item.get("type", "Normal")
            reason = item.get("reason", "Unknown")
            message = item.get("message", "")
            event_namespace = metadata.get("namespace", "unknown")
            involved_object = spec.get("name", "unknown")

            event_info = {
                "type": event_type,
                "reason": reason,
                "message": message,
                "namespace": event_namespace,
                "involved_object": involved_object,
            }

            events.append(event_info)

            # Check for warning events
            if event_type == "Warning" or reason in self.WARNING_REASONS:
                warning_msg = f"[{event_namespace}] {reason}: {message}"
                warnings.append(warning_msg)
                logger.warning(warning_msg)

        logger.info(
            f"Event analysis complete: {len(events)} events, "
            f"{len(warnings)} warnings"
        )

        return {
            "collected": True,
            "events": events,
            "warnings": warnings,
        }