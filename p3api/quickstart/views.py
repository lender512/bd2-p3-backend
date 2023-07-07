import pickle
import time
from django import http
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from quickstart.models import FaceVector
from quickstart.serializers import FaceVectorSerializer
from quickstart.serializers import UserSerializer, GroupSerializer
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
import numpy as np
import face_recognition
import rtree
import numpy as np
from sklearn.neighbors import KDTree


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class FaceVectorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = FaceVector.objects.all()
    serializer_class = FaceVectorSerializer
    permission_classes = [permissions.IsAuthenticated]

# view that gets and images and performs a knn search on the images


class FaceVectorSequential(mixins.ListModelMixin,
                           viewsets.GenericViewSet):

    # queryset = FaceVector.objects.all()
    serializer_class = FaceVectorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        print(self.request.data)

        # get the image from the request
        image = self.request.data['image']
        # get the vector from the request
        k = int(self.request.data['k'])
        # get the distance metric from the request
        distance_metric = self.request.data['distance_metric']

        # get the queryset
        queryset = FaceVector.objects.all()

        # get the image name
        image_name = image.name

        image = face_recognition.load_image_file(image)
        query_vector = face_recognition.face_encodings(image)[0]

        # get the k images with the smallest distance

        # get the k nearest neighbors

        heap = []
        execution_time = time.time()
        i = 0
        for face_vector in queryset:
            i += 1
            vector = face_vector.vector
            vector = np.fromstring(vector[1:-1], dtype=np.float64, sep=' ')

            if distance_metric == "euclidean":
                distance = np.linalg.norm(vector - query_vector)
            elif distance_metric == "manhattan":
                distance = np.sum(np.abs(vector - query_vector))
            elif distance_metric == "cosine":
                distance = np.dot(
                    vector, query_vector) / (np.linalg.norm(vector) * np.linalg.norm(query_vector))
            else:
                distance = np.linalg.norm(vector - query_vector)

            # store the distance in a heap of size k

            if len(heap) < k:
                heap.append((distance, face_vector))
            else:
                max_distance = max(heap, key=lambda x: x[0])
                if distance < max_distance[0]:
                    heap.remove(max_distance)
                    heap.append((distance, face_vector))

        execution_time = time.time() - execution_time

        # sort the heap
        heap.sort(key=lambda x: x[0])

        # get the k nearest neighbors
        k_nearest_neighbors = [x[1] for x in heap]

        # add distance to the queryset
        for i in range(len(k_nearest_neighbors)):
            k_nearest_neighbors[i].distance = heap[i][0]

        # create a response with the k nearest neighbors and the execution time
        response = {
            "execution_time": execution_time,
            "k_nearest_neighbors": FaceVectorSerializer(k_nearest_neighbors, many=True).data,
        }

        return Response(response, status=status.HTTP_200_OK)


class FaceVectorRTree(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    queryset = FaceVector.objects.all()
    serializer_class = FaceVectorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        image = self.request.data['image']
        k = int(self.request.data['k'])

        # get the queryset
        queryset = FaceVector.objects.all()

        # get the image name
        image_name = image.name

        image = face_recognition.load_image_file(image)
        query_vector = face_recognition.face_encodings(image)[0].tolist()
        # print(tuple(query_vector))

        # get the k images with the smallest distance

        # get the k nearest neighbors from the rtree
        p = rtree.index.Property()
        p.dimension = 128
        idx = rtree.index.Index('media/index/rtree', properties=p)

        execution_time = time.time()
        result = idx.nearest(tuple(query_vector), k, objects='true')
        execution_time = time.time() - execution_time
        k_nearest_neighbors = [x.object for x in result]

        response = {
            "execution_time": execution_time,
            "k_nearest_neighbors": FaceVectorSerializer(k_nearest_neighbors, many=True).data,
        }

        return Response(response, status=status.HTTP_200_OK)


class FaceVectorKDTree(mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    queryset = FaceVector.objects.all()
    serializer_class = FaceVectorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        image = self.request.data['image']
        k = int(self.request.data['k'])

        # get the queryset
        queryset = FaceVector.objects.all()

        # get the image name
        image_name = image.name

        image = face_recognition.load_image_file(image)
        query_vector = face_recognition.face_encodings(image)[0].tolist()

        # get the k images with the smallest distance
        #make and array of [name, vector]

        # y = []
        # for face_vector in queryset:
        #     vector = face_vector.vector
        #     vector = np.fromstring(vector[1:-1], dtype=np.float64, sep=' ')
        #     Y.a

        filename = 'media/index/kdtree'
        with open(filename, 'rb') as f:
            tree = pickle.load(f)

        rng = np.random.RandomState(0)
        execution_time = time.time()
        dist, ind = tree.query([query_vector], k=k)
        execution_time = time.time() - execution_time


        k_nearest_neighbors = [queryset[int(i)] for i in ind[0]]
        for i in range(len(k_nearest_neighbors)):
            k_nearest_neighbors[i].distance = dist[0][i]

        response = {
            "execution_time": execution_time,
            "k_nearest_neighbors": FaceVectorSerializer(k_nearest_neighbors, many=True).data,
        }

        return Response(response, status=status.HTTP_200_OK)


