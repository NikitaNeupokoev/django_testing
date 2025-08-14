import unittest.mock
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.views import NoteUpdate, NoteDelete

User = get_user_model()


class BaseTest(TestCase):
    """Базовый класс для тестовых классов."""
    NOTE_TITLE = 'Текст заголовка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'test-slug'


class TestNoteCreation(BaseTest):
    """Тесты для проверки создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """
        Подготовка тестовых данных:
        пользователь, URL, существующая заметка.
        """
        cls.user = User.objects.create(username='testuser')
        cls.URL_TO_DONE = reverse('notes:success')
        cls.URL_TO_ADD = reverse('notes:add')

        cls.existing_note = Note.objects.create(
            title='Существующая заметка',
            text='Текст существующей заметки',
            slug='existing-slug',
            author=cls.user
        )

    def setUp(self):
        """
        Подготовка перед каждым тестом:
        очистка БД, клиент, тестовые данные формы.
        """
        Note.objects.all().exclude(pk=self.existing_note.pk).delete()
        self.initial_notes_count = Note.objects.count()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.form_data = {
            'text': self.NOTE_TEXT,
            'title': self.NOTE_TITLE,
            'slug': self.NOTE_SLUG
        }

    def test_user_can_create_note(self):
        """
        Тест проверяет, что авторизованный
        пользователь может создать заметку.
        """
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)

        response = self.auth_client.post(
            self.URL_TO_ADD,
            data=self.form_data
        )

        self.assertRedirects(response, self.URL_TO_DONE)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()

        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        """
        Тест проверяет, что анонимный пользователь
        не может создать заметку.
        """
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)

        self.client.post(
            self.URL_TO_ADD,
            data=self.form_data
        )

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        """
        Тест проверяет, что при отсутствии
        slug он генерируется автоматически.
        """
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)

        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.auth_client.post(
            self.URL_TO_ADD,
            data=form_data
        )

        self.assertRedirects(
            response,
            self.URL_TO_DONE
        )
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.user
        )
        expected_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(new_note.slug, expected_slug)

    def test_not_unique_slug(self):
        """
        Тест проверяет, что при попытке создать заметку
        с неуникальным slug возникает ошибка.
        """
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)

        Note.objects.create(
            title='Существующая заметка',
            text='Текст существующей заметки',
            slug='existing-slug',
            author=self.user
        )

        form_data = {
            'text': self.NOTE_TEXT,
            'title': self.NOTE_TITLE,
            'slug': 'existing-slug'
        }

        response = self.auth_client.post(
            self.URL_TO_ADD,
            data=form_data
        )
        self.assertIn(
            WARNING,
            response.context['form'].errors['slug'][0]
        )
        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(BaseTest):
    """Тесты редактирования и удаления заметок."""

    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NEW_NOTE_TITLE = 'Обновлённый заголовок заметки'
    NEW_NOTE_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        """
        Подготовка тестовых данных:
        автор заметки и URL-адреса.
        """
        cls.author = User.objects.create(username='Автор заметки')
        cls.NOTE_LIST_URL = reverse('notes:list')
        cls.edit_success_url = reverse('notes:success')

    def setUp(self):
        """
        Подготовка перед каждым тестом:
        авторизация, создание заметки и тестовых данных.
        """
        self.auth_client = Client()
        self.auth_client.force_login(self.author)

        self.note = Note.objects.create(
            title=self.NOTE_TITLE,
            slug=self.NOTE_SLUG,
            author=self.author,
            text=self.NOTE_TEXT
        )
        self.edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.delete_url = reverse('notes:delete', args=(self.note.slug,))
        self.form_data = {
            'text': self.NEW_NOTE_TEXT,
            'title': self.NEW_NOTE_TITLE,
            'slug': self.NEW_NOTE_SLUG
        }
        self.notes_count = Note.objects.count()

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        self.assertEqual(Note.objects.count(), 1)

        with unittest.mock.patch.object(
            NoteUpdate,
            'get_success_url',
            return_value=TestNoteEditDelete.NOTE_LIST_URL
        ):
            self.assertRedirects(self.auth_client.post(
                self.edit_url,
                data=self.form_data),
                TestNoteEditDelete.NOTE_LIST_URL
            )

        updated_note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(updated_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(updated_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(updated_note.slug, self.NEW_NOTE_SLUG)

        final_notes_count = Note.objects.count()
        self.assertEqual(final_notes_count, 1)

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        initial_notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count, 1)

        with unittest.mock.patch.object(
            NoteDelete,
            'get_success_url',
            return_value=TestNoteEditDelete.NOTE_LIST_URL
        ):
            self.assertRedirects(
                self.auth_client.post(self.delete_url),
                TestNoteEditDelete.NOTE_LIST_URL
            )

            self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_note_of_another_user(self):
        """
        Проверяет, что пользователь
        не может редактировать чужую заметку.
        """
        initial_notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count, 1)

        reader = User.objects.create(username='reader')
        reader_client = Client()
        reader_client.force_login(reader)
        response = reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged_note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(unchanged_note.text, self.NOTE_TEXT)
        self.assertEqual(unchanged_note.title, self.NOTE_TITLE)
        self.assertEqual(unchanged_note.slug, self.NOTE_SLUG)

        self.assertEqual(Note.objects.count(), 1)

    def test_user_cant_delete_note_of_another_user(self):
        """
        Проверяет, что пользователь
        не может удалить чужую заметку.
        """
        initial_notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count, 1)

        reader = User.objects.create(username='reader')
        reader_client = Client()
        reader_client.force_login(reader)

        self.assertEqual(
            reader_client.post(self.delete_url).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), 1)
