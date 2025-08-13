"""Pydantic model generator using datamodel-code-generator."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class ModelGenerator:
    """Generate Pydantic v2 models from OpenAPI schemas."""

    def __init__(self, spec: dict[str, Any], config: dict[str, Any] = None):
        self.spec = spec
        self.config = config or {}

    def generate_models(self, output_dir: Path) -> None:
        """Generate Pydantic models using datamodel-code-generator."""
        models_dir = output_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        # Create temporary spec file for datamodel-code-generator
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(self.spec, temp_file, indent=2)
            temp_spec_path = Path(temp_file.name)

        try:
            # Run datamodel-code-generator with configuration
            cmd = [
                "datamodel-codegen",
                "--input",
                str(temp_spec_path),
                "--input-file-type",
                "openapi",
                "--output",
                str(models_dir / "__init__.py"),
                "--target-python-version",
                "3.10",
                "--enum-field-as-literal",
                "one",
                "--reuse-model",
                "--output-model-type",
                "pydantic_v2.BaseModel",
            ]

            # Apply model_options from config
            model_options = self.config.get("model_options", {})

            # Add conditional options based on config
            if model_options.get("field_constraints", True):
                cmd.append("--field-constraints")

            if model_options.get("use_generic_container_types", True):
                cmd.append("--use-generic-container-types")
            else:
                cmd.append("--use-standard-collections")

            if not model_options.get("use_standard_typing", False):
                # Use typing_extensions by default
                pass
            else:
                cmd.append("--use-standard-typing")

            # Add union operator support if enabled
            if self.config.get("use_union_operator", True):
                cmd.append("--use-union-operator")

            subprocess.run(cmd, capture_output=True, text=True, check=True)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to generate models: {e.stderr}") from e

        finally:
            # Clean up temporary file
            temp_spec_path.unlink()

    def _create_models_init(self, models_dir: Path) -> None:
        """Create __init__.py for models package."""
        init_file = models_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Generated Pydantic models."""\n')
