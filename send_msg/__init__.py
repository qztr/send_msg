from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from celery import Celery


conf = Config()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = conf.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = conf.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["CELERY_BROKER_URL"] = "amqp://guest:guest@localhost:5672"
app.secret_key = conf.SECRET_KEY
celery = Celery("tasks", broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)
db = SQLAlchemy(app)
db.init_app(app)


from send_msg import routes


class Supplier(db.Model):
    __tablename__ = "supplier"
    name = Column(TEXT(None, "Cyrillic_General_CI_AS"), nullable=True)
    contact_person = Column(TEXT(None, "Cyrillic_General_CI_AS"), nullable=True)
    inn = Column(String(15, "Cyrillic_General_CI_AS"), nullable=True)
    storage_address = Column(TEXT(None, "Cyrillic_General_CI_AS"))
    phone = Column(String(255, "Cyrillic_General_CI_AS"))
    id = Column(Integer, primary_key=True)
    subscription_cancelled = Column(
        BIT, nullable=True, comment="Отписан ли от рассылки"
    )
    subscription_admin = Column(
        BIT, nullable=True, comment="Отписан ли от рассылки админом"
    )
    district_id = Column(ForeignKey("district.id"), nullable=True, comment="id области")
    district = relationship("District")
    area_id = Column(ForeignKey("area.id"), nullable=True, comment="id района")
    area = relationship("Area")
    manager_id = Column(ForeignKey("user.id"), nullable=True)
    manager = relationship("User")
    land_crop = relationship(
        "LandCrop", secondary=supplier_land_crop, backref=backref("suppliers")
    )
    landuser = Column(String(255, "Cyrillic_General_CI_AS"), nullable=True)


class District(db.Model):
    __tablename__ = "district"
    id = Column(Integer, primary_key=True)
    name = Column(
        String(255, "Cyrillic_General_CI_AS"),
        nullable=False,
        comment="Название области",
    )
