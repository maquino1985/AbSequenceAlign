"""
Base adapter interface for external tools.
Defines the contract that all external tool adapters must implement.
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List
import subprocess
import os

from backend.core.interfaces import AbstractExternalToolAdapter
from backend.core.exceptions import ExternalToolError
from backend.logger import logger


class BaseExternalToolAdapter(AbstractExternalToolAdapter):
    """Base class for external tool adapters"""

    def __init__(self, tool_name: str, executable_path: Optional[str] = None):
        self.tool_name = tool_name
        self.executable_path = executable_path or self._find_executable()
        self._validate_tool_installation()
        logger.info(
            f"Initialized {tool_name} adapter with path: {self.executable_path}"
        )

    @abstractmethod
    def _find_executable(self) -> str:
        """Find the executable path for the tool"""
        pass

    @abstractmethod
    def _validate_tool_installation(self) -> None:
        """Validate that the tool is properly installed"""
        pass

    @abstractmethod
    def _build_command(self, **kwargs) -> List[str]:
        """Build the command to execute"""
        pass

    @abstractmethod
    def _parse_output(self, output: str, **kwargs) -> Dict[str, Any]:
        """Parse the tool output"""
        pass

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the external tool"""
        try:
            # Build command
            command = self._build_command(**kwargs)
            logger.debug(f"Executing command: {' '.join(command)}")

            # Execute command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self._get_timeout(),
                cwd=self._get_working_directory(),
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = f"Tool execution failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise ExternalToolError(error_msg, tool_name=self.tool_name)

            # Parse output
            output = result.stdout
            parsed_result = self._parse_output(output, **kwargs)

            logger.debug("Tool execution completed successfully")
            return parsed_result

        except subprocess.TimeoutExpired:
            error_msg = (
                f"Tool execution timed out after {self._get_timeout()} seconds"
            )
            logger.error(error_msg)
            raise ExternalToolError(error_msg, tool_name=self.tool_name)

        except FileNotFoundError:
            error_msg = f"Tool executable not found: {self.executable_path}"
            logger.error(error_msg)
            raise ExternalToolError(error_msg, tool_name=self.tool_name)

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg)
            raise ExternalToolError(error_msg, tool_name=self.tool_name)

    def _get_timeout(self) -> int:
        """Get the timeout for tool execution (in seconds)"""
        return 300  # 5 minutes default

    def _get_working_directory(self) -> Optional[str]:
        """Get the working directory for tool execution"""
        return None  # Use current directory

    def _check_executable_exists(self, path: str) -> bool:
        """Check if an executable exists and is executable"""
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def _find_executable_in_path(self, executable_name: str) -> Optional[str]:
        """Find an executable in the system PATH"""
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            if path_dir:
                executable_path = os.path.join(path_dir, executable_name)
                if self._check_executable_exists(executable_path):
                    return executable_path
        return None

    def get_version(self) -> Optional[str]:
        """Get the version of the external tool"""
        try:
            # Try to get version using --version flag
            result = subprocess.run(
                [self.executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout.strip()

            # Try -v flag
            result = subprocess.run(
                [self.executable_path, "-v"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout.strip()

            return None

        except Exception as e:
            logger.warning(
                f"Could not get version for {self.tool_name}: {str(e)}"
            )
            return None

    def is_available(self) -> bool:
        """Check if the tool is available and working"""
        try:
            version = self.get_version()
            return version is not None
        except Exception:
            return False

    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about the tool"""
        return {
            "name": self.tool_name,
            "executable_path": self.executable_path,
            "version": self.get_version(),
            "available": self.is_available(),
        }


class ToolConfiguration:
    """Configuration for external tools"""

    def __init__(self):
        self.timeout = 300
        self.working_directory = None
        self.environment_variables = {}
        self.additional_arguments = []

    def set_timeout(self, timeout: int) -> "ToolConfiguration":
        """Set the timeout for tool execution"""
        self.timeout = timeout
        return self

    def set_working_directory(self, directory: str) -> "ToolConfiguration":
        """Set the working directory for tool execution"""
        self.working_directory = directory
        return self

    def add_environment_variable(
        self, key: str, value: str
    ) -> "ToolConfiguration":
        """Add an environment variable"""
        self.environment_variables[key] = value
        return self

    def add_argument(self, argument: str) -> "ToolConfiguration":
        """Add an additional argument"""
        self.additional_arguments.append(argument)
        return self
