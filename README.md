# Inventory Management System

A simple inventory management system with low-stock alert functionality.  
Implemented using Python Flask + SQLAlchemy (ORM) and MySQL.

## Requirements

- Python 3.10+
- Flask
- SQLAlchemy
- MySQL

## Database Design

### Tables

1. **Companies**
   - id (PK), name
   - One company can have multiple warehouses

2. **Warehouses**
   - id (PK), name, location, company_id (FK → Companies)
   - Each warehouse belongs to a company

3. **Products**
   - id (PK), name, sku, price, is_bundle
   - Independent product table

4. **Inventory**
   - id (PK), product_id (FK → Products), warehouse_id (FK → Warehouses), quantity, low_stock_threshold
   - Tracks quantity per warehouse
   - Unique constraint on product_id + warehouse_id

5. **Suppliers**
   - id (PK), name, contact_email

6. **Product_Suppliers**
   - product_id + supplier_id (Many-to-Many mapping)

7. **Inventory History**
   - Tracks inventory changes (optional)

8. **Product Bundles**
   - Links products that are bundles containing other products
  
## Low Stock Alert API

### Endpoint
`GET /api/companies/<company_id>/low-stock-alerts`

### Logic
1. Fetch all warehouses of the company
2. Fetch inventory for each warehouse
3. Compare quantity with `low_stock_threshold`
4. Optionally, check recent sales
5. Return products that are low in stock, along with warehouse and supplier details

### response

<pre>{
  {
    "alerts": [
        {
            "current_stock": 3,
            "days_until_stockout": 1,
            "product_id": 2,
            "product_name": "Wireless Mouse",
            "sku": "WM-101",
            "supplier": null,
            "threshold": 10,
            "warehouse_id": 1,
            "warehouse_name": "Pune Warehouse"
        }
    ],
    "total_alerts": 1
}
</pre>


