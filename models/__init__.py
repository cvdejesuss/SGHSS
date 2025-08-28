# models/__init__.py
from . import user  # noqa: F401
from . import patient  # noqa: F401
from . import appointment  # noqa: F401
from . import item  # noqa: F401
from . import stock_movement  # noqa: F401

# Pacote pode ter variações de "record"
try:
    from . import record  # noqa: F401
except ImportError:
    pass

try:
    from . import records  # noqa: F401
except ImportError:
    pass

try:
    from . import medical_record  # noqa: F401
except ImportError:
    pass

