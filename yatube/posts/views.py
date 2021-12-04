from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': group.title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    name = f'{user.first_name} {user.last_name}'
    post_count = user.posts.count()
    post_list = user.posts.all()
    paginator = Paginator(post_list, settings.PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=user
    ):
        following = True
    context = {
        'title': f'Все посты пользователя {name}',
        'author': user,
        'post_count': post_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    author = post.author
    post_count = author.posts.count()
    context = {
        'title': f'Пост {post.text[:30]}',
        'post': post,
        'post_count': post_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    post = Post(author=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:profile', request.user)
    context = {
        'title': 'Добавить запись',
        'button_name': 'Добавить',
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    context = {
        'title': 'Редактировать запись',
        'is_edit': True,
        'form': form,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = Post.objects.get(id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_list = request.user.follower.all()
    users_list = []
    for follow in follow_list:
        users_list.append(follow.author)
    user_list = User.objects.filter(username__in=users_list)
    post_list = Post.objects.filter(author__in=user_list)
    paginator = Paginator(post_list, settings.PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'title': 'Посты избранных авторов',
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    follow_exist = False
    if Follow.objects.filter(user=request.user, author=author):
        follow_exist = True
    if request.user != author and follow_exist is False:
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author
    )
    follow.delete()
    return redirect('posts:profile', username=username)
