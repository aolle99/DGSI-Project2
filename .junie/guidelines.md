## 📘 Documentación Técnica – Simulador de Producción de Impresoras 3D

### 1. Visión General

**Objetivo**  
Desarrollar una plataforma de simulación que modele la producción diaria de una planta de impresoras 3D, centrada en la gestión de inventarios, compras y planificación.

**Usuarios objetivo**  
Estudiantes o desarrolladores que actuarán como planificadores de producción, tomando decisiones sobre compras y fabricación.

---

### 2. Requisitos del Sistema

#### 2.1 Requisitos Funcionales

- Generación de pedidos de fabricación diarios con parámetros configurables.
- Visualización del tablero de control (pedidos, inventario, BOM).
- Liberación de pedidos a producción.
- Emisión de órdenes de compra (producto, proveedor, cantidad, fecha).
- Simulación de eventos (producción, llegadas de compra).
- Avance del calendario (botón “Avanzar día”).
- Registro de eventos históricos y exportación/importación en formato JSON.
- API REST documentada con Swagger/OpenAPI para todas las funciones.

#### 2.2 Requisitos No Funcionales

- Código claro y comentado.
- Uso de control de versiones (Git + GitHub).
- Interfaz web accesible sin instalación local.
- Compatible con Windows, macOS y Linux.

---

### 3. Arquitectura del Sistema

#### 3.1 Tecnologías Utilizadas

| Capa        | Herramienta             | Justificación                              |
|-------------|-------------------------|---------------------------------------------|
| Lenguaje    | Python 3.11/3.12        | Popular, legible, gran ecosistema.          |
| Simulación  | SimPy                   | Simulación discreta eficiente.              |
| API         | FastAPI + Pydantic      | Rápida, moderna, validación integrada.      |
| Interfaz    | Streamlit               | Dashboards rápidos, ideal para prototipos.  |
| Datos       | SQLite y/o JSON         | Simples, portables.                         |
| Gráficas    | Matplotlib              | Integración directa en Streamlit.           |
| Versionado  | Git + GitHub            | Flujo de trabajo estándar.                  |

#### 3.2 Arquitectura
- Divide las funcionalidades
- Sigue patrones de diseño para poder estructurar el fichero adecuadamente
- Crea diagramas en el readme de la jerarquía de carpetas
- Usa clean code para organizar y reaprovechar el codigo.

---

### 4. Modelo de Datos

#### 4.1 Estructuras Clave

```python
class Product(BaseModel):
    id: int
    name: str
    type: Literal["raw", "finished"]

class InventoryItem(BaseModel):
    product_id: int
    qty: int

class Supplier(BaseModel):
    id: int
    product_id: int
    unit_cost: float
    lead_time: int

class PurchaseOrder(BaseModel):
    id: int
    supplier_id: int
    product_id: int
    quantity: int
    issue_date: date
    estimated_delivery: date
    status: Literal["pending", "received"]

class ManufacturingOrder(BaseModel):
    id: int
    created_at: date
    product_id: int
    quantity: int
    status: Literal["pending", "in_progress", "completed"]
```

---

### 5. Flujo de Trabajo Diario

1. Se generan nuevos pedidos al comenzar el día.
2. El usuario analiza inventario y decide qué producir y qué comprar.
3. SimPy simula producción y llegada de materiales.
4. Se actualiza el inventario y se registran eventos.
5. El usuario avanza al siguiente día.

---

### 6. Interfaz de Usuario (UI)

- **Panel de Control**: vista general del día simulado.
- **Pedidos**: tabla con pedidos pendientes y BOM.
- **Inventario**: niveles actuales, faltantes.
- **Compras**: formulario de emisión de órdenes.
- **Producción**: pedidos en cola, capacidad diaria.
- **Gráficas**: evolución de inventario y pedidos.

---

### 7. API RESTful

Todas las funcionalidades accesibles por interfaz también deben estar disponibles vía API REST. Documentación con Swagger/OpenAPI.

---

### 8. Pruebas y Escenario de Ejemplo

**Día 1:**  
Stock inicial de 30 kits. Se crean pedidos de 8 y 6 unidades. Se libera uno.

**Día 2:**  
Se generan nuevos pedidos. Se decide realizar una compra de 20 kits con lead time de 3 días.

---

### 9. Entregables

- Código fuente con README.
- Instrucciones de instalación y uso.
- Informe técnico (3–5 páginas).
- Presentación (máx. 10 diapositivas).
- Documentación de la API.
- Ejemplos de escenarios.

---

¿Quieres que lo convierta a formato Markdown, HTML o algún otro (como PDF para JetBrains Space o Confluence)? También puedo ayudarte a generar el Swagger completo si me das más detalles del diseño de la API.