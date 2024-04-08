from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'client_fixture, url_fixture, expected_status',
    [
        (
            'client',
            'url_home',
            HTTPStatus.OK
        ),
        (
            'admin_client',
            'url_edit',
            HTTPStatus.NOT_FOUND
        ),
        (
            'admin_client',
            'url_delete',
            HTTPStatus.NOT_FOUND
        ),
        (
            'author_client',
            'url_edit',
            HTTPStatus.OK
        ),
        (
            'author_client',
            'url_delete',
            HTTPStatus.OK
        )
    ]
)
def test_page_availability(
    client_fixture, url_fixture, expected_status, request
):
    """Проверка статусов всех страниц для разных клиентов."""
    client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'client_fixture, url_fixture',
    (
        ('client', 'url_edit'),
        ('client', 'url_delete')
    )
)
def test_redirects(client_fixture, url_fixture, url_login, request):
    """Проверка редиректов."""
    client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
