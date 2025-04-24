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
    return order


@app.post("/simulation/start/", response_model=SimulationState)
async def start_simulation(config: SimulationConfig):
    global simulation_config, simulation_state

    simulation_config = config
    simulation_state = SimulationState(
        current_date=date.today(),
        inventory=[],
        pending_orders=[],
        pending_purchases=[],
        production_history=[],
        purchase_history=[]
    )

    # Initialize inventory with config values
    for product_id, qty in config.initial_inventory.items():
        simulation_state.inventory.append(InventoryItem(product_id=product_id, qty=qty))

    return simulation_state


@app.post("/simulation/advance-day/", response_model=SimulationState)
async def advance_day():
    if not simulation_state:
        raise HTTPException(status_code=400, detail="Simulation not started")

    # Advance the date
    simulation_state.current_date += timedelta(days=1)

    # Generate new orders
    num_orders = random.randint(simulation_config.daily_order_min, simulation_config.daily_order_max)
    # Logic for generating orders would go here

    # Process pending purchase orders
    for po in simulation_state.pending_purchases:
        if po.estimated_delivery <= simulation_state.current_date:
            po.status = "received"
            # Update inventory
            for item in simulation_state.inventory:
                if item.product_id == po.product_id:
                    item.qty += po.quantity
                    break
            else:
                simulation_state.inventory.append(InventoryItem(product_id=po.product_id, qty=po.quantity))

            # Move to history
            simulation_state.purchase_history.append(po)
            simulation_state.pending_purchases.remove(po)

    # Process manufacturing orders
    # Logic for processing manufacturing orders would go here

    return simulation_state


@app.get("/simulation/export/", response_model=dict)
async def export_simulation():
    if not simulation_state:
        raise HTTPException(status_code=400, detail="Simulation not started")

    return {
        "config": simulation_config.dict(),
        "state": simulation_state.dict(),
        "products": [p.dict() for p in products],
        "suppliers": [s.dict() for s in suppliers],
        "bill_of_materials": [bom.dict() for bom in bill_of_materials]
    }


@app.post("/simulation/import/")
async def import_simulation(data: dict):
    global simulation_config, simulation_state, products, suppliers, bill_of_materials

    simulation_config = SimulationConfig(**data["config"])
    simulation_state = SimulationState(**data["state"])
    products = [Product(**p) for p in data["products"]]
    suppliers = [Supplier(**s) for s in data["suppliers"]]
    bill_of_materials = [BillOfMaterials(**bom) for bom in data["bill_of_materials"]]

    return {"message": "Simulation imported successfully"}
