from typing import Any
from loguru import logger


class FixRecommendationEngine:
    """Generate actionable Kubernetes fix recommendations."""

    def __init__(self):
        """Initialize fix recommendation engine."""
        self.common_fixes = {
            "CrashLoopBackOff": {
                "cause": "Container is crashing repeatedly",
                "fix": "Check container logs for startup errors. Common causes: missing environment variables, application errors, or resource constraints.",
                "kubectl": "kubectl logs <pod-name> -n <namespace> --previous",
                "prevention": "Implement proper health checks and resource limits. Use ConfigMaps/Secrets for configuration.",
            },
            "ImagePullBackOff": {
                "cause": "Cannot pull container image",
                "fix": "Verify image name and tag exist in the registry. Check image pull secrets if using private registry.",
                "kubectl": "kubectl describe pod <pod-name> -n <namespace>",
                "prevention": "Use immutable image tags. Set up proper image pull policies and secrets.",
            },
            "OOMKilled": {
                "cause": "Container exceeded memory limit",
                "fix": "Increase memory limits in deployment spec. Monitor application memory usage.",
                "kubectl": "kubectl edit deployment <deployment-name> -n <namespace>",
                "prevention": "Set appropriate resource requests and limits. Use Vertical Pod Autoscaler for right-sizing.",
            },
            "Pending": {
                "cause": "Pod cannot be scheduled",
                "fix": "Check node resources and pod resource requirements. Verify node selectors and taints/tolerations.",
                "kubectl": "kubectl describe pod <pod-name> -n <namespace>",
                "prevention": "Implement resource quotas and limit ranges. Monitor cluster capacity.",
            },
        }

    def recommend(self, diagnosis: dict[str, Any], investigation: dict[str, Any]) -> dict[str, Any]:
        """
        Generate fix recommendations based on diagnosis.

        Args:
            diagnosis: Root cause analysis from LLM
            investigation: Complete investigation payload

        Returns:
            Enhanced diagnosis with fix recommendations
        """
        logger.info("Generating fix recommendations")

        # Start with LLM diagnosis
        recommendation = diagnosis.copy()

        # Enhance with pattern-based recommendations if confidence is low
        confidence = diagnosis.get("confidence", 0)
        if confidence < 70:
            logger.info("Low confidence detected, enhancing with pattern-based recommendations")
            recommendation = self._enhance_with_patterns(recommendation, investigation)

        # Add practical kubectl commands
        recommendation = self._add_practical_commands(recommendation, investigation)

        logger.info("Fix recommendations generated")
        return recommendation

    def _enhance_with_patterns(self, diagnosis: dict[str, Any], investigation: dict[str, Any]) -> dict[str, Any]:
        """
        Enhance diagnosis with pattern-based recommendations.

        Args:
            diagnosis: Current diagnosis
            investigation: Investigation payload

        Returns:
            Enhanced diagnosis
        """
        enhanced = diagnosis.copy()

        # Check pod statuses for known issues
        pods = investigation.get("pods", {})
        problematic_pods = pods.get("problematic_pods", [])

        for pod in problematic_pods:
            status = pod.get("status", "")
            if status in self.common_fixes:
                fix_info = self.common_fixes[status]

                # Only enhance if current fix is generic
                if "No fix suggested" in enhanced.get("fix", ""):
                    enhanced["fix"] = fix_info["fix"]
                    enhanced["prevention"] = fix_info["prevention"]

                # Add specific kubectl command if not provided
                if "No command provided" in enhanced.get("kubectl_command", ""):
                    pod_name = pod.get("name", "<pod-name>")
                    namespace = pod.get("namespace", "<namespace>")
                    enhanced["kubectl_command"] = fix_info["kubectl_command"].replace(
                        "<pod-name>", pod_name
                    ).replace("<namespace>", namespace)

                break

        return enhanced

    def _add_practical_commands(self, diagnosis: dict[str, Any], investigation: dict[str, Any]) -> dict[str, Any]:
        """
        Add practical kubectl commands based on investigation findings.

        Args:
            diagnosis: Current diagnosis
            investigation: Investigation payload

        Returns:
            Diagnosis with practical commands
        """
        enhanced = diagnosis.copy()

        # If no kubectl command provided, add generic investigation commands
        if "No command provided" in enhanced.get("kubectl_command", ""):
            commands = []

            # Add pod investigation command
            pods = investigation.get("pods", {})
            problematic_pods = pods.get("problematic_pods", [])
            if problematic_pods:
                pod = problematic_pods[0]
                pod_name = pod.get("name", "<pod-name>")
                namespace = pod.get("namespace", "<namespace>")
                commands.append(f"kubectl logs {pod_name} -n {namespace} --previous")
                commands.append(f"kubectl describe pod {pod_name} -n {namespace}")

            # Add deployment command if deployment issues found
            deployments = investigation.get("deployments", {})
            if not deployments.get("healthy", True):
                commands.append("kubectl get deployments -A")
                commands.append("kubectl describe deployment <deployment-name> -n <namespace>")

            if commands:
                enhanced["kubectl_command"] = commands[0]
                enhanced["additional_commands"] = commands[1:] if len(commands) > 1 else []

        return enhanced