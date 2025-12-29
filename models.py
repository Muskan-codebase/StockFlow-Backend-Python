from database import db
from sqlalchemy import UniqueConstraint
from decimal import Decimal

# Company Model
class Company(db.Model):
    __tablename__ = "companies"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    warehouses = db.relationship("Warehouse", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"


# Warehouse Model
class Warehouse(db.Model):
    __tablename__ = "warehouses"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    company = db.relationship("Company", back_populates="warehouses")
    inventories = db.relationship("Inventory", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse {self.name}>"


# Product-Supplier Association Table (Many-to-Many)
product_suppliers = db.Table(
    "product_suppliers",
    db.Column("product_id", db.Integer, db.ForeignKey("products.id"), primary_key=True),
    db.Column("supplier_id", db.Integer, db.ForeignKey("suppliers.id"), primary_key=True)
)


# Product Model
class Product(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_bundle = db.Column(db.Boolean, default=False)
    
    # Relationships
    inventories = db.relationship("Inventory", back_populates="product")
    suppliers = db.relationship("Supplier", secondary=product_suppliers, back_populates="products")
    
    def __repr__(self):
        return f"<Product {self.sku}>"


# Supplier Model
class Supplier(db.Model):
    __tablename__ = "suppliers"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100))
    
    # Relationships
    products = db.relationship("Product", secondary=product_suppliers, back_populates="suppliers")
    
    def __repr__(self):
        return f"<Supplier {self.name}>"


# Inventory Model
class Inventory(db.Model):
    __tablename__ = "inventory"
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=10)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('product_id', 'warehouse_id', name='uix_product_warehouse'),
    )
    
    # Relationships
    product = db.relationship("Product", back_populates="inventories")
    warehouse = db.relationship("Warehouse", back_populates="inventories")
    
    def __repr__(self):
        return f"<Inventory P:{self.product_id} W:{self.warehouse_id} Qty:{self.quantity}>"
