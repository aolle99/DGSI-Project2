import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import date, timedelta
import random  # For generating sample historical data

# Set page configuration
st.set_page_config(
    page_title="3D Printer Production Simulator",
    page_icon="🏭",
    layout="wide"
)

# API URL
API_URL = "http://localhost:8000"

# Function to make API requests
def api_request(endpoint, method="get", data=None):
    url = f"{API_URL}{endpoint}"
    try:
        if method.lower() == "get":
            response = requests.get(url)
        elif method.lower() == "post":
            response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Function to generate sample historical data for visualization
def generate_historical_data(days=30, current_date=None):
    if current_date is None:
        current_date = date.today()

    # Convert string date to date object if needed
    if isinstance(current_date, str):
        current_date = date.fromisoformat(current_date)

    dates = [(current_date - timedelta(days=i)).isoformat() for i in range(days)]
    dates.reverse()  # Oldest to newest

    # Generate sample inventory data
    raw_material_data = [max(0, 100 - i * 3 + random.randint(-10, 10)) for i in range(days)]
    finished_product_data = [max(0, 20 + i * 1 + random.randint(-5, 8)) for i in range(days)]

    # Generate sample orders data
    manufacturing_orders = [random.randint(1, 5) for _ in range(days)]
    purchase_orders = [random.randint(0, 3) for _ in range(days)]

    # Generate sample production data
    production_completed = [random.randint(0, 4) for _ in range(days)]

    return {
        "dates": dates,
        "raw_material": raw_material_data,
        "finished_product": finished_product_data,
        "manufacturing_orders": manufacturing_orders,
        "purchase_orders": purchase_orders,
        "production_completed": production_completed
    }

# Title and description
st.title("🏭 3D Printer Production Simulator")
st.markdown("A simulation platform for 3D printer production management")

# Sidebar for controls
with st.sidebar:
    st.header("Simulation Controls")

    # Check if simulation is running
    simulation_status = api_request("/")
    simulation_running = simulation_status and "current_date" in simulation_status and simulation_status["current_date"] != "Simulation not started"

    if not simulation_running:
        st.info("Simulation not started")

        # Form to start simulation
        with st.form("start_simulation"):
            st.subheader("Start New Simulation")
            min_orders = st.slider("Min Daily Orders", 1, 10, 5)
            max_orders = st.slider("Max Daily Orders", min_orders, 20, 15)
            days = st.slider("Simulation Days", 10, 60, 30)

            # Initial inventory (simplified for now)
            st.subheader("Initial Inventory")
            raw_material_qty = st.number_input("Raw Material Quantity", 0, 1000, 100)
            finished_product_qty = st.number_input("Finished Product Quantity", 0, 100, 20)

            initial_inventory = {
                1: raw_material_qty,  # Assuming product_id 1 is raw material
                2: finished_product_qty  # Assuming product_id 2 is finished product
            }

            submit_button = st.form_submit_button("Start Simulation")

            if submit_button:
                config = {
                    "daily_order_min": min_orders,
                    "daily_order_max": max_orders,
                    "initial_inventory": initial_inventory,
                    "simulation_days": days
                }

                result = api_request("/simulation/start/", method="post", data=config)
                if result:
                    st.success("Simulation started!")
                    st.rerun()
    else:
        current_date = simulation_status.get("current_date", "Unknown")
        st.info(f"Current Date: {current_date}")

        # Button to advance day
        if st.button("Advance Day"):
            result = api_request("/simulation/advance-day/", method="post")
            if result:
                st.success(f"Advanced to {result['current_date']}")
                st.rerun()

