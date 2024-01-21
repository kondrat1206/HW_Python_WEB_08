from mongoengine import Document, connect
from mongoengine.fields import EmailField, BooleanField, StringField, ListField, ReferenceField


connection_string = "mongodb+srv://kondrat1206:ChSJUo9Jln1ioXfE@cluster0.8ryyiyk.mongodb.net/my_db?retryWrites=true&loadBalanced=false&replicaSet=atlas-up602c-shard-0&readPreference=primary&srvServiceName=mongodb&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1"

# Подключение к MongoDB
connect(host=connection_string)

class Author(Document):
    fullname = StringField(required=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()

class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author)
    quote = StringField()

class Contact(Document):
    CONTACT_METHOD_CHOICES = ('sms', 'email')
    full_name = StringField(required=True)
    email = EmailField(required=True)
    phone_number = StringField()
    preferred_contact_method = StringField(choices=CONTACT_METHOD_CHOICES, default='email')
    message_sent = BooleanField(default=False)
    company_name = StringField()