from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .common import CommonTestSetupMixin

User = get_user_model()


class NoteRoutesTestCase(CommonTestSetupMixin):
    """Класс тестов маршрутизации."""

    def test_pages_and_accessibility(self):
        """
        Проверка доступности страниц,
        доступа к ним для различных пользователей.
        """
        urls_and_statuses = [
            (self.client, self.HOME_URL, HTTPStatus.OK),
            (self.client, self.LOGIN_URL, HTTPStatus.OK),
            (self.client, self.LOGOUT_URL, HTTPStatus.OK),
            (self.client, self.SIGNUP_URL, HTTPStatus.OK),
            (self.author_client,
             reverse('notes:edit', kwargs={'slug': self.note1.slug}),
             HTTPStatus.OK),
            (self.author_client,
             reverse('notes:delete', kwargs={'slug': self.note1.slug}),
             HTTPStatus.OK),
            (self.author_client,
             reverse('notes:detail', kwargs={'slug': self.note1.slug}),
             HTTPStatus.OK),
            (self.reader_client,
             reverse('notes:edit', kwargs={'slug': self.note1.slug}),
             HTTPStatus.NOT_FOUND),
            (self.reader_client,
             reverse('notes:delete', kwargs={'slug': self.note1.slug}),
             HTTPStatus.NOT_FOUND),
            (self.reader_client,
             reverse('notes:detail', kwargs={'slug': self.note1.slug}),
             HTTPStatus.NOT_FOUND),
            (self.reader_client, self.ADD_NOTE_URL, HTTPStatus.OK),
            (self.reader_client, self.SUCCESS_URL, HTTPStatus.OK),
            (self.reader_client, self.LIST_VIEW_URL, HTTPStatus.OK),
        ]

        for user, url, status in urls_and_statuses:
            with self.subTest(user=user, url=url):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест переадресации для незарегистрированного пользователя."""
        REDIRECT_URLS = (
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:edit', {'slug': self.note1.slug}),
            ('notes:delete', {'slug': self.note1.slug}),
            ('notes:detail', {'slug': self.note1.slug}),
        )

        login_url = reverse('users:login')
        for name, args in REDIRECT_URLS:
            url = reverse(name, kwargs=args)
            with self.subTest(name=name):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
