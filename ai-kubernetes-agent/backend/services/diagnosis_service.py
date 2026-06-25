from typing import Any
from loguru import logger

from ..kubernetes.investigation_service import InvestigationService
from ..ai.prompt_builder import PromptBuilder
from ..ai.llm_client import LLMClient
from ..ai.root_cause_analyzer import RootCauseAnalyzer
from ..ai.fix_recommendation_engine import FixRecommendationEngine


class DiagnosisService:
    """Orchestrate investigation and AI reasoning."""

    def __init__(self, kubeconfig_path: str | None = None):
        """
        Initialize diagnosis service.

        Args:
            kubeconfig_path: Path to kubeconfig file
        """
        self.kubeconfig_path = kubeconfig_path
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.fix_recommendation_engine = FixRecommendationEngine()

    async def diagnose(self, namespace: str = "all-namespaces", context: str | None = None) -> dict[str, Any]:
        """
        Run complete diagnosis: investigation + AI reasoning.

        Args:
            namespace: Kubernetes namespace to investigate
            context: Kubernetes context to use

        Returns:
            Complete diagnosis with root cause and fix
        """
        context_info = f"context: {context}" if context else "default context"
        logger.info(f"Starting diagnosis for {context_info}, namespace: {namespace}")

        try:
            # Create investigation service with context
            investigation_service = InvestigationService(
                kubeconfig_path=self.kubeconfig_path,
                context=context
            )

            # Step 1: Collect Kubernetes evidence
            logger.info("Collecting Kubernetes evidence...")
            investigation = investigation_service.investigate(namespace)

            # Check if investigation failed
            if "error" in investigation:
                return {
                    "status": "error",
                    "error": investigation["error"],
                    "investigation": investigation,
                }

            # Step 2: Build prompt for LLM
            logger.info("Building LLM prompt...")
            prompt = self.prompt_builder.build_prompt(investigation)

            # Step 3: Get LLM response
            logger.info("Requesting AI diagnosis...")
            llm_response = await self.llm_client.generate(prompt)

            if not llm_response["success"]:
                logger.warning(f"LLM request failed: {llm_response.get('error', 'Unknown error')}")
                return {
                    "status": "partial",
                    "investigation": investigation,
                    "diagnosis": {
                        "root_cause": "AI analysis unavailable",
                        "explanation": f"LLM request failed: {llm_response.get('error', 'Unknown error')}",
                        "fix": "Review investigation data manually",
                        "kubectl_command": "No command available",
                        "prevention": "Ensure OpenRouter API key is configured",
                        "confidence": 0,
                    },
                }

            # Step 4: Parse LLM response
            logger.info("Analyzing LLM response...")
            diagnosis = self.root_cause_analyzer.analyze(llm_response["content"])

            # Step 5: Enhance with fix recommendations
            logger.info("Enhancing with fix recommendations...")
            enhanced_diagnosis = self.fix_recommendation_engine.recommend(
                diagnosis, investigation
            )

            logger.info("Diagnosis complete")

            return {
                "status": "success",
                "investigation": investigation,
                "diagnosis": enhanced_diagnosis,
            }

        except Exception as e:
            logger.error(f"Diagnosis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "investigation": {},
                "diagnosis": {},
            }