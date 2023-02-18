from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager


User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='default.png', upload_to='profile_pics')
    mobile = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}'


class Post(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    picture = models.ImageField(null=True, blank=True, upload_to='posts_pics')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True)
    tags = TaggableManager()
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('blog:detailed_post', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f'{self.title[:15]}...'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Comment by {self.user} in {self.post}'
