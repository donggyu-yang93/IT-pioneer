from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView

from blog.models import Post, Category

# def index(request):
#     return render(request, 'single_pages/landing.html')
#
# def about_me(request):
#     return render(request, 'single_pages/about_me.html')
#
# def landing(request):
#     recent_posts = Post.objects.order_by('-pk')[:3]
#     return render(request, 'single_pages/landing.html',{
#         'recent_posts': recent_posts,
#         })

class Landing(ListView):
    model = Post
    recent_posts = Post.objects.order_by('-pk')[:3]
    template_name = 'single_pages/landing.html'

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data()
        recent_posts = Post.objects.order_by('-pk')[:3]
        context['categories'] = Category.objects.all()
        # context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['recent_posts'] = recent_posts
        return context

class About_Me(ListView):
    model = Post
    template_name = 'single_pages/about_me.html'

    def get_context_data(self, **kwargs):
        context = super(About_Me, self).get_context_data()
        context['categories'] = Category.objects.all()
        # context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context