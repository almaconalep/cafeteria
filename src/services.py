from datetime import datetime            # Para timestamp e IDs
from typing import Dict, List, Tuple     # Tipos para claridad y validación de datos 
from models import (                     # Importa modelos de datos 
    MenuItem, Alumno, Profesor, Administrativo, Cliente, TipoCliente,
    Orden, OrdenItem, FormaPago, TipoEntrega
)

class CafeteriaService:   # Servicio principal de la cafetería 
    """Orquesta validaciones, cálculos y construcción de órdenes."""

    def _init_(self, menu: Dict[str, MenuItem], alumnos: Dict[str, Alumno], profesores: Dict[str, Profesor], administrativos: Dict[str, Administrativo]):   # Inicializa con catálogos de datos
        # Inyección de catálogos (desacopla E/S de la lógica)
        self.menu = menu
        self.alumnos = alumnos
        self.profesores = profesores
        self.administrativos = administrativos

    # ---------- Consultas ----------
    def listar_menu(self) -> List[MenuItem]:   # Devuelve lista de platillos/bebidas.
        """Devuelve lista de platillos/bebidas."""
        return list(self.menu.values())

    def buscar_cliente(self, tipo: TipoCliente, id_publico: str) -> Cliente | None:  # Busca cliente por tipo e ID.
        """Localiza un cliente por tipo e identificador (matrícula/empleado)."""
        if tipo == TipoCliente.ALUMNO:
            return self.alumnos.get(id_publico)
        if tipo == TipoCliente.PROFESOR:
            return self.profesores.get(id_publico)
        if tipo == TipoCliente.ADMINISTRATIVO:
            return self.administrativos.get(id_publico)
        return None

    # ---------- Reglas ----------
    def calcular_total(self, items: List[OrdenItem]) -> float:    # Calcula total de la orden.
        """Suma precio × cantidad; valida existencia de claves del menú."""
        total = 0.0
        for it in items:
            if it.clave_item not in self.menu:
                raise ValueError(f"Clave de menú inexistente: {it.clave_item}")
            total += self.menu[it.clave_item].precio * it.cantidad
        return round(total, 2)

    def estimar_tiempo(self, items: List[OrdenItem]) -> int:   # Estima tiempo de preparación.
        """Regla simple: 5 min base + 3 min por unidad total solicitada."""
        unidades = sum(i.cantidad for i in items)   # Total de unidades en la orden
        return 5 + 3 * max(unidades, 1)     # Tiempo mínimo de 5 minutos 

    def validar_pago(self, cliente: Cliente, forma_pago: FormaPago, total: float) -> None:     # Valida método de pago.
        """Verifica crédito/alineación cliente-método (crédito sólo alumnos)."""
        if forma_pago == FormaPago.CREDITO:
            if cliente.tipo != TipoCliente.ALUMNO:
                raise ValueError("El pago con crédito solo aplica a alumnos.")
            assert isinstance(cliente, Alumno)
            if cliente.credito_disponible < total:
                raise ValueError("Crédito insuficiente del alumno.")

    def aplicar_pago(self, cliente: Cliente, forma_pago: FormaPago, total: float) -> None:  # Aplica el pago.
        """Descuenta del crédito del alumno si aplica."""
        if forma_pago == FormaPago.CREDITO and isinstance(cliente, Alumno):   # Solo alumnos tienen crédito 
            cliente.credito_disponible = round(cliente.credito_disponible - total, 2)

    def crear_orden(self, cliente_tipo: TipoCliente, cliente_id: str, items: List[Tuple[str, int]], forma_pago: FormaPago, entrega: TipoEntrega, aula: str | None = None) -> Orden:  # Crea una orden completa.
        """
        Orquesta el flujo: valida insumos, calcula total, estima tiempos,
        genera ID y retorna la Orden lista para persistir.
        """
        if not items:
            raise ValueError("La orden debe contener al menos un artículo.")
        if entrega == TipoEntrega.AULA and not aula:
             raise ValueError("Debe especificar el aula para entrega en aula.")

        cliente = self.buscar_cliente(cliente_tipo, cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado.")

        # Normaliza y filtra cantidades válidas (>0)
        orden_items = [OrdenItem(clave_item=c, cantidad=int(q)) for c, q in items if int(q) > 0]

        total = self.calcular_total(orden_items)
        self.validar_pago(cliente, forma_pago, total)

        ahora = datetime.now()  # Timestamp actual
        tiempo_est = self.estimar_tiempo(orden_items)
        id_orden = f"ORD-{ahora.strftime('%Y%m%d%H%M%S')}-{cliente_id}"  # ID legible y único

        self.aplicar_pago(cliente, forma_pago, total)

        return Orden(       # Construye y retorna la orden completa 
            id_orden=id_orden,
            cliente_tipo=cliente_tipo,
            cliente_id=cliente_id,
            items=orden_items,
            fecha_solicitud=ahora.strftime("%Y-%m-%d"),
            hora_solicitud=ahora.strftime("%H:%M"),
            forma_pago=forma_pago,
            total=total,
            tiempo_estimado_min=tiempo_est,
            entrega=entrega,
            aula=aula
        )