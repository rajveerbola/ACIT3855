import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType  
from threading import Thread

import os
import json
import datetime
from base import Base
from cleaning_product_order import CleaningProductOrder
from car_part_order import CarPartOrder

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    
    
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s"% app_conf_file)
logger.info("Log Conf File: %s"% log_conf_file)


DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}'
                          f'@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/'
                          f'{app_config["datastore"]["db"]}')

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f'Connecting to Database {app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}')


def car_part_order(body):
    session = DB_SESSION()

    cpo = CarPartOrder(body['price_id'],
                       body['part_id'],
                       body['name_of_part'])

    session.add(cpo)

    session.commit()
    session.close()

    logger.debug(f'Stored event car part request with a unique id of {body["part_id"]}')



def cleaning_product_order(body):
    session = DB_SESSION()

    bp = CleaningProductOrder(body['price_id'],
                              body['brand_id'],
                              body['type_id'])
    session.add(bp)

    session.commit()
    session.close()

    logger.debug(f'Stored event cleaning product request with a unique id of {body["type_id"]}')

    


def get_car_part_order(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")      
    print(timestamp_datetime)

    readings = session.query(CarPartOrder).filter(and_(CarPartOrder.date_created >=
                                                start_timestamp_datetime,
                                                CarPartOrder.date_created < end_timestamp_datetime))
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Car Part Order after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200


def get_cleaning_product_order(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")      
    print(timestamp_datetime)
    
    readings = session.query(CleaningProductOrder).filter(and_(CleaningProductOrder.date_created >=
                                                        start_timestamp_datetime,
                                                        CleaningProductOrder.date_created < end_timestamp_datetime))
    results_list = []
    print(readings)
    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Cleaning Product Order after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def process_messages():
                 
    retry = 0
    max_retry = 100
    
    while retry < max_retry:
        logger.info("Connecting to Kafka" {retry} of {max_retry})
        try:

            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])] 
        
        expect:
                 logger.error("Failed to connect to Kafka")
                 retry += 1
                 time.sleep(3)
                 
                     
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                            reset_offset_on_start=False,
                                            auto_offset_reset=OffsetType.LATEST)
       
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "carpart":
            car_part_order(payload)


        elif msg["type"] == "cleaningproduct":
            cleaning_product_order(payload)
        
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
