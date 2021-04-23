from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
#from django.views.decorators.cache import cache_page
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Comment, Post, Group, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect(reverse("posts:index"))
    return render(request, "new_post.html", {'form': form, 'is_new': True})


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {'group': group, 'page': page}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=request.user)
        if Follow.objects.filter(user=user, author=author).exists():
            following = True
    post_list = Post.objects.filter(author=author).all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "author": author,
        "post_count": post_count,
        "following": following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    post_count = Post.objects.filter(author=author).all().count()
    form = CommentForm()
    comments = Comment.objects.filter(post=post).all()
    context = {
        "post": post,
        "author": author,
        "post_count": post_count,
        "form": form,
        "comments": comments
    }
    return render(
        request,
        'post.html',
        context
    )


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        edit_post = get_object_or_404(Post, id=post_id, author=author)
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=edit_post
        )
        if form.is_valid():
            form.save()
            return redirect("posts:post", username=username, post_id=post_id)
        return render(
            request,
            "new_post.html",
            {'form': form, "author": author, "post_id": post_id}
        )
    else:
        return redirect("posts:post", username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    user = get_object_or_404(User, username=request.user)
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = user
        new_comment.post = post
        new_comment.save()
        return redirect(
            reverse(
                "posts:post",
                kwargs={"username": username, "post_id": post_id}
            )
        )
    return redirect(
        reverse(
            "posts:post",
            kwargs={"username": username, "post_id": post_id}
        )
    )


@login_required
def follow_index(request):
    following_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    is_exist = Follow.objects.filter(user=user, author=author).exists()
    if (user != author) and (not is_exist):
        Follow.objects.create(user=user, author=author)
    return redirect(reverse("posts:profile", kwargs={"username": username}))


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    is_exist = Follow.objects.filter(user=user, author=author).exists()
    if (user != author) and is_exist:
        Follow.objects.filter(user=user, author=author).delete()
    return redirect(reverse("posts:profile", kwargs={"username": username}))