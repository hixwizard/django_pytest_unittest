from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    (
        ('client', HTTPStatus.OK),
        ('admin_client', HTTPStatus.NOT_FOUND),
        ('author_client', HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'url_fixture',
    (
        'url_home',
        'url_login',
        'url_logout',
        'url_signup',
        'url_detail'
    )
)
def test_page_availability(
    client_fixture, expected_status, url_fixture, request
):
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
    client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
