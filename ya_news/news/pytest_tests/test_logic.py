import pytest
from http import HTTPStatus
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def setup_news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def setup_authenticated_client(setup_news):
    username = 'Мимо Крокодил'
    if User.objects.filter(username=username).exists():
        username = f'{username}_{timezone.now().strftime("%Y%m%d%H%M%S")}'
    user = User.objects.create(username=username)
    client = Client()
    client.force_login(user)
    return user, client, setup_news


@pytest.fixture
def setup_comment(setup_news):
    author = User.objects.create(username='Автор комментария')
    return Comment.objects.create(
        news=setup_news,
        author=author,
        text='Текст комментария'
    )


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, setup_news):
    url = reverse('news:detail', args=(setup_news.id,))
    response = client.post(url, data={'text': 'Some comment'})
    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_user_can_create_comment(client, setup_authenticated_client):
    user, auth_client, news = setup_authenticated_client
    url = reverse('news:detail', args=(news.id,))
    response = auth_client.post(url, data={'text': 'Some comment'})
    assert Comment.objects.count() == 1
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_user_cant_use_bad_words(client, setup_authenticated_client):
    user, auth_client, news = setup_authenticated_client
    url = reverse('news:detail', args=(news.id,))
    response = auth_client.post(
        url, data={'text': f'Some {BAD_WORDS[0]} comment'}
    )
    assert Comment.objects.count() == 0
    assert response.context['form'].errors['text'] == [WARNING]


@pytest.mark.django_db
def test_author_can_edit_comment(client):
    user = User.objects.create(username='Мимо Крокодил')
    news = News.objects.create(title='Заголовок', text='Текст')
    comment = Comment.objects.create(
        news=news, author=user, text='Текст комментария'
    )
    auth_client = Client()
    auth_client.force_login(user)
    url = reverse('news:edit', args=(comment.id,))
    updated_text = 'Updated comment'
    data = {'text': updated_text}
    response = auth_client.post(url, data=data)
    redirected_path = urlparse(response.url).path
    assert response.status_code == HTTPStatus.FOUND
    expected_url = reverse('news:detail', args=(comment.news.id,))
    assert redirected_path == expected_url, (
        f"Expected URL: {expected_url}, "
        f"Redirected URL: {response.url}"
    )
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == updated_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    client, setup_authenticated_client, setup_comment
):
    other_user, other_auth_client, news = setup_authenticated_client
    comment = setup_comment
    url = reverse('news:edit', args=(comment.id,))
    response = other_auth_client.post(url, data={'text': 'Trying to update'})
    comment.refresh_from_db()
    assert comment.text != 'Trying to update'
    assert response.status_code == HTTPStatus.NOT_FOUND
