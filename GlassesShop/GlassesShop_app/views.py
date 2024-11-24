from django.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse
import psycopg2
from .models import  GlassesOrder, MToM, Lens, AuthUser

conn = psycopg2.connect(dbname="glasses_shop", host="localhost", user="postgres", password="1111", port="5432")

cursor = conn.cursor()

current_user_id = 1


def getLensById(lensId):
    return Lens.objects.get(lens_id=lensId, status='active')

def getDraftByOrderIdandUserId(GlassesOrderId, UserId):
    return GlassesOrder.objects.filter(glasses_order_id = GlassesOrderId, creator=UserId, status='draft').first()

def getMtoMByGlassesOrder(GlassesOrderId):
    return MToM.objects.filter(glasses_order_id=GlassesOrderId).all()

def getOrderByUserId(UserId):
    return GlassesOrder.objects.filter(creator=UserId, status='draft').first() 

def LensesController(request):

    LensInOrderCount = 0
    CurrentGlassesOrderId = -1

    CurGlassesOrder = getOrderByUserId(current_user_id)

    if CurGlassesOrder!= None:
        Lenses_in_current_glasses_order = getMtoMByGlassesOrder(CurGlassesOrder.glasses_order_id)
        LensInOrderCount = len(Lenses_in_current_glasses_order)
        CurrentGlassesOrderId = CurGlassesOrder.glasses_order_id

    search = ''
    if 'search_lens' in request.GET:
        search = request.GET['search_lens']

    lenses_found_by_search = Lens.objects.filter(name__icontains=search, status='active').all()

    return render(request, 'Lenses.html', {'data' : {
        'Lenses': lenses_found_by_search,
        'GlassesOrderCount' : LensInOrderCount,
        'GlassesOrder_id' : CurrentGlassesOrderId
    }})


def LensDescriptionController(request, id):

    lens = getLensById(id)    

    if lens == None:
        return redirect(LensesController)

    return render(request, 'OneLense.html', {'data' : {
        'Lens' : lens,
        'id': id
    }})

def GlassesOrderController(request, id):
    CurGlassesOrder = getDraftByOrderIdandUserId(id, current_user_id)
    if CurGlassesOrder == None:
        return HttpResponse(status = 404)

    Lenses = []
    Order_sum=0

    Lenses = MToM.objects.filter(glasses_order_id=CurGlassesOrder.glasses_order_id).select_related('lens')

    for lns in Lenses:
        Order_sum += lns.lens.price

    return render(request, 'GlassesOrder.html', {'data' : {
        'id': id,
        'date_created': CurGlassesOrder.date_created,
        'order_sum' : Order_sum,
        'phone' : CurGlassesOrder.phone,
        'lenses': Lenses,
        'lenses_count':len(Lenses)
    }})

def AddLensController(request, id):
    Lens = getLensById(id)
    if Lens == None:
        return redirect(LensesController)
    
    currentGlassesOrder = getOrderByUserId(current_user_id)
    if currentGlassesOrder == None:
        CurUser = AuthUser.objects.get(id=current_user_id)
        currentGlassesOrder = GlassesOrder.objects.create(creator = CurUser, status = 'draft', date_created = datetime.today())
    MToM.objects.get_or_create(glasses_order_id=currentGlassesOrder.glasses_order_id, lens_id=Lens.lens_id, dioptres='0,5')

    return redirect(LensesController)

def DeleteGlassesOrderController(request, id):
    cursor = conn.cursor()
    if id!=None:
        cursor.execute('UPDATE glasses_order SET status = %s WHERE glasses_order_id = %s', ("deleted", id,))
    conn.commit()
    return redirect(LensesController)