from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class CarPartOrder(Base):
    __tablename__ = "car_part_order"

    price_id = Column(Integer, primary_key=True)
    part_id = Column(String(250), nullable=False)
    name_of_part = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, price_id, part_id, name_of_part):
        """ Initializes a blood pressure reading """
        self.price_id = price_id
        self.part_id = part_id
        self.name_of_part = name_of_part
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['price_id'] = self.price_id
        dict['part_id'] = self.part_id
        dict['name_of_part'] = self.name_of_part
        dict['date_created'] = self.date_created

        return dict
