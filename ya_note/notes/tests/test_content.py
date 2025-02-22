from notes.forms import NoteForm
from notes.tests.conftest import BaseTest


class TestContent(BaseTest):

    def test_notes_list_for_auth_user(self):
        """
        Проверяем, что авторизованный
        пользователь видит свои заметки в списке.
        """
        response = self.author_client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_notes_list_for_anon_user(self):
        """
        Проверяем, что неавторизованный
        пользователь не видит чужие заметки в списке.
        """
        response = self.reader_client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_create_and_add_note_pages_contains_form(self):
        """
        Проверяем, что страницы создания и
        редактирования заметки содержат форму NoteForm.
        """
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
