#This is python app.py file aka main file
from flask import Flask, request, jsonify
from database import db
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from models import Product, Inventory, Warehouse, Company, Supplier
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app) #connect db with flask app

with app.app_context():
    db.create_all()  # first create tables

    if not Company.query.first():
        # Create companies
        company1 = Company(name="Tech Supplies Pvt Ltd")
        company2 = Company(name="Gadget World Ltd")
        db.session.add_all([company1, company2])
        db.session.commit()

        # Create warehouses for these companies
        db.session.add(Warehouse(name="Pune Warehouse", company_id=company1.id))
        db.session.add(Warehouse(name="Mumbai Warehouse", company_id=company1.id))
        db.session.add(Warehouse(name="Delhi Warehouse", company_id=company2.id))
        db.session.commit()


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()

    # Validation
    required_fields = ["name", "sku", "price", "warehouse_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    try:
        price = Decimal(str(data["price"]))
        if price <= 0:
            return jsonify({"error": "Price must be positive"}), 400
    except:
        return jsonify({"error": "Invalid price format"}), 400

    initial_quantity = data.get("initial_quantity", 0)
    if initial_quantity < 0:
        return jsonify({"error": "Quantity cannot be negative"}), 400

    low_stock_threshold = data.get("low_stock_threshold", 10)

    try:
        db.session.begin()

        # Warehouse check
        warehouse = Warehouse.query.get(data["warehouse_id"])
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Product SKU check
        existing_product = Product.query.filter_by(sku=data["sku"]).first()
        if existing_product:
            return jsonify({"error": "SKU already exists"}), 409

        # Create product
        product = Product(
            name=data["name"],
            sku=data["sku"],
            price=price
        )

        # Optional: add suppliers
        supplier_ids = data.get("supplier_ids", [])
        if supplier_ids:
            suppliers = Supplier.query.filter(Supplier.id.in_(supplier_ids)).all()
            product.suppliers = suppliers

        db.session.add(product)
        db.session.flush()

        # Create inventory
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=initial_quantity,
            low_stock_threshold=low_stock_threshold
        )
        db.session.add(inventory)
        db.session.commit()

        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database constraint violation"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/companies/<int:company_id>/alerts/low-stock", methods=["GET"])
def low_stock_alerts(company_id):
    alerts = []

    # 1️⃣ Fetch all warehouses for the company
    warehouses = Warehouse.query.filter_by(company_id=company_id).all()

    for wh in warehouses:
        # 2️⃣ Fetch inventory items below threshold
        low_stock_items = Inventory.query.filter(
            Inventory.warehouse_id == wh.id,
            Inventory.quantity < Inventory.low_stock_threshold
        ).all()

        for item in low_stock_items:
            product = item.product
            # 3️⃣ Assume supplier is the first one for simplicity
            supplier = product.suppliers[0] if product.suppliers else None

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "warehouse_id": wh.id,
                "warehouse_name": wh.name,
                "current_stock": item.quantity,
                "threshold": item.low_stock_threshold,
                "days_until_stockout": max(item.quantity // 5, 1),  # Example assumption
                "supplier": {
                    "id": supplier.id,
                    "name": supplier.name,
                    "contact_email": supplier.contact_email
                } if supplier else None
            })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    })


@app.route("/")
def home():
    return "Hello World. This is flask API"

if __name__ == "__main__":
    app.run(debug=True)