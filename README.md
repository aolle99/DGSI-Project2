# 3D Printer Production Simulator

A simulation platform for 3D printer production management, focusing on inventory management, purchasing, and planning.

## Overview

This project implements a simulation platform that models the daily production of a 3D printer manufacturing plant. It allows users to:

- Generate daily manufacturing orders
- Manage inventory of raw materials and finished products
- Create purchase orders for raw materials
- Simulate production and delivery of materials
- Track the history of production and purchases

## Data Model

The simulation is built around the following data models:

- **Product**: Represents raw materials or finished products
- **InventoryItem**: Tracks quantity of products in inventory
- **Supplier**: Information about suppliers for raw materials
- **PurchaseOrder**: Orders for raw materials from suppliers
- **ManufacturingOrder**: Production orders for finished products
- **BillOfMaterials**: Defines what raw materials are needed for each finished product
- **ProductionCapacity**: Tracks daily production capacity
- **SimulationConfig**: Configuration parameters for the simulation
- **SimulationState**: Tracks the current state of the simulation

## API Endpoints

The application provides a RESTful API with the following endpoints:

### Products
- `GET /products/`: Get all products
- `POST /products/`: Create a new product

### Inventory
- `GET /inventory/`: Get current inventory
- `POST /inventory/`: Update inventory item

### Suppliers
- `GET /suppliers/`: Get all suppliers
- `POST /suppliers/`: Create a new supplier

### Purchase Orders
- `GET /purchase-orders/`: Get all purchase orders
- `POST /purchase-orders/`: Create a new purchase order

### Manufacturing Orders
- `GET /manufacturing-orders/`: Get all manufacturing orders
- `POST /manufacturing-orders/`: Create a new manufacturing order

### Bill of Materials
- `GET /bill-of-materials/`: Get all BOM records or filter by finished product ID
- `POST /bill-of-materials/`: Create a new BOM record

### Simulation Control
- `POST /simulation/start/`: Start a new simulation
- `POST /simulation/advance-day/`: Advance the simulation by one day
- `GET /simulation/export/`: Export the current simulation state
- `POST /simulation/import/`: Import a simulation state
- `GET /simulation/purchase-suggestions/`: Get purchase suggestions based on material requirements

## Simulation Engine

The simulation is powered by SimPy, a process-based discrete-event simulation framework. The simulation engine:

- Models the production process as a series of discrete events
- Simulates the flow of materials through the production system
- Handles the timing of events such as order arrivals and material deliveries
- Manages resources such as production capacity
- Calculates material requirements based on Bill of Materials (BOM)
- Tracks inventory and suggests purchases when materials are low

The simulation engine is implemented in the `simulation.py` file, which defines the `ProductionSimulator` class. This class:

