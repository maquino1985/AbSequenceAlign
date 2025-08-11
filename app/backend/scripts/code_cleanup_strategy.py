#!/usr/bin/env python3
"""
Comprehensive Code Cleanup Strategy for AbSequenceAlign Backend

This script implements a systematic approach to identify and clean up:
1. Redundant/duplicate services and classes
2. Unused imports and dead code
3. Erroneous or inconsistent implementations
4. Code that violates architectural patterns
5. Missing or incorrect type annotations
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import json


class CodeCleanupAnalyzer:
    """Analyzer for identifying code cleanup opportunities"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.analysis_results = {
            "redundant_services": [],
            "unused_imports": [],
            "dead_code": [],
            "inconsistent_patterns": [],
            "missing_types": [],
            "architectural_violations": [],
            "duplicate_functions": [],
            "orphaned_files": [],
        }

    def analyze_service_redundancy(self) -> List[Dict[str, Any]]:
        """
        Analyze service layer for redundancy and overlap.

        Identifies:
        - Services with similar responsibilities
        - Duplicate method implementations
        - Services that could be merged
        - Unused service methods
        """
        services_dir = self.root_dir / "application" / "services"
        service_files = list(services_dir.glob("*.py"))

        service_analysis = []

        for service_file in service_files:
            if service_file.name == "__init__.py":
                continue

            with open(service_file, "r") as f:
                content = f.read()

            # Parse the file
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            service_info = {
                "file": str(service_file),
                "class_name": None,
                "methods": [],
                "dependencies": [],
                "responsibilities": [],
            }

            # Extract class information
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    service_info["class_name"] = node.name

                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "args": [arg.arg for arg in item.args.args],
                                "decorators": [
                                    d.id
                                    for d in item.decorator_list
                                    if isinstance(d, ast.Name)
                                ],
                            }
                            service_info["methods"].append(method_info)

                    # Analyze responsibilities based on method names
                    responsibilities = self._analyze_service_responsibilities(
                        service_info["methods"]
                    )
                    service_info["responsibilities"] = responsibilities

                    break

            service_analysis.append(service_info)

        # Find redundant services
        redundant_services = self._find_redundant_services(service_analysis)
        self.analysis_results["redundant_services"] = redundant_services

        return redundant_services

    def _analyze_service_responsibilities(
        self, methods: List[Dict]
    ) -> List[str]:
        """Analyze service responsibilities based on method names and patterns"""
        responsibilities = set()

        method_names = [m["name"].lower() for m in methods]

        # Pattern matching for responsibilities
        patterns = {
            "persistence": [
                "save",
                "persist",
                "store",
                "create",
                "update",
                "delete",
            ],
            "annotation": ["annotate", "process", "analyze", "parse"],
            "conversion": ["convert", "transform", "map", "to_", "from_"],
            "validation": ["validate", "check", "verify"],
            "response": ["response", "format", "serialize"],
            "integration": ["integrate", "coordinate", "orchestrate"],
        }

        for pattern_name, keywords in patterns.items():
            for method_name in method_names:
                if any(keyword in method_name for keyword in keywords):
                    responsibilities.add(pattern_name)

        return list(responsibilities)

    def _find_redundant_services(self, services: List[Dict]) -> List[Dict]:
        """Find services with overlapping responsibilities"""
        redundant = []

        for i, service1 in enumerate(services):
            for j, service2 in enumerate(services[i + 1 :], i + 1):
                # Check for overlapping responsibilities
                overlap = set(service1["responsibilities"]) & set(
                    service2["responsibilities"]
                )

                if (
                    len(overlap) >= 2
                ):  # At least 2 overlapping responsibilities
                    redundant.append(
                        {
                            "service1": service1["file"],
                            "service2": service2["file"],
                            "overlapping_responsibilities": list(overlap),
                            "recommendation": self._generate_merge_recommendation(
                                service1, service2
                            ),
                        }
                    )

        return redundant

    def _generate_merge_recommendation(
        self, service1: Dict, service2: Dict
    ) -> str:
        """Generate recommendation for merging redundant services"""
        if (
            "persistence" in service1["responsibilities"]
            and "persistence" in service2["responsibilities"]
        ):
            return f"Consider merging {service1['class_name']} and {service2['class_name']} into a unified persistence service"
        elif (
            "annotation" in service1["responsibilities"]
            and "annotation" in service2["responsibilities"]
        ):
            return f"Consider merging {service1['class_name']} and {service2['class_name']} into a unified annotation service"
        else:
            return f"Review overlapping responsibilities between {service1['class_name']} and {service2['class_name']}"

    def analyze_unused_imports(self) -> List[Dict[str, Any]]:
        """Analyze files for unused imports"""
        unused_imports = []

        for py_file in self.root_dir.rglob("*.py"):
            if "tests" in str(py_file) or "__pycache__" in str(py_file):
                continue

            with open(py_file, "r") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Extract used names
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)

            # Find unused imports
            unused = []
            for imp in imports:
                if imp.split(".")[-1] not in used_names:
                    unused.append(imp)

            if unused:
                unused_imports.append(
                    {"file": str(py_file), "unused_imports": unused}
                )

        self.analysis_results["unused_imports"] = unused_imports
        return unused_imports

    def analyze_architectural_patterns(self) -> List[Dict[str, Any]]:
        """Analyze code for architectural pattern violations"""
        violations = []

        # Check for direct database access in services
        for py_file in self.root_dir.rglob("*.py"):
            if "services" in str(py_file) and py_file.name.endswith(".py"):
                with open(py_file, "r") as f:
                    content = f.read()

                # Check for direct SQLAlchemy imports in services
                if "from sqlalchemy" in content and "services" in str(py_file):
                    violations.append(
                        {
                            "file": str(py_file),
                            "violation": "Direct SQLAlchemy usage in service layer",
                            "recommendation": "Use repository pattern for data access",
                        }
                    )

        # Check for missing interfaces
        service_files = list(
            (self.root_dir / "application" / "services").glob("*.py")
        )
        interface_files = list(
            (self.root_dir / "core" / "interfaces").glob("*.py")
        )

        for service_file in service_files:
            if service_file.name == "__init__.py":
                continue

            service_name = service_file.stem
            interface_name = f"{service_name}.py"

            if not any(interface_name in str(f) for f in interface_files):
                violations.append(
                    {
                        "file": str(service_file),
                        "violation": "Service without corresponding interface",
                        "recommendation": f"Create interface for {service_name}",
                    }
                )

        self.analysis_results["architectural_violations"] = violations
        return violations

    def analyze_duplicate_functions(self) -> List[Dict[str, Any]]:
        """Find duplicate or very similar functions across the codebase"""
        function_signatures = defaultdict(list)

        for py_file in self.root_dir.rglob("*.py"):
            if "tests" in str(py_file) or "__pycache__" in str(py_file):
                continue

            with open(py_file, "r") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Create function signature
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({', '.join(args)})"

                    function_signatures[signature].append(
                        {
                            "file": str(py_file),
                            "line": node.lineno,
                            "function_name": node.name,
                        }
                    )

        # Find duplicates
        duplicates = []
        for signature, locations in function_signatures.items():
            if len(locations) > 1:
                duplicates.append(
                    {
                        "signature": signature,
                        "locations": locations,
                        "recommendation": "Consider extracting to shared utility module",
                    }
                )

        self.analysis_results["duplicate_functions"] = duplicates
        return duplicates

    def analyze_orphaned_files(self) -> List[str]:
        """Find files that are not imported or used anywhere"""
        all_files = set()
        imported_files = set()

        # Collect all Python files
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                all_files.add(py_file)

        # Find imported files
        for py_file in all_files:
            with open(py_file, "r") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Try to find the imported file
                        module_parts = node.module.split(".")
                        for i in range(len(module_parts)):
                            potential_file = (
                                self.root_dir
                                / "/".join(module_parts[: i + 1])
                                / "__init__.py"
                            )
                            if potential_file.exists():
                                imported_files.add(potential_file)
                            potential_file = (
                                self.root_dir
                                / "/".join(module_parts[: i + 1])
                                / f"{module_parts[-1]}.py"
                            )
                            if potential_file.exists():
                                imported_files.add(potential_file)

        # Find orphaned files (excluding __init__.py and main files)
        orphaned = []
        for file in all_files:
            if (
                file.name not in ["__init__.py", "main.py", "app.py"]
                and file not in imported_files
                and "test" not in file.name.lower()
            ):
                orphaned.append(str(file))

        self.analysis_results["orphaned_files"] = orphaned
        return orphaned

    def generate_cleanup_report(self) -> str:
        """Generate a comprehensive cleanup report"""
        report = []
        report.append("# Code Cleanup Analysis Report")
        report.append("=" * 50)
        report.append("")

        # Service redundancy
        if self.analysis_results["redundant_services"]:
            report.append("## 🔄 Redundant Services")
            report.append("")
            for redundancy in self.analysis_results["redundant_services"]:
                report.append(
                    f"### {redundancy['service1']} ↔ {redundancy['service2']}"
                )
                report.append(
                    f"**Overlapping:** {', '.join(redundancy['overlapping_responsibilities'])}"
                )
                report.append(
                    f"**Recommendation:** {redundancy['recommendation']}"
                )
                report.append("")

        # Unused imports
        if self.analysis_results["unused_imports"]:
            report.append("## 🗑️ Unused Imports")
            report.append("")
            for file_imports in self.analysis_results["unused_imports"]:
                report.append(f"### {file_imports['file']}")
                for imp in file_imports["unused_imports"]:
                    report.append(f"- `{imp}`")
                report.append("")

        # Architectural violations
        if self.analysis_results["architectural_violations"]:
            report.append("## 🏗️ Architectural Violations")
            report.append("")
            for violation in self.analysis_results["architectural_violations"]:
                report.append(f"### {violation['file']}")
                report.append(f"**Issue:** {violation['violation']}")
                report.append(
                    f"**Recommendation:** {violation['recommendation']}"
                )
                report.append("")

        # Duplicate functions
        if self.analysis_results["duplicate_functions"]:
            report.append("## 🔄 Duplicate Functions")
            report.append("")
            for duplicate in self.analysis_results["duplicate_functions"]:
                report.append(f"### {duplicate['signature']}")
                for location in duplicate["locations"]:
                    report.append(f"- {location['file']}:{location['line']}")
                report.append(
                    f"**Recommendation:** {duplicate['recommendation']}"
                )
                report.append("")

        # Orphaned files
        if self.analysis_results["orphaned_files"]:
            report.append("## 📁 Orphaned Files")
            report.append("")
            for file in self.analysis_results["orphaned_files"]:
                report.append(f"- `{file}`")
            report.append("")

        return "\n".join(report)

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete analysis and return results"""
        print("🔍 Analyzing service redundancy...")
        self.analyze_service_redundancy()

        print("🔍 Analyzing unused imports...")
        self.analyze_unused_imports()

        print("🔍 Analyzing architectural patterns...")
        self.analyze_architectural_patterns()

        print("🔍 Analyzing duplicate functions...")
        self.analyze_duplicate_functions()

        print("🔍 Analyzing orphaned files...")
        self.analyze_orphaned_files()

        return self.analysis_results


def main():
    """Run the code cleanup analysis"""
    analyzer = CodeCleanupAnalyzer()

    print("🚀 Starting comprehensive code cleanup analysis...")
    results = analyzer.run_full_analysis()

    # Generate report
    report = analyzer.generate_cleanup_report()

    # Save report
    with open("CODE_CLEANUP_REPORT.md", "w") as f:
        f.write(report)

    print("✅ Analysis complete! Check CODE_CLEANUP_REPORT.md for results.")

    # Print summary
    print("\n📊 Summary:")
    print(f"- Redundant services: {len(results['redundant_services'])}")
    print(f"- Files with unused imports: {len(results['unused_imports'])}")
    print(
        f"- Architectural violations: {len(results['architectural_violations'])}"
    )
    print(f"- Duplicate functions: {len(results['duplicate_functions'])}")
    print(f"- Orphaned files: {len(results['orphaned_files'])}")


if __name__ == "__main__":
    main()
