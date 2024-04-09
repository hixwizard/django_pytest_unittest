from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils.text import slugify

from .common import CommonTestSetupMixin
from notes.models import Note


class NoteContentTests(CommonTestSetupMixin):
    """Класс тестов контента."""

    def setUp(self):
        """Уникальный тестовый пользователь и клиент."""
        super().setUp()
        self.client = Client()
        self.tester = User.objects.create(username='tester')
        self.client.force_login(self.tester)

    def test_individual_note_passed_to_list_view(self):
        """Отдельная заметка передаётся на страницу списка заметок."""
        tester_note1 = Note.objects.create(
            title='Заголовок1', text='Текст1', author=self.tester,
            slug=slugify('Заголовок1')
        )
        tester_note2 = Note.objects.create(
            title='Заголовок2', text='Текст2', author=self.tester,
            slug=slugify('Заголовок2')
        )
        response = self.client.get(self.LIST_VIEW_URL)
        self.assertIn(tester_note1, response.context['object_list'])
        self.assertIn(tester_note2, response.context['object_list'])

    def test_notes_of_other_users_not_in_list_view(self):
        """
        Заметки пользователей не попадают
        на страницу списка заметок другого пользователя.
        """
        other_note = Note.objects.create(
            title='Заметка читателя',
            text='Текст заметки читателя',
            author=self.reader
        )
        response = self.client.get(self.LIST_VIEW_URL)
        self.assertNotIn(other_note, response.context['object_list'])

    def test_note_create_view_contains_form(self):
        """Страница создания заметки содержит форму."""
        response = self.client.get(self.ADD_NOTE_URL)
        self.assertIsNotNone(response.context['form'])

    def test_note_edit_view_contains_form(self):
        """Страница редактирования заметки содержит форму."""
        note = Note.objects.create(
            title='Заголовок', text='Текст', author=self.tester
        )
        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': note.slug})
        )
        self.assertIsNotNone(response.context['form'])
