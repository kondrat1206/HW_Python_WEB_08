import docker
from time import sleep

def run_redis_container():

    print("Запускаем Redis-контейнер...")
    # Создаем клиент Docker
    client = docker.from_env()
    # Название образа Redis
    redis_image = "redis:latest"

    try:
        # Скачиваем образ, если его нет на локальной машине
        client.images.pull(redis_image)
        # Запускаем контейнер с проброской порта
        container = client.containers.run(
            image=redis_image,
            detach=True,  # Запускаем контейнер в фоновом режиме
            ports={'6379/tcp': 6379}  # Пробрасываем порт 6379 из контейнера на хост
        )
        print(f"Контейнер {container.id} запущен успешно.")
    except docker.errors.APIError as e:
        print(f"Произошла ошибка при работе с Docker API: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def run_rabbitmq_container():

    print("Запускаем RabbitMQ-контейнер...")
    # Создаем клиент Docker
    client = docker.from_env()
    # Название образа RabbitMQ
    rabbitmq_image = "rabbitmq:3-management"

    try:
        # Скачиваем образ, если его нет на локальной машине
        client.images.pull(rabbitmq_image)
        # Запускаем контейнер с проброской портов
        container = client.containers.run(
            image=rabbitmq_image,
            detach=True,  # Запускаем контейнер в фоновом режиме
            ports={'5672/tcp': 5672, '15672/tcp': 15672},  # Пробрасываем порты 5672 и 15672
            environment={"RABBITMQ_DEFAULT_USER": "guest", "RABBITMQ_DEFAULT_PASS": "guest"}  # Устанавливаем пользовательские переменные окружения
        )
        sleep(15)
        print(f"Контейнер {container.id} запущен успешно.")
    except docker.errors.APIError as e:
        print(f"Произошла ошибка при работе с Docker API: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

