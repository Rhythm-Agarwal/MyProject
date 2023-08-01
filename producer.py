# import pip

# package_names=['kafka'] #packages to install
# pip.main(['install'] + package_names + ['--upgrade'])

from faker import Faker
from kafka import KafkaProducer
import json
import time
from data import get_registered_user

fake=Faker()

def get_registered_user():
    return {
        "name": fake.name(),
        "address": fake.address(),
        "created_at": fake.year()
    }

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=json_serializer)

if __name__ == '__main__':
    while 1==1:
        registered_user = get_registered_user()
        print(registered_user)
        producer.send('registered_user', registered_user)
        time.sleep(4)

# from kafka import KafkaProducer
# import json
# import time
# from data import get_registered_user

# class JsonSerializer:
#     def __init__(self):
#         self.encoder = json.JSONEncoder()

#     def __call__(self, data):
#         return self.encoder.encode(data).encode('utf-8')

# producer = KafkaProducer(
#     bootstrap_servers=['localhost:9092'],
#     value_serializer=JsonSerializer()
# )

# if __name__ == '__main__':
#     while True:
#         registered_user = get_registered_user()
#         print(registered_user)
#         producer.send('registered_user', registered_user)
#         time.sleep(5)
