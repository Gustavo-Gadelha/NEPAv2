from collections import Counter, defaultdict

from flask import Flask

from app.database import Base
from app.features import FeatureConfig


class FeatureRegistry:
    def __init__(self, app: Flask | None = None):
        self.features_configs = {}
        self.all_models = defaultdict(dict)

        self.features_ready = False
        self.models_ready = False
        self.ready = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        app.extensions['registry'] = self
        installed_features = app.config.get('INSTALLED_FEATURES', [])
        self.populate(installed_features)

    def populate(self, installed_features: list[str]):
        if self.ready:
            return

        for entry in installed_features:
            feature_config = FeatureConfig.create(entry)

            if feature_config.label in self.features_configs:
                raise RuntimeError(f"Application labels aren't unique, duplicates: {feature_config.label}")

            self.features_configs[feature_config.label] = feature_config
            feature_config.features = self

        counts = Counter(feature_config.name for feature_config in self.features_configs.values())
        duplicates = [name for name, count in counts.most_common() if count > 1]
        if duplicates:
            raise RuntimeError(f"Application names aren't unique, duplicates: {', '.join(duplicates)}")

        self.features_ready = True

        for feature_config in self.features_configs.values():
            feature_config.import_models()

        for mapper in Base.registry.mappers:
            self.register_model(mapper.class_)

        self.models_ready = True

        for feature_config in self.get_feature_configs():
            feature_config.ready()

        self.ready = True

    def check_features_ready(self):
        if not self.features_ready:
            raise RuntimeError("Apps aren't loaded yet.")

    def check_models_ready(self):
        if not self.models_ready:
            raise RuntimeError("Models aren't loaded yet.")

    def get_feature_configs(self):
        self.check_features_ready()
        return self.features_configs.values()

    def get_feature_config(self, feature_label):
        self.check_features_ready()
        try:
            return self.features_configs[feature_label]
        except KeyError as e:
            raise LookupError(f"No installed feature with label '{feature_label}'.") from e

    def get_models(self):
        self.check_models_ready()

        result = []
        for feature_config in self.features_configs.values():
            result.extend(feature_config.get_models())

        return result

    def get_model(self, feature_label, model_name=None, require_ready=True):
        if require_ready:
            self.check_models_ready()
        else:
            self.check_features_ready()

        if model_name is None:
            feature_label, model_name = feature_label.split('.')

        feature_config = self.get_feature_config(feature_label)

        if not require_ready and feature_config.models is None:
            feature_config.import_models()

        return feature_config.get_model(model_name, require_ready=require_ready)

    def register_model(self, model):
        module_name = model.__module__

        for config in self.features_configs.values():
            if module_name.startswith(config.name):
                model_name = model.__name__.lower()

                self.all_models[config.label][model_name] = model
                return

        raise RuntimeError(f"Model '{model.__qualname__}' is not inside an installed feature.")

    def is_installed(self, feature_name):
        self.check_features_ready()
        return any(config.name == feature_name for config in self.features_configs.values())
