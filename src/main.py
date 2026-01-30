from pathlib import Path  # Construcción de rutas portables
from models import TipoCliente, FormaPago, TipoEntrega  # Enums para entradas
from io_utils import (
    cargar_menu, cargar_alumnos, cargar_profesores, cargar_administrativos, guardar_orden
)  # E/S de CSV
from services import CafeteriaService  # Lógica de negocio

# Rutas a CSV relativos a /data
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RUTA_MENU = DATA_DIR / "menu.csv"
RUTA_ALUMNOS = DATA_DIR / "alumnos.csv"
RUTA_PROFES = DATA_DIR / "profesores.csv"
RUTA_ADMINS = DATA_DIR / "administrativos.csv"
RUTA_ORDENES = DATA_DIR / "ordenes.csv"

def seleccionar_cliente():
    """Solicita tipo de cliente y su identificador (matrícula/empleado)."""
    print("\nSeleccione tipo de cliente:")
    print("1) Alumno")
    print("2) Profesor")
    print("3) Administrativo")
    op = input("Opción: ").strip()
    mapping = {"1": TipoCliente.ALUMNO, "2": TipoCliente.PROFESOR, "3": TipoCliente.ADMINISTRATIVO}
    tipo = mapping.get(op)
    if not tipo:
        raise ValueError("Tipo de cliente inválido")
    id_publico = input("Ingrese matrícula (alumno) o número de empleado: ").strip()
    return tipo, id_publico

def seleccionar_items(service: CafeteriaService):
    """Muestra menú y captura ítems como pares <CLAVE> <CANTIDAD>."""
    print("\n--- Menú ---")
    for it in service.listar_menu():
        print(f"{it.clave} - {it.nombre} : ${it.precio:.2f}")
    print("Ingrese artículos (ej. A01 2). Deje vacío para terminar.")
    items = []
    while True:
        linea = input("> ").strip()
        if not linea:
            break
        partes = linea.split()
        if len(partes) != 2:
            print("Formato: <clave> <cantidad>")
            continue
        clave, cant = partes[0].upper(), partes[1]
        try:
            cantidad = int(cant)
            if cantidad <= 0:
                print("Cantidad debe ser positiva.")
                continue
            items.append((clave, cantidad))
        except ValueError:
            print("Cantidad inválida.")
    return items

def seleccionar_pago():
    """Elige forma de pago y valida la opción."""
    print("\nForma de pago:")
    print("1) Efectivo")
    print("2) Tarjeta")
    print("3) Crédito (solo alumnos)")
    op = input("Opción: ").strip()
    mapping = {"1": FormaPago.EFECTIVO, "2": FormaPago.TARJETA, "3": FormaPago.CREDITO}
    pago = mapping.get(op)
    if not pago:
        raise ValueError("Forma de pago inválida")
    return pago

def seleccionar_entrega():
    """Define entrega: en aula (requiere aula) o recoger en cafetería."""
    print("\nEntrega:")
    print("1) En aula")
    print("2) Recoger en cafetería")
    op = input("Opción: ").strip()
    if op == "1":
        aula = input("Aula (ej. B-203): ").strip()
        return TipoEntrega.AULA, aula
    elif op == "2":
        return TipoEntrega.CAFETERIA, None
    else:
        raise ValueError("Opción de entrega inválida")

def main():
    # Carga de catálogos desde CSV
    menu = cargar_menu(str(RUTA_MENU))
    alumnos = cargar_alumnos(str(RUTA_ALUMNOS))
    profesores = cargar_profesores(str(RUTA_PROFES))
    administrativos = cargar_administrativos(str(RUTA_ADMINS))

    # Inyección de datos a la capa de negocio
    service = CafeteriaService(menu, alumnos, profesores, administrativos)

    print("=== Sistema de Cafetería (Demo) ===")
    try:
        # Flujo de captura
        tipo_cli, id_cli = seleccionar_cliente()
        items = seleccionar_items(service)
        forma_pago = seleccionar_pago()
        entrega, aula = seleccionar_entrega()

        # Construir y validar la orden
        orden = service.crear_orden(
            cliente_tipo=tipo_cli,
            cliente_id=id_cli,
            items=items,
            forma_pago=forma_pago,
            entrega=entrega,
             aula=aula
        )

        # Persistir la orden en CSV
        guardar_orden(str(RUTA_ORDENES), orden, append=True)

        # Resumen de salida
        print("\nOrden registrada con éxito:")
        print(f"ID: {orden.id_orden}")
        print(f"Cliente: {orden.cliente_tipo.value} - {orden.cliente_id}")
        print("Items:")
        for it in orden.items:
            print(f" - {it.clave_item} x {it.cantidad}")
        print(f"Total: ${orden.total:.2f}")
        print(f"Entrega: {orden.entrega.value} | Aula: {orden.aula or '-'}")
        print(f"Tiempo estimado: {orden.tiempo_estimado_min} min (aprox. {orden.hora_estimada_entrega})")
        print(f"Forma de pago: {orden.forma_pago.value}")

    except Exception as e:
        # Manejo simple de errores para didáctica
        print(f"\nERROR: {e}")

if __name__ == "__main__":  # Punto de entrada del script 
     main()