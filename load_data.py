import json
from models import Author, Quote, Contact
from faker import Faker


fake = Faker()


def load_authors():

    print("Загружаем данные модели Authors")
    with open('authors.json', 'r', encoding='utf-8') as file:
        authors_data = json.load(file)
        for author_data in authors_data:
            author = Author(**author_data)
            author.save()


def load_quotes():

    print("Загружаем данные модели Quotes")
    authors_dict = {author.fullname: author for author in Author.objects}
    with open('quotes.json', 'r', encoding='utf-8') as file:
        quotes_data = json.load(file)
        for quote_data in quotes_data:
            author_name = quote_data['author']
            author = authors_dict.get(author_name)
            if author:
                quote_data['author'] = author
                Quote(**quote_data).save()


def load_contacts():
    
    print("Загружаем данные модели Contacts")
    for _ in range(20):
        contact = Contact(
            full_name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
            preferred_contact_method=fake.random_element(elements=Contact.CONTACT_METHOD_CHOICES),
            company_name=fake.company()
        )
        contact.save()
