from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag, Comment
from .forms import CommentForm, PostCreateForm
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.db.models import Q


# CBV
class PostList(ListView):
    model = Post
    # template_name = 'blog/blog_list.html'
    ordering = '-pk'
    paginate_by = 12

    # def get_context_data(self, **kwargs):
    #     context = super(PostList, self).get_context_data()
    #     context['categories'] = Category.objects.all()
    #     # context['no_category_post_count'] = Post.objects.filter(category=None).count()
    #     return context

    def get_queryset(self):
        queryset = super().get_queryset()
        q1 = self.request.GET.get('search_ingredient', None)
        q2 = self.request.GET.get('search_menu', None)
        if q1:
            # keywords = q1.split(', ')
            keywords = (q1.replace(',', ' ', len(q1))).split()
            for i in keywords:
                queryset = queryset.filter(
                    Q(rcp_name__icontains=i) | Q(tags__name__icontains=i) | Q(category__name__icontains=i) | Q(
                        ingredient__icontains=i)
                )
            queryset = queryset.distinct()

            return queryset

        if q2:
            keywords = (q2.replace(',', ' ', len(q2))).split()
            temp_queryset = Post.objects.none()

            for i in keywords:
                temp_queryset = temp_queryset | queryset.filter(
                    Q(rcp_name__icontains=i)
                )
            temp_queryset = temp_queryset.distinct()

            return temp_queryset

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()

        q1 = self.request.GET.get('search_ingredient', None)
        q2 = self.request.GET.get('search_menu', None)
        if q1 != None:
            context['search_ingredient_info'] = f': {q1} ({self.get_queryset().count()})'

        if q2 != None:
            context['search_menu_info'] = f': {q2} ({self.get_queryset().count()})'

        return context


class PostDetail(DetailView):
    model = Post

    # template_name = 'blog/single_post_page.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        # context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class PostSearch(PostList):
    paginate_by = 12

    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(
            Q(rcp_name__contains=q) | Q(tags__name__contains=q) | Q(category__name__contains=q) | Q(ingredient__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context



class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostCreateForm


    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response

        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['rcp_name','large_img','small_img','ingredient','manual01', 'manual02', 'manual03', 'manual04', 'manual05', 'manual06', 'category']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied



# 카테고리별 눌러도 정렬기능 되게 클래스 상속
class NoCategoryPostList(PostList):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(category=None)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(NoCategoryPostList, self).get_context_data()
        context['category'] = '기타'
        return context

class CategoryPostList(PostList):
    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs['slug']
        self.category = Category.objects.get(slug=slug)
        queryset = queryset.filter(category=self.category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryPostList, self).get_context_data()
        context['category'] = self.category
        return context


#정렬
from django.db.models import Count
class Sortings(PostList):
    paginate_by = 12
    def get_queryset(self):
        sort = self.request.GET.get('sort', '')
        if sort == 'likes':
            post_list = Post.objects.annotate(like_count=Count('voter')).order_by('-like_count', '-id')
        elif sort == 'comments':
            post_list = Post.objects.annotate(comment_count=Count('comments')).order_by('-comment_count', '-id')
        elif sort == 'Bookmark':
            post_list = Post.objects.filter(like_users=self.request.user).order_by('-id')
        else:
            post_list = Post.objects.all().order_by('-id')
        return post_list

    def get_context_data(self, **kwargs):
        context = super(Sortings, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['sort'] = self.request.GET.get('sort', '')
        # context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context



# FBV
# def category_page(request, slug):
#     if slug == 'no_category':
#         category = '기타'
#         post_list = Post.objects.filter(category=None)
#
#     else:
#         category = Category.objects.get(slug=slug)
#         post_list = Post.objects.filter(category=category)
#
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'post_list': post_list,
#             'categories': Category.objects.all(),
#             'no_category_post_count': Post.objects.filter(category=None).count(),
#             'category': category,
#         }
#     )
#


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()
    return render(request, 'blog/post_list.html', {
        'post_list': post_list,
        'tag': tag,
        'categories': Category.objects.all(),
        'no_category_post_count': Post.objects.filter(category=None).count(),
    })


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())
        else:
            raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied



import requests
from .models import City
from .forms import CityForm



def weather(request):
    api_key = '1040b438745cc123940f7320c30a4e1d'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={{}}&appid={api_key}'
    cities = City.objects.all()

    weather_data = []

    for city in cities:
        city_weather = requests.get(url.format(city.name)).json()
        weather = {
            'city': city.name,
            'temperature': round(city_weather['main']['temp'] - 273.15, 1),
            'description': city_weather['weather'][0]['description'].capitalize(),
            'icon': city_weather['weather'][0]['icon']
        }
        weather_data.append(weather)

    if request.method == 'POST':
        new_city = request.POST.get('city', None)
        if new_city:
            city_weather = requests.get(url.format(new_city)).json()
            city = City.objects.create(name=new_city)
            weather = {
                'city': city.name,
                'temperature': round(city_weather['main']['temp'] - 273.15, 1),
                'description': city_weather['weather'][0]['description'].capitalize(),
                'icon': city_weather['weather'][0]['icon']
            }
            weather_data.append(weather)

    form = CityForm()
    context = {'weather_data': weather_data, 'form': form}
    return render(request, 'blog/weather.html', context)




from random import randint
from .models import Post

def random_post(request):
    # Post 모델의 전체 객체 수
    post_count = Post.objects.count()

    # 0부터 post_count - 1까지의 랜덤한 정수 생성
    random_int = randint(0, post_count - 1)

    # 랜덤하게 선택된 Post 객체
    random_post_obj = Post.objects.all()[random_int]

    # 랜덤 게시글 상세 페이지로 이동
    return redirect(random_post_obj)


from django.http import JsonResponse

def likes(request, post_pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=post_pk)
        liked = False
        message = ""

        if post.like_users.filter(pk=request.user.pk).exists():
            post.like_users.remove(request.user)
            message = '즐겨찾기가 취소되었습니다.'
        else:
            post.like_users.add(request.user)
            liked = True
            message = '즐겨찾기 되었습니다.'
        return JsonResponse({'liked':liked, 'post_pk':post_pk, 'message':message})
    return JsonResponse({'error':'즐겨찾기를 하시려면 로그인 하셔야 합니다.'})

# 추천

@login_required(login_url='common:login')
def comment_vote(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.author:
        return JsonResponse({'status': 'error', 'message': '본인이 작성한 글은 추천할 수 없습니다.'})
    else:
        comment.voter.add(request.user)
        votes = comment.voter.count()
        return JsonResponse({'status': 'success', 'votes': votes})


@login_required(login_url='common:login')
def vote_recipe(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.user == post.author:
        return JsonResponse({'status': 'error', 'message': '본인이 작성한 글은 추천할 수 없습니다.'})
    else:
        if request.user in post.voter.all():
            post.voter.remove(request.user)
            votes = post.voter.count()
            return JsonResponse({'status': 'unvoted', 'votes': votes, 'message': '추천을 취소하였습니다.'})
        else:
            post.voter.add(request.user)
            votes = post.voter.count()
            return JsonResponse({'status': 'success', 'votes': votes})




# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#     return render(request, 'blog/blog.html', {'imsi':posts})
#
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#     return render(request, 'blog/single_post_page.html', {'post':post})
