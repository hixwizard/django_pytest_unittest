from http import HTTPStatus

from django.http import HttpResponseRedirect
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from .common import CommonTestSetupMixin
from notes.forms import WARNING


class NoteLogicTests(CommonTestSetupMixin):
    """Класс тестов логики."""

    def test_authenticated_user_can_create_note(self):
        """Проверка, что залогиненный пользователь может создать заметку."""
        initial_note_count = Note.objects.count()
        response = self.author_client.post(
            self.ADD_NOTE_URL, self.new_note_data
        )
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count + 1)
        last_note = Note.objects.latest('pk')
        self.assertEqual(last_note.author, self.author)
        self.assertEqual(last_note.text, self.new_note_data['text'])

    def test_anonymous_user_cannot_create_note(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        initial_note_count = Note.objects.count()
        response = self.client.post(self.ADD_NOTE_URL, self.new_note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count)

    def test_unique_slug_generation(self):
        """Проверка, что нельзя создать две заметки с одинаковым slug."""
        slug = 'my-slug'
        first_response = self.author_client.post(self.ADD_NOTE_URL, {
            'title': 'First note',
            'text': 'Text of first note',
            'slug': slug
        })
        self.assertEqual(first_response.status_code, HTTPStatus.FOUND)
        second_response = self.author_client.post(self.ADD_NOTE_URL, {
            'title': 'Second note',
            'text': 'Text of second note',
            'slug': slug
        })
        self.assertEqual(second_response.status_code, HTTPStatus.OK)
        form = second_response.context['form']
        self.assertTrue('slug' in form.errors)
        self.assertEqual(
            form.errors['slug'],
            [slug + WARNING]
        )

    def test_slug_generation(self):
        """Проверка генерации slug при создании заметки без указания слага."""
        slug_note = Note.objects.create(
            title='Название заметки для проверки слага',
            text='Текст заметки для проверки слага',
            author=self.author
        )
        generated_slug = slugify(slug_note.title)
        self.assertEqual(slug_note.slug, generated_slug)

    def test_user_can_update_own_note(self):
        """Проверка, что пользователь может редактировать свою заметку."""
        updated_title = 'Новый заголовок'
        updated_text = 'Новый текст'
        self.author_client.post(
            reverse('notes:edit', kwargs={'slug': self.note1.slug}),
            {'title': updated_title, 'text': updated_text}
        )
        updated_note = Note.objects.get(id=self.note1.id)
        self.assertEqual(updated_note.title, updated_title)
        self.assertEqual(updated_note.text, updated_text)

    def test_user_can_delete_own_note(self):
        """Проверка, что пользователь может удалить свою заметку."""
        test_note = Note.objects.create(
            title='Название новой заметки',
            text='Текст новой заметки',
            author=self.author
        )
        self.assertTrue(Note.objects.filter(id=test_note.id).exists())
        self.author_client.post(reverse(
            'notes:delete', kwargs={'slug': test_note.slug})
        )
        self.assertFalse(Note.objects.filter(id=test_note.id).exists())

    def test_user_cannot_update_other_users_note(self):
        """Проверка, что пользователь не может редактировать чужую заметку."""
        other_note = Note.objects.create(
            title='Заметка другого пользователя',
            text='Текст заметки',
            author=self.author
        )
        original_title = other_note.title
        original_text = other_note.text
        response = self.reader_client.post(
            reverse('notes:edit', kwargs={'slug': other_note.slug}),
            {'title': 'Попытка изменения чужой заметки', 'text': 'Новый текст'}
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        other_note.refresh_from_db()
        self.assertEqual(other_note.title, original_title)
        self.assertEqual(other_note.text, original_text)

    def test_user_cannot_delete_other_users_note(self):
        """Проверка, что пользователь не может удалить чужую заметку."""
        initial_note_count = Note.objects.count()
        original_title = self.note1.title
        original_text = self.note1.text

        self.reader_client.post(reverse(
            'notes:delete', kwargs={'slug': self.note1.slug}
        ))
        self.note1.refresh_from_db()
        self.assertEqual(Note.objects.count(), initial_note_count)
        self.assertEqual(self.note1.title, original_title)
        self.assertEqual(self.note1.text, original_text)
        self.assertTrue(Note.objects.filter(id=self.note1.id).exists())
