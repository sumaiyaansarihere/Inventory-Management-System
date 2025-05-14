#Assignment by sir aneeq khatri
import streamlit as st
from abc import ABC, abstractmethod
from datetime import datetime
import json

# --- Exceptions ---
class InsufficientStockError(Exception): pass
class DuplicateProductError(Exception): pass
class InvalidProductDataError(Exception): pass

# --- ye abstract product card k liye hai ---
class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    def restock(self, amount): self._quantity_in_stock += amount
    def sell(self, quantity):
        if quantity > self._quantity_in_stock:
            raise InsufficientStockError("❌ Not enough stock available.")
        self._quantity_in_stock -= quantity
    def get_total_value(self): return self._price * self._quantity_in_stock

    @abstractmethod
    def __str__(self): pass
    @abstractmethod
    def to_dict(self): pass

class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, warranty_years, brand):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._warranty_years = warranty_years
        self._brand = brand
    def __str__(self):
        return f"📱 Electronics - {self._name} | ID: {self._product_id} | Price: {self._price} | Stock: {self._quantity_in_stock} | Warranty: {self._warranty_years} yrs | Brand: {self._brand}"
    def to_dict(self):
        return {
            "type": "Electronics", "product_id": self._product_id, "name": self._name,
            "price": self._price, "quantity_in_stock": self._quantity_in_stock,
            "warranty_years": self._warranty_years, "brand": self._brand
        }

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
    def is_expired(self): return self._expiry_date < datetime.now()
    def __str__(self):
        status = "❗ Expired" if self.is_expired() else "✅ Fresh"
        return f"🥫 Grocery - {self._name} | ID: {self._product_id} | Price: {self._price} | Stock: {self._quantity_in_stock} | Expiry: {self._expiry_date.date()} | {status}"
    def to_dict(self):
        return {
            "type": "Grocery", "product_id": self._product_id, "name": self._name,
            "price": self._price, "quantity_in_stock": self._quantity_in_stock,
            "expiry_date": self._expiry_date.strftime("%Y-%m-%d")
        }

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._size = size
        self._material = material
    def __str__(self):
        return f"👗 Clothing - {self._name} | ID: {self._product_id} | Price: {self._price} | Stock: {self._quantity_in_stock} | Size: {self._size} | Material: {self._material}"
    def to_dict(self):
        return {
            "type": "Clothing", "product_id": self._product_id, "name": self._name,
            "price": self._price, "quantity_in_stock": self._quantity_in_stock,
            "size": self._size, "material": self._material
        }

class Inventory:
    def __init__(self):
        self._products = {}

    def add_product(self, product):
        if product._product_id in self._products:
            raise DuplicateProductError("⚠️ Duplicate Product ID.")
        self._products[product._product_id] = product

    def remove_product(self, product_id): self._products.pop(product_id, None)
    def search_by_name(self, name): return [p for p in self._products.values() if p._name.lower() == name.lower()]
    def search_by_type(self, product_type): return [p for p in self._products.values() if type(p).__name__ == product_type]
    def list_all_products(self): return list(self._products.values())
    def sell_product(self, product_id, quantity): self._products[product_id].sell(quantity)
    def restock_product(self, product_id, quantity): self._products[product_id].restock(quantity)
    def total_inventory_value(self): return sum(p.get_total_value() for p in self._products.values())
    def remove_expired_products(self):
        expired_ids = [pid for pid, p in self._products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired_ids: del self._products[pid]
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump([p.to_dict() for p in self._products.values()], f)
    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            for item in data:
                ptype = item["type"]
                if ptype == "Electronics":
                    obj = Electronics(**item)
                elif ptype == "Grocery":
                    obj = Grocery(**item)
                elif ptype == "Clothing":
                    obj = Clothing(**item)
                else:
                    raise InvalidProductDataError("⚠️ Invalid product type.")
                self.add_product(obj)

# --- Streamlit UI ---
st.set_page_config(page_title="Inventory Manager", layout="wide")
st.title("📦 Inventory Management System")

if 'inventory' not in st.session_state:
    st.session_state.inventory = Inventory()

inv = st.session_state.inventory

tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Product", "📋 View & Search", "💰 Inventory Ops", "💾 Save/Load"])

# --- Add Product ---
with tab1:
    st.subheader("Add a New Product")
    ptype = st.selectbox("Product Type", ["Electronics", "Grocery", "Clothing"])
    pid = st.text_input("Product ID")
    name = st.text_input("Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    extra_fields = {}
    if ptype == "Electronics":
        extra_fields["warranty_years"] = st.number_input("Warranty (years)", min_value=0)
        extra_fields["brand"] = st.text_input("Brand")
    elif ptype == "Grocery":
        extra_fields["expiry_date"] = st.date_input("Expiry Date").strftime("%Y-%m-%d")
    elif ptype == "Clothing":
        extra_fields["size"] = st.text_input("Size")
        extra_fields["material"] = st.text_input("Material")

    if st.button("Add Product"):
        try:
            if ptype == "Electronics":
                p = Electronics(pid, name, price, stock, extra_fields["warranty_years"], extra_fields["brand"])
            elif ptype == "Grocery":
                p = Grocery(pid, name, price, stock, extra_fields["expiry_date"])
            elif ptype == "Clothing":
                p = Clothing(pid, name, price, stock, extra_fields["size"], extra_fields["material"])
            inv.add_product(p)
            st.success("✅ Product added.")
        except DuplicateProductError as e:
            st.error(str(e))

# --- View & Search ---
with tab2:
    st.subheader("📋 All Products")
    for prod in inv.list_all_products():
        st.text(str(prod))

    st.markdown("---")
    st.subheader("🔍 Search")
    search_type = st.selectbox("Search by", ["Name", "Type"])
    query = st.text_input("Search Query")
    if st.button("Search"):
        results = inv.search_by_name(query) if search_type == "Name" else inv.search_by_type(query)
        for res in results:
            st.text(str(res))

# --- Inventory Ops ---
with tab3:
    st.subheader("💰 Operations")
    pid = st.text_input("Product ID for Sell/Restock")
    qty = st.number_input("Quantity", min_value=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💸 Sell"):
            try:
                inv.sell_product(pid, qty)
                st.success("✅ Product sold.")
            except Exception as e:
                st.error(str(e))
    with col2:
        if st.button("🔄 Restock"):
            try:
                inv.restock_product(pid, qty)
                st.success("✅ Product restocked.")
            except Exception as e:
                st.error(str(e))

    if st.button("🗑 Remove Expired Grocery Products"):
        inv.remove_expired_products()
        st.warning("Expired products removed.")

    st.write(f"💵 **Total Inventory Value:** {inv.total_inventory_value():.2f}")

# --- Save/Load ---
with tab4:
    st.subheader("💾 Save to File")
    save_name = st.text_input("Filename to save", value="inventory.json")
    if st.button("Save Inventory"):
        inv.save_to_file(save_name)
        st.success("✅ Inventory saved.")

    st.subheader("📂 Load from File")
    load_name = st.text_input("Filename to load", value="inventory.json")
    if st.button("Load Inventory"):
        try:
            inv.load_from_file(load_name)
            st.success("📂 Inventory loaded.")
        except Exception as e:
            st.error(str(e))
