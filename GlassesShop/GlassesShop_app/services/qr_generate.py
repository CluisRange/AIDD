import segno
import base64
from io import BytesIO
from GlassesShop_app.models import MToM

def statustranslate(status):
    if status == 'draft':
        return 'Черновик'
    elif status == 'formed':
        return 'Сформирован'
    elif status == 'accepted':
        return 'Принят'
    elif status == 'cancelled':
        return 'Отменен'
    elif status == 'deleted':
        return 'Удален'
    else:
        return 'Неизвестный статус'

def generate_glasses_order_qr(glasses_order):
    # Формируем информацию для QR-кода
    info = f"Заказ №{glasses_order.glasses_order_id}\n\n"
    info += "Статус: " + statustranslate(glasses_order.status) + "\n\n"
    if(glasses_order.status == 'accepted' or glasses_order.status == 'cancelled'):
        info += "Общая стоимость: " + str(glasses_order.order_sum) + "\n"

    # Добавляем информацию о линзах и диоптриях
    info += "Линзы:\n"
    lenses = MToM.objects.filter(glasses_order=glasses_order)

    for lens in lenses:
        print(lens.lens.name)
        info += f"- {lens.lens.name}"
        print(info)
        if(lens.dioptres!=None): 
            info += f": {lens.dioptres} диоптрий\n"
        info += f"  Цена: {lens.lens.price}\n"

    info += "\nдата создания: " + str(glasses_order.date_created) + "\n"
    info += "дата формирования: " + str(glasses_order.date_formed) + "\n"
    info += "дата модерации: " + str(glasses_order.date_ended) + "\n"
    

    # Генерация QR-кода
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    # Конвертация изображения в base64
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return qr_image_base64