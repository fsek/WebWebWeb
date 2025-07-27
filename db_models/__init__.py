# db_models/__init__.py

import pkgutil
import importlib

# Walk this package’s directory for modules
for finder, module_name, is_pkg in pkgutil.iter_modules(__path__):
    # Skip any private or unintended modules
    if module_name.startswith("_"):
        continue

    # Dynamically import db_models.<module_name>
    module = importlib.import_module(f"{__name__}.{module_name}")

    # Pull every class ending in "_DB" into the package namespace
    for attr_name in dir(module):
        if not attr_name.endswith("_DB"):
            continue
        globals()[attr_name] = getattr(module, attr_name)

# Now auto‑build __all__ from those names
__all__ = [name for name in globals() if name.endswith("_DB")]  # type: ignore[reportUnsupportedDunderAll]
