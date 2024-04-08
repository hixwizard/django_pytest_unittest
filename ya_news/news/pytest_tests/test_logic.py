from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, comment_data, detail_url):
    """Гость не может оставлять комментарий."""
    response = client.post(detail_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(**comment_data).exists()


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, comment_data, detail_url):
    """Пользователь может оставлять комментарий."""
    response = auth_client.post(detail_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(**comment_data).exists()


@pytest.mark.django_db
def test_user_cant_use_bad_words(auth_client, comment_data, detail_url):
    """Пользователь не может использовать плохие слова."""
    comment_data['text'] = f'Текст {BAD_WORDS}'
    response = auth_client.post(detail_url, data=comment_data)
    assertFormError(response, 'form', 'text', errors=(WARNING,))
    assert not Comment.objects.filter(**comment_data).exists()


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment_data, comment_edit_url
):
    """Автор комментария может редактировать свой комментарий."""
    response = author_client.post(comment_edit_url, data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    edited_comment = Comment.objects.get(pk=comment_edit_url.split('/')[-1])
    assert edited_comment.text == comment_data['text']
    assert edited_comment.author == comment_data['author']


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, comment_data, comment_delete_url
):
    """Автор комментария может удалить свой комментарий."""
    response = author_client.post(comment_delete_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment_data.id).exists()


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    author_client, comment_data, comment_edit_url
):
    """Пользователь не может редактировать чужой комментарий."""
    response = author_client.post(comment_edit_url, data=comment_data)
    assert response.status_code == HTTPStatus.FORBIDDEN
    edited_comment = Comment.objects.get(pk=comment_edit_url.split('/')[-1])
    assert edited_comment.text != comment_data['text']


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_data, comment_delete_url
):
    """Пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(comment_delete_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment_data.id).exists()
