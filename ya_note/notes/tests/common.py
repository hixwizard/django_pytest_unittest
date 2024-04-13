from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class CommonTestSetupMixin(TestCase):
    """Миксин для общих настроек тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.guest_client = Client()
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note1 = Note.objects.create(
            title='Заголовок1', text='Текст1', author=cls.author
        )
        cls.note2 = Note.objects.create(
            title='Заголовок2', text='Текст2', author=cls.author
        )
        cls.new_note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки'
        }
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    SLUG = {'slug': 'some-slug'}
    LIST_VIEW_URL = reverse('notes:list')
    ADD_NOTE_URL = reverse('notes:add')
    EDIT_NOTE_URL = reverse('notes:edit', kwargs=SLUG)
    DELETE_NOTE_URL = reverse('notes:delete', kwargs=SLUG)
    DETAIL_NOTE_URL = reverse('notes:detail', kwargs=SLUG)
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    SUCCESS_URL = reverse('notes:success')
