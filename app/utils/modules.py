from importlib.util import find_spec


def module_has_submodule(package, module_name):
    try:
        package_path = package.__path__
        package_name = package.__name__
    except AttributeError:
        return False

    full_name = f'{package_name}.{module_name}'

    try:
        return find_spec(full_name, package_path) is not None
    except ModuleNotFoundError:
        return False