- Initializes the simulation environment and state
- Defines processes for daily operations, order generation, and material processing
- Provides methods to advance the simulation by one day
- Handles the creation and processing of purchase and manufacturing orders
- Calculates material requirements for manufacturing orders based on BOM
- Checks if materials are available in inventory before starting production
- Consumes materials from inventory when manufacturing orders are processed
- Suggests purchases based on material requirements for pending orders

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install fastapi uvicorn pydantic simpy streamlit pandas matplotlib plotly altair
   ```

## Running the Application

1. Start the API server:
   ```
   uvicorn main:app --reload
   ```
2. Access the API documentation at http://localhost:8000/docs

3. Start the Streamlit dashboard (in a separate terminal):
   ```
   streamlit run dashboard.py
   ```
4. Access the dashboard at http://localhost:8501

## Testing

Run the data model tests with:
```
python test_models.py
```

Run the simulation tests with:
```
python test_simulation.py
```

The simulation tests verify:
- Correct initialization of the simulator
- Proper advancement of the simulation date
- Processing of purchase orders
- Addition of manufacturing orders

## Daily Workflow

1. Start a new simulation with initial configuration
2. Define the Bill of Materials (BOM) for each finished product
3. Each day:
   - Review pending orders and inventory
   - Check material requirements for pending manufacturing orders
   - Review purchase suggestions based on material requirements
   - Create purchase orders for needed materials
   - Release manufacturing orders to production
   - Advance to the next day
4. Export the simulation state for later analysis

## Dashboard Interface

The dashboard provides a comprehensive view of the simulation with interactive visualizations and data management tools. The interface is divided into five main tabs:

### Overview Tab

- **Key Metrics**: Real-time display of pending orders, pending purchases, completed orders, and total inventory with trend indicators
- **Production Trends**: Interactive charts showing:
  - Inventory levels over time for raw materials and finished products
  - Daily order activity (manufacturing orders, purchase orders, completed production)
  - Production order status distribution (pending, in progress, completed)
- **Production Capacity**: Visual indicator of daily production capacity utilization

### Inventory Tab

- **Current Inventory**: Interactive table with color-coded status indicators (low, medium, high)
- **Inventory Visualization**: 
  - Bar chart showing inventory levels by product
  - Pie chart showing inventory distribution by product type
- **Inventory Alerts**: Notifications for low inventory items that need restocking
- **Inventory History**: Time-series chart showing inventory levels over time
- **Data Export**: Download inventory data as CSV

### Manufacturing Orders Tab

- **Active Orders**: Filterable table of manufacturing orders with status indicators
- **Order Analytics**:
  - Bar chart showing orders by status
  - Pie chart showing production volume by product
  - Timeline visualization of order progress
- **Create Order**: Intuitive form for creating new manufacturing orders with:
  - Product selection with icons
  - Quantity slider
  - Material requirements preview
  - One-click submission

### Purchase Orders Tab

- **Active Orders**: Filterable table of purchase orders with delivery status
- **Purchase Suggestions**: AI-generated suggestions for materials to purchase based on pending orders
- **Purchase Analytics**:
  - Bar chart showing purchase orders by status
  - Pie chart showing purchase volume by product
  - Timeline visualization of upcoming deliveries
  - Calendar view of expected deliveries
- **Supplier Performance**: Metrics on supplier reliability and costs
- **Create Order**: Streamlined form for creating new purchase orders with:
  - Supplier selection
  - Cost calculation
  - Delivery date estimation

### BOM & Materials Tab

- **BOM Entries**: Filterable table of Bill of Materials entries
- **BOM Relationships**: Visual representation of product components
- **Material Analysis**:
  - Material requirements calculation for pending orders
  - Comparison of required vs. available materials
  - Shortage detection and visualization
  - Status summary (sufficient, partial, insufficient)
- **Create Entry**: Interactive form for creating new BOM entries with live preview

## Interactive Features

The dashboard includes several interactive features to enhance usability:

- **Filtering**: Filter data tables by various criteria (status, product, supplier, etc.)
- **Sorting**: Sort data tables by clicking on column headers
- **Tooltips**: Hover over elements to see additional information
- **Data Download**: Export data from any tab as CSV files
- **Color Coding**: Visual indicators for status (low/medium/high inventory, pending/in-progress/completed orders)
- **Responsive Layout**: Adapts to different screen sizes
- **Real-time Updates**: Dashboard refreshes automatically when data changes

## Estado del Proyecto

![Estado de Desarrollo](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow?style=for-the-badge)

## Equipo y Contacto

### Desarrolladores
* **Junjie Li** - [![GitHub](https://img.shields.io/badge/GitHub-junjielyu13-181717?style=flat-square&logo=github)](https://github.com/junjielyu13) - junjie.li@estudiantat.upc.edu
* **Aleix Padrell** - [![GitHub](https://img.shields.io/badge/GitHub-aleixpg-181717?style=flat-square&logo=github)](https://github.com/aleixpg) - aleix.padrell@estudiantat.upc.edu
* **Alfonso Cano** - [![GitHub](https://img.shields.io/badge/GitHub-Alfons0Cano-181717?style=flat-square&logo=github)](https://github.com/Alfons0Cano) - alfonso.cano@estudiantat.upc.edu
* **Àlex Ollé** - [![GitHub](https://img.shields.io/badge/GitHub-aolle99-181717?style=flat-square&logo=github)](https://github.com/aolle99) - alex.olle@estudiantat.upc.edu

### Supervisión Académica
**Dr. Marc Alier** - [![GitHub](https://img.shields.io/badge/GitHub-granludo-181717?style=flat-square&logo=github)](https://github.com/granludo) - marc.alier@upc.edu  
Profesor del Departamento de Ingeniería de Servicios y Sistemas de Información

### Contexto Académico
Este proyecto se ha desarrollado en el marco de la asignatura **Desarrollo y Gestión de Sistemas Inteligentes (DGSI)** del Máster en Ingeniería Informática de la [Facultad de Informática de Barcelona (FIB)](https://www.fib.upc.edu/) de la [Universitat Politècnica de Catalunya (UPC)](https://www.upc.edu/).

**Curso académico:** 2024/2025 - Segundo cuatrimestre

## Licencia

Este proyecto está bajo la Licencia MIT - vea el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">
  <img src="https://dse.upc.edu/es/logosfooter-es/fib/@@images/image-400-f2beea873ec10b898a274f29520bed2c.png" alt="FIB-UPC Logo" width="200"/>
  <p>Desarrollado con ❤️ en la FIB-UPC</p>
</div>
