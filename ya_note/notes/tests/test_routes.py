from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.NOTE_DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.NOTE_EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.NOTE_DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))
        cls.NOTE_ADD_URL = reverse('notes:add')
        cls.NOTE_LIST_URL = reverse('notes:list')
        cls.NOTE_SUCCESS_URL = reverse('notes:success')

        cls.PUBLIC_URLS = [
            cls.HOME_URL,
            cls.LOGIN_URL,
            cls.LOGOUT_URL,
            cls.SIGNUP_URL,
        ]

        cls.AUTHOR_URLS = [
            cls.NOTE_ADD_URL,
            cls.NOTE_LIST_URL,
            cls.NOTE_SUCCESS_URL,
        ]

        cls.ANONIMOUS_URLS = [
            cls.NOTE_DETAIL_URL,
            cls.NOTE_EDIT_URL,
            cls.NOTE_DELETE_URL,
            cls.NOTE_ADD_URL,
            cls.NOTE_LIST_URL,
            cls.NOTE_SUCCESS_URL,
        ]

    def test_pages_availability(self):
        """Проверяем доступность публичных страниц."""
        for url in self.PUBLIC_URLS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_note_accessibility(self):
        """Проверяем доступность страниц заметки для разных пользователей."""
        url_status_map = {
            self.NOTE_DETAIL_URL: {
                self.author_client: HTTPStatus.OK,
                self.reader_client: HTTPStatus.NOT_FOUND
            },
            self.NOTE_EDIT_URL: {
                self.author_client: HTTPStatus.OK,
                self.reader_client: HTTPStatus.NOT_FOUND
            },
            self.NOTE_DELETE_URL: {
                self.author_client: HTTPStatus.OK,
                self.reader_client: HTTPStatus.NOT_FOUND
            },
        }
        for url, user_status in url_status_map.items():
            for user, status in user_status.items():
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(
                        response.status_code, status)

    def test_author_pages_availability(self):
        """Проверяем доступность страниц для автора."""
        for url in self.AUTHOR_URLS:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверяем редирект для анонимного пользователя."""
        for url in self.ANONIMOUS_URLS:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
