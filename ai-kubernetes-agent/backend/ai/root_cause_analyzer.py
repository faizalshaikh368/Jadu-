import re
from typing import Any
from loguru import logger


class RootCauseAnalyzer:
    """Analyze LLM response to extract structured root cause information."""

    def __init__(self):
        """Initialize root cause analyzer."""
        self.patterns = {
            "root_cause": r"(?i)root cause:?\s*(.+?)(?:\n|$)",
            "explanation": r"(?i)explanation:?\s*(.+?)(?:\n|$)",
            "fix": r"(?i)suggested fix:?\s*(.+?)(?:\n|$)",
            "kubectl_command": r"(?i)kubectl command:?\s*(.+?)(?:\n|$)",
            "prevention": r"(?i)prevention:?\s*(.+?)(?:\n|$)",
            "confidence": r"(?i)confidence(?:\s+score)?:?\s*(\d+)",
        }

    def analyze(self, llm_response: str) -> dict[str, Any]:
        """
        Parse LLM response and extract structured diagnosis.

        Args:
            llm_response: Raw LLM response text

        Returns:
            Structured diagnosis dictionary
        """
        logger.info("Analyzing LLM response for root cause")

        diagnosis = {
            "root_cause": "Unable to determine root cause",
            "explanation": "No explanation provided",
            "fix": "No fix suggested",
            "kubectl_command": "No command provided",
            "prevention": "No prevention steps provided",
            "confidence": 0,
        }

        # Extract each field using regex patterns
        for field, pattern in self.patterns.items():
            match = re.search(pattern, llm_response, re.DOTALL | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # Clean up markdown formatting
                value = re.sub(r'\*\*', '', value)
                value = re.sub(r'```', '', value)
                value = value.strip()

                if field == "confidence":
                    try:
                        diagnosis[field] = int(value)
                        # Clamp to 0-100
                        diagnosis[field] = max(0, min(100, diagnosis[field]))
                    except ValueError:
                        diagnosis[field] = 50  # Default if parsing fails
                else:
                    diagnosis[field] = value

                logger.debug(f"Extracted {field}: {diagnosis[field][:100]}...")

        logger.info(f"Root cause analysis complete. Confidence: {diagnosis['confidence']}%")

        return diagnosis