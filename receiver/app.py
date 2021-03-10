import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
from pykafka import KafkaClient
import datetime


import json

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def car_part_order(body):
    logger.info(f'Received event car part request with a unique id of {body["part_id"]}')
    headers = {'Content-Type': 'application/json'}
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer =  topic.get_sync_producer()

    msg = { "type":"carpart", 
             "datetime" : datetime.datetime.now().strftime("%Y-m-%dT%H:%M:%S"),
                "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    
    logger.info(f'Returned event car part response {body["part_id"]} with status 201')

    return NoContent, 201


def cleaning_product_order(body):
    logger.info(f'Received event cleaning product request with a unique id of {body["type_id"]}')
    headers = {'Content-Type': 'application/json'}
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer =  topic.get_sync_producer()

    msg = { "type":"cleaningproduct", 
             "datetime" : datetime.datetime.now().strftime("%Y-m-%dT%H:%M:%S"),
                "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))




    logger.info(f'Returned event cleaning product response {body["type_id"]} with status 201')

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
