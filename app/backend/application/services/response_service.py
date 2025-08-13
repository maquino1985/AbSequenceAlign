"""
Pure response service for formatting API responses.
"""

from typing import Dict, Any, List
from backend.core.interfaces import ProcessingResult
from backend.logger import logger


class ResponseService:
    """Service for formatting API responses"""

    def __init__(self):
        """Initialize the response service"""
        pass

    def format_annotation_response(
        self, result: ProcessingResult
    ) -> Dict[str, Any]:
        """
        Format an annotation result for API response.

        Args:
            result: The processing result to format

        Returns:
            Formatted response dictionary
        """
        try:
            if not result.success:
                return self.create_error_response(result.error)

            # Extract the annotated sequence
            annotated_sequence = result.data

            # Format the response
            response = {
                "success": True,
                "message": "Successfully annotated",
                "data": {
                    "sequence": {
                        "name": annotated_sequence.biologic_name,
                        # "biologic_type": annotated_sequence.biologic_type.value,
                        "chains": annotated_sequence.chains,
                    }
                },
            }
            return response

        except Exception as e:
            logger.error(f"Error formatting annotation response: {e}")
            return self.create_error_response(
                f"Response formatting error: {str(e)}"
            )

    def format_workflow_response(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format a workflow result for API response.

        Args:
            results: List of workflow results to format

        Returns:
            Formatted response dictionary
        """
        try:
            response = {
                "success": True,
                "message": "Workflow completed",
                "data": {
                    "results": [],
                    "summary": {
                        "total": len(results),
                        "successful": 0,
                        "failed": 0,
                    },
                },
            }

            for result in results:
                if result["success"]:
                    response["data"]["summary"]["successful"] += 1
                    # Format successful result
                    formatted_result = self.format_annotation_response(
                        ProcessingResult(success=True, data=result["result"])
                    )
                    response["data"]["results"].append(
                        {
                            "name": result["name"],
                            "success": True,
                            "data": formatted_result["data"],
                        }
                    )
                else:
                    response["data"]["summary"]["failed"] += 1
                    response["data"]["results"].append(
                        {
                            "name": result["name"],
                            "success": False,
                            "error": result["error"],
                        }
                    )

            return response

        except Exception as e:
            logger.error(f"Error formatting workflow response: {e}")
            return self.create_error_response(
                f"Workflow response formatting error: {str(e)}"
            )

    def create_error_response(self, error: str) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error: The error message

        Returns:
            Error response dictionary
        """
        return {"success": False, "error": error, "data": None}

    def validate_response_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate response data.

        Args:
            data: The response data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not data:
                logger.error("Response data is empty")
                return False

            # Check for required fields
            required_fields = ["success"]
            for field in required_fields:
                if field not in data:
                    logger.error(
                        f"Missing required field in response: {field}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating response data: {e}")
            return False
