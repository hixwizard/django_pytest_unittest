import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def news_data():
    news = News.objects.create(title='Заголовок', text='Заголовок')
    author = User.objects.create(username='Лев Толстой')
    reader = User.objects.create(username='Читатель простой')
    comment = Comment.objects.create(
        news=news, author=author, text='Текст комментария'
    )
    return news, author, reader, comment


@pytest.mark.django_db
def test_home_page_availability(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_page_availability(client, news_data):
    news, _, _, _ = news_data
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name', ['users:login', 'users:logout', 'users:signup']
)
@pytest.mark.django_db
def test_auth_pages_availability(client, url_name):
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
@pytest.mark.django_db
def test_edit_delete_comment_pages_access(client, news_data, url_name):
    _, author, reader, comment = news_data
    url = reverse(url_name, args=[comment.id])

    client.force_login(author)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    client.force_login(reader)
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
@pytest.mark.django_db
def test_anonymous_redirect_to_login(client, news_data, url_name):
    _, _, _, comment = news_data
    url = reverse(url_name, args=[comment.id])
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'

    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
