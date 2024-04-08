import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name', (
        'news:detail',
        'news:edit',
        'news:delete',
        'news:home',
        'users:login',
        'users:logout'
    ))
@pytest.mark.django_db
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status
):
    """Проверка статусов всех страниц для разных клиентов."""
    url = reverse(name)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args')),
    ),
)
@pytest.mark.django_db
def test_redirects(client, name, args):
    """Проверка редиректов."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
