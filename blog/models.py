from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
from django.conf import settings
import os


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, primary_key=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'categories'


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='author_question')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    rcp_name = models.CharField(max_length=30, null=True, default='None')
    large_img = models.ImageField(upload_to='large_images/', null=True, blank=True)
    small_img = models.ImageField(upload_to='small_images/', null=True, blank=True)
    ingredient = models.TextField(max_length=200, blank=True, null=True)
    manual01 = models.TextField(max_length=200, blank=True, null=True)
    manual02 = models.TextField(max_length=200, blank=True, null=True)
    manual03 = models.TextField(max_length=200, blank=True, null=True)
    manual04 = models.TextField(max_length=200, blank=True, null=True)
    manual05 = models.TextField(max_length=200, blank=True, null=True)
    manual06 = models.TextField(max_length=200, blank=True, null=True)
    manual_img01 = models.TextField(max_length=200, blank=True, null=True)
    manual_img02 = models.TextField(max_length=200, blank=True, null=True)
    manual_img03 = models.TextField(max_length=200, blank=True, null=True)
    manual_img04 = models.TextField(max_length=200, blank=True, null=True)
    manual_img05 = models.TextField(max_length=200, blank=True, null=True)
    manual_img06 = models.TextField(max_length=200, blank=True, null=True)

    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_articles') # 게시글 즐겨찾기
    voter = models.ManyToManyField(User, related_name='voter_recipe')  # 게시글 추천


    def __str__(self):
        return f'[{self.pk}]요리이름 :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.ingredient)

    def get_avatar_url(self):
        if self.author :
            if self.author.socialaccount_set.exists():
                return self.author.socialaccount_set.first().get_avatar_url()
            else:
                return f'https://doitdjango.com/avatar/id/1525/b75de63e8975ed88/svg/{self.author.email}.png'

    def like_count(self):
        return self.like_users.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # comments로 써야 해.
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')  # 댓글 추천

    @property
    def get_count(self):
        return Comment.objects.filter(post=self.post).count()

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            social_account = self.author.socialaccount_set.first()

            if social_account.provider == 'google':
                return social_account.extra_data['picture']
            elif social_account.provider == 'naver':
                profile_image = social_account.extra_data.get('profile_image', None)
                if profile_image:  # 프로필 이미지 제공에 동의한 사용자
                    return profile_image
                else:  # 프로필 이미지 제공에 동의하지 않은 사용자
                    return f'https://doitdjango.com/avatar/id/1525/b75de63e8975ed88/svg/{self.author.email}.png'
            elif social_account.provider == 'kakao':
                return social_account.extra_data['properties']['profile_image']

        # 소셜 계정 정보가 없는 경우 기본 프로필 사진 제공
        return f'https://doitdjango.com/avatar/id/1525/b75de63e8975ed88/svg/{self.author.email}.png'

    def comment_count(self):
        return Comment.objects.filter(post=self.post).count()


class City(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self): #대시보드에 실제 도시 이름을 표시함
        return self.name


    class Meta: #show the plural of city as cities instead of citys
        verbose_name_plural = 'cities'



