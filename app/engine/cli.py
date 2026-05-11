import keyword
import os
from pathlib import Path
from typing import TYPE_CHECKING

import click
from flask import current_app
from jinja2 import Environment, PackageLoader, StrictUndefined
from slugify import slugify

if TYPE_CHECKING:
    from app.engine import FeatureRegistry

FEATURE_TEMPLATES = {
    '__init__.py.j2': '__init__.py',
    'models.py.j2': 'models.py',
    'routes.py.j2': 'routes.py',
}


def _get_registry() -> FeatureRegistry:
    registry = current_app.extensions.get('registry')
    if registry is None:
        raise click.ClickException('No FeatureRegistry found. Is it registered on the app?')

    return registry


@click.group('features')
def features_cli() -> None:
    """Manage application features."""


@features_cli.command('create')
@click.argument('name')
@click.option(
    '--path', default='app/features', show_default=True, help='Parent directory to create the feature package in.'
)
@click.option('--url-prefix', default=None, help='Blueprint URL prefix. Defaults to /<name>.')
@click.option('--verbose-name', default=None, help='Human-readable feature name.')
@click.option('--with-models/--no-models', default=True, show_default=True, help='Generate a models.py.')
@click.option('--with-routes/--no-routes', default=True, show_default=True, help='Generate a routes.py.')
def create_feature(
    name: str,
    path: str,
    url_prefix: str | None,
    verbose_name: str | None,
    with_models: bool,
    with_routes: bool,
) -> None:
    """Scaffold a new feature package under PATH/NAME."""
    slug = slugify(name, separator='_')
    feature_dir = Path(path) / slug

    if feature_dir.exists():
        raise click.ClickException(f"Directory '{feature_dir}' already exists.")

    context = {
        'name': slug,
        'verbose_name': verbose_name or slug.replace('_', ' ').title(),
        'url_prefix': url_prefix or f'/{slug}',
        'with_models': with_models,
        'with_routes': with_routes,
    }

    env = Environment(
        loader=PackageLoader('app.engine', 'templates'),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    feature_dir.mkdir(parents=True)
    click.echo(f'  Created {feature_dir}{os.sep}')

    active_templates = {
        template: output
        for template, output in FEATURE_TEMPLATES.items()
        if template == '__init__.py.j2'
        or (template == 'models.py.j2' and with_models)
        or (template == 'routes.py.j2' and with_routes)
    }

    for template_name, output_name in active_templates.items():
        template = env.get_template(template_name)
        output_path = feature_dir / output_name
        output_path.write_text(template.render(**context))
        click.echo(f'  Created {output_path}')

    module_path = Path(path).as_posix().replace('/', '.').strip('.')

    click.echo(f"\nFeature '{slug}' created. Add it to INSTALLED_FEATURES:")
    click.echo(f'  INSTALLED_FEATURES = [..., "{module_path}.{slug}"]')


@features_cli.command('list')
@click.option('--verbose', '-v', is_flag=True, help='Show additional details per feature.')
def list_features(verbose: bool) -> None:
    """List all installed features."""
    registry = _get_registry()

    features = list(registry.get_features())
    if not features:
        click.echo('No features installed.')
        return

    click.echo(f'{len(features)} installed feature(s):\n')
    for feature in features:
        click.echo(f'  {click.style(feature.name, fg="green")}  {feature.verbose_name}')
        if verbose:
            click.echo(f'    url_prefix  {feature.url_prefix or "-"}')
            click.echo(f'    import_name {feature.import_name}')
            click.echo(f'    models      {len(feature.models)}')


@features_cli.command('models')
@click.argument('feature_name', required=False)
def list_models(feature_name: str | None) -> None:
    """List registered models, optionally scoped to a single feature."""
    registry = _get_registry()

    if feature_name:
        try:
            features = [registry.get_feature(feature_name)]
        except LookupError as e:
            raise click.ClickException(str(e)) from e
    else:
        features = list(registry.get_features())

    total = 0
    for feature in features:
        models = list(feature.get_models())
        if not models:
            continue
        click.echo(f'{click.style(feature.name, fg="green")}')
        for model in models:
            click.echo(f'  {model.__name__}')
            total += 1

    click.echo(f'\n{total} model(s) total.')


@features_cli.command('check')
def check_features() -> None:
    """Verify that all installed features and their models loaded correctly."""
    registry = _get_registry()
    ok = True

    for feature in registry.get_features():
        issues = []

        if '-' in feature.name:
            issues.append("feature name contains '-'")

        if keyword.iskeyword(feature.name):
            issues.append('feature name is a Python keyword')

        if not feature.models and Path(feature.root_path).joinpath('models.py').exists():
            issues.append('models.py exists but no models were registered')

        if issues:
            ok = False
            click.echo(f'{click.style(feature.name, fg="red")}')
            for issue in issues:
                click.echo(f'  ! {issue}')
        else:
            click.echo(f'{click.style(feature.name, fg="green")}  ok')

    if not ok:
        click.echo('\nFix these issues before running the application')
