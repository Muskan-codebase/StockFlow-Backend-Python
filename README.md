# Inventory Management System

A simple inventory management system with low-stock alert functionality.  
Implemented using Python Flask + SQLAlchemy (ORM) and MySQL.

## Requirements

- Python 3.10+
- Flask
- SQLAlchemy
- MySQL

---

## Part 1: Debugging and fixing API

- **Create Product API** (`POST /api/products`)  
  - Adds a new product to the database.  
  - Automatically creates an initial inventory entry for the product in a warehouse.
 
### Original Issues

1. **No Data Validation**
   - Fields like `name`, `price`, and `initial_quantity` were not validated.
   - **Impact:** Incorrect or null data could be saved, causing issues in production.

2. **Warehouse Existence Not Verified**
   - Warehouse ID was not checked before creating a product.
   - **Impact:** Could lead to foreign key errors or products assigned to non-existent warehouses.

3. **No Proper Data Referencing**
   - Product had `warehouse_id` in its table, limiting it to a single warehouse.
   - **Impact:** Cannot track products across multiple warehouses.

4. **Missing Duplicate Entry Prevention**
   - `sku` was not unique.
   - **Impact:** Duplicate products could be created, leading to redundancy.

5. **No Transaction Safety**
   - Products and inventory were committed in separate transactions.
   - **Impact:** Could save products without inventory, causing referential issues.

### Fixes Implemented

- Added **field validation** before inserting products.
- Verified **warehouse existence** before creating product.
- Created a **separate Inventory table** with foreign keys to Products and Warehouses.
- Added **unique constraint on `sku`** to prevent duplicates.
- Combined database commits into a **single transaction** to ensure data consistency.

### Database Schema

**Tables and Relationships:**

### 1. Products
| Column           | Type          | Description                       |
|-----------------|---------------|-----------------------------------|
| id               | INT (PK)      | Unique product ID                  |
| name             | VARCHAR       | Product name                       |
| sku              | VARCHAR       | Unique SKU                         |
| price            | DECIMAL       | Product price                      |
| initial_quantity | INT           | Quantity used to create inventory  |

### 2. Inventory
| Column       | Type          | Description                         |
|-------------|---------------|-------------------------------------|
| id          | INT (PK)      | Unique inventory record ID          |
| product_id  | INT (FK → Products.id) | Links inventory to a product |
| warehouse_id| INT (FK → Warehouses.id) | Links inventory to a warehouse |
| quantity    | INT           | Quantity of the product in warehouse |

### 3. Warehouses
| Column   | Type     | Description       |
|---------|----------|------------------|
| id       | INT (PK) | Unique warehouse ID |
| name     | VARCHAR  | Warehouse name    |
| location | VARCHAR  | Warehouse location |

### Database Relationships

Current Implementation: Products → Inventory → Warehouses

**Explanation of Relationships:**

- Each **Product** can have **inventory entries in multiple warehouses**.  
- Each **Inventory** record links **one Product** to **one Warehouse**.  
- Each **Warehouse** can store **many products** via inventory.  
- This setup allows tracking **quantity of each product per warehouse**.

---

## Part 2: Database Design

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

  ---
  
## Part 3: Low Stock Alert API

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


