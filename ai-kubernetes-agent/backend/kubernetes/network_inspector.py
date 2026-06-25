from typing import Any
from loguru import logger

from .kubectl_executor import KubectlExecutor


class NetworkInspector:
    """Inspect services and networking."""

    def __init__(self, executor: KubectlExecutor):
        """
        Initialize network inspector.

        Args:
            executor: KubectlExecutor instance
        """
        self.executor = executor

    def inspect(self, namespace: str = "all-namespaces") -> dict[str, Any]:
        """
        Inspect services and networking.

        Args:
            namespace: Kubernetes namespace to inspect

        Returns:
            Dictionary with network investigation results
        """
        logger.info(f"Inspecting network in namespace: {namespace}")

        services_data = self.executor.get_services(namespace)
        if not services_data:
            logger.warning("Failed to fetch services data")
            return {
                "healthy": False,
                "services": [],
                "issues": ["Failed to fetch services"],
            }

        items = services_data.get("items", [])
        services = []
        issues = []

        for item in items:
            metadata = item.get("metadata", {})
            spec = item.get("spec", {})

            name = metadata.get("name", "unknown")
            service_namespace = metadata.get("namespace", "unknown")
            service_type = spec.get("type", "ClusterIP")
            cluster_ip = spec.get("clusterIP", "None")

            # Get ports
            ports = []
            for port in spec.get("ports", []):
                ports.append({
                    "name": port.get("name", ""),
                    "port": port.get("port", 0),
                    "target_port": port.get("targetPort", 0),
                    "protocol": port.get("protocol", "TCP"),
                })

            # Check for selector
            selector = spec.get("selector", {})
            if not selector:
                issues.append(
                    f"Service {name} in {service_namespace} has no selector"
                )

            services.append({
                "name": name,
                "namespace": service_namespace,
                "type": service_type,
                "cluster_ip": cluster_ip,
                "selector": selector,
                "ports": ports,
            })

        # Check for services without endpoints
        for service in services:
            if service["cluster_ip"] == "None":
                issues.append(
                    f"Service {service['name']} in {service['namespace']} has no cluster IP"
                )

        healthy = len(issues) == 0

        logger.info(
            f"Network inspection complete: {len(services)} services, "
            f"healthy={healthy}"
        )

        return {
            "healthy": healthy,
            "services": services,
            "issues": issues,
        }