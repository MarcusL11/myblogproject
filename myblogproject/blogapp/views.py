from django.shortcuts import render
from . models import BlogPost

def home(request):
    blogs = BlogPost.objects.all()

    context = {
        'blogs': blogs
    }

    return render(request, 'blogapp/home.html', context)

def blogpage(request, slug=None):
    if request.method == "GET":
        try: 
            blog = BlogPost.objects.get(slug=slug)
            context = {
                'blog': blog
            }
        
            return render(request, 'blogapp/blogpage.html', context)

        except BlogPost.DoesNotExist:
            return render(request, 'blogapp/blogpage.html')
        
    return render(request, 'blogapp/blogpage.html')