import subprocess
import json
from typing import Any
from loguru import logger


class KubectlExecutor:
    """Safe kubectl command executor with structured output."""

    def __init__(self, kubeconfig_path: str | None = None, context: str | None = None):
        """
        Initialize kubectl executor.

        Args:
            kubeconfig_path: Path to kubeconfig file. Uses default if not provided.
            context: Kubernetes context to use. Uses current context if not provided.
        """
        self.kubeconfig_path = kubeconfig_path
        self.context = context
        self.base_command = ["kubectl"]

        if kubeconfig_path:
            self.base_command.extend(["--kubeconfig", kubeconfig_path])

        if context:
            self.base_command.extend(["--context", context])

    def execute(self, args: list[str], timeout: int = 30) -> dict[str, Any]:
        """
        Execute kubectl command and return structured output.

        Args:
            args: kubectl command arguments
            timeout: Command timeout in seconds

        Returns:
            Dictionary with success, stdout, stderr, and return_code
        """
        command = self.base_command + args
        logger.info(f"Executing: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "return_code": -1,
            }

        except Exception as e:
            logger.error(f"Command failed: {' '.join(command)}. Error: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }

    def get_json(self, args: list[str], timeout: int = 30) -> dict[str, Any] | None:
        """
        Execute kubectl command and parse JSON output.

        Args:
            args: kubectl command arguments (should include -o json)
            timeout: Command timeout in seconds

        Returns:
            Parsed JSON dictionary or None if failed
        """
        args_with_output = args + ["-o", "json"]
        result = self.execute(args_with_output, timeout)

        if not result["success"]:
            logger.warning(f"kubectl command failed: {result['stderr']}")
            return None

        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON output: {str(e)}")
            return None

    def get_pods(self, namespace: str = "all-namespaces") -> dict[str, Any] | None:
        """Get all pods in namespace."""
        return self.get_json(["get", "pods", "-n", namespace])

    def get_events(self, namespace: str = "all-namespaces") -> dict[str, Any] | None:
        """Get all events in namespace."""
        return self.get_json(["get", "events", "-n", namespace])

    def get_deployments(self, namespace: str = "all-namespaces") -> dict[str, Any] | None:
        """Get all deployments in namespace."""
        return self.get_json(["get", "deployments", "-n", namespace])

    def get_services(self, namespace: str = "all-namespaces") -> dict[str, Any] | None:
        """Get all services in namespace."""
        return self.get_json(["get", "services", "-n", namespace])

    def get_logs(self, pod_name: str, namespace: str, tail_lines: int = 100) -> dict[str, Any]:
        """Get logs for a specific pod."""
        return self.execute([
            "logs", pod_name, "-n", namespace, "--tail", str(tail_lines)
        ])

    def describe_deployment(self, deployment_name: str, namespace: str) -> dict[str, Any]:
        """Describe a deployment."""
        return self.execute(["describe", "deployment", deployment_name, "-n", namespace])

    def get_contexts(self) -> dict[str, Any]:
        """Get all available kubectl contexts."""
        result = self.execute(["config", "get-contexts", "-o", "name"])
        if result["success"]:
            contexts = [ctx.strip() for ctx in result["stdout"].split("\n") if ctx.strip()]
            return {"success": True, "contexts": contexts}
        return {"success": False, "contexts": [], "error": result["stderr"]}

    def get_current_context(self) -> dict[str, Any]:
        """Get current kubectl context."""
        result = self.execute(["config", "current-context"])
        if result["success"]:
            return {"success": True, "context": result["stdout"].strip()}
        return {"success": False, "context": None, "error": result["stderr"]}