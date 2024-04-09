from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects
from django.contrib.auth import get_user_model

from news.models import Comment
from news.forms import WARNING

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, url_detail, url_login
):
    """Гость не может оставлять комментарий."""
    comments_count = Comment.objects.count()
    response = client.post(url_detail, data=form_data)
    expected_redirect = f'{url_login}?next={url_detail}'
    assertRedirects(response, expected_redirect)
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_auth_user_can_create_comment(
    author_client, author, form_data, url_detail, news
):
    """Пользователь может оставлять комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(url_detail, data=form_data)
    comment = Comment.objects.last()
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_comments_count + 1
    assert comment.news == news
    assert comment.author == author
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_users_cant_use_badwords_(
    bad_words, author_client, url_detail
):
    """Пользователь не может использовать плохие слова."""
    comments_count = Comment.objects.count()
    response = author_client.post(url_detail, data=bad_words)
    assertFormError(response, 'form', 'text', [WARNING])
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, form_data, url_edit
):
    """Автор комментария может редактировать свой комментарий."""
    initial_comments_count = Comment.objects.count()
    author_client.post(url_edit, form_data)
    assert Comment.objects.count() == initial_comments_count
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news_id == comment.news_id
    assert comment.author == comment.author
    assert comment.created == comment.created


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, url_delete):
    """Автор комментария может удалить свой комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(url_delete)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.id).exists()
    assert Comment.objects.count() == initial_comments_count - 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    author, admin_client, news, comment, form_data, url_edit
):
    """Пользователь не может редактировать чужой комментарий."""
    initial_comments_count = Comment.objects.count()
    comment_text = comment.text
    response = admin_client.post(url_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author
    assert Comment.objects.count() == initial_comments_count


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    admin_client, comment, url_delete
):
    """Пользователь не может удалить чужой комментарий."""
    initial_comments_count = Comment.objects.count()
    initial_comment_text = comment.text
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    initial_comment_created = comment.created

    response = admin_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert Comment.objects.count() == initial_comments_count
    assert comment.text == initial_comment_text
    assert comment.author == initial_comment_author
    assert comment.news == initial_comment_news
    assert comment.created == initial_comment_created
