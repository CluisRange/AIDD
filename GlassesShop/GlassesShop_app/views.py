from django.shortcuts import render, redirect
import psycopg2
from .models import  GlassesOrder, MToM, Lens, AuthUser
from rest_framework.response import Response
from rest_framework.views import APIView
from GlassesShop_app.serializers import *
from rest_framework import status
from GlassesShop_app.minio import delete_pic, add_pic
from datetime import datetime, timedelta

conn = psycopg2.connect(dbname="glasses_shop", host="localhost", user="postgres", password="1111", port="5432")

cursor = conn.cursor()

current_user_id = 1

def getActiveUser(): 
    return 1

def getDraftGlassesOrderByUserId(userId): #поиск черновой заявки по id текущего пользователя
    glases_order = None
    try:
        glases_order = GlassesOrder.objects.get(creator=userId, status = 'draft')
    except GlassesOrder.DoesNotExist:
        glases_order = GlassesOrder.objects.create(creator= AuthUser.objects.get(id = userId), status = 'draft', date_created = datetime.now())
    return glases_order

class LensesMethods(APIView):
    model_class = Lens
    serializer_class = LensSerializer

    def get(self, request): #список с фильтрацией
        search_lens = ''
        if 'search_lens' in request.GET:
            search_lens = request.GET['search_lens']
        lenses = self.model_class.objects.filter(status='active', name__icontains=search_lens).all()
        serializer = self.serializer_class(lenses, many=True)

        draft_GlassesOrder_id = getDraftGlassesOrderByUserId(getActiveUser()).glasses_order_id
        draft_GlassesOrder_lens_count = len(MToM.objects.filter(glasses_order_id=draft_GlassesOrder_id).all())

        if not draft_GlassesOrder_id:
            draft_GlassesOrder_id = -1
            draft_GlassesOrder_lens_count = 0

        return Response({
            'draft_GlassesOrder_id': draft_GlassesOrder_id,
            'draft_GlassesOrder_lens_count': draft_GlassesOrder_lens_count,
            'lenses': serializer.data
        })
    
    def post(self, request):    #добавление без изображения
        serializer = self.serializer_class(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

class SingleLensMethods(APIView):
    model_class = Lens
    serializer_class = LensSerializer

    def get(self, request, id): #одна запись
        try:
            lens = self.model_class.objects.get(lens_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(lens)
        return Response(serializer.data)

    def put(self, request, id): #изменение записи
        try:
            lens = self.model_class.objects.get(lens_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if lens.status != 'active':
            return Response({'Error':'Only active lenses may be changed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(lens, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id): #удаление записи
        try:
            lens = self.model_class.objects.get(lens_id=id, status='active')
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        img_result = delete_pic(lens)
        if 'error' in img_result.data:
            return img_result
        lens.status = 'deleted'
        lens.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddLens(APIView):    
    model_class = MToM
    serializer_class = MToMSerializer

    def post(self, request, id):    #добавление линзы в черновик
        try:
            lens = Lens.objects.get(lens_id=id)
        except lens.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        glasses_order = getDraftGlassesOrderByUserId(getActiveUser())
        MToM.objects.get_or_create(glasses_order_id=glasses_order.glasses_order_id, lens_id=lens.lens_id)
        return Response(status=status.HTTP_200_OK)

class LensAddPicture(APIView): 
    model_class = Lens
    serializer_class = LensSerializer

    def post(self, request, id): 
        try:
            lens = self.model_class.objects.get(lens_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if lens.status != 'active':
            return Response({'Error':'Only active lenses may be changed'}, status=status.HTTP_400_BAD_REQUEST)

        img_result = add_pic(lens, request.FILES.get('image'))
        if 'error' in img_result.data:
            return img_result
        return Response(status=status.HTTP_200_OK)

class GlassesOrdersMethods(APIView):     
    model_class = GlassesOrder
    serializer_class = GlassesOrderSerializer

    def get(self, request):     #список заявок с фильтрацией
        filter_status = None
        min_date_formed = None
        max_date_formed = None

        if 'status' in request.GET:
            filter_status = request.GET['status']
        if 'min_date_formed' in request.GET:
            min_date_formed = request.GET['min_date_formed']
        if 'max_date_formed' in request.GET:
            max_date_formed = request.GET['max_date_formed']

        glasses_order = self.model_class.objects.filter(status__in=['formed', 'accepted', 'cancelled']).all()

        if filter_status != None:
            glasses_order = glasses_order.filter(status=filter_status)
        if min_date_formed != None and max_date_formed!=None:
            glasses_order = glasses_order.filter(date_formed__range=[min_date_formed, max_date_formed])

        if not glasses_order:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.serializer_class(glasses_order, many=True)
        return Response(serializer.data)

class GlassesOrderMethods(APIView):    
    model_class = GlassesOrder
    serializer_class = SingleGlassesOrderSerializer

    def get(self, request, id):     #одна заявка
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(glasses_order)
        return Response(serializer.data)

    def put(self, request, id):     #изменение полей заявки
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if glasses_order.status != 'draft':
            return Response({'Error':'Only draft orders may be changed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(glasses_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):  #удаление заявки
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if glasses_order.status == 'deleted':
            return Response({'Error':'Order already deleted'}, status=status.HTTP_400_BAD_REQUEST)
        
        glasses_order.status = 'deleted'
        glasses_order.date_formed = datetime.now()
        glasses_order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SaveGlassesOrder(APIView):
    model_class = GlassesOrder
    serializer_class = GlassesOrderSerializer

    def put(self, request, id): #сформировать создателем
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if glasses_order.status != 'draft':
            return Response({'Error':'Only draft orders may be formed'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not glasses_order.phone:
            return Response({'Error': 'Required fields are not filled in'})
        
        glasses_order.date_formed = datetime.now()
        glasses_order.status = 'formed'
        glasses_order.save()
        serializer = self.serializer_class(glasses_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ModerateGlassesOrder(APIView):
    model_class = GlassesOrder
    serializer_class = GlassesOrderSerializer

    def put(self, request, id):
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if glasses_order.status != 'formed':
            return Response({'Error':'Only formed orders may be accepted'}, status=status.HTTP_400_BAD_REQUEST)
        
        glasses_order.moderator = AuthUser.objects.get(id = getActiveUser())
        glasses_order.date_ended = datetime.now()
        isAccepted = request.query_params.get('isAccepted')

        lenses_in_order = MToM.objects.filter(glasses_order_id=id).all()
        OrderSum = 0
        for lens in lenses_in_order:
            lens_object = Lens.objects.get(lens_id=lens.lens_id)
            OrderSum += lens_object.price
        glasses_order.order_sum = OrderSum

        if isAccepted == '1':
            glasses_order.status = 'accepted'
        else:
            glasses_order.status = 'cancelled'
        

        glasses_order.save()
        serializer = self.serializer_class(glasses_order)
        return Response(serializer.data, status=status.HTTP_200_OK)            

class MToMMethods(APIView):
    model_class = MToM
    serializer_class = MToMSerializer

    def delete(self, request, glasses_order_id, lens_id):  #удаление линзы из заявки
        try:
            glasses_order = GlassesOrder.objects.get(glasses_order_id=glasses_order_id, creator = getActiveUser())
        except glasses_order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if glasses_order.status in ['accepted', 'cancelled']:
            return Response({'Error':'Lenses in moderated glasses orders couldnt be changed deleted'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            MToM = self.model_class.objects.get(glasses_order_id=glasses_order_id, lens_id=lens_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        MToM.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, glasses_order_id, lens_id): #изменение полей м-м
        try:
            glasses_order = GlassesOrder.objects.get(glasses_order_id=glasses_order_id, creator = getActiveUser())
        except glasses_order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if glasses_order.status in ['confirmed', 'rejected']:
            return Response({'Error':'Lenses in moderated glasses orders couldnt be changed'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            MToM = self.model_class.objects.get(glasses_order_id=glasses_order_id, lens_id=lens_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        dioptres = request.query_params.get('dioptres')

        serializer = self.serializer_class(MToM, data={'dioptres': dioptres}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Registration(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer

    def post(self, request):    #регистрация пользователя
        if not request.data.get('username') or not request.data.get('password') or not request.data.get('email'):
            return Response({"error": "Registration information not provided"}, status=status.HTTP_400_BAD_REQUEST)
        if self.model_class.objects.filter(username=request.data.get('username')).exists():
            return Response({"error": "This username is taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = self.model_class.objects.create_user(username=request.data.get('username'), 
                                                    password=request.data.get('password'), 
                                                    email=request.data.get('email'),
                                                    is_superuser = request.data.get('is_superuser'),
                                                    first_name = request.data.get('first_name'),
                                                    last_name = request.data.get('last_name'),
                                                    is_staff = request.data.get('is_staff'),
                                                    is_active = request.data.get('is_active'),
                                                    date_joined = datetime.now())
        return Response(status=status.HTTP_201_CREATED)
       
class PersonalAccount(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer

    def put(self, request):     #ЛК пользователя
        user = self.model_class.objects.get(id=getActiveUser())
        return Response(self.serializer(user).data)
        
class Authentication(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer

    def post(self, request):    #аутентификация пользователя
        if not request.data.get('username') or not request.data.get('password'):
            return Response({"error": "Authorization details not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.model_class.objects.get(username=request.data.get('username'))
        except self.model_class.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(request.data.get('password')):
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'authentification':'success'}, status=status.HTTP_200_OK)

class Deauthorization(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer    

    def post(self, request):    #деавторизация пользователя
        return Response({'deauthorisation':'complete'})



