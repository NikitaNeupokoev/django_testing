from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Новый текст'}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client,
    detail_url
):
    """
    Проверяет, что анонимный пользователь
    не может создать комментарий.
    """
    Comment.objects.all().delete()
    assert Comment.objects.count() == 0

    assert client.post(
        detail_url,
        data=FORM_DATA
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url
):
    """
    Проверяет, что авторизованный пользователь
    может создать комментарий.
    """
    Comment.objects.all().delete()

    assertRedirects(
        author_client.post(
            detail_url,
            data=FORM_DATA
        ), f'{detail_url}#comments'
    )

    assert Comment.objects.count() == 1

    comment = Comment.objects.first()

    assert comment.text == FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news
    assert comment.created is not None


@pytest.mark.parametrize(
    'bad_word', BAD_WORDS
)
def test_user_cant_use_bad_words(
    admin_client,
    news,
    detail_url,
    bad_word
):
    """
    Проверяет, что пользователь не может использовать
    запрещенные слова в комментариях.
    """
    bad_words_data = {'text': f'Некорректный {bad_word}, текст'}
    response = admin_client.post(
        detail_url,
        data=bad_words_data
    )

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client,
    comment,
    news,
    delete_url,
    detail_url
):
    """
    Проверяет, что автор комментария
    может удалить свой комментарий.
    """
    initial_count = Comment.objects.count()
    assert initial_count == 1

    assertRedirects(
        author_client.delete(delete_url),
        f'{detail_url}#comments'
    )

    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    news,
    edit_url,
    detail_url
):
    """
    Проверяет, что автор комментария
    может его отредактировать.
    """
    original_comment_count = Comment.objects.count()
    original_created = comment.created

    assertRedirects(
        author_client.post(
            edit_url,
            data=FORM_DATA
        ),
        f"{detail_url}#comments")

    assert Comment.objects.count() == original_comment_count

    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == FORM_DATA['text']

    assert updated_comment.created == original_created
    assert updated_comment.news == news
    assert updated_comment.author == comment.author


def test_user_cant_edit_comment_of_another_user(
    admin_client,
    comment,
    news
):
    """
    Проверяет, что пользователь не может
    редактировать комментарий другого пользователя.
    """
    initial_comment_count = Comment.objects.count()

    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    original_created = comment.created
    comment_id = comment.id

    assert admin_client.post(
        reverse(
            'news:edit',
            args=(comment_id,)
        ),
        FORM_DATA).status_code == HTTPStatus.NOT_FOUND

    updated_comment = Comment.objects.get(id=comment_id)

    assert updated_comment.text == original_text
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news
    assert updated_comment.created == original_created

    assert Comment.objects.count() == initial_comment_count


def test_user_cant_delete_comment_of_another_user(
    admin_client,
    comment
):
    """
    Проверяет, что пользователь не может
    удалить комментарий другого пользователя.
    """
    initial_comment_count = Comment.objects.count()
    comment_id = comment.id

    assert admin_client.post(
        reverse(
            'news:delete',
            args=(comment_id,)
        )
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comment_count
    assert Comment.objects.filter(id=comment_id).exists()
