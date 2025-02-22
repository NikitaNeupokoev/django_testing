from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

DELETE_URL = lazy_fixture('delete_url')
EDIT_URL = lazy_fixture('edit_url')


def test_home_availability_for_anonymous_user(client, home_url):
    """
    Проверяет доступность главной страницы
    для анонимного пользователя.
    """
    assert client.get(home_url).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, expected_status',
    [
        (pytest.lazy_fixture('detail_url'), HTTPStatus.OK),
        (pytest.lazy_fixture('login_url'), HTTPStatus.OK),
        (pytest.lazy_fixture('logout_url'), HTTPStatus.OK),
        (pytest.lazy_fixture('signup_url'), HTTPStatus.OK),
    ],
)
def test_pages_availability_for_anonymous_user(client, url, expected_status):
    """Проверяет доступность страниц для анонимного пользователя."""
    assert client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        ('admin_client', HTTPStatus.NOT_FOUND),
        ('author_client', HTTPStatus.OK),
    ],
)
@pytest.mark.parametrize(
    'url_fixture',
    [
        EDIT_URL,
        DELETE_URL,
    ],
)
def test_pages_availability_for_different_users(
    client_fixture, url_fixture, expected_status, request
):
    """
    Проверяет доступность страниц редактирования и
    удаления для разных пользователей.
    """
    assert request.getfixturevalue(
        client_fixture
    ).get(
        url_fixture
    ).status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    [
        EDIT_URL,
        DELETE_URL,
    ],
)
def test_redirects(client, url_fixture, request):
    """
    Проверяет перенаправление анонимных
    пользователей на страницу входа.
    """
    login_url = reverse('users:login')
    assertRedirects(
        client.get(url_fixture),
        f'{login_url}?next={url_fixture}'
    )
