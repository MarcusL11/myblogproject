from django.db import models

from django.utils.text import slugify

class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    slug = models.SlugField(max_length=150, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)