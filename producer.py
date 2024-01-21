import json
import pika
from models import Contact
from load_data import load_contacts
from mongoengine.connection import get_db
from docker_manager import run_rabbitmq_container


 # Параметры подключения к RabbitMQ
connection_params = pika.ConnectionParameters(
    host='localhost',  # IP-адрес RabbitMQ
    port=5672,          # Порт для подключения к RabbitMQ
    virtual_host='/',
    credentials=pika.PlainCredentials(username='guest', password='guest')
)


def is_models_exists():

    try:
        db = get_db()
        contact_collection_exists = Contact._get_collection().name in db.list_collection_names()

        if contact_collection_exists:
            print("Модель существуе в базе данных.")
            return True
        else:
            print("Модель отсутствует в базе данных.")
            return False

    except Exception as e:
        print(f"Ошибка при проверке наличия моделей в базе данных: {e}")
        return False


def check_rabbitmq_connection():

    print("Проверяем соединение с RabbitMQ...")
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        print("Соединение с RabbitMQ установлено успешно.")
        connection.close()
        return True
    except pika.exceptions.AMQPError as e:
        print(f"Произошла ошибка при подключении к RabbitMQ: {e}")
        return False


def publish_contacts_to_sms(contacts):

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='sms_queue')

    for contact in contacts:
        message_body = {f'{contact.full_name}! Ваша заявка принята. Вам присвоен идентификатор contact_id': str(contact.id), 'Канал': str(contact.preferred_contact_method), 'Телефон': str(contact.phone_number)}
        print(f"Отправляем сообщение: {message_body}")
        channel.basic_publish(exchange='', routing_key='sms_queue', body=json.dumps(message_body))
        contact.message_sent = True
        contact.save()

    connection.close()


def publish_contacts_to_email(contacts):

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='email_queue')

    for contact in contacts:
        message_body = {f'{contact.full_name}! Ваша заявка принята. Вам присвоен идентификатор contact_id': str(contact.id), 'Канал': str(contact.preferred_contact_method), 'Email': str(contact.email)}
        print(f"Отправляем сообщение: {message_body}")
        channel.basic_publish(exchange='', routing_key='email_queue', body=json.dumps(message_body))
        contact.message_sent = True
        contact.save()

    connection.close()


def main():

    load_contacts()

    if not check_rabbitmq_connection():
        run_rabbitmq_container()

    contacts_sms = Contact.objects.filter(message_sent=False, preferred_contact_method='sms')
    publish_contacts_to_sms(contacts_sms)
    contacts_email = Contact.objects.filter(message_sent=False, preferred_contact_method='email')
    publish_contacts_to_email(contacts_email)


if __name__ == "__main__":

    main()