from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class CleaningProductOrder(Base):
    __tablename__ = "cleaning_product_order"

    price_id = Column(Integer, primary_key=True)
    brand_id = Column(String(250), nullable=False)
    type_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, price_id, brand_id , type_id ):
        """ Initializes a blood pressure reading """
        self.price_id = price_id
        self.brand_id = brand_id
        self.type_id = type_id
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['price_id'] = self.price_id
        dict['brand_id'] = self.brand_id
        dict['type_id'] = self.type_id
        dict['date_created'] = self.date_created

        return dict
