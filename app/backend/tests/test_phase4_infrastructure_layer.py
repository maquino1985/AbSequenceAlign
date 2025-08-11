"""
Tests for Phase 4: Infrastructure Layer
Tests repository pattern, dependency injection, and external tool adapters.
"""

from unittest.mock import Mock, patch, AsyncMock
from backend.domain.models import (
    ChainType,
    DomainType,
    NumberingScheme,
    RegionType,
)

import pytest
import tempfile
import os

from backend.infrastructure.repositories.sequence_repository import (
    SequenceRepository,
)
from backend.infrastructure.dependency_container import (
    DependencyContainer,
    get_container,
    register_service,
    register_factory,
    register_config,
    get_service,
    get_config,
    configure_default_services,
)
from backend.infrastructure.adapters.base_adapter import (
    BaseExternalToolAdapter,
    ToolConfiguration,
)
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
    BiologicDomain,
    BiologicFeature,
)
from backend.domain.models import (
    NumberingScheme,
)


class TestSequenceRepository:
    """Test sequence repository functionality"""

    def setup_method(self):
        """Setup test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.repository = SequenceRepository(storage_path=self.temp_dir)

    def teardown_method(self):
        """Teardown test method"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_repository_creation(self):
        """Test creating a sequence repository"""
        assert self.repository is not None
        assert self.repository.storage_path == self.temp_dir
        assert os.path.exists(self.temp_dir)

    def test_save_and_find_sequence(self):
        """Test saving and finding a sequence"""
        # Create test sequence
        sequence = self._create_test_sequence("test_sequence")

        # Save sequence
        saved_sequence = self.repository.save(sequence)
        assert saved_sequence.id is not None

        # Find sequence by ID
        found_sequence = self.repository.find_by_id(saved_sequence.id)
        assert found_sequence is not None
        assert found_sequence.name == "test_sequence"
        assert found_sequence.id == saved_sequence.id

    def test_find_by_name(self):
        """Test finding sequence by name"""
        sequence = self._create_test_sequence("unique_name")
        self.repository.save(sequence)

        found_sequence = self.repository.find_by_name("unique_name")
        assert found_sequence is not None
        assert found_sequence.name == "unique_name"

    def test_find_by_chain_type(self):
        """Test finding sequences by chain type"""
        # Create sequences with different chain types
        heavy_sequence = self._create_test_sequence("heavy_seq")
        heavy_sequence.chains[0].chain_type = ChainType.HEAVY
        self.repository.save(heavy_sequence)

        light_sequence = self._create_test_sequence("light_seq")
        light_sequence.chains[0].chain_type = ChainType.LIGHT
        self.repository.save(light_sequence)

        # Find heavy chains
        heavy_sequences = self.repository.find_by_chain_type("H")
        assert len(heavy_sequences) == 1
        assert heavy_sequences[0].name == "heavy_seq"

        # Find light chains
        light_sequences = self.repository.find_by_chain_type("L")
        assert len(light_sequences) == 1
        assert light_sequences[0].name == "light_seq"

    def test_find_by_domain_type(self):
        """Test finding sequences by domain type"""
        # Create sequence with variable domain
        sequence = self._create_test_sequence("var_seq")
        sequence.chains[0].sequences[0].domains[0].domain_type = "VARIABLE"
        self.repository.save(sequence)

        # Find variable domains
        var_sequences = self.repository.find_by_domain_type("VARIABLE")
        assert len(var_sequences) == 1
        assert var_sequences[0].name == "var_seq"

    def test_delete_sequence(self):
        """Test deleting a sequence"""
        sequence = self._create_test_sequence("to_delete")
        saved_sequence = self.repository.save(sequence)

        # Verify it exists
        assert self.repository.find_by_id(saved_sequence.id) is not None

        # Delete it
        success = self.repository.delete(saved_sequence.id)
        assert success is True

        # Verify it's gone
        assert self.repository.find_by_id(saved_sequence.id) is None

    def test_count_sequences(self):
        """Test counting sequences"""
        assert self.repository.count() == 0

        # Add some sequences
        self.repository.save(self._create_test_sequence("seq1"))
        self.repository.save(self._create_test_sequence("seq2"))
        self.repository.save(self._create_test_sequence("seq3"))

        assert self.repository.count() == 3

    def test_find_all_sequences(self):
        """Test finding all sequences"""
        # Add sequences
        seq1 = self.repository.save(self._create_test_sequence("seq1"))
        seq2 = self.repository.save(self._create_test_sequence("seq2"))

        # Find all
        all_sequences = self.repository.find_all()
        assert len(all_sequences) == 2

        sequence_names = [seq.name for seq in all_sequences]
        assert "seq1" in sequence_names
        assert "seq2" in sequence_names

    def _create_test_sequence(self, name: str) -> BiologicEntity:
        """Create a test biologic entity"""
        biologic_entity = BiologicEntity(name=name, biologic_type="antibody")

        # Add a heavy chain with sequence and domain
        heavy_chain = BiologicChain(name="Heavy", chain_type="HEAVY")
        sequence = BiologicSequence(
            sequence_type="PROTEIN", sequence_data="ACDEFGHIKLMNPQRSTVWY"
        )

        # Add a variable domain
        domain = BiologicDomain(
            domain_type="VARIABLE",
            start_position=0,
            end_position=19,
            confidence_score=90,
        )
        sequence.domains.append(domain)
        heavy_chain.sequences.append(sequence)
        biologic_entity.add_chain(heavy_chain)

        return biologic_entity


