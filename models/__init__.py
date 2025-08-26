# Importa os MÓDULOS, não as classes.
# Isso já registra as tabelas no Base.metadata via as classes declaradas neles.

from . import user
from . import patient
from . import appointment

# Alguns projetos chamam o arquivo de record.py, outros de records.py, ou medical_record.py.
# Tente importar o(s) que existir(em) sem quebrar:
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
