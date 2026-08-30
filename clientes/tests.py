from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PerfilPasswordTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='teste-perfil',
            password='SenhaAtual123!',
        )
        self.client.force_login(self.user)

    def test_password_change_requires_current_password(self):
        response = self.client.post(
            reverse('perfil_edit'),
            {
                'action': 'password',
                'old_password': 'senha-incorreta',
                'new_password1': 'NovaSenha123!',
                'new_password2': 'NovaSenha123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('SenhaAtual123!'))
        self.assertContains(
            response,
            'A sua palavra-passe antiga foi introduzida incorretamente.',
        )

    def test_password_change_keeps_user_logged_in(self):
        response = self.client.post(
            reverse('perfil_edit'),
            {
                'action': 'password',
                'old_password': 'SenhaAtual123!',
                'new_password1': 'NovaSenha123!',
                'new_password2': 'NovaSenha123!',
            },
        )

        self.assertRedirects(response, reverse('perfil_edit'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NovaSenha123!'))
        self.assertFalse(self.user.check_password('SenhaAtual123!'))
        self.assertEqual(self.client.get(reverse('perfil_edit')).status_code, 200)
