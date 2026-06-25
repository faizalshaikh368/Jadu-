from typing import Any
from loguru import logger

from .kubectl_executor import KubectlExecutor
from .pod_inspector import PodInspector
from .logs_collector import LogsCollector
from .events_analyzer import EventsAnalyzer
from .deployment_inspector import DeploymentInspector
from .network_inspector import NetworkInspector


class InvestigationService:
    """Orchestrate Kubernetes investigation components."""

    def __init__(self, kubeconfig_path: str | None = None, context: str | None = None):
        """
        Initialize investigation service.

        Args:
            kubeconfig_path: Path to kubeconfig file
            context: Kubernetes context to use
        """
        self.kubeconfig_path = kubeconfig_path
        self.context = context
        self.executor = KubectlExecutor(kubeconfig_path, context)
        self.pod_inspector = PodInspector(self.executor)
        self.logs_collector = LogsCollector(self.executor)
        self.events_analyzer = EventsAnalyzer(self.executor)
        self.deployment_inspector = DeploymentInspector(self.executor)
        self.network_inspector = NetworkInspector(self.executor)

    def investigate(self, namespace: str = "all-namespaces") -> dict[str, Any]:
        """
        Run complete Kubernetes investigation.

        Args:
            namespace: Kubernetes namespace to investigate

        Returns:
            Complete investigation payload
        """
        context_info = f"context: {self.context}" if self.context else "default context"
        logger.info(f"Starting investigation for {context_info}, namespace: {namespace}")

        try:
            # Step 1: Check Pods
            logger.info("Step 1: Checking pods...")
            pods_result = self.pod_inspector.inspect(namespace)

            # Step 2: Collect Logs
            logger.info("Step 2: Collecting logs...")
            problematic_pods = pods_result.get("problematic_pods", [])
            logs_result = self.logs_collector.collect(problematic_pods)

            # Step 3: Analyze Events
            logger.info("Step 3: Analyzing events...")
            events_result = self.events_analyzer.analyze(namespace)

            # Step 4: Inspect Deployments
            logger.info("Step 4: Inspecting deployments...")
            deployments_result = self.deployment_inspector.inspect(namespace)

            # Step 5: Check Networking
            logger.info("Step 5: Checking networking...")
            network_result = self.network_inspector.inspect(namespace)

            logger.info("Investigation complete")

            return {
                "pods": pods_result,
                "logs": logs_result,
                "events": events_result,
                "deployments": deployments_result,
                "network": network_result,
            }

        except Exception as e:
            logger.error(f"Investigation failed: {str(e)}")
            return {
                "pods": {"healthy": False, "total_pods": 0, "problematic_pods": []},
                "logs": {"collected": False, "entries": []},
                "events": {"collected": False, "events": [], "warnings": [str(e)]},
                "deployments": {"healthy": False, "deployments": []},
                "network": {"healthy": False, "services": [], "issues": [str(e)]},
                "error": str(e),
            }