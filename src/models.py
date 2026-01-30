from __future__ import annotations  # Permite referencias de tipos a clases definidas más abajo
from dataclasses import dataclass   # Facilita clases de datos sin _init_ manual
from datetime import datetime, timedelta  # Manejo de fechas/horas y sumas de tiempo
from enum import Enum               # Enumeraciones para valores controlados
from typing import List, Optional   # Tipos para listas y valores opcionales


class TipoCliente(Enum):
    """Enum: clasifica clientes y evita usar strings sueltos."""
    ALUMNO = "alumno"
    PROFESOR = "profesor"
    ADMINISTRATIVO = "administrativo"


class FormaPago(Enum):
    """Enum: lista de formas de pago válidas."""
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    CREDITO = "credito"  # Sólo alumnos


class TipoEntrega(Enum):
    """Enum: modalidad de entrega del pedido."""
    AULA = "aula"
    CAFETERIA = "cafeteria"  # Recoger en cafetería


@dataclass              # Genera un Constructor (_init) automáticamente: No necesitas escribir def __init_(self, ...):
class MenuItem:
    """Platillo o bebida del menú."""
    clave: str   # Clave única (ej. A01)
    nombre: str  # Nombre legible (ej. Sándwich)
    precio: float  # Precio unitario


@dataclass  ## Clase base: factor común para tipos de cliente.
class Cliente:
    """Clase base: factor común para tipos de cliente."""
    id_publico: str  # Matrícula (alumno) o núm. de empleado
    nombre: str
    tipo: TipoCliente  # Uno de TipoCliente


@dataclass   # Alumno hereda de Cliente e incluye carrera, fecha de nacimiento y crédito disponible.
class Alumno(Cliente):
    """Alumno con atributos y saldo de crédito."""
    carrera: str
    fecha_nacimiento: str  # YYYY-MM-DD
    credito_disponible: float
    """self. es una referencia a la instancia específica del objeto, 
        Sirve para asegurar que los datos del alumno (matricula, nombre, carrera, fecha, crédito) 
        e guarden dentro del objeto único que acabas de crear, y no en la clase en general."""
    def _init_(self, matricula: str, nombre: str, carrera: str, fecha_nacimiento: str, credito_disponible: float):
        # super(): inicializa los campos heredados de Cliente
        super()._init_(id_publico=matricula, nombre=nombre, tipo=TipoCliente.ALUMNO)
        self.carrera = carrera
        self.fecha_nacimiento = fecha_nacimiento
        self.credito_disponible = credito_disponible


@dataclass  # Profesor hereda de Cliente e incluye turno y grado profesional.
class Profesor(Cliente):
    """Profesor con turno y grado profesional."""
    turno: str
    estudio_profesional: str

    def _init_(self, numero_empleado: str, nombre: str, turno: str, estudio_profesional: str):
        super()._init_(id_publico=numero_empleado, nombre=nombre, tipo=TipoCliente.PROFESOR)
        self.turno = turno
        self.estudio_profesional = estudio_profesional


@dataclass   # Administrativo hereda de Cliente e incluye puesto.
class Administrativo(Cliente):
    """Administrativo con puesto."""
    puesto: str

    def _init_(self, numero_empleado: str, nombre: str, puesto: str):
        super()._init_(id_publico=numero_empleado, nombre=nombre, tipo=TipoCliente.ADMINISTRATIVO)
        self.puesto = puesto


@dataclass     # Ítem de una orden: clave de menú y cantidad.
class OrdenItem:
    """Ítem de una orden: clave de menú y cantidad."""
    clave_item: str
    cantidad: int


@dataclass    ## Orden completa: cliente, lista de ítems, totales y metadatos de tiempo.
class Orden:
    """Orden completa: cliente, lista de ítems, totales y metadatos de tiempo."""
    id_orden: str
    cliente_tipo: TipoCliente
    cliente_id: str
    items: List[OrdenItem]
    fecha_solicitud: str  # YYYY-MM-DD
    hora_solicitud: str   # HH:MM
    forma_pago: FormaPago
    total: float
    tiempo_estimado_min: int
    entrega: TipoEntrega
    aula: Optional[str] = None  # Requerido si entrega = AULA

    @property
    def timestamp(self) -> datetime:   # Propiedad calculada: no se almacena directamente
        """Convierte fecha+hora de la orden a datetime para cálculos."""
        return datetime.strptime(self.fecha_solicitud + " " + self.hora_solicitud, "%Y-%m-%d %H:%M")

    @property
    def hora_estimada_entrega(self) -> str:    # Propiedad calculada: no se almacena directamente
        """Calcula hora estimada sumando minutos al timestamp."""
        hora = self.timestamp + timedelta(minutes=self.tiempo_estimado_min)  
        return hora.strftime("%H:%M")     # Formatea de vuelta a string HH:MM