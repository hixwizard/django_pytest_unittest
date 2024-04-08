from django.contrib.auth.models import User
from django.test import Client, TestCase
from notes.models import Note


class CommonTestSetupMixin(TestCase):
    """Фикстуры."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note1 = Note.objects.create(
            title='Заголовок1', text='Текст1', author=cls.author
        )
        cls.note2 = Note.objects.create(
            title='Заголовок2', text='Текст2', author=cls.author
        )
