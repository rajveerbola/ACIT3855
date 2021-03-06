import connexion
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import yaml
import logging
import logging.config
import requests
from pykafka import KafkaClient
import os
import json
import datetime

with open("app_conf.yaml", "r") as f:
    app_config = yaml.safe_load(f.read())
with open('app_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


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
                           params={"timestamp": stats['last_updated']})
    cleaning = requests.get(f"{app_config['eventstore']['url']}/orders/cleaning-product",
                            params={"timestamp": stats['last_updated']})

    stats['num_car_parts'] = len(carpart.json())
    stats['num_cleaning_products'] = len(cleaning.json())

    sum_price = 0
    max_price = 0

    for event in carpart.json():
        print(carpart.json())
        sum_price += event['price_id']
        if event['price_id'] > max_price:
            max_price = event['price_id']
    if len(carpart.json()) > 0:
        stats['average_car_part_price'] = sum_price / len(carpart.json())
    stats['max_price'] = max_price
    stats['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(stats_file_name, 'w') as f:
        f.write(json.dumps(stats, indent=4))


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])

    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
