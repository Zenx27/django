from django.shortcuts import render, redirect
from .forms import UploadForm
from .models import Upload

def upload_file(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("upload_list")
    else:
        form = UploadForm()
    return render(request, "uploads/upload_form.html", {"form": form})

def upload_list(request):
    files = Upload.objects.all()
    return render(request, "uploads/upload_list.html", {"files": files})
