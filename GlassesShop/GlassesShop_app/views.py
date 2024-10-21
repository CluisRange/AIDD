from django.shortcuts import render
from datetime import date


Glasses_Orders_list = [
    {
        'id': 1,
        'ItemIds':[1, 2, 3]
    },
    {
        'id': 2,
        'ItemIds':[]
    },
    {
        'id': 3,
        'ItemIds':[3, 4, 5, 1]
    }
]

Lenses_list = [
    {'image': 'http://localhost:9000/glassesimgs/img1.jpeg',
    'name': 'Однофокальные линзы',
    'dscr': 'Однофокальные (или монофокальные) линзы имеют одну оптическую зону и поэтому подходят для коррекции только одного фокусного расстояния – дальнего или близкого. Они имеют одинаковую оптическую силу по всей поверхности и считаются стандартными.',
    'price': '2 000 рублей',
    'id': 1
    },
    {'image': 'http://localhost:9000/glassesimgs/img2.jpeg',
    'name': 'Прогрессивные линзы',
    'dscr': 'Особенность таких линз − определенная оптическая сила на разных участках. Посмотрев через верхнюю часть, можно с легкостью разглядеть предметы на значительном расстоянии. Нижняя половина предназначена для рассмотрения объектов, расположенных вблизи. К примеру, если нужно прочитать газету или поработать с мелкими деталями, смотрят через нижнюю область. Для того, чтобы хорошо видеть птицу на далеко стоящем дереве, используют только верхнюю зону.',
    'price': '1 000 рублей',
    'id': 2
    },
    {'image': 'http://localhost:9000/glassesimgs/img3.jpeg',
    'name': 'Офисные линзы',
    'dscr': 'Офисные линзы – это упрощённая разновидность прогрессивных линз– идеальное решение для тех, кому необходимо четкое зрение на близких и средних расстояниях в одних очках одновременно. Т. е. в первую очередь для людей которым приходится использовать две пары очков: одни для чтения, а вторые для компьютера.',
    'price': '1 500 рублей',
    'id': 3
    },
    {'image':  'http://localhost:9000/glassesimgs/img4.jpeg',  
    'name': 'Линзы с защитой от компьютера',
    'dscr': 'Специальная линза, которую называют «С защитой от синего света», «Компьютерной» или BlueBlocker, не пропускает этот вредный свет за счет специального отражающего покрытия. Очки для компьютера с такими линзами блокируют воздействие вредной части спектра на сетчатку.',
    'price': '2 000 рублей',
    'id': 4
    },
    {'image': 'http://localhost:9000/glassesimgs/img5.jpeg', 
    'name': 'Спортивные линзы',
    'dscr': 'В первую очередь задачей спортивных очков является защита глаз спортсмена (от излишнего света, ветра, пыли, грязи и т.д.). При этом конструкция очков и материалы, из которых они изготовлены должны быть таковы, чтобы ни при каких обстоятельствах они не могли травмировать лицо и, главное, глаза спортсмена. Однако нередко  встаёт ещё одна задача: в случае слабого зрения спортсмена необходима его коррекция. При этом возникает ряд сложностей, как конструктивного (надёжно, безопасно разместить все элементы в достаточно малом объёма очков), так и оптического свойства (особенности конструкции спортивных очков резко сужают возможности использования обычных очковых линз).',
    'price': '6 000 рублей',
    'id': 5
    },
    {'image': 'http://localhost:9000/glassesimgs/img6.jpeg', 
    'name': 'Фотохромные линзы',
    'dscr': 'Фотохромные линзы, или линзы-хамелеоны, обладают переменным светопропусканием. Это означает, что они меняют прозрачность в зависимости от освещенности. При попадании на них ультрафиолета линзы становятся темными, но стоит зайти в помещение — и они снова бесцветные, как у обычных очков для зрения.',
    'price': '10 000 рублей',
    'id': 6
    }
]

def GlassesOrderController(request, id):

    linses_in_order_list = []

    for GlassesOrder in Glasses_Orders_list:
        if GlassesOrder['id'] == id:
            for i in GlassesOrder['ItemIds']:
                for Lens in Lenses_list:
                    if Lens['id'] == i:
                        linses_in_order_list.append(Lens)

    return render(request, 'GlassesOrder.html', {'data' : {
        'id': id,
        'lenses': linses_in_order_list
    }})

def LensesController(request):

    GlassesOrder_id = 3

    GlassesOrderCount = 0
    for Order in Glasses_Orders_list:
        if Order['id'] == GlassesOrder_id:
            GlassesOrderCount =  len(Order['ItemIds'])

    search = ''
    if 'search_lens' in request.GET:
        search = request.GET['search_lens']

    lenses_list_main = []

    for order in Lenses_list:
        if search.lower() in order['name'].lower():
            lenses_list_main.append(order)

    return render(request, 'Lenses.html', {'data' : {
        'Lenses': lenses_list_main,
        'GlassesOrderCount' : GlassesOrderCount,
        'GlassesOrder_id' : GlassesOrder_id
    }})

def LensDescriptionController(request, id):
    return render(request, 'OneLense.html', {'data' : {
        'Lens' : Lenses_list[id-1],
        'id': id
    }})

