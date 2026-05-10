from app.database import Base
from app.extensions import features


def get_model(identifier: str, require_ready: bool = True):
    if require_ready:
        features.check_models_ready()

    if '.' in identifier:
        feature_label, model_name = identifier.split('.', 1)
        model_name = model_name.lower()
        return features.get_model(feature_label, model_name)

    model_name = identifier.lower()

    matches = []

    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if not hasattr(cls, '__table__'):
            continue

        if cls.__name__.lower() == model_name:
            matches.append(cls)

    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise LookupError(f"No model found matching '{identifier}'.")

    raise LookupError(
        f"Ambiguous model name '{identifier}'. Matches: {[m.__module__ + '.' + m.__name__ for m in matches]}"
    )
