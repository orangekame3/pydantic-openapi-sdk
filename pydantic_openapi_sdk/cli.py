"""Command-line interface for the SDK generator."""

from pathlib import Path

import click

from .config import GenerationConfig, load_config, merge_config_with_args
from .generator import CodeGenerator
from .parser import OpenAPIParser


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file (.yaml or .yml)",
)
@click.option(
    "--spec",
    type=str,
    help="OpenAPI specification file or URL (.yaml or .json)",
)
@click.option(
    "--out",
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for generated SDK",
)
@click.option(
    "--package",
    "--package-name",
    help="Package name for generated SDK",
)
@click.option(
    "--base-url",
    help="Default base URL for the API client",
)
@click.option(
    "--timeout",
    type=int,
    help="Default HTTP timeout in seconds",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def generate(
    config: Path | None,
    spec: str | None,
    out: Path | None,
    package: str | None,
    base_url: str | None,
    timeout: int | None,
    verbose: bool,
) -> None:
    """Generate Python SDK from OpenAPI specification."""
    try:
        # Load configuration
        if config:
            if verbose:
                click.echo(f"Loading configuration from {config}")
            generation_config = load_config(config)
        else:
            # Create minimal config from CLI args
            if not spec or not out or not package:
                click.echo(
                    "❌ Error: Either --config file or --spec, --out, and --package must be provided",
                    err=True,
                )
                raise click.Abort()
            generation_config = GenerationConfig(
                spec=spec,
                output_dir=str(out),
                package_name=package,
            )

        # Merge with CLI arguments (CLI takes precedence)
        generation_config = merge_config_with_args(
            generation_config,
            spec=spec,
            output_dir=str(out) if out else None,
            package_name=package,
            base_url=base_url,
            timeout=timeout,
            verbose=verbose,
        )

        if generation_config.verbose:
            click.echo(f"Loading OpenAPI specification from {generation_config.spec}")

        # Parse OpenAPI specification
        parser = OpenAPIParser(generation_config.spec)

        if generation_config.verbose:
            info = parser.get_info()
            click.echo(f"API Title: {info.get('title', 'Unknown')}")
            click.echo(f"API Version: {info.get('version', 'Unknown')}")
            click.echo(f"Tags: {', '.join(sorted(parser.get_tags()))}")
            click.echo(f"Operations: {len(parser.get_operations())}")

        # Generate SDK
        output_path = Path(generation_config.output_dir)
        package_name = generation_config.package_name

        if generation_config.verbose:
            click.echo(f"Generating SDK in {output_path / package_name}")

        generator = CodeGenerator(parser, generation_config.model_dump())
        generator.generate_sdk(output_path, package_name)

        click.echo(f"✅ SDK generated successfully in {output_path / package_name}")

        # Show usage example
        click.echo("\nUsage example:")
        click.echo(f"from {package_name} import Client")
        base_url = generation_config.base_url or "https://api.example.com"
        click.echo(f"client = Client(base_url='{base_url}')")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort() from e


@click.group()
@click.version_option()
def main() -> None:
    """Pydantic OpenAPI SDK Generator."""
    pass


main.add_command(generate)


if __name__ == "__main__":
    main()
