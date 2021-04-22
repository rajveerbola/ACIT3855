import connexion
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import yaml
import logging
import logging.config
import requests
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
import os
import json
import datetime
import os

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


def get_stats():
    stats_file_name = app_config['datastore']['filename']
    with open(stats_file_name) as f:
        stats = json.load(f)

    return stats, 200


def populate_stats():
    stats_file_name = app_config['datastore']['filename']
    if os.path.isfile(stats_file_name):
        with open(stats_file_name) as f:
            stats = json.load(f)
    else:
        stats = {'num_car_parts': 0,
                 'num_cleaning_products': 0,
                 'average_car_part_price': 0,
                 'max_price': 0,
                 'last_updated': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                 }

    carpart = requests.get(f"{app_config['eventstore']['url']}/orders/car-part",
                           params={"start_timestamp": stats['last_updated']; "end_timestamp": 
                                   "current_timestamp"})

    cleaning = requests.get(f"{app_config['eventstore']['url']}/orders/cleaning-product",
                            params={"start_timestamp": stats['last_updated']; "end_timestamp":
                                   "current_timestamp"})

    carpart_results = carpart.json()
    cleaning_results = cleaning.json()

    if carpart.status_code == 200:

    	stats['num_car_parts'] = len(carpart_results)

	sum_price = 0
    	max_price = 0

    	for event in carpart_results:
            print(carpart_results)
            sum_price += event['price_id']
            if event['price_id'] > max_price:
            	max_price = event['price_id']
        stats['max_price'] = max_price

    	if len(carpart.json()) > 0:
            stats['average_car_part_price'] = sum_price / len(carpart.json())

    if cleaning.status_code == 200:

	stats['num_cleaning_products'] = len(cleaning_results)


    stats['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    print(stats)
    with open(stats_file_name, 'w') as f:
        f.write(json.dumps(stats, indent=4))


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])

    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV"  in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
