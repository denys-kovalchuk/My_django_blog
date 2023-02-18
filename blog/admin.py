from django.contrib import admin
from .models import Author, Post, Comment


admin.site.register(Author)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'date')
    list_filter = ('date', 'author')
    search_fields = ('title', 'text')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    ordering = ('-date', '-author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'post', 'text')
    list_filter = ('user', 'date')
    search_fields = ('user', 'date', 'post', 'text')