class TestDependencyContainer:
    """Test dependency injection container functionality"""

    def setup_method(self):
        """Setup test method"""
        self.container = DependencyContainer()

    def test_container_creation(self):
        """Test creating a dependency container"""
        assert self.container is not None
        assert len(self.container.get_registered_services()) == 0

    def test_register_and_get_service(self):
        """Test registering and getting a service"""
        mock_service = Mock()
        self.container.register_service("test_service", mock_service)

        retrieved_service = self.container.get_service("test_service")
        assert retrieved_service == mock_service

    def test_register_and_get_factory(self):
        """Test registering and getting a factory"""

        def create_service(param=None):
            return Mock()

        self.container.register_factory("test_factory", create_service)

        service1 = self.container.get_service("test_factory")
        service2 = self.container.get_service("test_factory")

        assert service1 is not None
        assert service2 is not None
        assert service1 != service2  # Different instances

    def test_register_and_get_singleton(self):
        """Test registering and getting a singleton"""

        def create_singleton():
            return Mock()

        self.container.register_singleton("test_singleton", create_singleton)

        service1 = self.container.get_service("test_singleton")
        service2 = self.container.get_service("test_singleton")

        assert service1 is not None
        assert service2 is not None
        assert service1 == service2  # Same instance

    def test_register_and_get_config(self):
        """Test registering and getting configuration"""
        self.container.register_config("test_key", "test_value")

        value = self.container.get_config("test_key")
        assert value == "test_value"

        # Test default value
        default_value = self.container.get_config("nonexistent_key", "default")
        assert default_value == "default"

    def test_has_service(self):
        """Test checking if service exists"""
        assert self.container.has_service("nonexistent") is False

        self.container.register_service("test_service", Mock())
        assert self.container.has_service("test_service") is True

    def test_has_config(self):
        """Test checking if config exists"""
        assert self.container.has_config("nonexistent") is False

        self.container.register_config("test_key", "test_value")
        assert self.container.has_config("test_key") is True

    def test_get_registered_services(self):
        """Test getting list of registered services"""
        self.container.register_service("service1", Mock())
        self.container.register_factory("factory1", lambda: Mock())
        self.container.register_singleton("singleton1", lambda: Mock())

        services = self.container.get_registered_services()
        assert "service1" in services
        assert "factory1" in services
        assert "singleton1" in services
        assert services["service1"] == "instance"
        assert services["factory1"] == "factory"

    def test_get_configuration(self):
        """Test getting all configuration"""
        self.container.register_config("key1", "value1")
        self.container.register_config("key2", "value2")

        config = self.container.get_configuration()
        assert config["key1"] == "value1"
        assert config["key2"] == "value2"

    def test_clear_container(self):
        """Test clearing the container"""
        self.container.register_service("test_service", Mock())
        self.container.register_config("test_key", "test_value")

        assert len(self.container.get_registered_services()) > 0
        assert len(self.container.get_configuration()) > 0

        self.container.clear()

        assert len(self.container.get_registered_services()) == 0
        assert len(self.container.get_configuration()) == 0

    def test_service_not_found(self):
        """Test getting non-existent service"""
        with pytest.raises(KeyError):
            self.container.get_service("nonexistent_service")


class TestGlobalContainer:
    """Test global container functionality"""

    def setup_method(self):
        """Setup test method"""
        # Clear global container
        from backend.infrastructure.dependency_container import _container

        global _container
        _container = None

    def test_global_container_singleton(self):
        """Test that global container is a singleton"""
        container1 = get_container()
        container2 = get_container()

        assert container1 is container2

    def test_global_register_and_get_service(self):
        """Test global service registration and retrieval"""
        mock_service = Mock()
        register_service("global_service", mock_service)

        retrieved_service = get_service("global_service")
        assert retrieved_service == mock_service

    def test_global_register_and_get_config(self):
        """Test global config registration and retrieval"""
        register_config("global_key", "global_value")

        value = get_config("global_key")
        assert value == "global_value"


