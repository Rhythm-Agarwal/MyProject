# import pip

# package_names=['psycopg2', 'confluent-kafka'] #packages to install
# pip.main(['install'] + package_names + ['--upgrade']) 

import psycopg2
from confluent_kafka import Producer 
import logging 
from datetime import datetime
import time 

# Configure logging
logging.basicConfig(filename='logstash-plain.txt', level=logging.ERROR)

try:
    connection = psycopg2.connect(
    host='localhost',
    port=5432,
    database='fastapi',
    user='postgres',
    password='root'
    )
    cur = connection.cursor()
    producer = Producer({
    'bootstrap.servers': 'localhost:9092'
    #'client.id': 'your_client_id'
    })
    kafka_topic = 'my-topic'

    # Create a valid timestamp
    last_timestamp = datetime(2023, 7, 1, 0, 0, 0)  # Adjust the date and time as needed

    query = "SELECT title, id, content, published, created_at FROM posts WHERE created_at > %s"
    #query = "SELECT published FROM posts"

    # # Function to retrieve the last processed timestamp from a file
    def get_last_processed_timestamp():
        try:
            with open('last_processed_timestamp.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return '1970-01-01 00:00:00'  # Initial timestamp if the file doesn't exist

    # # Function to update the last processed timestamp in a file
    def update_last_processed_timestamp(timestamp):
        with open('last_processed_timestamp.txt', 'w') as file:
            file.write(timestamp)
    while True:
    # Fetch data from PostgreSQL and publish to Kafka
        try:
        # Get the last known timestamp processed
            last_timestamp = get_last_processed_timestamp()

        # Execute the query with the last known timestamp
            cur.execute(query, (last_timestamp,))

            rows = cur.fetchall()   

            for row in rows:
                payload = str(row[0]).encode('utf-8')  # Convert payload to bytes

                producer.produce(kafka_topic, value=payload)

            producer.flush()

        # Update the last processed timestamp if needed
            if rows:
                last_p_timestamp=rows[-1][1]  # Assuming the timestamp column is at index 1 in the result

        except psycopg2.Error as e:
            connection.rollback()
            print(f"Error occurred: {e}")

        finally:
        # Close Kafka producer
        #producer.close()
        # Close PostgreSQL connection
            cur.close()
            cur=connection.cursor()
        time.sleep(5)

    cur.close()
    connection.close()

    # last_processed_record = 0  # Replace with your mechanism to track the last processed record
    # cur = connection.cursor()
    # cur.execute(f"SELECT * FROM posts WHERE id > {last_processed_record}")
    # new_records = cur.fetchall()

    # for record in new_records:
    #     message = {
    #         'value': str(record),  # Modify the value as per your desired message format
    #         'topic': ''
    #     }
    #     producer.produce(**message)

    # # Flush any remaining messages
    # producer.flush()


    # def trigger_function(payload):
    #     # Extract the required data from the payload
    #     data = payload['data']

    #     # Format the data as per your desired message structure
    #     message = {
    #         'key': 'your_message_key',
    #         'value': data,
    #         'topic': 'transactions'
    #     }

    #     # Send the data to Kafka
    #     producer.produce(**message)
    #     producer.flush()

    # cur = connection.cursor()
    # cur.execute("CREATE TRIGGER your_trigger_name AFTER INSERT OR UPDATE OR DELETE ON posts FOR EACH ROW EXECUTE FUNCTION your_trigger_function()")

except Exception as e:
# Log the exception
    logging.exception("An error occurred during synchronization:")
