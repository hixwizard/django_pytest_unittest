from datetime import timedelta, timezone

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import News, Comment
from django.utils import timezone


@pytest.fixture
def author(django_user_model):
    """Создание пользователя с ролью автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создание обычного пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Создание клиента с ролью автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Создание обычного клиента."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def new():
    """Создание новости."""
    return News.objects.create(
        title='Заголовок',
        text='тест новости',
    )


@pytest.fixture
def pk_for_args(new):
    """Ключ для заметки."""
    return (new.pk,)


@pytest.fixture
def create_news_list():
    """Создание списка новостей."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comments_list(author, new):
    """Создание списка комментариев к новости."""
    comments = [
        {'text': f'Комментарий {i}', 'author': author, 'news': new}
        for i in range(1, 11)
    ]
    return Comment.objects.bulk_create([Comment(**data) for data in comments])


@pytest.fixture
def comment_data():
    """Кверисет комментария."""
    return {
        'text': 'Some comment'
    }


@pytest.fixture
def home_url():
    """Адрес домашней страницы."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Адрес страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Адрес страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def detail_url(new):
    """Адрес страницы с новостями"""
    return reverse('news:detail', args=[new.pk])


@pytest.fixture
def comment_edit_url(create_comments_list):
    """URL для редактирования комментария."""
    return reverse('news:edit', args=(create_comments_list[0].pk,))


@pytest.fixture
def comment_delete_url(create_comments_list):
    """URL для удаления комментария."""
    return reverse('news:delete', args=(create_comments_list[0].pk,))


@pytest.fixture
def news_data():
    """Кверисет новости."""
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'date': timezone.now(),
        'author': 'Автор'
    }


@pytest.fixture
def comment_data():
    """Кверисет комментария."""
    return {
        'text': 'Some comment'
    }
