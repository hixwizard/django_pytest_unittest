from django.test import TestCase
from django.urls import reverse

from .common import CommonTestSetupMixin
from notes.models import Note


class NoteContentTests(CommonTestSetupMixin, TestCase):
    """Класс тестов контента."""

    def setUp(self):
        """Авторизация."""
        super().setUp()
        self.client.force_login(self.author)

    def test_individual_note_passed_to_list_view(self):
        """Отдельная заметка передаётся на страницу списка заметок."""
        response = self.client.get(reverse('notes:list'))
        self.assertIn(self.note1, response.context['object_list'])
        self.assertIn(self.note2, response.context['object_list'])

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
        response = self.client.get(reverse('notes:list'))
        self.assertNotIn(other_note, response.context['object_list'])

    def test_note_create_view_contains_form(self):
        """Страница создания заметки содержит форму."""
        response = self.client.get(reverse('notes:add'))
        self.assertIsNotNone(response.context['form'])

    def test_note_edit_view_contains_form(self):
        """Страница редактирования заметки содержит форму."""
        note = Note.objects.create(
            title='Заголовок', text='Текст', author=self.author
        )
        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': note.slug})
        )
        self.assertIsNotNone(response.context['form'])
