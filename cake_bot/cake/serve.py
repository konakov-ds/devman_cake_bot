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


def validate_phone(phone):
    pass


def write_user_to_db(user_info):
    Profile.objects.create(
        **user_info
    )


def get_cake_level(level):
    levels = {i[1]: i[0] for i in Level.LEVELS}
    return Level.objects.get(name=levels[level])


def get_cake_shape(shape):
    shapes = {i[1]: i[0] for i in Shape.SHAPES}
    return Shape.objects.get(name=shapes[shape])


def get_cake_topping(topping):
    toppings = {i[1]: i[0] for i in Topping.TOPPINGS}
    return Topping.objects.get(name=toppings[topping])


def get_cake_berry(berry):
    berries = {i[1]: i[0] for i in Berry.BERRIES}
    return Berry.objects.get(name=berries[berry])


def get_cake_decor(decor):
    decors = {i[1]: i[0] for i in Decor.DECORS}
    return Decor.objects.get(name=decors[decor])


def get_cake_title(order_id):
    return Title.objects.get(order=order_id)


def create_order(update):
    profile = Profile.objects.get(tg_id=update.effective_chat.id)
    order = Order.objects.create(
        profile=profile,
    )
    return order


def create_cake(cake_params, order_id):
    cake = Cake.objects.create(
        level=get_cake_level(cake_params['level']),
        shape=get_cake_shape(cake_params['shape']),
        topping=get_cake_topping(cake_params['topping']),
        order=Order.objects.get(id=order_id)
    )
    return cake


def check_client_orders(client_id):
    client = Profile.objects.get(tg_id=client_id)
    orders = Order.objects.filter(profile=client)
    return orders.count() > 0