# Main dashboard area (only shown if simulation is running)
if simulation_running:
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Inventory", "Manufacturing Orders", "Purchase Orders", "BOM & Materials"])

    # Get current simulation state
    state = api_request("/simulation/advance-day/", method="post")

    with tab1:
        st.header("📊 Simulation Overview")

        # Display current date with better styling
        st.markdown(f"<h3 style='text-align: center; color: #1E88E5;'>Current Date: {state['current_date']}</h3>", unsafe_allow_html=True)

        # Create columns for key metrics with improved styling
        st.markdown("### Key Metrics")
        col1, col2, col3, col4 = st.columns(4)

        # Calculate metrics
        pending_orders = len(state["pending_orders"])
        pending_purchases = len(state["pending_purchases"])
        completed_orders = len(state["production_history"])
        total_inventory = sum(item["qty"] for item in state["inventory"])

        # Display metrics with delta indicators (comparing to previous values)
        with col1:
            st.metric(
                "📦 Pending Orders", 
                pending_orders,
                delta=random.randint(-2, 2),  # Simulated change
                delta_color="inverse"
            )

        with col2:
            st.metric(
                "🛒 Pending Purchases", 
                pending_purchases,
                delta=random.randint(-1, 1),  # Simulated change
                delta_color="inverse"
            )

        with col3:
            st.metric(
                "✅ Completed Orders", 
                completed_orders,
                delta=random.randint(0, 3),  # Simulated change
                delta_color="normal"
            )

        with col4:
            st.metric(
                "📊 Total Inventory", 
                total_inventory,
                delta=random.randint(-10, 20),  # Simulated change
                delta_color="normal"
            )

        # Generate historical data for charts
        historical_data = generate_historical_data(days=15, current_date=state["current_date"])

        st.markdown("---")
        st.markdown("### Production Trends")

        # Create tabs for different charts
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Inventory Trends", "Order Activity", "Production Distribution"])

        with chart_tab1:
            # Create inventory trend chart using Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=historical_data["dates"], 
                y=historical_data["raw_material"],
                mode='lines+markers',
                name='Raw Materials',
                line=dict(color='#1E88E5', width=2),
                marker=dict(size=6)
            ))
            fig.add_trace(go.Scatter(
                x=historical_data["dates"], 
                y=historical_data["finished_product"],
                mode='lines+markers',
                name='Finished Products',
                line=dict(color='#43A047', width=2),
                marker=dict(size=6)
            ))
            fig.update_layout(
                title='Inventory Levels Over Time',
                xaxis_title='Date',
                yaxis_title='Quantity',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

        with chart_tab2:
            # Create order activity chart
            order_data = pd.DataFrame({
                'Date': historical_data["dates"],
                'Manufacturing Orders': historical_data["manufacturing_orders"],
                'Purchase Orders': historical_data["purchase_orders"],
                'Completed Production': historical_data["production_completed"]
            })

            # Melt the dataframe for easier plotting
            order_data_melted = pd.melt(
                order_data, 
                id_vars=['Date'], 
                value_vars=['Manufacturing Orders', 'Purchase Orders', 'Completed Production'],
                var_name='Order Type', 
                value_name='Count'
            )

            # Create a bar chart with Altair
            chart = alt.Chart(order_data_melted).mark_bar().encode(
                x=alt.X('Date:O', title='Date'),
                y=alt.Y('Count:Q', title='Number of Orders'),
                color=alt.Color('Order Type:N', scale=alt.Scale(
                    domain=['Manufacturing Orders', 'Purchase Orders', 'Completed Production'],
                    range=['#FF7043', '#5C6BC0', '#66BB6A']
                )),
                tooltip=['Date', 'Order Type', 'Count']
            ).properties(
                title='Daily Order Activity',
                height=400
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

        with chart_tab3:
            # Create a pie chart for production distribution
            fig = px.pie(
                names=['Pending', 'In Progress', 'Completed'],
                values=[
                    sum(1 for o in state["pending_orders"] if o["status"] == "pending"),
                    sum(1 for o in state["pending_orders"] if o["status"] == "in_progress"),
                    len(state["production_history"])
                ],
                title='Production Order Status Distribution',
                color_discrete_sequence=px.colors.sequential.Viridis,
                hole=0.4,
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Production capacity progress
        st.markdown("---")
        st.markdown("### Production Capacity Utilization")

        # Simulate production capacity data
        max_capacity = 20
        used_capacity = sum(order["quantity"] for order in state["pending_orders"] if order["status"] == "in_progress")
        capacity_percentage = min(100, int((used_capacity / max_capacity) * 100))

        # Create a progress bar
        st.progress(capacity_percentage / 100)
        st.markdown(f"<div style='text-align: center;'><b>{capacity_percentage}%</b> of daily production capacity used ({used_capacity}/{max_capacity} units)</div>", unsafe_allow_html=True)

    with tab2:
        st.header("📦 Inventory Management")

        # Get products to display names
        products = api_request("/products/")

        # Create a dictionary to map product_id to name
        product_names = {p["id"]: p["name"] for p in products} if products else {}
        product_types = {p["id"]: p["type"] for p in products} if products else {}

        # Create a DataFrame for inventory
        inventory_data = []
        for item in state["inventory"]:
            product_id = item["product_id"]
            product_name = product_names.get(product_id, f"Product {product_id}")
            product_type = product_types.get(product_id, "unknown")

            # Determine icon based on product type
            icon = "🧱" if product_type == "raw" else "🖨️" if product_type == "finished" else "📦"

            inventory_data.append({
                "Product ID": product_id,
                "Product Name": f"{icon} {product_name}",
                "Type": product_type.capitalize(),
                "Quantity": item["qty"]
            })

        inventory_df = pd.DataFrame(inventory_data)

        # Add column for inventory status
        def get_status(row):
            qty = row["Quantity"]
            if qty <= 10:
                return "Low"
            elif qty <= 50:
                return "Medium"
            else:
                return "High"

        inventory_df["Status"] = inventory_df.apply(get_status, axis=1)

        # Add color coding for status
        def color_status(val):
            if val == "Low":
                return "background-color: #FFCDD2; color: #B71C1C"
            elif val == "Medium":
                return "background-color: #FFF9C4; color: #F57F17"
            else:
                return "background-color: #C8E6C9; color: #1B5E20"

        # Display the styled dataframe with sorting enabled
        st.markdown("### Current Inventory Levels")
        st.dataframe(
            inventory_df.style.map(color_status, subset=["Status"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Product ID": st.column_config.NumberColumn("ID", help="Product identifier"),
                "Product Name": st.column_config.TextColumn("Product", help="Product name"),
                "Type": st.column_config.TextColumn("Type", help="Product type"),
                "Quantity": st.column_config.NumberColumn("Quantity", help="Current quantity in inventory"),
                "Status": st.column_config.TextColumn("Status", help="Inventory level status")
            }
        )

        # Add inventory visualization
        st.markdown("### Inventory Distribution")

        # Create columns for charts
        col1, col2 = st.columns(2)

        with col1:
            # Create a bar chart for inventory levels
            if not inventory_df.empty:
                fig = px.bar(
                    inventory_df,
                    x="Product Name",
                    y="Quantity",
                    color="Type",
                    color_discrete_map={"Raw": "#5C6BC0", "Finished": "#66BB6A"},
                    title="Current Inventory Levels by Product",
                    labels={"Product Name": "Product", "Quantity": "Quantity in Stock"},
                    height=400,
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventory data available")

        with col2:
            # Create a pie chart for inventory distribution by type
            if not inventory_df.empty:
                # Group by type and sum quantities
                type_totals = inventory_df.groupby("Type")["Quantity"].sum().reset_index()

                fig = px.pie(
                    type_totals,
                    names="Type",
                    values="Quantity",
                    title="Inventory Distribution by Product Type",
                    color="Type",
                    color_discrete_map={"Raw": "#5C6BC0", "Finished": "#66BB6A"},
                    hole=0.4,
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventory data available")

        # Add inventory alerts section
        st.markdown("### Inventory Alerts")

        # Filter for low inventory items
        low_inventory = inventory_df[inventory_df["Status"] == "Low"]

        if not low_inventory.empty:
            st.warning("The following items have low inventory levels and may need to be restocked:")
            for _, row in low_inventory.iterrows():
                st.markdown(f"- **{row['Product Name']}**: {row['Quantity']} units remaining")
        else:
            st.success("All inventory levels are adequate. No immediate action needed.")

        # Add inventory history chart using the historical data
        st.markdown("### Inventory History")
        historical_data = generate_historical_data(days=15, current_date=state["current_date"])

        # Create a line chart for inventory history
        history_df = pd.DataFrame({
            "Date": historical_data["dates"],
            "Raw Materials": historical_data["raw_material"],
            "Finished Products": historical_data["finished_product"]
        })

        # Melt the dataframe for easier plotting
        history_melted = pd.melt(
            history_df,
            id_vars=["Date"],
            value_vars=["Raw Materials", "Finished Products"],
            var_name="Product Type",
            value_name="Quantity"
        )

        # Create an interactive line chart with Altair
        chart = alt.Chart(history_melted).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Quantity:Q", title="Quantity"),
            color=alt.Color("Product Type:N", scale=alt.Scale(
                domain=["Raw Materials", "Finished Products"],
                range=["#5C6BC0", "#66BB6A"]
            )),
            tooltip=["Date", "Product Type", "Quantity"]
        ).properties(
            title="Inventory Levels Over Time",
            height=400
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # Add download button for inventory data
        csv = inventory_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Inventory Data",
            data=csv,
            file_name="inventory_data.csv",
            mime="text/csv",
        )

    with tab3:
        st.header("🏭 Manufacturing Orders")

        # Create tabs for different manufacturing order views
        mo_tab1, mo_tab2, mo_tab3 = st.tabs(["Active Orders", "Order Analytics", "Create Order"])

        # Prepare manufacturing orders data
        orders_data = []
        for order in state["pending_orders"]:
            # Get product details
            product_id = order["product_id"]
            product_name = product_names.get(product_id, f"Product {product_id}")

            # Determine status icon
            status = order["status"]
            status_icon = "⏳" if status == "pending" else "⚙️" if status == "in_progress" else "✅"

            # Calculate days since creation
            created_date = date.fromisoformat(order["created_at"]) if isinstance(order["created_at"], str) else order["created_at"]
            current_date = date.fromisoformat(state["current_date"]) if isinstance(state["current_date"], str) else state["current_date"]
            days_active = (current_date - created_date).days

            orders_data.append({
                "Order ID": order["id"],
                "Product": f"🖨️ {product_name}",
                "Quantity": order["quantity"],
                "Created": order["created_at"],
                "Days Active": days_active,
                "Status": f"{status_icon} {status.capitalize()}",
                "Raw Status": status  # For filtering
            })

        # Add completed orders from history
        for order in state["production_history"]:
            product_id = order["product_id"]
            product_name = product_names.get(product_id, f"Product {product_id}")

            created_date = date.fromisoformat(order["created_at"]) if isinstance(order["created_at"], str) else order["created_at"]
            current_date = date.fromisoformat(state["current_date"]) if isinstance(state["current_date"], str) else state["current_date"]
            days_active = (current_date - created_date).days

            orders_data.append({
                "Order ID": order["id"],
                "Product": f"🖨️ {product_name}",
                "Quantity": order["quantity"],
                "Created": order["created_at"],
                "Days Active": days_active,
                "Status": "✅ Completed",
                "Raw Status": "completed"
            })

        orders_df = pd.DataFrame(orders_data)

        with mo_tab1:
            st.markdown("### Current Manufacturing Orders")

            # Add filter options
            st.markdown("#### Filter Orders")
            col1, col2 = st.columns(2)

            with col1:
                status_filter = st.multiselect(
                    "Status",
                    options=["pending", "in_progress", "completed"],
                    default=["pending", "in_progress"],
                    format_func=lambda x: x.capitalize()
                )

            with col2:
                if not orders_df.empty and "Product" in orders_df.columns:
                    product_filter = st.multiselect(
                        "Product",
                        options=orders_df["Product"].unique(),
                        default=orders_df["Product"].unique()
                    )
                else:
                    product_filter = []

            # Filter the dataframe
            filtered_df = orders_df
            if status_filter and not orders_df.empty and "Raw Status" in orders_df.columns:
                filtered_df = filtered_df[filtered_df["Raw Status"].isin(status_filter)]
            if product_filter:
                filtered_df = filtered_df[filtered_df["Product"].isin(product_filter)]

            # Display the filtered dataframe with improved styling
            if not filtered_df.empty:
                # Add color coding for status
                def color_status(val):
                    if "Pending" in val:
                        return "background-color: #FFF9C4; color: #F57F17"
                    elif "In Progress" in val:
                        return "background-color: #BBDEFB; color: #0D47A1"
                    else:
                        return "background-color: #C8E6C9; color: #1B5E20"

                # Remove the raw status column for display
                display_df = filtered_df.drop(columns=["Raw Status"])

                st.dataframe(
                    display_df.style.map(color_status, subset=["Status"]),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Order ID": st.column_config.NumberColumn("ID", help="Order identifier"),
                        "Product": st.column_config.TextColumn("Product", help="Product being manufactured"),
                        "Quantity": st.column_config.NumberColumn("Qty", help="Quantity ordered"),
                        "Created": st.column_config.DateColumn("Created", help="Order creation date"),
                        "Days Active": st.column_config.NumberColumn("Days", help="Days since creation"),
                        "Status": st.column_config.TextColumn("Status", help="Current order status")
                    }
                )

                # Add download button for orders data
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Orders Data",
                    data=csv,
                    file_name="manufacturing_orders.csv",
                    mime="text/csv",
                )
            else:
                st.info("No orders match the selected filters.")

        with mo_tab2:
            st.markdown("### Manufacturing Analytics")

            # Create columns for charts
            col1, col2 = st.columns(2)

            with col1:
                # Create a bar chart for orders by status
                if not orders_df.empty:
                    status_counts = orders_df["Raw Status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]

                    # Map status to better labels
                    status_map = {"pending": "Pending", "in_progress": "In Progress", "completed": "Completed"}
                    status_counts["Status"] = status_counts["Status"].map(status_map)

                    fig = px.bar(
                        status_counts,
                        x="Status",
                        y="Count",
                        color="Status",
                        color_discrete_map={
                            "Pending": "#F57F17",
                            "In Progress": "#0D47A1",
                            "Completed": "#1B5E20"
                        },
                        title="Orders by Status",
                        labels={"Status": "Order Status", "Count": "Number of Orders"},
                        height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No order data available")

            with col2:
                # Create a pie chart for order quantities by product
                if not orders_df.empty:
                    # Group by product and sum quantities
                    product_totals = orders_df.groupby("Product")["Quantity"].sum().reset_index()

                    fig = px.pie(
                        product_totals,
                        names="Product",
                        values="Quantity",
                        title="Production Volume by Product",
                        hole=0.4,
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No order data available")

            # Add a timeline chart for orders
            st.markdown("### Order Timeline")

            if not orders_df.empty:
                # Create a Gantt-like chart using Plotly
                # First, sort by creation date
                timeline_df = orders_df.sort_values("Created")

                # Create a figure
                fig = go.Figure()

                # Add a trace for each status
                for status in ["pending", "in_progress", "completed"]:
                    status_df = timeline_df[timeline_df["Raw Status"] == status]
                    if not status_df.empty:
                        color = "#F57F17" if status == "pending" else "#0D47A1" if status == "in_progress" else "#1B5E20"
                        name = "Pending" if status == "pending" else "In Progress" if status == "in_progress" else "Completed"

                        fig.add_trace(go.Bar(
                            x=status_df["Days Active"],
                            y=status_df["Order ID"].astype(str),
                            orientation='h',
                            name=name,
                            marker=dict(color=color),
                            hovertemplate="<b>Order %{y}</b><br>Days Active: %{x}<br>Status: " + name + "<extra></extra>"
                        ))

                fig.update_layout(
                    title="Order Timeline (Days Active)",
                    xaxis_title="Days",
                    yaxis_title="Order ID",
                    barmode='stack',
                    height=400,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No order data available for timeline visualization")

        with mo_tab3:
            st.markdown("### Create New Manufacturing Order")

            # Form to create new manufacturing order with improved UI
            with st.form("create_manufacturing_order"):
                # Get the next available ID
                next_id = 1
                if orders_data:
                    next_id = max(order["Order ID"] for order in orders_data) + 1

                st.markdown(f"**New Order ID: {next_id}**")

                # Product selection with better UI
                st.markdown("#### Select Product")
                product_options = [p["id"] for p in products if p["type"] == "finished"] if products else [2]

                product_id = st.selectbox(
                    "Product",
                    options=product_options,
                    format_func=lambda x: f"🖨️ {product_names.get(x, f'Product {x}')}"
                )

                # Quantity with slider for better UX
                st.markdown("#### Set Quantity")
                quantity = st.slider("Quantity to Produce", 1, 100, 10)

                # Show BOM requirements if available
                st.markdown("#### Material Requirements")

                # Get BOM data for this product
                bom_data = api_request(f"/bill-of-materials/?finished_product_id={product_id}")

                if bom_data:
                    st.info(f"This order will require the following raw materials:")
                    for bom in bom_data:
                        raw_material_id = bom["raw_material_id"]
                        raw_material_name = product_names.get(raw_material_id, f"Raw Material {raw_material_id}")
                        qty_needed = bom["quantity_needed"] * quantity
                        st.markdown(f"- **{raw_material_name}**: {qty_needed} units")
                else:
                    st.warning("No Bill of Materials defined for this product. Material requirements cannot be calculated.")

                # Submit button with better styling
                submit_col1, submit_col2 = st.columns([3, 1])
                with submit_col2:
                    submit_button = st.form_submit_button("🏭 Create Order")

                if submit_button:
                    order_data = {
                        "id": next_id,
                        "created_at": state["current_date"],
                        "product_id": product_id,
                        "quantity": quantity,
                        "status": "pending"
                    }

                    result = api_request("/manufacturing-orders/", method="post", data=order_data)
                    if result:
                        st.success(f"Manufacturing order created with ID: {result['id']}")
                        st.rerun()

    with tab4:
        st.header("🛒 Purchase Orders & Suppliers")

        # Create tabs for different purchase order views
        po_tab1, po_tab2, po_tab3 = st.tabs(["Active Orders", "Purchase Analytics", "Create Order"])

        # Get suppliers
        suppliers = api_request("/suppliers/")

        # Create a dictionary to map supplier_id to details
        supplier_details = {s["id"]: s for s in suppliers} if suppliers else {}

        # Prepare purchase orders data
        po_data = []
        for po in state["pending_purchases"]:
            supplier_id = po["supplier_id"]
            product_id = po["product_id"]

            # Get supplier and product details
            supplier_name = f"Supplier {supplier_id}"
            product_name = product_names.get(product_id, f"Product {product_id}")

            # Calculate days until delivery
            issue_date = date.fromisoformat(po["issue_date"]) if isinstance(po["issue_date"], str) else po["issue_date"]
            delivery_date = date.fromisoformat(po["estimated_delivery"]) if isinstance(po["estimated_delivery"], str) else po["estimated_delivery"]
            current_date = date.fromisoformat(state["current_date"]) if isinstance(state["current_date"], str) else state["current_date"]

            days_until_delivery = (delivery_date - current_date).days
            delivery_status = "Overdue" if days_until_delivery < 0 else "Today" if days_until_delivery == 0 else f"{days_until_delivery} days"

            # Determine status icon
            status = po["status"]
            status_icon = "🕒" if status == "pending" else "✅"

            po_data.append({
                "Order ID": po["id"],
                "Supplier": f"🏭 {supplier_name}",
                "Product": f"🧱 {product_name}",
                "Quantity": po["quantity"],
                "Issue Date": po["issue_date"],
                "Delivery Date": po["estimated_delivery"],
                "Delivery Status": delivery_status,
                "Days Until Delivery": days_until_delivery,
                "Status": f"{status_icon} {status.capitalize()}",
                "Raw Status": status  # For filtering
            })

        # Add completed purchases from history
        for po in state["purchase_history"]:
            supplier_id = po["supplier_id"]
            product_id = po["product_id"]

            # Get supplier and product details
            supplier_name = f"Supplier {supplier_id}"
            product_name = product_names.get(product_id, f"Product {product_id}")

            po_data.append({
                "Order ID": po["id"],
                "Supplier": f"🏭 {supplier_name}",
                "Product": f"🧱 {product_name}",
                "Quantity": po["quantity"],
                "Issue Date": po["issue_date"],
                "Delivery Date": po["estimated_delivery"],
                "Delivery Status": "Delivered",
                "Days Until Delivery": 0,
                "Status": "✅ Received",
                "Raw Status": "received"
            })

        po_df = pd.DataFrame(po_data)

        with po_tab1:
            st.markdown("### Current Purchase Orders")

            # Add filter options
            st.markdown("#### Filter Orders")
            col1, col2 = st.columns(2)

            with col1:
                status_filter = st.multiselect(
                    "Status",
                    options=["pending", "received"],
                    default=["pending"],
                    format_func=lambda x: "Pending" if x == "pending" else "Received"
                )

            with col2:
                if not po_df.empty and "Supplier" in po_df.columns:
                    supplier_filter = st.multiselect(
                        "Supplier",
                        options=po_df["Supplier"].unique(),
                        default=po_df["Supplier"].unique()
                    )
                else:
                    supplier_filter = []            # Filter the dataframe
            filtered_df = po_df
            if status_filter:
                # Print columns for debugging
                print("DataFrame columns:", filtered_df.columns.tolist())
                # Check if "Raw Status" column exists
                if "Raw Status" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df["Raw Status"].isin(status_filter)]
                else:
                    st.error("Column 'Raw Status' not found in the DataFrame")
                    # Alternative: Check if it might be named differently
                    status_columns = [col for col in filtered_df.columns if "status" in col.lower()]
                    if status_columns:
                        st.warning(f"Found similar columns: {status_columns}. Using {status_columns[0]}")
                        filtered_df = filtered_df[filtered_df[status_columns[0]].isin(status_filter)]
            if supplier_filter:
                filtered_df = filtered_df[filtered_df["Supplier"].isin(supplier_filter)]

            # Display the filtered dataframe with improved styling
            if not filtered_df.empty:
                # Add color coding for status and delivery
                def color_status(val):
                    if "Pending" in val:
                        return "background-color: #FFF9C4; color: #F57F17"
                    else:
                        return "background-color: #C8E6C9; color: #1B5E20"

                def color_delivery(val):
                    if val == "Overdue":
                        return "background-color: #FFCDD2; color: #B71C1C"
                    elif val == "Today":
                        return "background-color: #BBDEFB; color: #0D47A1"
                    elif val == "Delivered":
                        return "background-color: #C8E6C9; color: #1B5E20"
                    else:
                        return ""

                # Remove the raw status column for display
                display_df = filtered_df.drop(columns=["Raw Status", "Days Until Delivery"])

                st.dataframe(
                    display_df.style
                        .map(color_status, subset=["Status"])
                        .map(color_delivery, subset=["Delivery Status"]),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Order ID": st.column_config.NumberColumn("ID", help="Order identifier"),
                        "Supplier": st.column_config.TextColumn("Supplier", help="Supplier name"),
                        "Product": st.column_config.TextColumn("Product", help="Product being purchased"),
                        "Quantity": st.column_config.NumberColumn("Qty", help="Quantity ordered"),
                        "Issue Date": st.column_config.DateColumn("Issued", help="Order issue date"),
                        "Delivery Date": st.column_config.DateColumn("Expected", help="Expected delivery date"),
                        "Delivery Status": st.column_config.TextColumn("Delivery", help="Delivery status"),
                        "Status": st.column_config.TextColumn("Status", help="Current order status")
                    }
                )

                # Add download button for purchase orders data
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Purchase Orders Data",
                    data=csv,
                    file_name="purchase_orders.csv",
                    mime="text/csv",
                )
            else:
                st.info("No purchase orders match the selected filters.")

            # Get purchase suggestions
            st.markdown("### 💡 Purchase Suggestions")
            suggestions = api_request("/simulation/purchase-suggestions/")

            if suggestions:
                suggestions_data = []
                for suggestion in suggestions:
                    supplier_id = suggestion["supplier_id"]
                    product_id = suggestion["product_id"]

                    # Get supplier and product details
                    supplier_name = f"Supplier {supplier_id}"
                    product_name = product_names.get(product_id, f"Product {product_id}")

                    suggestions_data.append({
                        "Product": f"🧱 {product_name}",
                        "Supplier": f"🏭 {supplier_name}",
                        "Quantity Needed": suggestion["quantity"],
                        "Lead Time (days)": suggestion["lead_time"],
                        "Estimated Cost": round(suggestion["quantity"] * supplier_details.get(supplier_id, {}).get("unit_cost", 0), 2)
                    })

                suggestions_df = pd.DataFrame(suggestions_data)

                # Display suggestions with better styling
                st.dataframe(
                    suggestions_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Product": st.column_config.TextColumn("Product", help="Raw material needed"),
                        "Supplier": st.column_config.TextColumn("Supplier", help="Supplier for this material"),
                        "Quantity Needed": st.column_config.NumberColumn("Quantity", help="Quantity needed"),
                        "Lead Time (days)": st.column_config.NumberColumn("Lead Time", help="Days until delivery"),
                        "Estimated Cost": st.column_config.NumberColumn("Est. Cost", help="Estimated cost", format="$%.2f")
                    }
                )

                st.info("These suggestions are based on material requirements for pending manufacturing orders.")

                # Quick order buttons for suggestions
                st.markdown("#### Quick Order")

                # Create a row of buttons for each suggestion
                for i, suggestion in enumerate(suggestions_data):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**{suggestion['Product']}** from {suggestion['Supplier']}: {suggestion['Quantity Needed']} units")

                    with col2:
                        if st.button(f"Order Now", key=f"order_suggestion_{i}"):
                            # Extract product_id and supplier_id from the suggestion
                            product_id = next((p["id"] for p in products if f"🧱 {product_names.get(p['id'], '')}" == suggestion["Product"]), None)
                            supplier_id = next((s["id"] for s in suppliers if f"🏭 Supplier {s['id']}" == suggestion["Supplier"]), None)

                            if product_id and supplier_id:
                                # Create a new purchase order
                                next_id = 1
                                if po_data:
                                    next_id = max(po["Order ID"] for po in po_data) + 1

                                po_data = {
                                    "id": next_id,
                                    "supplier_id": supplier_id,
                                    "product_id": product_id,
                                    "quantity": suggestion["Quantity Needed"],
                                    "issue_date": state["current_date"],
                                    "estimated_delivery": state["current_date"],  # This will be calculated by the API
                                    "status": "pending"
                                }

                                result = api_request("/purchase-orders/", method="post", data=po_data)
                                if result:
                                    st.success(f"Purchase order created with ID: {result['id']}")
                                    st.rerun()
            else:
                st.info("No purchase suggestions at this time.")

        with po_tab2:
            st.markdown("### Purchase Analytics")

            # Create columns for charts
            col1, col2 = st.columns(2)

            with col1:
                # Create a bar chart for orders by status
                if not po_df.empty:
                    status_counts = po_df["Raw Status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]

                    # Map status to better labels
                    status_map = {"pending": "Pending", "received": "Received"}
                    status_counts["Status"] = status_counts["Status"].map(status_map)

                    fig = px.bar(
                        status_counts,
                        x="Status",
                        y="Count",
                        color="Status",
                        color_discrete_map={
                            "Pending": "#F57F17",
                            "Received": "#1B5E20"
                        },
                        title="Purchase Orders by Status",
                        labels={"Status": "Order Status", "Count": "Number of Orders"},
                        height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No purchase order data available")

            with col2:
                # Create a pie chart for purchase quantities by product
                if not po_df.empty:
                    # Group by product and sum quantities
                    product_totals = po_df.groupby("Product")["Quantity"].sum().reset_index()

                    fig = px.pie(
                        product_totals,
                        names="Product",
                        values="Quantity",
                        title="Purchase Volume by Product",
                        hole=0.4,
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No purchase order data available")

            # Add a timeline chart for upcoming deliveries
            st.markdown("### Upcoming Deliveries")

            if not po_df.empty and any(po_df["Raw Status"] == "pending"):
                # Filter for pending orders
                pending_df = po_df[po_df["Raw Status"] == "pending"].sort_values("Delivery Date")

                # Create a Gantt chart for delivery timeline
                fig = px.timeline(
                    pending_df,
                    x_start="Issue Date",
                    x_end="Delivery Date",
                    y="Order ID",
                    color="Supplier",
                    hover_name="Product",
                    hover_data=["Quantity", "Delivery Status"],
                    title="Purchase Order Delivery Timeline",
                    height=400,
                )
                fig.update_yaxes(autorange="reversed")  # Reverse the y-axis to show the earliest orders at the top
                st.plotly_chart(fig, use_container_width=True)

                # Add a calendar view of upcoming deliveries
                st.markdown("### Delivery Calendar")

                # Group deliveries by date
                deliveries_by_date = {}
                for _, row in pending_df.iterrows():
                    delivery_date = row["Delivery Date"]
                    if isinstance(delivery_date, str):
                        delivery_date = date.fromisoformat(delivery_date)

                    if delivery_date not in deliveries_by_date:
                        deliveries_by_date[delivery_date] = []

                    deliveries_by_date[delivery_date].append({
                        "Order ID": row["Order ID"],
                        "Product": row["Product"],
                        "Quantity": row["Quantity"],
                        "Supplier": row["Supplier"]
                    })

                # Display the next 7 days of deliveries
                current_date = date.fromisoformat(state["current_date"]) if isinstance(state["current_date"], str) else state["current_date"]

                # Create a 7-day calendar
                calendar_cols = st.columns(7)
                for i in range(7):
                    day = current_date + timedelta(days=i)
                    day_name = day.strftime("%a")
                    day_date = day.strftime("%m/%d")

                    with calendar_cols[i]:
                        st.markdown(f"**{day_name}**")
                        st.markdown(f"*{day_date}*")

                        if day in deliveries_by_date:
                            for delivery in deliveries_by_date[day]:
                                st.markdown(f"""
                                <div style="background-color: #E3F2FD; padding: 5px; border-radius: 5px; margin-bottom: 5px;">
                                    <small><b>#{delivery['Order ID']}</b>: {delivery['Product']}<br>
                                    Qty: {delivery['Quantity']}<br>
                                    {delivery['Supplier']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("<small>No deliveries</small>", unsafe_allow_html=True)
            else:
                st.info("No pending purchase orders to display")

            # Add supplier performance metrics
            st.markdown("### Supplier Performance")

            if suppliers:
                # Create a dataframe for supplier metrics
                supplier_metrics = []

                for supplier in suppliers:
                    supplier_id = supplier["id"]
                    product_id = supplier["product_id"]

                    # Count orders for this supplier
                    supplier_orders = [po for po in po_data if po["Supplier"] == f"🏭 Supplier {supplier_id}"]
                    total_orders = len(supplier_orders)
                    total_quantity = sum(po["Quantity"] for po in supplier_orders)
                    total_cost = total_quantity * supplier["unit_cost"]

                    # Calculate on-time delivery rate (simulated)
                    on_time_rate = random.randint(80, 100)

                    supplier_metrics.append({
                        "Supplier": f"🏭 Supplier {supplier_id}",
                        "Product": f"🧱 {product_names.get(product_id, f'Product {product_id}')}",
                        "Lead Time": supplier["lead_time"],
                        "Unit Cost": supplier["unit_cost"],
                        "Total Orders": total_orders,
                        "Total Quantity": total_quantity,
                        "Total Cost": total_cost,
                        "On-Time Rate": on_time_rate
                    })

                supplier_df = pd.DataFrame(supplier_metrics)

                # Display supplier metrics
                st.dataframe(
                    supplier_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Supplier": st.column_config.TextColumn("Supplier", help="Supplier name"),
                        "Product": st.column_config.TextColumn("Product", help="Product supplied"),
                        "Lead Time": st.column_config.NumberColumn("Lead Time (days)", help="Average lead time"),
                        "Unit Cost": st.column_config.NumberColumn("Unit Cost", help="Cost per unit", format="$%.2f"),
                        "Total Orders": st.column_config.NumberColumn("Orders", help="Total number of orders"),
                        "Total Quantity": st.column_config.NumberColumn("Quantity", help="Total quantity ordered"),
                        "Total Cost": st.column_config.NumberColumn("Total Cost", help="Total cost of all orders", format="$%.2f"),
                        "On-Time Rate": st.column_config.ProgressColumn("On-Time Delivery", help="Percentage of on-time deliveries", format="%d%%", min_value=0, max_value=100)
                    }
                )
            else:
                st.info("No supplier data available")

        with po_tab3:
            st.markdown("### Create New Purchase Order")

            # Form to create new purchase order with improved UI
            with st.form("create_purchase_order"):
                # Get the next available ID
                next_id = 1
                if po_data:
                    next_id = max(po["Order ID"] for po in po_data) + 1

                st.markdown(f"**New Order ID: {next_id}**")

                # Supplier selection with better UI
                st.markdown("#### Select Supplier")

                supplier_options = [s["id"] for s in suppliers] if suppliers else [1]

                supplier_id = st.selectbox(
                    "Supplier",
                    options=supplier_options,
                    format_func=lambda x: f"🏭 Supplier {x} (Lead Time: {supplier_details.get(x, {}).get('lead_time', 'Unknown')} days)"
                )

                # Get the product_id associated with the selected supplier
                product_id = None
                if supplier_id and supplier_details:
                    product_id = supplier_details.get(supplier_id, {}).get("product_id")

                if product_id:
                    product_name = product_names.get(product_id, f"Product {product_id}")
                    unit_cost = supplier_details.get(supplier_id, {}).get("unit_cost", 0)

                    st.markdown(f"#### Product: 🧱 **{product_name}**")
                    st.markdown(f"Unit Cost: **${unit_cost:.2f}**")

                    # Quantity with slider for better UX
                    st.markdown("#### Set Quantity")
                    quantity = st.slider("Quantity to Order", 1, 1000, 50)

                    # Show cost calculation
                    total_cost = quantity * unit_cost
                    st.markdown(f"Total Cost: **${total_cost:.2f}**")

                    # Show estimated delivery
                    lead_time = supplier_details.get(supplier_id, {}).get("lead_time", 0)
                    current_date = date.fromisoformat(state["current_date"]) if isinstance(state["current_date"], str) else state["current_date"]
                    delivery_date = current_date + timedelta(days=lead_time)

                    st.markdown(f"Estimated Delivery: **{delivery_date.isoformat()}** ({lead_time} days)")

                    # Submit button with better styling
                    submit_col1, submit_col2 = st.columns([3, 1])
                    with submit_col2:
                        submit_button = st.form_submit_button("🛒 Place Order")

                    if submit_button:
                        po_data = {
                            "id": next_id,
                            "supplier_id": supplier_id,
                            "product_id": product_id,
                            "quantity": quantity,
                            "issue_date": state["current_date"],
                            "estimated_delivery": state["current_date"],  # This will be calculated by the API
                            "status": "pending"
                        }

                        result = api_request("/purchase-orders/", method="post", data=po_data)
                        if result:
                            st.success(f"Purchase order created with ID: {result['id']}")
                            st.rerun()
                else:
                    st.warning("No product associated with this supplier.")

    with tab5:
        st.header("🧩 Bill of Materials & Material Requirements")

        # Create tabs for different BOM views
        bom_tab1, bom_tab2, bom_tab3 = st.tabs(["BOM Entries", "Material Analysis", "Create Entry"])

        # Get BOM data
        bom_data = api_request("/bill-of-materials/")

        # Get pending manufacturing orders to calculate material requirements
        pending_orders = state["pending_orders"]

        with bom_tab1:
            st.markdown("### Bill of Materials Entries")

            if bom_data:
                # Create a DataFrame for BOM with improved formatting
                bom_df_data = []
                for bom in bom_data:
                    finished_product_id = bom["finished_product_id"]
                    raw_material_id = bom["raw_material_id"]

                    # Get product names with icons
                    finished_product_name = product_names.get(finished_product_id, f"Product {finished_product_id}")
                    raw_material_name = product_names.get(raw_material_id, f"Product {raw_material_id}")

                    bom_df_data.append({
                        "Finished Product ID": finished_product_id,
                        "Finished Product": f"🖨️ {finished_product_name}",
                        "Raw Material ID": raw_material_id,
                        "Raw Material": f"🧱 {raw_material_name}",
                        "Quantity Needed": bom["quantity_needed"]
                    })

                bom_df = pd.DataFrame(bom_df_data)

                # Add filter options
                st.markdown("#### Filter BOM Entries")
                col1, col2 = st.columns(2)

                with col1:
                    if not bom_df.empty and "Finished Product" in bom_df.columns:
                        finished_filter = st.multiselect(
                            "Finished Product",
                            options=bom_df["Finished Product"].unique(),
                            default=bom_df["Finished Product"].unique()
                        )
                    else:
                        finished_filter = []

                with col2:
                    if not bom_df.empty and "Raw Material" in bom_df.columns:
                        raw_filter = st.multiselect(
                            "Raw Material",
                            options=bom_df["Raw Material"].unique(),
                            default=bom_df["Raw Material"].unique()
                        )
                    else:
                        raw_filter = []

                # Filter the dataframe
                filtered_df = bom_df
                if finished_filter:
                    filtered_df = filtered_df[filtered_df["Finished Product"].isin(finished_filter)]
                if raw_filter:
                    filtered_df = filtered_df[filtered_df["Raw Material"].isin(raw_filter)]

                # Display the filtered dataframe with improved styling
                if not filtered_df.empty:
                    # Remove ID columns for display
                    display_df = filtered_df.drop(columns=["Finished Product ID", "Raw Material ID"])

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Finished Product": st.column_config.TextColumn("Finished Product", help="Product being manufactured"),
                            "Raw Material": st.column_config.TextColumn("Raw Material", help="Required component"),
                            "Quantity Needed": st.column_config.NumberColumn("Qty Needed", help="Quantity of raw material needed per unit of finished product")
                        }
                    )

                    # Add download button for BOM data
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download BOM Data",
                        data=csv,
                        file_name="bom_data.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No BOM entries match the selected filters.")

                # Add BOM visualization
                st.markdown("### BOM Relationships")

                # Create a network graph of BOM relationships
                if not bom_df.empty:
                    # Group by finished product to show components
                    st.markdown("#### Components by Finished Product")

                    # Create columns for each finished product
                    unique_finished = bom_df["Finished Product"].unique()
                    cols = st.columns(min(3, len(unique_finished)))

                    for i, product in enumerate(unique_finished):
                        col_idx = i % len(cols)
                        with cols[col_idx]:
                            components = bom_df[bom_df["Finished Product"] == product]

                            st.markdown(f"**{product}**")
                            st.markdown("Components:")

                            for _, row in components.iterrows():
                                st.markdown(f"""
                                <div style="background-color: #E3F2FD; padding: 8px; border-radius: 5px; margin-bottom: 5px;">
                                    <b>{row['Raw Material']}</b><br>
                                    Quantity: {row['Quantity Needed']} units
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No BOM data available. Create some BOM entries to get started.")

        with bom_tab2:
            st.markdown("### Material Requirements Analysis")

            if bom_data and pending_orders:
                # Calculate material requirements for pending orders
                material_requirements = {}

                for order in pending_orders:
                    product_id = order["product_id"]
                    quantity = order["quantity"]

                    # Find BOM entries for this product
                    for bom in bom_data:
                        if bom["finished_product_id"] == product_id:
                            raw_material_id = bom["raw_material_id"]
                            qty_needed = bom["quantity_needed"] * quantity

                            if raw_material_id in material_requirements:
                                material_requirements[raw_material_id] += qty_needed
                            else:
                                material_requirements[raw_material_id] = qty_needed

                # Create a DataFrame for material requirements
                if material_requirements:
                    requirements_data = []

                    for material_id, qty in material_requirements.items():
                        material_name = product_names.get(material_id, f"Product {material_id}")

                        # Find current inventory level
                        inventory_level = 0
                        for item in state["inventory"]:
                            if item["product_id"] == material_id:
                                inventory_level = item["qty"]
                                break

                        # Calculate shortage
                        shortage = max(0, qty - inventory_level)

                        # Determine status
                        if inventory_level >= qty:
                            status = "Sufficient"
                        elif inventory_level > 0:
                            status = "Partial"
                        else:
                            status = "Insufficient"

                        requirements_data.append({
                            "Material ID": material_id,
                            "Material": f"🧱 {material_name}",
                            "Required": qty,
                            "In Stock": inventory_level,
                            "Shortage": shortage,
                            "Status": status
                        })

                    req_df = pd.DataFrame(requirements_data)

                    # Add color coding for status
                    def color_status(val):
                        if val == "Sufficient":
                            return "background-color: #C8E6C9; color: #1B5E20"
                        elif val == "Partial":
                            return "background-color: #FFF9C4; color: #F57F17"
                        else:
                            return "background-color: #FFCDD2; color: #B71C1C"

                    # Display the dataframe with improved styling
                    st.markdown("#### Material Requirements for Pending Orders")

                    # Remove ID column for display
                    display_df = req_df.drop(columns=["Material ID"])

                    st.dataframe(
                        display_df.style.map(color_status, subset=["Status"]),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Material": st.column_config.TextColumn("Material", help="Raw material"),
                            "Required": st.column_config.NumberColumn("Required", help="Total quantity required for all pending orders"),
                            "In Stock": st.column_config.NumberColumn("In Stock", help="Current inventory level"),
                            "Shortage": st.column_config.NumberColumn("Shortage", help="Additional quantity needed"),
                            "Status": st.column_config.TextColumn("Status", help="Inventory status for this material")
                        }
                    )

                    # Add charts for material requirements
                    st.markdown("#### Material Requirements Visualization")

                    col1, col2 = st.columns(2)

                    with col1:
                        # Create a bar chart comparing required vs. in stock
                        compare_df = pd.melt(
                            req_df,
                            id_vars=["Material"],
                            value_vars=["Required", "In Stock"],
                            var_name="Metric",
                            value_name="Quantity"
                        )

                        fig = px.bar(
                            compare_df,
                            x="Material",
                            y="Quantity",
                            color="Metric",
                            barmode="group",
                            title="Required vs. Available Materials",
                            color_discrete_map={
                                "Required": "#FF7043",
                                "In Stock": "#66BB6A"
                            },
                            height=400
                        )
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Create a pie chart for material shortages
                        if any(req_df["Shortage"] > 0):
                            shortage_df = req_df[req_df["Shortage"] > 0]

                            fig = px.pie(
                                shortage_df,
                                names="Material",
                                values="Shortage",
                                title="Material Shortages",
                                hole=0.4,
                                height=400
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.success("No material shortages detected!")

                            # Show a placeholder chart
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=[1, 2, 3],
                                y=[1, 1, 1],
                                mode="markers",
                                marker=dict(color="#66BB6A", size=20),
                                name="All materials available"
                            ))
                            fig.update_layout(
                                title="Material Availability Status",
                                xaxis_title="",
                                yaxis_title="",
                                xaxis=dict(showticklabels=False),
                                yaxis=dict(showticklabels=False),
                                height=400,
                                annotations=[
                                    dict(
                                        x=2,
                                        y=1,
                                        text="All materials available!",
                                        showarrow=False,
                                        font=dict(size=16)
                                    )
                                ]
                            )
                            st.plotly_chart(fig, use_container_width=True)

                    # Add material requirements summary
                    st.markdown("#### Material Requirements Summary")

                    total_materials_needed = len(requirements_data)
                    materials_sufficient = sum(1 for item in requirements_data if item["Status"] == "Sufficient")
                    materials_partial = sum(1 for item in requirements_data if item["Status"] == "Partial")
                    materials_insufficient = sum(1 for item in requirements_data if item["Status"] == "Insufficient")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "✅ Sufficient Materials",
                            materials_sufficient,
                            f"{int(materials_sufficient/total_materials_needed*100)}%"
                        )

                    with col2:
                        st.metric(
                            "⚠️ Partial Materials",
                            materials_partial,
                            f"{int(materials_partial/total_materials_needed*100)}%"
                        )

                    with col3:
                        st.metric(
                            "❌ Insufficient Materials",
                            materials_insufficient,
                            f"{int(materials_insufficient/total_materials_needed*100)}%"
                        )

                    # Add download button for requirements data
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Requirements Data",
                        data=csv,
                        file_name="material_requirements.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No material requirements calculated. This could be because there are no pending manufacturing orders or no BOM entries defined.")
            else:
                st.info("Material requirements analysis requires BOM data and pending manufacturing orders.")

        with bom_tab3:
            st.markdown("### Create New BOM Entry")

            # Form to create new BOM entry with improved UI
            with st.form("create_bom"):
                # Finished product selection with better UI
                st.markdown("#### Select Finished Product")
                finished_options = [p["id"] for p in products if p["type"] == "finished"] if products else [2]

                finished_product_id = st.selectbox(
                    "Finished Product",
                    options=finished_options,
                    format_func=lambda x: f"🖨️ {product_names.get(x, f'Product {x}')}"
                )

                # Raw material selection with better UI
                st.markdown("#### Select Raw Material")
                raw_options = [p["id"] for p in products if p["type"] == "raw"] if products else [1]

                raw_material_id = st.selectbox(
                    "Raw Material",
                    options=raw_options,
                    format_func=lambda x: f"🧱 {product_names.get(x, f'Product {x}')}"
                )

                # Quantity with slider for better UX
                st.markdown("#### Set Quantity Needed")
                quantity_needed = st.slider("Quantity of Raw Material per Finished Product", 1, 100, 5)

                # Preview the BOM entry
                st.markdown("#### BOM Entry Preview")

                finished_name = product_names.get(finished_product_id, f"Product {finished_product_id}")
                raw_name = product_names.get(raw_material_id, f"Product {raw_material_id}")

                st.markdown(f"""
                <div style="background-color: #E3F2FD; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4 style="margin-top: 0;">Bill of Materials Entry</h4>
                    <p><b>Finished Product:</b> 🖨️ {finished_name}</p>
                    <p><b>Raw Material:</b> 🧱 {raw_name}</p>
                    <p><b>Quantity Needed:</b> {quantity_needed} units per finished product</p>
                </div>
                """, unsafe_allow_html=True)

                # Submit button with better styling
                submit_col1, submit_col2 = st.columns([3, 1])
                with submit_col2:
                    submit_button = st.form_submit_button("🧩 Create Entry")

                if submit_button:
                    bom_data = {
                        "finished_product_id": finished_product_id,
                        "raw_material_id": raw_material_id,
                        "quantity_needed": quantity_needed
                    }

                    result = api_request("/bill-of-materials/", method="post", data=bom_data)
                    if result:
                        st.success("BOM entry created successfully!")
                        st.rerun()
else:
    # Show instructions if simulation is not running
    st.info("Please start a simulation using the controls in the sidebar.")

    # Show some example data or instructions
    st.header("Getting Started")
    st.markdown("""
    1. Configure the simulation parameters in the sidebar
    2. Start the simulation
    3. Use the dashboard to:
       - View inventory levels
       - Create manufacturing orders
       - Create purchase orders
       - Advance the simulation day by day
    """)
