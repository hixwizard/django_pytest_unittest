from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class NoteRoutesTestCase(TestCase):
    """Класс тестов маршрутизации."""

    @classmethod
    def setUpTestData(cls):
        """Создание пользователя и заметки."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )

    def test_urls_availability(self):
        """Тест адресов."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        self.client.force_login(self.author)
        auth_urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
            ('notes:detail', {'slug': self.note.slug}),
        )
        for name, args in auth_urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_delete_detail(self):
        """Тест доступа для редактирования и удаления."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            urls = (
                ('edit', {'slug': self.note.slug}),
                ('delete', {'slug': self.note.slug}),
                ('detail', {'slug': self.note.slug})
            )
            for name, kwargs in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(f'notes:{name}', kwargs=kwargs)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест переадресации для незарегистрированного пользователя."""
        login_url = reverse('users:login')
        urls = (
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
            ('notes:detail', {'slug': self.note.slug}),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
