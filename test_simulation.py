import unittest
from datetime import date, timedelta
from models import (
    Product,
    InventoryItem,
    Supplier,
    PurchaseOrder,
    ManufacturingOrder,
    BillOfMaterials,
    SimulationConfig,
    SimulationState
)
from simulation import ProductionSimulator

class TestSimulation(unittest.TestCase):
    def setUp(self):
        # Create a basic simulation configuration
        self.config = SimulationConfig(
            daily_order_min=1,
            daily_order_max=3,
            initial_inventory={1: 100, 2: 20},
            simulation_days=10
        )
        
        # Create a simulator
        self.simulator = ProductionSimulator(self.config)
    
    def test_initialization(self):
        """Test that the simulator initializes correctly."""
        # Check that the simulator has the correct configuration
        self.assertEqual(self.simulator.config.daily_order_min, 1)
        self.assertEqual(self.simulator.config.daily_order_max, 3)
        self.assertEqual(self.simulator.config.initial_inventory, {1: 100, 2: 20})
        
        # Check that the state is initialized correctly
        self.assertEqual(len(self.simulator.state.inventory), 2)
        self.assertEqual(self.simulator.state.inventory[0].product_id, 1)
        self.assertEqual(self.simulator.state.inventory[0].qty, 100)
        self.assertEqual(self.simulator.state.inventory[1].product_id, 2)
        self.assertEqual(self.simulator.state.inventory[1].qty, 20)
    
    def test_run_day(self):
        """Test that running the simulation for a day advances the date."""
        initial_date = self.simulator.state.current_date
        
        # Run the simulation for one day
        self.simulator.run_day()
        
        # Check that the date advanced by one day
        self.assertEqual(self.simulator.state.current_date, initial_date + timedelta(days=1))
    
    def test_purchase_order(self):
        """Test that purchase orders are processed correctly."""
        # Create a supplier
        supplier = Supplier(id=1, product_id=3, unit_cost=10.0, lead_time=2)
        
        # Create a purchase order for a product that's not in inventory
        today = date.today()
        po = PurchaseOrder(
            id=1,
            supplier_id=1,
            product_id=3,
            quantity=50,
            issue_date=today,
            estimated_delivery=today + timedelta(days=2),
            status="pending"
        )
        
        # Add the purchase order to the simulator
        self.simulator.create_purchase_order(po)
        
        # Check that the purchase order is in the pending purchases
        self.assertEqual(len(self.simulator.state.pending_purchases), 1)
        self.assertEqual(self.simulator.state.pending_purchases[0].id, 1)
        
        # Run the simulation for one day
        self.simulator.run_day()
        
        # Check that the purchase order is still pending
        self.assertEqual(len(self.simulator.state.pending_purchases), 1)
        
        # Run the simulation for another day
        self.simulator.run_day()
        
        # Check that the purchase order has been received and inventory updated
        self.assertEqual(len(self.simulator.state.pending_purchases), 0)
        self.assertEqual(len(self.simulator.state.purchase_history), 1)
        
        # Check that the product is now in inventory
        found = False
        for item in self.simulator.state.inventory:
            if item.product_id == 3:
                self.assertEqual(item.qty, 50)
                found = True
        self.assertTrue(found, "Product should be in inventory after purchase order is received")
    
    def test_manufacturing_order(self):
        """Test that manufacturing orders are added to the simulator."""
        # Create a manufacturing order
        today = date.today()
        mo = ManufacturingOrder(
            id=1,
            created_at=today,
            product_id=2,
            quantity=5,
            status="pending"
        )
        
        # Add the manufacturing order to the simulator
        self.simulator.create_manufacturing_order(mo)
        
        # Check that the manufacturing order is in the pending orders
        self.assertEqual(len(self.simulator.state.pending_orders), 1)
        self.assertEqual(self.simulator.state.pending_orders[0].id, 1)

if __name__ == "__main__":
    unittest.main()