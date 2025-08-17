#!/usr/bin/env python3
"""
Standalone test script for BLAST services
"""

import sys

sys.path.append(".")


def test_blast_services():
    """Test BLAST services directly"""
    print("Testing BLAST services...")

    try:
        # Test service imports
        from services.blast_service import BlastService
        from services.igblast_service import IgBlastService

        print("✅ BLAST services imported successfully")

        # Test service initialization
        blast_service = BlastService()
        igblast_service = IgBlastService()
        print("✅ BLAST services initialized successfully")

        # Test getting databases
        databases = blast_service.get_available_databases()
        print(f"✅ Available databases: {list(databases.keys())}")

        # Test getting organisms
        organisms = igblast_service.get_supported_organisms()
        print(f"✅ Supported organisms: {organisms}")

        # Test sequence validation
        test_sequence = "ASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPELQLEESCAEAQDGELDGLWTTITIFITLFLLSVCYSATVTFFKVKWIFSSVVDLKQTIIPDYRNMIGQGA"
        is_valid = blast_service.validate_sequence(test_sequence, "protein")
        print(f"✅ Sequence validation: {is_valid}")

        print("🎉 All BLAST service tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_blast_services()
    sys.exit(0 if success else 1)
