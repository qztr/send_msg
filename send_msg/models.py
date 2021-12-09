"""
Я взял только те поля, которые используются при решении задачи
для увеличения читаемости кода тестового задания
"""

from send_msg import db


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), index=True, unique=True)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    subscription_cancelled = db.Column(db.Boolean, default=False, unique=False)
    subscription_admin = db.Column(db.Boolean, default=False, unique=False)
    phone = db.Column(db.String(64), index=True, unique=True)


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), index=True, unique=True)

    supplier = db.relationship("Supplier", backref="district")
