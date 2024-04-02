from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class NoteContentTests(TestCase):
    """Класс тестов контента."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='hix', password='password'
        )
        cls.note1 = Note.objects.create(
            title='Заметка 1',
            text='Текст заметки 1',
            author=cls.user
        )
        cls.note2 = Note.objects.create(
            title='Заметка 2',
            text='Текст заметки 2',
            author=cls.user
        )

    def user_login(self):
        """Метод для входа в систему."""
        self.client.login(username='hix', password='password')

    def test_individual_note_passed_to_list_view(self):
        """Отдельная заметка передаётся на страницу списка заметок."""
        self.user_login()
        response = self.client.get(reverse('notes:list'))
        self.assertIn(self.note1, response.context['object_list'])
        self.assertIn(self.note2, response.context['object_list'])

    def test_notes_of_other_users_not_in_list_view(self):
        """
        Заметки пользователей не попадают
        на страницу списка заметок другого пользователя.
        """
        other_user = User.objects.create_user(
            username='other_user', password='password'
        )
        other_note = Note.objects.create(
            title='Заметка другого пользователя',
            text='Текст заметки другого пользователя',
            author=other_user
        )
        self.user_login()
        response = self.client.get(reverse('notes:list'))
        self.assertNotIn(other_note, response.context['object_list'])

    def test_note_view_contains_form(self):
        """Страница создания и редактирования заметки содержит форму."""
        self.user_login()
        response_create = self.client.get(reverse('notes:add'))
        self.assertIsNotNone(response_create.context['form'])
        note = Note.objects.create(
            title='Test Note', text='Test Text', author=self.user
        )
        response_edit = self.client.get(reverse(
            'notes:edit', kwargs={'slug': note.slug}
        ))
        self.assertIsNotNone(response_edit.context['form'])
