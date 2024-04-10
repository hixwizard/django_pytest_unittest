from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test import Client

from news.forms import BAD_WORDS
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    """Создание пользователя с ролью автора."""
    return User.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Создание клиента с ролью автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader():
    """Создание обычного пользователя."""
    return User.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    """Создание обычного клиента."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    """Создание новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст 0',
        date=timezone.now()
    )


@pytest.fixture
def list_news():
    """Создание списка новостей."""
    news_list = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title='Заголовок',
            text='Текст {index}',
            date=timezone.now() + timedelta(days=i)
        )
        news_list.append(news)
    News.objects.bulk_create(news_list)


@pytest.fixture
def comments_list(author, news):
    """Создание списка новостей."""
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text='Test commen {i}',
        )
        comment.created = now + timedelta(days=i)
        comment.save()


@pytest.fixture
def comment(author, news):
    """Создание комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Test comment',
    )


@pytest.fixture
def form_data():
    """Кверисет комментария."""
    return {
        'title': 'Test title',
        'text': 'Test text',
    }


@pytest.fixture
def url_home():
    """Адрес домашней страницы."""
    return reverse('news:home')


@pytest.fixture
def url_detail(news):
    """Адрес страницы с новостями"""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_edit(comment):
    """URL для редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_delete(comment):
    """URL для удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_login():
    """Адрес страницы входа."""
    return reverse('users:login')


@pytest.fixture
def url_logout():
    """Адрес страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    """Адрес страницы решистриции."""
    return reverse('users:signup')


@pytest.fixture
def bad_words():
    """Плохие слова."""
    return {'text': f' Текст {BAD_WORDS[0]}, текст.'}
