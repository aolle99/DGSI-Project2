from fastapi import FastAPI, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, timedelta
import random
import json
from models import (
    Product, 
    InventoryItem, 
    Supplier, 
    PurchaseOrder, 
    ManufacturingOrder,
    BillOfMaterials,
    ProductionCapacity,
    SimulationConfig,
    SimulationState
)
from simulation import ProductionSimulator

app = FastAPI(
    title="3D Printer Production Simulator",
    description="A simulation platform for 3D printer production management",
    version="1.0.0"
)

# In-memory storage for simulation data
# In a real application, this would be stored in a database
products = []
inventory = []
suppliers = []
purchase_orders = []
manufacturing_orders = []
bill_of_materials = []
production_capacity = []
simulation_config = SimulationConfig()
simulation_state = None
simulator = None  # SimPy simulator instance


@app.get("/")
async def root():
    return {
        "message": "3D Printer Production Simulator API",
        "documentation": "/docs",
        "current_date": simulation_state.current_date if simulation_state else "Simulation not started"
    }


@app.get("/products/", response_model=List[Product])
async def get_products():
    return products


@app.post("/products/", response_model=Product)
async def create_product(product: Product):
    for p in products:
        if p.id == product.id:
            raise HTTPException(status_code=400, detail="Product ID already exists")
    products.append(product)
    return product


@app.get("/inventory/", response_model=List[InventoryItem])
async def get_inventory():
    return inventory


@app.post("/inventory/", response_model=InventoryItem)
async def update_inventory(item: InventoryItem):
    for i, inv_item in enumerate(inventory):
        if inv_item.product_id == item.product_id:
            inventory[i] = item
            return item
    inventory.append(item)
    return item


@app.get("/suppliers/", response_model=List[Supplier])
async def get_suppliers():
    return suppliers


@app.post("/suppliers/", response_model=Supplier)
async def create_supplier(supplier: Supplier):
    for s in suppliers:
        if s.id == supplier.id:
            raise HTTPException(status_code=400, detail="Supplier ID already exists")
    suppliers.append(supplier)
    return supplier


@app.get("/purchase-orders/", response_model=List[PurchaseOrder])
async def get_purchase_orders(status: Optional[str] = None):
    if status:
        return [po for po in purchase_orders if po.status == status]
    return purchase_orders


@app.post("/purchase-orders/", response_model=PurchaseOrder)
async def create_purchase_order(order: PurchaseOrder):
    for po in purchase_orders:
        if po.id == order.id:
            raise HTTPException(status_code=400, detail="Purchase Order ID already exists")

    # Find the supplier to get the lead time
    supplier = next((s for s in suppliers if s.id == order.supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Calculate estimated delivery date
    order.estimated_delivery = order.issue_date + timedelta(days=supplier.lead_time)

    purchase_orders.append(order)

    # Add the order to the simulator if it's running
    if simulator:
        simulator.create_purchase_order(order)

    return order


@app.get("/manufacturing-orders/", response_model=List[ManufacturingOrder])
async def get_manufacturing_orders(status: Optional[str] = None):
    if status:
        return [mo for mo in manufacturing_orders if mo.status == status]
    return manufacturing_orders


@app.post("/manufacturing-orders/", response_model=ManufacturingOrder)
async def create_manufacturing_order(order: ManufacturingOrder):
    for mo in manufacturing_orders:
        if mo.id == order.id:
            raise HTTPException(status_code=400, detail="Manufacturing Order ID already exists")
    manufacturing_orders.append(order)

    # Add the order to the simulator if it's running
    if simulator:
        simulator.create_manufacturing_order(order)

    return order


@app.get("/bill-of-materials/", response_model=List[BillOfMaterials])
async def get_bill_of_materials(finished_product_id: Optional[int] = None):
    if finished_product_id:
        return [bom for bom in bill_of_materials if bom.finished_product_id == finished_product_id]
    return bill_of_materials


@app.post("/bill-of-materials/", response_model=BillOfMaterials)
async def create_bill_of_materials(bom: BillOfMaterials):
    # Check if this BOM entry already exists
    for existing_bom in bill_of_materials:
        if (existing_bom.finished_product_id == bom.finished_product_id and 
            existing_bom.raw_material_id == bom.raw_material_id):
            raise HTTPException(
                status_code=400, 
                detail="BOM entry for this finished product and raw material already exists"
            )

    bill_of_materials.append(bom)
    return bom


@app.post("/simulation/start/", response_model=SimulationState)
async def start_simulation(config: SimulationConfig):
    global simulation_config, simulation_state, simulator

    simulation_config = config

    # Initialize the SimPy simulator
    simulator = ProductionSimulator(config)

    # Pass the bill of materials and suppliers to the simulator
    simulator.bill_of_materials = bill_of_materials
    simulator.suppliers = suppliers

    simulation_state = simulator.state

    return simulation_state


@app.post("/simulation/advance-day/", response_model=SimulationState)
async def advance_day():
    global simulation_state

    if not simulator:
        raise HTTPException(status_code=400, detail="Simulation not started")

    # Use the SimPy simulator to advance the simulation by one day
    simulation_state = simulator.run_day()

    return simulation_state


@app.get("/simulation/export/", response_model=dict)
async def export_simulation():
    if not simulator:
        raise HTTPException(status_code=400, detail="Simulation not started")

    return {
        "config": simulation_config.dict(),
        "state": simulation_state.dict(),
        "products": [p.dict() for p in products],
        "suppliers": [s.dict() for s in suppliers],
        "bill_of_materials": [bom.dict() for bom in bill_of_materials]
    }


@app.get("/simulation/purchase-suggestions/")
async def get_purchase_suggestions():
    if not simulator:
        raise HTTPException(status_code=400, detail="Simulation not started")

    # Get purchase suggestions from the simulator
    suggestions = simulator.suggest_purchases()

    return suggestions


@app.post("/simulation/import/")
async def import_simulation(data: dict):
    global simulation_config, simulation_state, products, suppliers, bill_of_materials, simulator

    simulation_config = SimulationConfig(**data["config"])
    simulation_state = SimulationState(**data["state"])
    products = [Product(**p) for p in data["products"]]
    suppliers = [Supplier(**s) for s in data["suppliers"]]
    bill_of_materials = [BillOfMaterials(**bom) for bom in data["bill_of_materials"]]

    # Initialize the simulator with the imported state
    simulator = ProductionSimulator(simulation_config, simulation_state)

    # Pass the bill of materials and suppliers to the simulator
    simulator.bill_of_materials = bill_of_materials
    simulator.suppliers = suppliers

    return {"message": "Simulation imported successfully"}
