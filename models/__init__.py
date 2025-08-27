# models/__init__.py

from . import user
from . import patient
from . import appointment
from . import item, stock_movement


try:
    from . import record
except ImportError:
    pass

try:
    from . import records
except ImportError:
    pass

try:
    from . import medical_record
except ImportError:
    pass
