#!/usr/bin/env python
import ast
import time
import pika
import uuid
import argparse
import urllib.parse

SERVER_URL = 'goose.rmq2.cloudamqp.com'
SERVER_VHOST = 'ocejnqtp'
SERVER_USER = '<REPLACE_ME>'
SERVER_PASSWORD = '<REPLACE_ME>'
SERVER_QUEUE = 'ampfactor-hysea-complete'
CLIENT_QUEUE = 'spada-ampfactor-complete'
SAS_TOKEN = '<REPLACE_ME>'


class Receiver(object):
    def __init__(self):

        self.response: bytes | None = None
        self.corr_id: str | None = None

        self.credentials = pika.PlainCredentials(SERVER_USER, SERVER_PASSWORD)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            SERVER_URL, 5672, SERVER_VHOST, self.credentials, heartbeat=5))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=CLIENT_QUEUE, durable=True, exclusive=False, auto_delete=False)
        self.channel.basic_consume(queue=CLIENT_QUEUE,
                                   on_message_callback=self.on_response,
                                   auto_ack=True)

    def on_response(self, ch: pika.channel.Channel, method: pika.spec.Basic.Deliver, props: pika.spec.BasicProperties, body: bytes):
        print(f"Got response: {body}")
        parsed_response = urllib.parse.parse_qs(body)
        if b'corr_id' in parsed_response and parsed_response[b'corr_id'][0].decode() == self.corr_id:
            self.response = body

    def call(self, hysea_id: int) -> bytes | None:

        self.response = None
        self.corr_id = str(uuid.uuid4())

        body = urllib.parse.urlencode({"hysea_job_id": hysea_id, "corr_id": self.corr_id})
        print(f"Publishing: {body}")
        self.channel.basic_publish(
            exchange='',
            routing_key=SERVER_QUEUE,
            body=body)

        sleep_counter = 0
        while self.response is None:
            if sleep_counter % 10 == 0:
                print("Response is not ready. Waiting for response.")
            time.sleep(1)
            sleep_counter += 1
            self.connection.process_data_events()
        self.channel.close()
        self.connection.close()
        return self.response


def create_url_with_auth(url: str, sas_token: str) -> str:
    return f"{url}?{SAS_TOKEN}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('hysea_id')
    args = parser.parse_args()

    t0 = time.perf_counter()
    receiver = Receiver()

    response = receiver.call(args.hysea_id)
    print("%r" % response)
    t1 = time.perf_counter()
    print(f"Execution time: {t1 - t0} seconds")

    parsed_response = urllib.parse.parse_qs(response)
    result_paths = ast.literal_eval(parsed_response[b'result_paths'][0].decode())
    print("Results paths:")
    for p in result_paths:
        print(create_url_with_auth(p, SAS_TOKEN))
