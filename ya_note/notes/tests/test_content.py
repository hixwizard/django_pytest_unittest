from django.urls import reverse

from .common import CommonTestSetupMixin
from notes.models import Note
from notes.forms import NoteForm


class NoteContentTests(CommonTestSetupMixin):
    """Класс тестов контента."""

    def test_individual_note_passed_to_list_view(self):
        """Отдельная заметка передаётся на страницу списка заметок."""
        response = self.author_client.get(self.LIST_VIEW_URL)
        # этот тест всё время выдаёт ошибку, если я пробую сделать его от гостя
        # TypeError: 'NoneType' object is not subscriptable
        # как бы я не старался добавить заметки, у меня пустой список
        self.assertIn(self.note1, response.context['object_list'])
        self.assertIn(self.note2, response.context['object_list'])

    def test_notes_of_other_users_not_in_list_view(self):
        """
        Заметки пользователей не попадают
        на страницу списка заметок другого пользователя.
        """
        response = self.reader_client.get(self.LIST_VIEW_URL)
        self.assertNotIn(self.note1, response.context['object_list'])

    def test_note_create_view_contains_form(self):
        """Страница создания заметки содержит форму."""
        response = self.author_client.get(self.ADD_NOTE_URL)
        self.assertIsNotNone(response.context['form'])
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_edit_view_contains_form(self):
        """Страница редактирования заметки содержит форму."""
        note = Note.objects.create(
            title='Заголовок', text='Текст', author=self.author
        )
        response = self.author_client.get(
            reverse('notes:edit', kwargs={'slug': note.slug})
        )
        self.assertIsNotNone(response.context['form'])
