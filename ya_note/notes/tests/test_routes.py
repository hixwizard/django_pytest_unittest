from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from .common import CommonTestSetupMixin


class NoteRoutesTestCase(CommonTestSetupMixin, TestCase):
    """Класс тестов маршрутизации."""

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

    def test_availability_for_note_edit_delete_detail(self):
        """Тест доступа для редактирования и удаления."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            urls = (
                ('edit', {'slug': self.note1.slug}),
                ('delete', {'slug': self.note1.slug}),
                ('detail', {'slug': self.note1.slug})
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
            ('notes:edit', {'slug': self.note1.slug}),
            ('notes:delete', {'slug': self.note1.slug}),
            ('notes:detail', {'slug': self.note1.slug}),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
