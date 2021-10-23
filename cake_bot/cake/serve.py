from cake.models import *

# Serving functional


def get_base_user_info(update):
    user_info = {
        'tg_id': update.message.chat_id,
        'name': update.message.chat.first_name,
        'last_name': update.message.chat.last_name
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


def validate_phone(phone):
    pass


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
    levels = {i[1]: i[0] for i in Level.LEVELS}
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
    berries = {i[1]: i[0] for i in Berry.BERRIES}
    berry = Berry.objects.get(name=berries[berry])
    berry_p = berry.price
    return berry, berry_p


def get_cake_decor(decor):
    decors = {i[1]: i[0] for i in Decor.DECORS}
    decor = Decor.objects.get(name=decors[decor])
    decor_p = decor.price
    return decor, decor_p


def get_cake_title(order):
    title = Title.objects.get(order=order)
    title_p = title.price
    return title, title_p


def create_order(update):
    profile = Profile.objects.get(tg_id=update.effective_chat.id)
    order = Order.objects.create(
        profile=profile,
    )
    return order


def create_cake(cake_params, order):
    level, level_p = get_cake_level(cake_params['level'])
    shape, shape_p = get_cake_shape(cake_params['shape'])
    topping, topping_p = get_cake_topping(cake_params['topping'])
    berry, berry_p = get_cake_berry(cake_params['berry'])
    decor, decor_p = get_cake_decor(cake_params['decor'])
    title, title_p = get_cake_title(order)
    cake_price = level_p + shape_p + topping_p + berry_p + decor_p + title_p
    Cake.objects.create(
        level=level,
        shape=shape,
        topping=topping,
        berry=berry,
        decor=decor,
        title=title,
        order=order
    )
    order.price = cake_price
    order.save()
    return cake_price


def check_client_orders(client_id):
    client = Profile.objects.get(tg_id=client_id)
    orders = Order.objects.filter(profile=client)
    return orders.count() > 0