import csv  # Módulo estándar para CSV en Python
from typing import Dict  # Para tipado de diccionarios 
from models import MenuItem, Alumno, Profesor, Administrativo, Orden  # Importar clases de modelos definidas en models.py 

def cargar_menu(ruta: str) -> Dict[str, MenuItem]:   #  Ruta al archivo CSV del menú 
    """Lee el CSV del menú y devuelve dict por clave de platillo."""
    menu: Dict[str, MenuItem] = {} # Diccionario para almacenar ítems del menú 
    # newline='' evita problemas de salto de línea en diferentes SO
    with open(ruta, newline='', encoding='utf-8') as f:
        archivo = csv.DictReader(f)  # Acceso por nombres de columnas 
        for fila in archivo:  # Iterar filas del CSV
            menu[fila["clave"]] = MenuItem(  # Crear instancia MenuItem
                clave=fila["clave"].strip(),   # Limpieza de espacios
                nombre=fila["nombre"].strip(), # Limpieza de espacios
                precio=float(fila["precio"])   # Conversión a float
            )
    return menu  # Devolver diccionario de ítems del menú

def cargar_alumnos(ruta: str) -> Dict[str, Alumno]:   #  Ruta al archivo CSV de alumnos 
    """Carga alumnos desde CSV indexando por matrícula."""
    alumnos: Dict[str, Alumno] = {}  
    with open(ruta, newline='', encoding='utf-8') as f:  # Abrir archivo CSV
        archivo = csv.DictReader(f)
        for r in archivo:
            alumnos[r["matricula"]] = Alumno(
                matricula=r["matricula"].strip(),
                nombre=r["nombre"].strip(),
                carrera=r["carrera"].strip(),
                fecha_nacimiento=r["fecha_nacimiento"].strip(),
                credito_disponible=float(r["credito_disponible"])
            )
    return alumnos

def cargar_profesores(ruta: str) -> Dict[str, Profesor]:
    """Carga profesores desde CSV indexando por número de empleado."""
    profes: Dict[str, Profesor] = {}
    with open(ruta, newline='', encoding='utf-8') as f:
        archivo = csv.DictReader(f)
        for r in archivo:
            profes[r["numero_empleado"]] = Profesor(
                numero_empleado=r["numero_empleado"].strip(),
                nombre=r["nombre"].strip(),
                turno=r["turno"].strip(),
                estudio_profesional=r["estudio_profesional"].strip()
            )
    return profes

def cargar_administrativos(ruta: str) -> Dict[str, Administrativo]:
    """Carga administrativos desde CSV indexando por número de empleado."""
    advo: Dict[str, Administrativo] = {}
    with open(ruta, newline='', encoding='utf-8') as f:
        archivo = csv.DictReader(f)
        for r in archivo:
            advo[r["numero_empleado"]] = Administrativo(
                numero_empleado=r["numero_empleado"].strip(),
                nombre=r["nombre"].strip(),
                puesto=r["puesto"].strip()
            )
    return advo

def guardar_orden(ruta: str, orden: Orden, append: bool = True) -> None:
    """
    Guarda la orden en un CSV.
    - Si el archivo está vacío, escribe encabezados.
    - Serializa items como 'A01:2|B01:1' en una sola celda.
    """
    modo = 'a' if append else 'w'  # 'a' agrega al final; 'w' sobrescribe
    with open(ruta, modo, newline='', encoding='utf-8') as f:
        campos = [
            "id_orden", "cliente_tipo", "cliente_id", "items",
            "fecha_solicitud", "hora_solicitud", "forma_pago",
            "total", "tiempo_estimado_min", "entrega", "aula", "hora_estimada_entrega"
        ]
        writer = csv.DictWriter(f, fieldnames=campos)
        if f.tell() == 0:           # f.tell()==0 ⇒ archivo recién creado o vacío
            writer.writeheader()

        elementos_str = "|".join([f"{i.clave_item}:{i.cantidad}" for i in orden.items])
        writer.writerow({
            "id_orden": orden.id_orden,
            "cliente_tipo": orden.cliente_tipo.value,     # .value del Enum
            "cliente_id": orden.cliente_id,
            "items": elementos_str,
            "fecha_solicitud": orden.fecha_solicitud,
            "hora_solicitud": orden.hora_solicitud,
            "forma_pago": orden.forma_pago.value,
            "total": "{:.2f}".format(orden.total),        # 2 decimales
            "tiempo_estimado_min": orden.tiempo_estimado_min,
            "entrega": orden.entrega.value,
            "aula": orden.aula or "",                     # vacío si None
            "hora_estimada_entrega": orden.hora_estimada_entrega
        })