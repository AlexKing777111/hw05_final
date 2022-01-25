import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Stas")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст1",
        )
        cls.group_1 = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "author": User,
            "text": "Тестовый текст",
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "Stas"})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст", image="posts/small.gif"
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        big_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
        )
        uploaded = SimpleUploadedFile(
            name="big.gif", content=big_gif, content_type="image/gif"
        )
        form_data = {
            "author": User,
            "text": "Тестовый текст change",
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст change", image="posts/big.gif"
            ).exists()
        )
