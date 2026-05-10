import inspect
from abc import ABCMeta, abstractmethod
from importlib import import_module

from app.utils.modules import module_has_submodule

CONF_MODULE_NAME = 'config'
MODELS_MODULE_NAME = 'models'


class FeatureConfig(metaclass=ABCMeta):
    labels = None
    name = None
    verbose_name = None

    def __init__(self, name, module):
        self.name = name
        self.module = module

        self.features = None

        if not hasattr(self, 'label'):
            self.label = name.rpartition('.')[2]

        if not self.label or not self.label.isidentifier():
            raise RuntimeError(f'The feature label "{self.label}" is not a valid Python identifier.')

        if not hasattr(self, 'verbose_name'):
            self.verbose_name = self.label.title()

        self.models = {}
        self.models_module = None

    @classmethod
    def create(cls, entry):
        feature_module = import_module(entry)

        conf_module_name = f'{entry}.{CONF_MODULE_NAME}'
        if not module_has_submodule(feature_module, CONF_MODULE_NAME):
            raise RuntimeError(f'"{entry}" does not define a {CONF_MODULE_NAME}.py module.')

        conf_module = import_module(conf_module_name)
        config_classes = [
            candidate
            for _, candidate in inspect.getmembers(conf_module, inspect.isclass)
            if issubclass(candidate, cls) and candidate is not cls
        ]

        if len(config_classes) != 1:
            raise RuntimeError(f'{conf_module_name!r} must define exactly one {cls.__name__} subclass.')

        config_class = config_classes[0]
        feature_name = config_class.name
        if not feature_name:
            raise RuntimeError(f'"{config_class.__qualname__}" must define a "name" attribute.')

        try:
            feature_module = import_module(feature_name)
        except ImportError as e:
            raise RuntimeError(f'Cannot import feature module "{feature_name}".') from e

        return config_class(feature_name, feature_module)

    def get_model(self, model_name, require_ready=True):
        if require_ready:
            self.features.check_models_ready()  # ty:ignore[unresolved-attribute]
        else:
            self.features.check_features_ready()  # ty:ignore[unresolved-attribute]
        try:
            return self.models[model_name.lower()]
        except KeyError as e:
            raise LookupError(f"App '{self.label}' doesn't have a '{model_name}' model.") from e

    def get_models(self):
        self.features.check_models_ready()  # ty:ignore[unresolved-attribute]
        yield from self.models.values()

    def import_models(self):
        self.models = self.features.all_models[self.label]  # ty:ignore[unresolved-attribute]

        if module_has_submodule(self.module, MODELS_MODULE_NAME):
            models_module_name = f'{self.name}.{MODELS_MODULE_NAME}'
            self.models_module = import_module(models_module_name)

    @abstractmethod
    def ready(self):
        pass