class TestToolConfiguration:
    """Test tool configuration functionality"""

    def test_configuration_creation(self):
        """Test creating a tool configuration"""
        config = ToolConfiguration()
        assert config.timeout == 300
        assert config.working_directory is None
        assert len(config.environment_variables) == 0
        assert len(config.additional_arguments) == 0

    def test_set_timeout(self):
        """Test setting timeout"""
        config = ToolConfiguration().set_timeout(600)
        assert config.timeout == 600

    def test_set_working_directory(self):
        """Test setting working directory"""
        config = ToolConfiguration().set_working_directory("/tmp")
        assert config.working_directory == "/tmp"

    def test_add_environment_variable(self):
        """Test adding environment variable"""
        config = ToolConfiguration().add_environment_variable(
            "TEST_VAR", "test_value"
        )
        assert config.environment_variables["TEST_VAR"] == "test_value"

    def test_add_argument(self):
        """Test adding argument"""
        config = ToolConfiguration().add_argument("--verbose")
        assert "--verbose" in config.additional_arguments

    def test_fluent_interface(self):
        """Test fluent interface for configuration"""
        config = (
            ToolConfiguration()
            .set_timeout(600)
            .set_working_directory("/tmp")
            .add_environment_variable("TEST_VAR", "test_value")
            .add_argument("--verbose")
        )

        assert config.timeout == 600
        assert config.working_directory == "/tmp"
        assert config.environment_variables["TEST_VAR"] == "test_value"
        assert "--verbose" in config.additional_arguments


class MockExternalToolAdapter(BaseExternalToolAdapter):
    """Mock external tool adapter for testing"""

    def _find_executable(self) -> str:
        return "/usr/bin/mock_tool"

    def _validate_tool_installation(self) -> None:
        pass

    def _build_command(self, **kwargs) -> list:
        return ["mock_tool", "--test"]

    def _parse_output(self, output: str, **kwargs) -> dict:
        return {"result": "success", "output": output}

    def validate_output(self, output: str) -> bool:
        """Validate tool output"""
        return "success" in output.lower()


class TestBaseExternalToolAdapter:
    """Test base external tool adapter functionality"""

    @patch("subprocess.run")
    def test_execute_success(self, mock_run):
        """Test successful tool execution"""
        # Mock successful execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        adapter = MockExternalToolAdapter("mock_tool")
        result = adapter.execute()

        assert result["result"] == "success"
        assert result["output"] == "success output"

    @patch("subprocess.run")
    def test_execute_failure(self, mock_run):
        """Test failed tool execution"""
        # Mock failed execution
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error message"
        mock_run.return_value = mock_result

        adapter = MockExternalToolAdapter("mock_tool")

        with pytest.raises(Exception):
            adapter.execute()

    @patch("subprocess.run")
    def test_get_version(self, mock_run):
        """Test getting tool version"""
        # Mock version command
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Mock Tool v1.0.0"
        mock_run.return_value = mock_result

        adapter = MockExternalToolAdapter("mock_tool")
        version = adapter.get_version()

        assert version == "Mock Tool v1.0.0"

    def test_get_tool_info(self):
        """Test getting tool information"""
        adapter = MockExternalToolAdapter("mock_tool")
        info = adapter.get_tool_info()

        assert info["name"] == "mock_tool"
        assert info["executable_path"] == "/usr/bin/mock_tool"
        assert "version" in info
        assert "available" in info


class TestInfrastructureIntegration:
    """Test infrastructure layer integration"""

    def setup_method(self):
        """Setup test method"""
        self.container = DependencyContainer()
        configure_default_services(self.container)

    def test_default_services_configuration(self):
        """Test that default services are properly configured"""
        services = self.container.get_registered_services()

        # Check that key services are registered
        assert "sequence_repository" in services
        assert "anarci_adapter" in services
        assert "hmmer_adapter" in services
        assert "annotation_service" in services
        assert "alignment_service" in services
        assert "processing_service" in services

    def test_service_dependency_injection(self):
        """Test that services can be retrieved from container"""
        # Configure container to use temporary directory for repository
        import tempfile

        temp_dir = tempfile.mkdtemp()
        self.container.register_config("storage_path", temp_dir)

        # Test repository
        repository = self.container.get_service("sequence_repository")
        assert repository is not None
        assert isinstance(repository, SequenceRepository)

        # Test adapters
        anarci_adapter = self.container.get_service("anarci_adapter")
        assert anarci_adapter is not None

        hmmer_adapter = self.container.get_service("hmmer_adapter")
        assert hmmer_adapter is not None

        # Test services
        annotation_service = self.container.get_service("annotation_service")
        assert annotation_service is not None

        alignment_service = self.container.get_service("alignment_service")
        assert alignment_service is not None

        processing_service = self.container.get_service("processing_service")
        assert processing_service is not None
