from datetime import timedelta

from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    tg_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = PhoneNumberField(region='RU', blank=True)
    street = models.CharField(max_length=100, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    flat_number = models.CharField(max_length=20, blank=True)


class Level(models.Model):
    LEVELS = [
        ('1L', '1 уровень'),
        ('2L', '2 уровня'),
        ('3L', 'З уровня'),
    ]
    name = models.CharField(
        max_length=10,
        choices=LEVELS,
    )
    price = models.DecimalField(max_digits=5, decimal_places=1)


class Shape(models.Model):
    SHAPES = [
        ('SQUARE', 'Квадрат'),
        ('CIRCLE', 'Круг'),
        ('RECTANGLE', 'Прямоугольник'),
    ]
    name = models.CharField(
        max_length=30,
        choices=SHAPES,
    )
    price = models.DecimalField(max_digits=5, decimal_places=1)


class Topping(models.Model):
    TOPPINGS = [
        ('ZERO', 'Без топпинга'),
        ('WHITE', 'Белый соус'),
        ('CARAMEL', 'Карамельный сироп'),
        ('MAPLE', 'Кленовый сироп'),
        ('STRAWBERRY', 'Клубничный сироп'),
        ('BLUEBERRY', 'Черничный сироп'),
        ('MILK', 'Молочный шоколад'),
    ]
    name = models.CharField(
        max_length=30,
        choices=TOPPINGS,
    )
    price = models.DecimalField(max_digits=5, decimal_places=1)


class Berry(models.Model):
    BERRIES = [
        ('BLACKBERRY', 'Ежевика'),
        ('RASPBERRY', 'Малина'),
        ('BLUEBERRY', 'Голубика'),
        ('STRAWBERRY', 'Клубника'),
    ]
    name = models.CharField(
        max_length=30,
        choices=BERRIES,
    )
    price = models.DecimalField(max_digits=5, decimal_places=1)


class Decor(models.Model):
    DECORS = [
        ('PISTACHIO', 'Фисташки'),
        ('MERINGUE', 'Безе'),
        ('HAZELNUTS', 'Фундук'),
        ('PECAN', 'Пекан'),
        ('MARSHMALLOW', 'Маршмеллоу'),
        ('MARZIPAN', 'Марципан'),
    ]
    name = models.CharField(
        max_length=30,
        choices=DECORS,
    )
    price = models.DecimalField(max_digits=5, decimal_places=1)


class Order(models.Model):
    ORDER_STATUS = [
        ('START', 'Заказ создан'),
        ('CANCELED', 'Заказ отменен'),
        ('PROCESSING', 'Заказ обрабатывается'),
        ('MANUFACTURING', 'Готовим ваш торт'),
        ('DELIVERING', 'Торт в пути'),
        ('DONE', 'Торт у вас'),

    ]
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="client"
    )
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS,
        default='START'
    )
    promo = models.CharField(max_length=15, blank=True)
    comment = models.TextField(blank=True)
    default_delivery = timezone.now() + timedelta(days=3)
    delivery_date = models.DateTimeField(default=default_delivery)
    price = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0
    )


class Title(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="cake_title"
    )
    name = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=1)


class Cake(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="level"
    )
    shape = models.ForeignKey(
        Shape,
        on_delete=models.CASCADE,
        related_name="shape"
    )
    topping = models.ForeignKey(
        Topping,
        on_delete=models.CASCADE,
        related_name="topping"
    )
    berry = models.ForeignKey(
        Berry,
        on_delete=models.CASCADE,
        related_name="berry",
        blank=True,
        null=True
    )
    decor = models.ForeignKey(
        Decor,
        on_delete=models.CASCADE,
        related_name="decor",
        blank=True,
        null=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="decor",
        blank=True,
        null=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )