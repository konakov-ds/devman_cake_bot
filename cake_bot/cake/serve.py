from datetime import datetime
from cake.models import *

# Serving functional


def get_base_user_info(update):

    if not update.message.chat.last_name:
        last_name = ''
    else:
        last_name = update.message.chat.last_name

    user_info = {
        'tg_id': update.message.chat_id,
        'name': update.message.chat.first_name,
        'last_name': last_name
    }
    if update.message.contact:
        user_info['phone'] = update.message.contact.phone_number
    return user_info


def get_user_info_from_db(tg_id):
    client = Profile.objects.get(tg_id=tg_id)
    user_info = {
        'tg_id': tg_id,
        'name': client.name,
        'last_name': client.last_name,
        'phone': client.phone.as_e164,
        'street': client.street,
    }
    return user_info


def validate_delivery_time(time):
    try:
        time = datetime.strptime(time, '%d.%m.%Y | %H:%M')
        return time
    except Exception:
        return False


def check_fast_delivery(time):
    now = datetime.now()
    delay = time - now
    return delay.days < 1


def write_user_to_db(user_info):
    Profile.objects.create(
        **user_info
    )


def write_title_db(order, name, price):
    Title.objects.create(
        order=order,
        name=name,
        price=price
    )


def get_cake_level(level):
    print(level)
    levels = {i[1]: i[0] for i in Level.LEVELS}
    print(levels)
    level = Level.objects.get(name=levels[level])
    level_p = level.price
    return level, level_p


def get_cake_shape(shape):
    shapes = {i[1]: i[0] for i in Shape.SHAPES}
    shape = Shape.objects.get(name=shapes[shape])
    shape_p = shape.price
    return shape, shape_p


def get_cake_topping(topping):
    toppings = {i[1]: i[0] for i in Topping.TOPPINGS}
    topping = Topping.objects.get(name=toppings[topping])
    topping_p = topping.price
    return topping, topping_p


def get_cake_berry(berry):
    if berry != 'Без ягод':
        berries = {i[1]: i[0] for i in Berry.BERRIES}
        berry = Berry.objects.get(name=berries[berry])
        berry_p = berry.price
    else:
        berry = None
        berry_p = 0
    return berry, berry_p


def get_cake_decor(decor):
    if decor != 'Без декора':
        decors = {i[1]: i[0] for i in Decor.DECORS}
        decor = Decor.objects.get(name=decors[decor])
        decor_p = decor.price
    else:
        decor = None
        decor_p = 0
    return decor, decor_p


def get_title_price(title):
    if title:
        return 500
    else:
        return 0


def get_order_info(cake_params):
    level, level_p = get_cake_level(cake_params['level'])
    shape, shape_p = get_cake_shape(cake_params['shape'])
    topping, topping_p = get_cake_topping(cake_params['topping'])
    berry, berry_p = get_cake_berry(cake_params['berry'])
    decor, decor_p = get_cake_decor(cake_params['decor'])
    title_p = get_title_price(cake_params['title'])
    cake_price = level_p + shape_p + topping_p + berry_p + decor_p + title_p
    cake_wrapper = [level, shape, topping, berry, decor]
    return cake_wrapper, cake_price


def get_cake_title(title, order):
    if title:
        title = Title.objects.get_or_create(
            order=order,
            name=title,
            price=500
        )
        title_p = 500
    else:
        title = Title.objects.get_or_create(
            order=order,
            name=title,
            price=0
        )
        title_p = 0
    return title, title_p


def create_order(user_info, order_info):
    profile = Profile.objects.get(tg_id=user_info['tg_id'])
    comment = order_info['comment']
    delivery_date = order_info['delivery_date']
    price = order_info['price']

    order = Order.objects.create(
        profile=profile,
        comment=comment,
        delivery_date=delivery_date,
        price=price
    )
    return order


def create_cake(order, order_info):
    params = get_order_info(order_info)[0]
    title = get_cake_title(order_info['title'], order)[0][0]

    Cake.objects.create(
        level=params[0],
        shape=params[1],
        topping=params[2],
        berry=params[3],
        decor=params[4],
        title=title,
        order=order
    )


def check_client_orders(client_id):
    client = Profile.objects.get(tg_id=client_id)
    orders = Order.objects.filter(profile=client)
    return orders.count() > 0