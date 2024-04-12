from django.urls import reverse
from django.utils.text import slugify

from .common import CommonTestSetupMixin
from notes.models import Note


class NoteContentTests(CommonTestSetupMixin):
    """Класс тестов контента."""

    def test_individual_note_passed_to_list_view(self):
        """Отдельная заметка передаётся на страницу списка заметок."""
        test_note1 = Note.objects.create(
            title='Заголовок1', text='Текст1', author=self.author,
            slug=slugify('Заголовок1')
        )
        test_note2 = Note.objects.create(
            title='Заголовок2', text='Текст2', author=self.author,
            slug=slugify('Заголовок2')
        )
        response = self.author_client.get(self.LIST_VIEW_URL)
        self.assertIn(test_note1, response.context['object_list'])
        self.assertIn(test_note2, response.context['object_list'])

    def test_notes_of_other_users_not_in_list_view(self):
        """
        Заметки пользователей не попадают
        на страницу списка заметок другого пользователя.
        """
        other_note = Note.objects.create(
            title='Заметка читателя',
            text='Текст заметки читателя',
            author=self.author
        )
        response = self.reader_client.get(self.LIST_VIEW_URL)
        self.assertNotIn(other_note, response.context['object_list'])

    def test_note_create_view_contains_form(self):
        """Страница создания заметки содержит форму."""
        response = self.author_client.get(self.ADD_NOTE_URL)
        self.assertIsNotNone(response.context['form'])

    def test_note_edit_view_contains_form(self):
        """Страница редактирования заметки содержит форму."""
        note = Note.objects.create(
            title='Заголовок', text='Текст', author=self.author
        )
        response = self.author_client.get(
            reverse('notes:edit', kwargs={'slug': note.slug})
        )
        self.assertIsNotNone(response.context['form'])
