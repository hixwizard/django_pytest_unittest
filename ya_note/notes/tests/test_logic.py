from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from .common import CommonTestSetupMixin


class NoteLogicTests(CommonTestSetupMixin, TestCase):
    """Класс тестов логики."""

    def test_authenticated_user_can_create_note(self):
        """Проверка, что залогиненный пользователь может создать заметку."""
        self.client.force_login(self.author)
        initial_note_count = Note.objects.count()
        response = self.client.post(reverse('notes:add'), {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки'
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count + 1)

    def test_anonymous_user_cannot_create_note(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        initial_note_count = Note.objects.count()
        response = self.client.post(reverse('notes:add'), {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки'
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count)

    def test_unique_slug_generation(self):
        """Проверка, что нельзя создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        first_response = self.client.post(reverse('notes:add'), {
            'title': 'First note',
            'text': 'Text of first note',
            'slug': 'my-slug'
        })
        self.assertEqual(first_response.status_code, HTTPStatus.FOUND)
        second_response = self.client.post(reverse('notes:add'), {
            'title': 'Second note',
            'text': 'Text of second note',
            'slug': 'my-slug'
        })
        self.assertEqual(second_response.status_code, HTTPStatus.OK)
        form = second_response.context['form']
        self.assertTrue('slug' in form.errors)
        self.assertEqual(
            form.errors['slug'],
            ['my-slug - такой slug уже существует, '
             'придумайте уникальное значение!']
        )

    def test_slug_generation(self):
        """Проверка генерации slug."""
        note = Note.objects.create(
            title="Test note",
            text="Text of the test note",
            author=self.author
        )
        generated_slug = slugify(note.title)
        self.assertEqual(note.slug, generated_slug)

    def test_user_can_update_own_note(self):
        """Проверка, что пользователь может редактировать свою заметку."""
        self.client.force_login(self.author)
        note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст тестовой заметки',
            author=self.author
        )
        self.client.post(
            reverse('notes:edit', kwargs={'slug': note.slug}),
            {'title': 'Новый заголовок', 'text': 'Новый текст'}
        )
        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.title, 'Новый заголовок')
        self.assertEqual(updated_note.text, 'Новый текст')

    def test_user_can_delete_own_note(self):
        """Проверка, что пользователь может удалить свою заметку."""
        self.client.force_login(self.author)
        note = Note.objects.create(
            title='Заметка для удаления',
            text='Текст заметки',
            author=self.author
        )
        self.client.post(reverse(
            'notes:delete', kwargs={'slug': note.slug}
        ))
        self.assertFalse(Note.objects.filter(id=note.id).exists())

    def test_user_cannot_update_other_users_note(self):
        """Проверка, что пользователь не может редактировать чужую заметку."""
        other_note = Note.objects.create(
            title='Заметка другого пользователя',
            text='Текст заметки',
            author=self.reader
        )
        self.client.force_login(self.author)
        response = self.client.post(
            reverse('notes:edit', kwargs={'slug': other_note.slug}),
            {'title': 'Попытка изменения чужой заметки', 'text': 'Новый текст'}
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_cannot_delete_other_users_note(self):
        """Проверка, что пользователь не может удалить чужую заметку."""
        other_note = Note.objects.create(
            title='Заметка для удаления другого пользователя',
            text='Текст заметки',
            author=self.reader
        )
        self.client.force_login(self.author)
        self.client.post(reverse(
            'notes:delete', kwargs={'slug': other_note.slug}
        ))
        self.assertTrue(Note.objects.filter(id=other_note.id).exists())
