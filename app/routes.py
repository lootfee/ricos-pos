import random

from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db, photos
import os
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Item, RetailPrice, Inventory, Sale, SaleItem
from app.forms import LoginForm, AddItemForm, EditItemForm, EditRetailPriceForm, AddInventoryForm, EditSaleItemForm, EditSaleDateForm
from app.custom_decorators import admin_required
from werkzeug.urls import url_parse
from sqlalchemy import extract
from datetime import datetime
from time import time
from pytz import timezone
import pytz
import calendar


# from app.email import send_password_reset_email, send_approve_partner_email
import smtplib
# from oauth import OAuthSignIn
# from flask_mail import Message
import json
from sqlalchemy.orm import class_mapper


def phil_time():
    return datetime.now(timezone('Asia/Manila'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = phil_time()
        db.session.commit()


@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')


@app.context_processor
def inject_datetime_now():
    return {'datetime_now': phil_time()}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'alert-warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)


@app.route('/checkout_items', methods=['POST'])
@login_required
def checkout_items():
    items = request.get_json()
    sale = Sale(date_sold=phil_time(), seller_id=current_user.id, comment=items[-1]["comment"])
    db.session.add(sale)
    db.session.commit()

    for item in items[:-1]:
        deducted_qty = 0
        inventory = Inventory.query.filter_by(item_id=int(item['item_id'])).filter(
            Inventory.quantity > Inventory.used_quantity).first()
        while (inventory.quantity - inventory.used_quantity) < item['quantity']:
            deducted_qty = inventory.quantity - inventory.used_quantity
            inventory.used_quantity += deducted_qty
            db.session.commit()

            sale_item = SaleItem(sale_id=sale.id,
                                 item_id=item['item_id'],
                                 quantity=deducted_qty,
                                 cost_per_piece=inventory.price_per_piece,
                                 price_per_piece=item['price_per_piece'],
                                 total_cost=item['total_cost'])
            db.session.add(sale_item)
            db.session.commit()

            inventory = Inventory.query.filter_by(item_id=item['item_id']).filter(
                Inventory.quantity > Inventory.used_quantity).first()
        else:
            inventory.used_quantity += (item['quantity'] - deducted_qty)
            db.session.commit()

            sale_item = SaleItem(sale_id=sale.id,
                                 item_id=item['item_id'],
                                 quantity=item['quantity'] - deducted_qty,
                                 cost_per_piece=inventory.price_per_piece,
                                 price_per_piece=item['price_per_piece'],
                                 total_cost=item['total_cost'])
            db.session.add(sale_item)
            db.session.commit()

    return "ok"


@app.route('/monthly_sales/<int:year>/<int:month>', methods=['GET', 'POST'])
@login_required
def monthly_sales(year, month):
    items = Item.query.all()
    current_year = year
    years = list(range(phil_time().year, 2022, -1))
    current_month = month
    months = [{'id': i + 1, 'name': calendar.month_abbr[i + 1]} for i in range(12)]
    current_month_name = calendar.month_name[current_month]
    num_days = calendar.monthrange(year, month)[1]
    daily_sales = []
    for day in range(1, num_days + 1):
        sales = Sale.query.filter(extract('year', Sale.date_sold) == year,
                                extract('month', Sale.date_sold) == month,
                                extract('day', Sale.date_sold) == day).order_by(Sale.date_sold.asc()).all()
        transaction_count = len(sales)
        items_sold = 0
        gross = 0
        expenses = 0
        for sale in sales:
            for item in sale.items:
                items_sold += item.quantity
                gross += (item.price_per_piece * item.quantity)
                expenses += (item.cost_per_piece * item.quantity)
        net = gross - expenses
        daily_sales.append({'day': day,
                            'transaction_count': transaction_count,
                            'items_sold': items_sold,
                            'gross': gross,
                            'expenses': expenses,
                            'net': net})


    return render_template('monthly_sales.html', items=items, current_year=current_year, years=years,
                           current_month=current_month, months=months, current_month_name=current_month_name,
                           num_days=num_days, daily_sales=daily_sales)


@app.route('/get_monthly_sales/<int:year>', methods=['GET'])
@login_required
def get_monthly_sales(year):
    st = time()
    months = [{'id': i + 1, 'name': calendar.month_abbr[i + 1]} for i in range(12)]
    monthly_sales = []
    monthly_transactions = []
    for month in months:
        monthly_sale_data = []
        monthly_sale_data.append(month['name'])
        monthly_transaction_data = []
        monthly_transaction_data.append(month['name'])

        cost = 0
        gross = 0
        sales = Sale.query.filter(extract('year', Sale.date_sold) == year,
                                  extract('month', Sale.date_sold) == month['id']
                                  ).order_by(Sale.date_sold.asc()).all()
        transactions = len(sales)
        for sale in sales:
            for sale_item in sale.items:
                cost += (sale_item.cost_per_piece * sale_item.quantity)
                gross += (sale_item.price_per_piece * sale_item.quantity)

        monthly_sale_data.append(float(gross))
        monthly_sale_data.append(float(cost))
        monthly_sale_data.append(float(gross - cost))
        monthly_sales.append(monthly_sale_data)

        monthly_transaction_data.append(transactions)
        monthly_transactions.append(monthly_transaction_data)

    et = time()
    print(et - st)
    return jsonify([monthly_sales, monthly_transactions])



@app.route('/get_daily_sales/<int:year>/<int:month>', methods=['GET'])
@login_required
def get_daily_sales(year, month):
    # months = [{'id': i + 1, 'name': calendar.month_abbr[i + 1]} for i in range(12)]
    num_days = calendar.monthrange(year, month)[1]
    daily_sales = [['Month', 'Gross', 'Expense', 'Net']]
    daily_transactions = [['Month', 'Transactions']]
    for day in range(1, num_days + 1):
        daily_sale_data = []
        daily_sale_data.append(str(day))
        daily_transaction_data = []
        daily_transaction_data.append(str(day))
        # transactions = 0
        cost = 0
        gross = 0
        sales = Sale.query.filter(extract('year', Sale.date_sold) == year,
                                  extract('month', Sale.date_sold) == month,
                                  extract('day', Sale.date_sold) == day
                                  ).order_by(Sale.date_sold.asc()).all()
        transactions = len(sales)
        for sale in sales:
            for sale_item in sale.items:
                cost += (sale_item.cost_per_piece * sale_item.quantity)
                gross += (sale_item.price_per_piece * sale_item.quantity)

        daily_sale_data.append(float(gross))
        daily_sale_data.append(float(cost))
        daily_sale_data.append(float(gross - cost))
        daily_sales.append(daily_sale_data)

        daily_transaction_data.append(transactions)
        daily_transactions.append(daily_transaction_data)

    return jsonify([daily_sales, daily_transactions])



@app.route('/daily_sales/<int:year>/<int:month>/<int:day>', methods=['GET', 'POST'])
@login_required
def daily_sales(year, month, day):
    current_year = year
    years = list(range(phil_time().year, 2022, -1))
    current_month = month
    months = [{'id': i + 1, 'name': calendar.month_abbr[i + 1]} for i in range(12)]
    current_month_name = calendar.month_name[current_month]
    num_days = calendar.monthrange(year, month)[1]
    sales = Sale.query.filter(extract('year', Sale.date_sold) == year,
                              extract('month', Sale.date_sold) == month,
                              extract('day', Sale.date_sold) == day).order_by(Sale.date_sold.asc()).all()
    return render_template('daily_sales.html', current_year=current_year, years=years,
                           current_month=current_month, months=months, current_month_name=current_month_name,
                           day=day, num_days=num_days, sales=sales)


@app.route('/edit_sale_date/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_sale_date(id):
    sale = Sale.query.get(id)
    form = EditSaleDateForm()
    if form.validate_on_submit():
        sale.date_sold = form.date.data
        db.session.commit()
        flash('Sale date updated.', 'alert-info')
        return redirect(url_for('daily_sales', year=phil_time().year, month=phil_time().month, day=phil_time().day))
    elif request.method == 'GET':
        form.date.data = sale.date_sold
    return render_template('edit_sale.html', form=form, sale=sale)


@app.route('/edit_sale_item/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_sale_item(id):
    sale_item = SaleItem.query.get(id)
    form = EditSaleItemForm()
    if form.validate_on_submit():
        sale_item.quantity = form.quantity.data
        sale_item.price_per_piece = sale_item.item.last_retail_price()
        sale_item.total_cost = sale_item.quantity * sale_item.price_per_piece
        db.session.commit()
        flash('Sale item edited.', 'alert-info')
        return redirect(url_for('daily_sales', year=phil_time().year, month=phil_time().month, day=phil_time().day))
    elif request.method == 'GET':
        form.quantity.data = sale_item.quantity
        form.retail_price.data = sale_item.item.last_retail_price()
        form.total_cost.data = sale_item.quantity * sale_item.item.last_retail_price()
    return render_template('edit_sale_item.html', form=form, sale_item=sale_item)


@app.route('/delete_sale/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_sale(id):
    sale = Sale.query.get(id)
    for item in sale.items:
        db.session.delete(item)
        db.session.commit()
    db.session.delete(sale)
    db.session.commit()
    flash(f"Sale and sale items deleted", 'alert-info')
    return redirect(url_for('daily_sales', year=phil_time().year, month=phil_time().month, day=phil_time().day))


@app.route('/delete_sale_tem/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_sale_tem(id):
    sale_item = SaleItem.query.get(id)
    db.session.delete(sale_item)
    db.session.commit()
    flash(f"Sale item deleted", 'alert-info')
    return redirect(url_for('daily_sales', year=phil_time().year, month=phil_time().month, day=phil_time().day))


@app.route('/items', methods=['GET', 'POST'])
@login_required
@admin_required
def items():
    form = AddItemForm()
    items = Item.query.all()
    if form.validate_on_submit():
        item = Item(item_name=form.item_name.data, description=form.description.data, barcode=form.barcode.data)
        db.session.add(item)
        db.session.commit()
        retail_price = RetailPrice(item_id=item.id, retail_price=form.retail_price.data, date_effective=phil_time())
        db.session.add(retail_price)
        db.session.commit()
        flash("Items successfully saved", "alert-info")
        return redirect(url_for('items'))
    return render_template('items.html', form=form, items=items)


@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(id):
    form = EditItemForm()
    item = Item.query.get(id)
    if form.validate_on_submit():
        item.item_name = form.item_name.data
        item.description = form.description.data
        item.barcode = form.barcode.data
        db.session.commit()
        flash(f"Item {item.item_name} successfully edited", "alert-info")
        return redirect(url_for('items'))
    elif request.method == 'GET':
        form.item_name.data = item.item_name
        form.description.data = item.description
        form.barcode.data = item.barcode
    return render_template('edit_item.html', form=form, item=item)


@app.route('/update_retail_price/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_retail_price(item_id):
    form = EditRetailPriceForm()
    item = Item.query.get(item_id)
    latest_price = item.last_retail_price()
    if form.validate_on_submit():
        retail_price = RetailPrice(item_id=item.id, retail_price=form.retail_price.data, date_effective=phil_time())
        db.session.add(retail_price)
        db.session.commit()
        flash(f"Item {item.item_name} reatil price successfully updated", "alert-info")
        return redirect(url_for('items'))

    return render_template('update_retail_price.html', form=form, item=item, latest_price=latest_price)


@app.route('/discontinue_item/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def discontinue_item(id):
    item = Item.query.get(id)
    item.date_discontinued = phil_time()
    db.session.commit()
    flash(f"Item {item.item_name} discontinued", 'alert-info')
    return redirect(url_for('items'))


@app.route('/inventories', methods=['GET', 'POST'])
@login_required
@admin_required
def inventories():
    form = AddInventoryForm()
    items = Item.query.order_by(Item.item_name.asc()).all()
    form.item.choices = [(0, 'Select Item')] + [(i.id, f"{i.item_name} ({i.barcode})") for i in items]
    if form.validate_on_submit():
        price_per_piece = round(form.purchase_price.data / form.quantity.data, 2)
        inventory = Inventory(item_id=form.item.data, quantity=form.quantity.data,
                              purchase_price=form.purchase_price.data, date_received=form.date_received.data,
                              price_per_piece=price_per_piece)
        db.session.add(inventory)
        db.session.commit()
        flash("Inventory successfully added", "alert-info")
        return redirect(url_for('inventories'))
    return render_template('inventories.html', form=form, inventories=inventories, items=items)


@app.route('/edit_inventory/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_inventory(id):
    form = AddInventoryForm()
    inventory = Inventory.query.get(id)
    items = Item.query.order_by(Item.item_name.asc()).all()
    form.item.choices = [(0, 'Select Item')] + [(i.id, f"{i.item_name} ({i.barcode})") for i in items]
    if form.validate_on_submit():
        price_per_piece = round(form.purchase_price.data / form.quantity.data, 2)
        inventory.item_id = form.item.data
        inventory.quantity = form.quantity.data
        inventory.purchase_price = form.purchase_price.data
        inventory.date_received = form.date_received.data
        inventory.price_per_piece = price_per_piece
        db.session.commit()
        flash("Inventory successfully updated", "alert-info")
        return redirect(url_for('inventories'))
    elif request.method == 'GET':
        form.item.data = inventory.item_id
        form.quantity.data = inventory.quantity
        form.purchase_price.data = inventory.purchase_price
        form.date_received.data = inventory.date_received
    return render_template('edit_inventory.html', form=form)


@app.route('/delete_inventory/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_inventory(id):
    inv = Inventory.query.get(id)
    db.session.delete(inv)
    db.session.commit()
    flash(f"Inventory for {inv.item.item_name} - {inv.date_received.strftime('%b %d, %Y')} deleted", 'alert-info')
    return redirect(url_for('inventories'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     gmaps_api = os.getenv('GOOGLE_API_KEY')
#     print(gmaps_api)
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data, address=form.address.data,
#                     birthday=form.birthday.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form, gmaps_api=gmaps_api)
#
#
# @app.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm(current_user.username, current_user.email)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.email.data = current_user.email
#     return render_template('edit_profile.html', title='Edit Profile',
#                            form=form)
#
#
# @app.route('/reset_password_request', methods=['GET', 'POST'])
# def reset_password_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = ResetPasswordRequestForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             send_password_reset_email(user)
#         flash('Check your email for the instructions to reset your password')
#         return redirect(url_for('login'))
#     return render_template('reset_password_request.html', title='Reset Password', form=form)
#
#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     user = User.verify_reset_password_token(token)
#     if not user:
#         return redirect(url_for('index'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         user.set_password(form.password.data)
#         db.session.commit()
#         flash('Your password has been reset.')
#         return redirect(url_for('login'))
#     return render_template('reset_password.html', form=form)
#
#
# @app.route('/user', methods=['GET', 'POST'])
# @login_required
# def user():
#     return render_template('user.html')



