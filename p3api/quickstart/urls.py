import quickstart.views as views
from rest_framework import routers
from django.urls import path


router = routers.DefaultRouter()

urlpatterns = [
    path('rtree_knn/', views.FaceVectorRTree.as_view({'post': 'list'}), name='rtree_knn'),
    path('secuential_knn/', views.FaceVectorSequential.as_view({'post': 'list'}), name='secuential_knn'),
    path('kdtree_knn/', views.FaceVectorKDTree.as_view({'post': 'list'}), name='kdtree_knn'),
]


# urlpatterns = router.urls
