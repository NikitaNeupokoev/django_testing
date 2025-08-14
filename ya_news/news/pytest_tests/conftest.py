import pytest

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def home_url():
    """Фикстура, возвращающая URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Фикстура, возвращающая URL страницы детализации новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    """Создает URL для редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Создает URL для удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    """Фикстура, возвращающая URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура, возвращающая URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Фикстура, возвращающая URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def admin_client(another_user):
    """Авторизованный клиент с другим пользователем."""
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def author():
    """Создает объект пользователя."""
    return User.objects.create_user(
        username='testuser',
        password='password'
    )


@pytest.fixture
def author_client(author):
    """Создает клиента и логинит автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def another_user(django_user_model):
    """Создает другого пользователя."""
    return django_user_model.objects.create_user(
        username='another_user'
    )


@pytest.fixture
def news():
    """Создает объект новости для использования в тестах."""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    """Создает комментарий для использования в тесте."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Исходный комментарий',
    )


@pytest.fixture
def news_list():
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.'
        )
        for index in range(
            settings.NEWS_COUNT_ON_HOME_PAGE + 1
        )
    )


@pytest.fixture
def comments(author, new):
    now = timezone.now()
    comments = [
        Comment.objects.create(
            news=new,
            author=author,
            text=f"Текст {index}",
            created=now + timedelta(days=index)
        )
        for index in range(2)
    ]
    return comments
