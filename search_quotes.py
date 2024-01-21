from models import Quote, Author
from docker_manager import run_redis_container
from mongoengine.connection import get_db
from load_data import load_authors, load_quotes
import re
import redis
import json
import pickle

# Connection Pool для Redis
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0, socket_timeout=1)
redis_client = redis.StrictRedis(connection_pool=redis_pool)

def is_models_exists():
    try:
        db = get_db()

        # Проверяем наличие коллекций в базе данных
        author_collection_exists = Author._get_collection().name in db.list_collection_names()
        quote_collection_exists = Quote._get_collection().name in db.list_collection_names()

        if author_collection_exists and quote_collection_exists:
            print("Все Модели существуют в базе данных.")
            return True
        else:
            print("Одна или несколько моделей отсутствуют в базе данных.")
            return False

    except Exception as e:
        print(f"Ошибка при проверке наличия моделей в базе данных: {e}")
        return False


def check_redis_connection():
    try:
        with redis_client.pipeline() as pipe:
            pipe.ping()
            response = pipe.execute()[0]

        if response:
            print("Соединение с Redis успешно установлено.")
            return True
        else:
            print("Не удалось установить соединение с Redis.")
            return False

    except Exception as e:
        print(f"Ошибка при проверке соединения с Redis: {e}")
        return False


def search_quotes(command):
    try:
        parts = command.split(':', 1)
        print(parts)
        if len(parts) != 2:
            return []

        field, value = parts
        field = field.strip().lower()
        value = value.strip()
        redis_key = f"search:{field}:{value}"

        cached_result = redis_client.get(redis_key)
        if cached_result:
            return pickle.loads(cached_result)

        regex_pattern = re.compile(f'.*{re.escape(value)}.*', re.IGNORECASE)

        with redis_client.pipeline() as pipe:
            if field == 'name':
                authors = Author.objects.filter(fullname__regex=regex_pattern)
                author_ids = [author.id for author in authors]
                result = Quote.objects.filter(author__in=author_ids)
            elif field == 'tag':
                result =  Quote.objects.filter(tags__regex=regex_pattern)
            elif field == 'tags':
                tags = [tag.strip() for tag in value.split(',')]
                result =  Quote.objects.filter(tags__in=tags)

            pipe.set(redis_key, pickle.dumps(result), ex=300)
            pipe.execute()

        return result

    except Exception as e:
        print(f"Ошибка при поиске цитат: {e}")
        return []


def main():

    if not is_models_exists():
        load_authors()
        load_quotes()

    if not check_redis_connection():
        run_redis_container()

    while True:
        user_input = input("Введите строку поиска: ").strip()

        if user_input == 'exit':
            break

        quotes = search_quotes(user_input)
        for quote in quotes:
            print(f"Author: {quote.author.fullname}, Quote: {quote.quote}, Tags: {quote.tags}")


if __name__ == "__main__":

    main()
