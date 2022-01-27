from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from django.conf import settings


User = get_user_model()


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.PER_PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template = "posts/index.html"
    context = {
        "posts": posts,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.post_set.all()
    paginator = Paginator(posts, settings.PER_PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "posts": posts,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.PER_PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author, user=request.user
        ).exists()
    else:
        following = False
    context = {
        "posts": posts,
        "page_obj": page_obj,
        "author": author,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    counter = Post.objects.filter(author=posts.author)
    form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        "form": form,
        "comments": comments,
        "counter": counter,
        "posts": posts,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    template = "posts/post_create.html"
    group_choice = Group.objects.all().order_by("title")
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", username=post.author)
    else:
        form = PostForm()
    context = {
        "form": form,
        "group_choice": group_choice,
        "title": "Новый пост",
        "btn_text": "Добавить",
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if post.author == request.user and form.is_valid():
        post = form.save()
        post.save()
        return redirect("posts:post_detail", post_id=post.pk)
    context = {
        "post": post,
        "form": form,
        "is_edit": is_edit,
    }
    return render(request, "posts/post_create.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PER_PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = User(request.user.id)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect("posts:profile", username)
