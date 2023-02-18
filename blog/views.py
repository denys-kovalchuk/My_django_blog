from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import UserRegistrationForm, CommentForm, PostForm, AuthorForm, PasswordChangeForm
from django.views.generic import DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
from django.db.models import Count


def detailed_post(request, post):
    post = get_object_or_404(Post, slug=post)
    new_comment = None
    comments = post.comments.filter(post=post)
    user = request.user
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = user
            new_comment.save()
            return redirect('detailed_post', post=post.slug)
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-date')[:4]

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
        'user': user
    }
    return render(request, 'blog/detailed_post.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detailed_post.html'


def home(request, tag_slug=None):
    all_posts = Post.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags__in=[tag])

    paginator = Paginator(all_posts, 4)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'page': page,
        'posts': posts,
        'tag': tag
    }

    return render(request, 'users/home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created. You can log in now!')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'users/register.html', context)


def account(request):
    if request.method == 'POST':
        user = request.user
        form = AuthorForm(request.POST, request.FILES, instance=user.author)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        user = request.user
        form = AuthorForm(instance=user.author)
    context = {'form': form}
    return render(request, 'users/account.html', context)


def new_post(request):
    form = PostForm(request.POST or None)
    user = request.user

    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = user
        obj.picture = request.FILES.get('picture')
        if obj.picture:
            picture_saved = FileSystemStorage().save(obj.picture.name, obj.picture)
        else:
            obj.picture = None
        obj.save()
        form.save_m2m()
        print(form.cleaned_data)
        return redirect('home')

    return render(request, 'blog/new_post.html', context={'form': form})


def edit_post(request, post):
    post = get_object_or_404(Post, slug=post)

    if request.method == 'GET':
        context = {'form': PostForm(instance=post), 'slug': post}
        return render(request, 'blog/edit_post.html', context)

    elif request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'The post has been updated successfully!')
            return redirect('detailed_post', post=post.slug)
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request, 'blog/edit_post.html', context={'form': form})


def account_edit(request):
    user = request.user
    if request.method == 'GET':
        context = {'form_author': AuthorForm()}
        return render(request, 'users/account_edit.html', context)

    elif request.method == 'POST':
        form_author = AuthorForm(request.POST, request.FILES, instance=user.author)
        if form_author.is_valid():
            form_author.save()
            messages.success(request, 'The post has been updated successfully!')
            return redirect('account')
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request, 'users/account_edit.html', context={'form_author': form_author})


def password_edit(request):
    user = request.user
    if request.method == 'GET':
        context = {'form_password': PasswordChangeForm(user)}
        return render(request, 'users/password_edit.html', context)

    elif request.method == 'POST':
        form_password = PasswordChangeForm(user, request.POST)
        if form_password.is_valid():
            form_password.save()
            update_session_auth_hash(request, form_password.user)
            messages.success(request, 'The password has been updated successfully!')
            return redirect('account')
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request, 'users/password_edit.html',
                          context={'form_password': form_password})
