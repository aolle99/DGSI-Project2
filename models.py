from datetime import date
from typing import Literal
from pydantic import BaseModel

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

# Additional models that might be useful for the simulation

class BillOfMaterials(BaseModel):
    """Represents the components needed to build a finished product"""
    finished_product_id: int
    raw_material_id: int
    quantity_needed: int

class ProductionCapacity(BaseModel):
    """Represents the daily production capacity"""
    date: date
    max_units: int
    used_units: int = 0

class SimulationConfig(BaseModel):
    """Configuration parameters for the simulation"""
    daily_order_min: int = 5
    daily_order_max: int = 15
    initial_inventory: dict[int, int] = {}  # product_id: quantity
    simulation_days: int = 30

class SimulationState(BaseModel):
    """Current state of the simulation"""
    current_date: date
    inventory: list[InventoryItem]
    pending_orders: list[ManufacturingOrder]
    pending_purchases: list[PurchaseOrder]
    production_history: list[ManufacturingOrder]
    purchase_history: list[PurchaseOrder]