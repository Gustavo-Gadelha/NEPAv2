from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from .registry import FeatureRegistry


class Feature(Blueprint):
    def __init__(
        self,
        name: str,
        import_name: str,
        *,
        verbose_name: str | None = None,
        models_module: str = 'models',
        **blueprint_kwargs,
    ) -> None:
        super().__init__(name, import_name, **blueprint_kwargs)
        self.verbose_name = verbose_name or name.replace('_', ' ').title()
        self.models_module = models_module
        self.models: dict[str, type] = {}
        self.registry: FeatureRegistry | None = None
        self.ready = False

        self._on_load_callbacks: list[Callable] = []

    def on_load(self, f: Callable) -> Callable:
        """
        Register a callback to run after all features and models are ready.

        Unlike Blueprint.record(), this runs once during registry population,
        not at app.register_blueprint() time, so all other features are
        guaranteed to be available.

            @feature.on_load
            def connect_signals():
                from other_feature import some_model  # safe here
        """
        self._on_load_callbacks.append(f)
        return f

    def load(self) -> None:
        if self.ready:
            return

        for callback in self._on_load_callbacks:
            callback()

        self.ready = True

    def get_model(self, name: str) -> type:
        try:
            return self.models[name.lower()]
        except KeyError:
            raise LookupError(f"Feature '{self.name}' has no registered model '{name}'.") from None

    def get_models(self) -> Iterator[type]:
        yield from self.models.values()

    def __repr__(self) -> str:
        return f"<Feature '{self.name}'>"
