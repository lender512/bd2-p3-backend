from django.apps import AppConfig
import face_recognition
import rtree
import numpy as np
import pickle

import os

from sklearn.neighbors import KDTree


class QuickstartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quickstart'

    def ready(self):
        from django.db import connection
        from .models import FaceVector

        #go to media/images
        #go to each folder
        #get all images
        #get all vectors

        path = "media/images"

        # FaceVector.objects.all().delete()

        if FaceVector.objects.all().count() == 0:        
            i = 0
            for folder in os.listdir(path):
                folder_path = os.path.join(path, folder)

                for image in os.listdir(folder_path):
                    image_name = image
                    image_path = os.path.join(folder_path, image)
                    image = face_recognition.load_image_file(image_path)
                    face_locations = face_recognition.face_locations(image)
                    face_encodings = face_recognition.face_encodings(image, face_locations)
                    for face_encoding in face_encodings:
                        FaceVector.objects.create(vector=face_encoding, name=image_name)
                    i += 1
                print(f"registering m{i} {folder_path}")

        if not os.path.exists("media/index/rtree.idx"):
            #create rtree of 128 dimensions and store it in media/index
            #get the queryset
            queryset = FaceVector.objects.all()
            #create the index
            p = rtree.index.Property()
            p.dimension = 128

            

            idx = rtree.index.Index('media/index/rtree', properties=p)

            i = 0
            for face_vector in queryset:
                vector = face_vector.vector
                vector = np.fromstring(vector[1:-1], dtype=np.float64, sep=' ')
                #duplicate each dimension so that is x, x y, y, z, z ...
                # vector = np.repeat(vector, 2)
                # print(vector)
                idx.insert(face_vector.id, tuple(vector), obj=face_vector)
                i += 1
                print(i)
            print("saved rtree")

        if not os.path.exists("media/index/kdtree"):
            queryset = FaceVector.objects.all()

            X = []
            for face_vector in queryset:
                vector = face_vector.vector
                vector = np.fromstring(vector[1:-1], dtype=np.float64, sep=' ')
                X.append(vector)

            tree = KDTree(X, leaf_size=2, metric='euclidean')

            filename = 'media/index/kdtree'
            with open(filename, 'wb') as file:
                pickle.dump(tree, file)
                print("saved kdtree")



            



