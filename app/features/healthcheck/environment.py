from app.extensions import registry


def installed_features():
    return [
        {
            feature.name: {
                'name': feature.name,
                'verbose_name': feature.verbose_name,
                'models_module': feature.models_module,
                'import_name': feature.import_name,
                'root_path': feature.root_path,
            }
        }
        for feature in registry.get_features()
    ]
