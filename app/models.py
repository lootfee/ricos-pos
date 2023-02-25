from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import hashlib
from time import time
# import jwt



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def is_super_admin(self):
        return self.id == 1

    def is_admin(self):
        return self.id <= 2


class Item(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    barcode = db.Column(db.String(256), index=True)
    date_discontinued = db.Column(db.DateTime)

    def last_retail_price(self):
        last_retail_price = self.retail_prices[-1].retail_price
        return last_retail_price

    # def last_purchase_per_piece_price(self):
    #     last_purchase_price = self.inventories.order_by(Inventory.date_received.desc()).first().price_per_piece
    #     return last_purchase_price

    def get_total_inv(self):
        total_inv = 0
        inventories = self.inventories.filter(Inventory.quantity > Inventory.used_quantity).all()
        for inv in inventories:
            total_inv += (inv.quantity - inv.used_quantity)
        return total_inv

    def current_inventory(self):
        inventories = self.inventories.filter(
            Inventory.quantity > Inventory.used_quantity
        ).order_by(Inventory.date_received.asc()).all()
        return inventories


class RetailPrice(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    retail_price = db.Column(db.Numeric(10, 2))
    date_effective = db.Column(db.DateTime)

    item = db.relationship('Item', backref=db.backref('retail_prices'), lazy='joined')


class Inventory(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)
    used_quantity = db.Column(db.Integer, default=0)
    purchase_price = db.Column(db.Numeric(10, 2))
    price_per_piece = db.Column(db.Numeric(10, 2))
    date_received = db.Column(db.DateTime)

    item = db.relationship('Item', backref=db.backref('inventories', lazy='dynamic'), lazy='joined')


class Sale(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(512))
    date_sold = db.Column(db.DateTime)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    seller = db.relationship('User', backref=db.backref('sales', lazy='dynamic'), lazy='joined')


class SaleItem(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)
    cost_per_piece = db.Column(db.Numeric(10, 2))
    price_per_piece = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))

    item = db.relationship('Item', backref=db.backref('sales', lazy='dynamic'), lazy='joined')
    sale = db.relationship('Sale', backref=db.backref('items', lazy='dynamic'), lazy='joined')


