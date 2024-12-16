import psycopg2
from .models import  GlassesOrder, MToM, Lens
from rest_framework.response import Response
from rest_framework.views import APIView
from GlassesShop_app.serializers import *
from rest_framework import status
from GlassesShop_app.minio import delete_pic, add_pic
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
import uuid
from .GetUserBySessionId import getUserBySessionId, session_storage
from django.contrib.auth.models import AnonymousUser
from .permissions import *

conn = psycopg2.connect(dbname="glasses_shop", host="localhost", user="postgres", password="1111", port="5432")

cursor = conn.cursor()

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            user = getUserBySessionId(self.request)
            if user == AnonymousUser():
                return Response({"detail": "Authentication credentials were not providedsss."}, status=401)
            else:
                try:
                    self.check_permissions(self.request)
                except Exception as e:
                    return Response({"detail": "You do not have permission to perform this action."}, status=403)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

def getDraftGlassesOrderByUserId(request): #поиск черновой заявки по id текущего пользователя
    glases_order = None
    user = getUserBySessionId(request)
    if user == None:
        return None
    try:
        glases_order = GlassesOrder.objects.get(creator=user.pk, status = 'draft')
    except GlassesOrder.DoesNotExist:
        glases_order = GlassesOrder.objects.create(creator= get_user_model().objects.get(id = user.pk), status = 'draft', date_created = datetime.now())
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

        CurrentUser = getUserBySessionId(request)
        if CurrentUser != AnonymousUser():
            draft_GlassesOrder = GlassesOrder.objects.filter(creator=CurrentUser, status='draft').first()
            if draft_GlassesOrder:
                draft_GlassesOrder_id = getDraftGlassesOrderByUserId(request).glasses_order_id
                draft_GlassesOrder_lens_count = len(MToM.objects.filter(glasses_order_id=draft_GlassesOrder_id).all())
            else:
                draft_GlassesOrder_id = 0
                draft_GlassesOrder_lens_count = 0
        else:
            draft_GlassesOrder_id = 0
            draft_GlassesOrder_lens_count = 0

        return Response({
            'draft_GlassesOrder_id': draft_GlassesOrder_id,
            'draft_GlassesOrder_lens_count': draft_GlassesOrder_lens_count,
            'lenses': serializer.data
        })
    
    @method_permission_classes((IsAdmin,))
    @swagger_auto_schema(request_body=serializer_class)
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

    @method_permission_classes((IsAdmin,))
    @swagger_auto_schema(request_body=serializer_class)
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
    
    @method_permission_classes((IsAdmin,))
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

    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, id):    #добавление линзы в черновик
        try:
            lens = Lens.objects.get(lens_id=id)
        except lens.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        glasses_order = getDraftGlassesOrderByUserId(request)
        MToM.objects.get_or_create(glasses_order_id=glasses_order.glasses_order_id, lens_id=lens.lens_id)
        return Response(status=status.HTTP_200_OK)

class LensAddPicture(APIView): 
    model_class = Lens
    serializer_class = LensSerializer

    @method_permission_classes((IsAdmin,))
    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, id): #добавление изображения
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

    @method_permission_classes((IsAuth,))
    def get(self, request):     #список заявок с фильтрацией
        filter_status = None
        min_date_formed = None
        max_date_formed = None
        CurrentUser = getUserBySessionId(request)

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
        if not (CurrentUser.is_staff or CurrentUser.is_superuser):
            glasses_order = glasses_order.filter(creator = CurrentUser)

        if not glasses_order:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.serializer_class(glasses_order, many=True)
        return Response(serializer.data)

class GlassesOrderMethods(APIView):    
    model_class = GlassesOrder
    serializer_class = SingleGlassesOrderSerializer

    @method_permission_classes((IsAuth,))
    def get(self, request, id):     #одна заявка
        CurrentUser = getUserBySessionId(request)
        try:
            if not (CurrentUser.is_staff or CurrentUser.is_superuser):
                glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = CurrentUser)
            else:
                glasses_order = self.model_class.objects.get(glasses_order_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(glasses_order)
        return Response(serializer.data)

    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, id):     #изменение полей заявки
        CurrentUser = getUserBySessionId(request)
        try:
            if not (CurrentUser.is_staff or CurrentUser.is_superuser):
                glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = CurrentUser)
            else:
                glasses_order = self.model_class.objects.get(glasses_order_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if glasses_order.status != 'draft':
            return Response({'Error':'Only draft orders may be changed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(glasses_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAuth,))
    def delete(self, request, id):  #удаление заявки
        CurrentUser = getUserBySessionId(request)
        try:
            if not (CurrentUser.is_staff or CurrentUser.is_superuser):
                glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = CurrentUser)
            else:
                glasses_order = self.model_class.objects.get(glasses_order_id=id)
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

    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, id): #сформировать создателем
        CurrentUser = getUserBySessionId(request)
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id, creator = CurrentUser)
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

    @method_permission_classes((IsManager,))
    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, id): #модерация
        try:
            glasses_order = self.model_class.objects.get(glasses_order_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if glasses_order.status != 'formed':
            return Response({'Error':'Only formed orders may be accepted'}, status=status.HTTP_400_BAD_REQUEST)
        
        glasses_order.moderator = get_user_model().objects.get(id = getUserBySessionId(request).id)
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

    @method_permission_classes((IsAuth,))
    def delete(self, request, glasses_order_id, lens_id):  #удаление линзы из заявки
        CurrentUser = getUserBySessionId(request)
        try:
            glasses_order = GlassesOrder.objects.get(glasses_order_id=glasses_order_id, creator = CurrentUser)
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

    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, glasses_order_id, lens_id): #изменение полей м-м
        CurrentUser = getUserBySessionId(request)
        try:
            glasses_order = GlassesOrder.objects.get(glasses_order_id=glasses_order_id, creator = CurrentUser)
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
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        if not request.data.get('password') or not request.data.get('email'):
            return Response({"status": "Не указаны данные для регистрации"}, status=status.HTTP_400_BAD_REQUEST)

        if self.model_class.objects.filter(email=request.data.get('email'), username = request.data.get('username')).exists():
            return Response({"status": "Пользователь с такими данными уже существует"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.model_class.objects.create_user(
            username=request.data['username'],
            email=request.data['email'], 
            password=request.data['password'],
            is_staff=request.data['is_staff'],
            is_superuser=request.data['is_superuser']
        )
        return Response({'status': 'Успех'}, status=status.HTTP_200_OK)
       
class PersonalAccount(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request):     #ЛК пользователя
        user = getUserBySessionId(request)
        if user!= AnonymousUser():
            serializer = self.serializer_class(user, data=request.data, partial=True)
        else: 
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class Authentication(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):    #аутентификация пользователя
        if not request.data.get('username') or not request.data.get('password'):
            return Response({"error": "Authorization details not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None:
            random_key = uuid.uuid4().hex
            for key in session_storage.scan_iter():
                if session_storage.get(key).decode('utf-8') == user.email:
                    session_storage.delete(key)
            session_storage.set(random_key, user.email)
            response = Response(self.serializer_class(user).data)
            response.set_cookie('session_id', random_key)
            return response
        
        return Response({"error": "Incorrect login or password"}, status=status.HTTP_400_BAD_REQUEST)

class Deauthorization(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer    

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):    #деавторизация пользователя
        session_id = request.COOKIES.get('session_id')
        session_storage.delete(session_id)
        return Response(status=status.HTTP_204_NO_CONTENT)



