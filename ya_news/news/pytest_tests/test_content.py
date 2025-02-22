import pytest

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_list, home_url):
    """
    Проверяет, что количество новостей
    на главной странице соответствует ожидаемому.
    """
    assert 'object_list' in client.get(home_url).context
    assert client.get(home_url).context['object_list'].count() == (
        settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, news_list, home_url):
    """
    Проверяет, что новости на главной
    странице упорядочены по дате в порядке убывания.
    """
    news_list = client.get(home_url).context['object_list']
    news_dates = [news.date for news in news_list]
    sorted_dates = sorted(news_dates, reverse=True)

    assert news_dates == sorted_dates


def test_comments_order(client, news, detail_url):
    """
    Проверяет, что комментарии к новости отображаются
    в порядке возрастания даты создания.
    """
    assert "news" in client.get(detail_url).context

    news_from_context = client.get(detail_url).context['news']
    comment_list = list(news_from_context.comment_set.all())
    sorted_comments = sorted(
        comment_list,
        key=lambda comment: comment.created
    )

    assert comment_list == sorted_comments


@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_availability_for_different_users(
        parametrized_client,
        form_in_page,
        detail_url
):
    """
    Проверяет доступность формы
    комментариев для разных типов пользователей.
    """
    assert (
        'form' in parametrized_client.get(detail_url).context
    ) is form_in_page


def test_comment_form_in_context_for_authorized_user(
    author_client,
    detail_url
):
    """
    Проверяет, что форма комментариев присутствует в контексте для
    авторизованного пользователя и имеет ожидаемый тип.
    """
    assert 'form' in author_client.get(detail_url).context
    assert isinstance(
        author_client.get(detail_url).context['form'],
        CommentForm
    )
