from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Post, Comment
from .forms import PostForm, CommentForm, RegisterForm
import json

def home(request):
    posts = Post.objects.all().order_by("-created_at")
    paginator = Paginator(posts, 5)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "post_list.html", {"page_obj": page_obj})

def post_controller(request):
    if request.method == "GET":
        posts = Post.objects.all().order_by("-created_at")
        page = request.GET.get("page", 1)
        paginator = Paginator(posts, 5)
        page_obj = paginator.get_page(page)
        data = [{"id": p.id, "title": p.title, "author": p.author.username, "created_at": p.created_at} for p in page_obj]
        return JsonResponse({"results": data, "num_pages": paginator.num_pages})
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            title = payload.get("title")
            content = payload.get("content")
            author_id = payload.get("author")
            post = Post.objects.create(title=title, content=content, author_id=author_id)
            return JsonResponse({"id": post.id}, status=201)
        except Exception:
            return HttpResponseBadRequest()

@method_decorator(login_required, name="dispatch")
class CommentController(View):
    def get(self, request):
        post_id = request.GET.get("post")
        if not post_id:
            comments = Comment.objects.all().order_by("created_at")
        else:
            comments = Comment.objects.filter(post_id=post_id).order_by("created_at")
        paginator = Paginator(comments, 10)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        data = [{"id": c.id, "post": c.post_id, "author": c.author.username, "content": c.content} for c in page_obj]
        return JsonResponse({"results": data, "num_pages": paginator.num_pages})
    def post(self, request):
        try:
            payload = json.loads(request.body)
            comment = Comment.objects.create(post_id=payload["post"], author_id=payload["author"], content=payload["content"])
            return JsonResponse({"id": comment.id}, status=201)
        except Exception:
            return HttpResponseBadRequest()

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()
    comments = post.comments.all().order_by("created_at")
    return render(request, "post_detail.html", {"post": post, "comments": comments, "form": form})

def post_create(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            p.save()
            return redirect(p.get_absolute_url())
    else:
        form = PostForm()
    return render(request, "post_form.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})





from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def users_api(request, user_id=None):
    if request.method == "GET":
        if user_id:
            user = User.objects.filter(id=user_id, is_active=True).first()
            if not user:
                return JsonResponse({"detail": "Not found"}, status=404)
            return JsonResponse({"id": user.id, "username": user.username, "email": user.email})
        users = User.objects.filter(is_active=True).order_by("id")
        paginator = Paginator(users, 10)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        data = [{"id": u.id, "username": u.username, "email": u.email} for u in page_obj]
        return JsonResponse({"results": data, "num_pages": paginator.num_pages})
    if request.method == "POST":
        payload = json.loads(request.body)
        user = User.objects.create_user(username=payload["username"], password=payload["password"], email=payload.get("email", ""))
        return JsonResponse({"id": user.id}, status=201)
    if request.method == "PUT" and user_id:
        payload = json.loads(request.body)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"detail": "Not found"}, status=404)
        user.username = payload.get("username", user.username)
        if payload.get("password"):
            user.set_password(payload["password"])
        user.save()
        return JsonResponse({"id": user.id})
    if request.method == "DELETE" and user_id:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"detail": "Not found"}, status=404)
        user.is_active = False
        user.save()
        return HttpResponse(status=204)

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("register")  
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})