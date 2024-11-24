from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('glassesimgs', image_name, file_object, file_object.size)
        return f"http://localhost:9000/glassesimgs/{image_name}"
    except Exception as e:
        return {"error": str(e)}
    
def process_file_delete(client, image_name):
    try:
        client.remove_object('glassesimgs', image_name)
        return {'status':'success'}
    except Exception as e:
        return {'ERROR': str(e)}

def add_pic(lens, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    i = lens.lens_id
    img_obj_name = f"{i}.jpg"

    if pic == None:
        return Response({"error": "No image uploaded."})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    lens.url = result
    lens.save()

    return Response({"message": "success"})

def delete_pic(lens):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    pic_url = lens.url
    lens.url = None
    lens.save()
    if pic_url:
        pic_url = '/'.join(pic_url.split('/')[4:])

    result = process_file_delete(client, pic_url)
    if 'error' in result:
        return Response(result)

    return Response({"message": "success"})