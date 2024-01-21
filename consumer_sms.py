import json
import pika
from models import Contact
from docker_manager import run_rabbitmq_container
from producer import check_rabbitmq_connection

def process_sms_message(ch, method, properties, body):
    print(f"Получено SMS-сообщение:")
    message = json.loads(body)
    print(message)
    

def main():
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials(username='guest', password='guest')
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='sms_queue')
    
    channel.basic_consume(queue='sms_queue', on_message_callback=process_sms_message, auto_ack=True)

    print('Ожидание SMS-сообщений. Для выхода нажмите CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':

    if not check_rabbitmq_connection():
        run_rabbitmq_container()
        main()
    else:
        main()
