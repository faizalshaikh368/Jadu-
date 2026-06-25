from typing import Any


class PromptBuilder:
    """Build structured Kubernetes troubleshooting prompts for LLM."""

    SYSTEM_PROMPT = """You are a Senior Kubernetes SRE with deep expertise in troubleshooting production Kubernetes clusters.

Your role is to analyze Kubernetes investigation evidence and provide:
1. Root Cause - The primary reason for the failure
2. Explanation - Why this happened and how Kubernetes components are involved
3. Suggested Fix - Step-by-step actionable fix
4. kubectl Command - Exact command to apply the fix
5. Prevention - How to prevent this in the future
6. Confidence Score - Your confidence level (0-100)

Be specific, practical, and beginner-friendly. Avoid generic advice.
Focus on Kubernetes-specific solutions."""

    def build_prompt(self, investigation: dict[str, Any]) -> str:
        """
        Build a structured prompt from investigation data.

        Args:
            investigation: Complete investigation payload

        Returns:
            Formatted prompt string
        """
        prompt_parts = [self.SYSTEM_PROMPT, "\n\n"]
        prompt_parts.append("=" * 60)
        prompt_parts.append("\nKUBERNETES INVESTIGATION EVIDENCE\n")
        prompt_parts.append("=" * 60 + "\n\n")

        # Pod Status
        pods = investigation.get("pods", {})
        prompt_parts.append("## POD STATUS\n")
        prompt_parts.append(f"Total Pods: {pods.get('total_pods', 0)}\n")
        prompt_parts.append(f"Healthy: {pods.get('healthy', False)}\n\n")

        problematic_pods = pods.get("problematic_pods", [])
        if problematic_pods:
            prompt_parts.append("### Problematic Pods:\n")
            for pod in problematic_pods:
                prompt_parts.append(
                    f"- **{pod.get('name', 'unknown')}** "
                    f"(namespace: {pod.get('namespace', 'unknown')})\n"
                    f"  - Status: {pod.get('status', 'Unknown')}\n"
                    f"  - Restarts: {pod.get('restarts', 0)}\n"
                    f"  - Node: {pod.get('node', 'unknown')}\n"
                )
        else:
            prompt_parts.append("No problematic pods detected.\n")

        prompt_parts.append("\n")

        # Logs
        logs = investigation.get("logs", {})
        prompt_parts.append("## LOGS\n")
        prompt_parts.append(f"Collected: {logs.get('collected', False)}\n\n")

        log_entries = logs.get("entries", [])
        if log_entries:
            prompt_parts.append("### Recent Logs from Problematic Pods:\n")
            for entry in log_entries[:3]:  # Limit to 3 pods
                prompt_parts.append(
                    f"\n**Pod:** {entry.get('pod_name', 'unknown')} "
                    f"(namespace: {entry.get('namespace', 'unknown')})\n"
                    f"```\n{entry.get('logs', 'No logs available')[:500]}\n```\n"
                )
        else:
            prompt_parts.append("No logs collected.\n")

        prompt_parts.append("\n")

        # Events
        events = investigation.get("events", {})
        prompt_parts.append("## EVENTS\n")
        prompt_parts.append(f"Collected: {events.get('collected', False)}\n\n")

        warnings = events.get("warnings", [])
        if warnings:
            prompt_parts.append("### Warnings:\n")
            for warning in warnings[:10]:  # Limit to 10 warnings
                prompt_parts.append(f"- {warning}\n")
        else:
            prompt_parts.append("No warning events detected.\n")

        prompt_parts.append("\n")

        # Deployments
        deployments = investigation.get("deployments", {})
        prompt_parts.append("## DEPLOYMENTS\n")
        prompt_parts.append(f"Healthy: {deployments.get('healthy', False)}\n\n")

        deployment_list = deployments.get("deployments", [])
        if deployment_list:
            prompt_parts.append("### Deployment Status:\n")
            for dep in deployment_list[:5]:  # Limit to 5 deployments
                status = "✓" if dep.get("healthy", False) else "✗"
                prompt_parts.append(
                    f"- {status} **{dep.get('name', 'unknown')}** "
                    f"(namespace: {dep.get('namespace', 'unknown')})\n"
                    f"  - Replicas: {dep.get('available_replicas', 0)}/{dep.get('replicas', 0)} available\n"
                )
        else:
            prompt_parts.append("No deployments found.\n")

        prompt_parts.append("\n")

        # Network
        network = investigation.get("network", {})
        prompt_parts.append("## NETWORKING\n")
        prompt_parts.append(f"Healthy: {network.get('healthy', False)}\n\n")

        issues = network.get("issues", [])
        if issues:
            prompt_parts.append("### Issues:\n")
            for issue in issues[:5]:  # Limit to 5 issues
                prompt_parts.append(f"- {issue}\n")
        else:
            prompt_parts.append("No networking issues detected.\n")

        prompt_parts.append("\n")
        prompt_parts.append("=" * 60 + "\n")
        prompt_parts.append("\nBased on the evidence above, provide your diagnosis in the following format:\n\n")
        prompt_parts.append("1. **Root Cause:** [One sentence describing the primary issue]\n\n")
        prompt_parts.append("2. **Explanation:** [2-3 sentences explaining why this happened]\n\n")
        prompt_parts.append("3. **Suggested Fix:** [Step-by-step actionable fix]\n\n")
        prompt_parts.append("4. **kubectl Command:** [Exact kubectl command to fix the issue]\n\n")
        prompt_parts.append("5. **Prevention:** [How to prevent this in the future]\n\n")
        prompt_parts.append("6. **Confidence Score:** [0-100 with brief reasoning]\n")

        return "".join(prompt_parts)