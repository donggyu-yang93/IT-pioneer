from django.urls import path
from .views import random_post, CategoryPostList, NoCategoryPostList
from . import views    # .은 자기자신의 위치를 뜻함(자기자신이 포함된 폴더)


app_name = 'blog'
urlpatterns = [

    #127.0.0.1:8000/blog/
    # CBV
    path('<int:pk>/', views.PostDetail.as_view(), name='detail'),
    path('', views.PostList.as_view(), name='home'),
    path('create_post/', views.PostCreate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    # path('search/<str:q>/', views.PostSearch.as_view()),
    path('search/<str:q>/', views.PostList.as_view(), name='blog'),
    path('search1/<str:q>/', views.PostList.as_view(), name='blog'),
    path('weather/', views.weather, name='weather'),
    path('random_post/', random_post, name='random_post'), # /blog/random_post/ 주소 요청 시, random_post() 뷰 함수 실행
    path('category/no_category/', NoCategoryPostList.as_view(), name='no_category_page'),  # 카테고리
    path('category/<str:slug>/', CategoryPostList.as_view(), name='category_page'),  # 카테고리
    path('sorting/', views.Sortings.as_view(), name='Sortings'),  # 정렬



    # FBV
    # path('category/<str:slug>/', views.category_page),
    path('tag/<str:slug>/', views.tag_page),
    path('<int:pk>/new_comment/', views.new_comment),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('<int:post_pk>/likes/', views.likes, name='likes'),
    path('vote_comment/<int:comment_pk>/', views.comment_vote, name='vote_comment'),
    path('vote_recipe/<int:post_pk>/', views.vote_recipe, name='vote_recipe'),


    # path('<int:pk>/', views.single_post_page),
    # path('', views.index),

]