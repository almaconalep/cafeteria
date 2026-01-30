import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from models import TipoCliente, FormaPago, TipoEntrega
from io_utils import cargar_menu, cargar_alumnos, cargar_profesores, cargar_administrativos, guardar_orden
from services import CafeteriaService

# tests/demo.py



DATA = Path(__file__).resolve().parents[1] / "data"
svc = CafeteriaService(
    cargar_menu(str(DATA / "menu.csv")),
    cargar_alumnos(str(DATA / "alumnos.csv")),
    cargar_profesores(str(DATA / "profesores.csv")),
    cargar_administrativos(str(DATA / "administrativos.csv"))
)

# Orden: Alumno 2023001, A01 x2, B01 x1, crédito, entrega en aula B-203.
orden = svc.crear_orden(
    cliente_tipo=TipoCliente.ALUMNO,
    cliente_id="2023001",
    items=[("A01", 2), ("B01", 1)],
    forma_pago=FormaPago.CREDITO,
    entrega=TipoEntrega.AULA,
    aula="B-203"
)

guardar_orden(str(DATA / "ordenes.csv"), orden)
print("OK:", orden.id_orden, orden.total, orden.hora_estimada_entrega)