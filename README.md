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

### Simulation Control
- `POST /simulation/start/`: Start a new simulation
- `POST /simulation/advance-day/`: Advance the simulation by one day
- `GET /simulation/export/`: Export the current simulation state
- `POST /simulation/import/`: Import a simulation state

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
   pip install fastapi uvicorn pydantic
   ```

## Running the Application

1. Start the server:
   ```
   uvicorn main:app --reload
   ```
2. Access the API documentation at http://localhost:8000/docs

## Testing

Run the tests with:
```
python test_models.py
```

## Daily Workflow

1. Start a new simulation with initial configuration
2. Each day:
   - Review pending orders and inventory
   - Create purchase orders for needed materials
   - Release manufacturing orders to production
   - Advance to the next day
3. Export the simulation state for later analysis

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