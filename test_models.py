import unittest
from datetime import date, timedelta
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

class TestModels(unittest.TestCase):
    def test_product_model(self):
        # Test creating a raw material product
        raw_product = Product(id=1, name="Plastic Filament", type="raw")
        self.assertEqual(raw_product.id, 1)
        self.assertEqual(raw_product.name, "Plastic Filament")
        self.assertEqual(raw_product.type, "raw")
        
        # Test creating a finished product
        finished_product = Product(id=2, name="3D Printer Model X", type="finished")
        self.assertEqual(finished_product.id, 2)
        self.assertEqual(finished_product.name, "3D Printer Model X")
        self.assertEqual(finished_product.type, "finished")
    
    def test_inventory_item_model(self):
        inventory_item = InventoryItem(product_id=1, qty=100)
        self.assertEqual(inventory_item.product_id, 1)
        self.assertEqual(inventory_item.qty, 100)
    
    def test_supplier_model(self):
        supplier = Supplier(id=1, product_id=1, unit_cost=10.5, lead_time=3)
        self.assertEqual(supplier.id, 1)
        self.assertEqual(supplier.product_id, 1)
        self.assertEqual(supplier.unit_cost, 10.5)
        self.assertEqual(supplier.lead_time, 3)
    
    def test_purchase_order_model(self):
        today = date.today()
        purchase_order = PurchaseOrder(
            id=1,
            supplier_id=1,
            product_id=1,
            quantity=50,
            issue_date=today,
            estimated_delivery=today + timedelta(days=3),
            status="pending"
        )
        self.assertEqual(purchase_order.id, 1)
        self.assertEqual(purchase_order.supplier_id, 1)
        self.assertEqual(purchase_order.product_id, 1)
        self.assertEqual(purchase_order.quantity, 50)
        self.assertEqual(purchase_order.issue_date, today)
        self.assertEqual(purchase_order.estimated_delivery, today + timedelta(days=3))
        self.assertEqual(purchase_order.status, "pending")
    
    def test_manufacturing_order_model(self):
        today = date.today()
        manufacturing_order = ManufacturingOrder(
            id=1,
            created_at=today,
            product_id=2,
            quantity=10,
            status="pending"
        )
        self.assertEqual(manufacturing_order.id, 1)
        self.assertEqual(manufacturing_order.created_at, today)
        self.assertEqual(manufacturing_order.product_id, 2)
        self.assertEqual(manufacturing_order.quantity, 10)
        self.assertEqual(manufacturing_order.status, "pending")
    
    def test_bill_of_materials_model(self):
        bom = BillOfMaterials(
            finished_product_id=2,
            raw_material_id=1,
            quantity_needed=5
        )
        self.assertEqual(bom.finished_product_id, 2)
        self.assertEqual(bom.raw_material_id, 1)
        self.assertEqual(bom.quantity_needed, 5)
    
    def test_production_capacity_model(self):
        today = date.today()
        capacity = ProductionCapacity(
            date=today,
            max_units=20,
            used_units=5
        )
        self.assertEqual(capacity.date, today)
        self.assertEqual(capacity.max_units, 20)
        self.assertEqual(capacity.used_units, 5)
    
    def test_simulation_config_model(self):
        config = SimulationConfig(
            daily_order_min=5,
            daily_order_max=15,
            initial_inventory={1: 100, 2: 20},
            simulation_days=30
        )
        self.assertEqual(config.daily_order_min, 5)
        self.assertEqual(config.daily_order_max, 15)
        self.assertEqual(config.initial_inventory, {1: 100, 2: 20})
        self.assertEqual(config.simulation_days, 30)
    
    def test_simulation_state_model(self):
        today = date.today()
        inventory = [InventoryItem(product_id=1, qty=100)]
        pending_orders = [
            ManufacturingOrder(
                id=1,
                created_at=today,
                product_id=2,
                quantity=10,
                status="pending"
            )
        ]
        pending_purchases = [
            PurchaseOrder(
                id=1,
                supplier_id=1,
                product_id=1,
                quantity=50,
                issue_date=today,
                estimated_delivery=today + timedelta(days=3),
                status="pending"
            )
        ]
        
        state = SimulationState(
            current_date=today,
            inventory=inventory,
            pending_orders=pending_orders,
            pending_purchases=pending_purchases,
            production_history=[],
            purchase_history=[]
        )
        
        self.assertEqual(state.current_date, today)
        self.assertEqual(len(state.inventory), 1)
        self.assertEqual(state.inventory[0].product_id, 1)
        self.assertEqual(state.inventory[0].qty, 100)
        self.assertEqual(len(state.pending_orders), 1)
        self.assertEqual(state.pending_orders[0].id, 1)
        self.assertEqual(len(state.pending_purchases), 1)
        self.assertEqual(state.pending_purchases[0].id, 1)
        self.assertEqual(len(state.production_history), 0)
        self.assertEqual(len(state.purchase_history), 0)

if __name__ == "__main__":
    unittest.main()