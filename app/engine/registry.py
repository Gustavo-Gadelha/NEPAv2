import contextlib
import importlib
from collections.abc import Iterator

from flask import Flask

from app.database import Model
from app.engine.feature import Feature


class Registry:
    def __init__(self, app: Flask | None = None, command: str = 'features') -> None:
        self._features: dict[str, Feature] = {}
        self._all_models: dict[str, dict[str, type]] = {}
        self.features_ready = False
        self.models_ready = False
        self.command = command

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if 'registry' in app.extensions:
            raise RuntimeError('A FeatureRegistry is already registered on this app.')

        installed: list[str] = app.config.get('INSTALLED_FEATURES', [])

        # Phase 1 — discover Feature objects
        for module_path in installed:
            feature = self._import_feature(module_path)
            if feature.name in self._features:
                raise RuntimeError(f"Duplicate feature name: '{feature.name}'. Each feature must have a unique name.")

            self._features[feature.name] = feature
            feature.registry = self

        self.features_ready = True

        # Phase 2 — import models from each feature's models module
        for feature in self._features.values():
            self._import_models(feature)

        # Phase 3 — walk SQLAlchemy's mapper registry and assign models
        for mapper in Model.registry.mappers:
            self._register_model(mapper.class_)

        self.models_ready = True

        # Phase 4 — fire on_load hooks now that everything is ready
        for feature in self._features.values():
            feature.load()

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['registry'] = self

        from app.engine.cli import features_cli

        app.cli.add_command(features_cli, name=self.command)

    def _import_feature(self, module_path: str) -> Feature:
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise RuntimeError(f"Could not import feature module '{module_path}'.") from e

        # Find a Feature instance in the module's namespace
        candidates = [obj for obj in vars(module).values() if isinstance(obj, Feature)]

        if not candidates:
            raise RuntimeError(
                f"Module '{module_path}' does not define a Feature instance. "
                'Add `myfeature = Feature("myfeature", __name__)` to its __init__.py.'
            )
        if len(candidates) > 1:
            raise RuntimeError(
                f"Module '{module_path}' defines multiple Feature instances. Each module must define exactly one."
            )

        return candidates[0]

    def _import_models(self, feature: Feature) -> None:
        models_module = f'{feature.import_name}.{feature.models_module}'
        with contextlib.suppress(ImportError):
            importlib.import_module(models_module)

    def _register_model(self, model: type) -> None:
        module = model.__module__
        for feature in self._features.values():
            if module == feature.import_name or module.startswith(feature.import_name + '.'):
                self._all_models.setdefault(feature.name, {})[model.__name__.lower()] = model
                feature.models[model.__name__.lower()] = model
                return

        raise RuntimeError(
            f"Model '{model.__qualname__}' (module: '{module}') does not belong to any installed feature."
        )

    def _assert_features_ready(self) -> None:
        if not self.features_ready:
            raise RuntimeError('Features have not been loaded yet.')

    def _assert_models_ready(self) -> None:
        if not self.models_ready:
            raise RuntimeError('Models have not been loaded yet.')

    def get_feature(self, name: str) -> Feature:
        self._assert_features_ready()
        try:
            return self._features[name]
        except KeyError:
            raise LookupError(f"No installed feature named '{name}'.") from None

    def get_features(self) -> Iterator[Feature]:
        self._assert_features_ready()
        yield from self._features.values()

    def get_model(self, feature_name: str, model_name: str) -> type:
        self._assert_models_ready()
        return self.get_feature(feature_name).get_model(model_name)

    def get_models(self) -> Iterator[type]:
        self._assert_models_ready()
        for feature in self._features.values():
            yield from feature.get_models()

    def is_installed(self, feature_name: str) -> bool:
        self._assert_features_ready()
        return feature_name in self._features

    def __repr__(self) -> str:
        names = list(self._features)
        return f'<FeatureRegistry features={names}>'
