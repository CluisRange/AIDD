from django.db import models

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

class GlassesOrder(models.Model):
    glasses_order_id = models.AutoField(primary_key=True)
    status = models.TextField()
    date_created = models.DateTimeField()
    creator = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='creator')
    date_formed = models.DateTimeField(blank=True, null=True)
    moderator = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='moderator', related_name='glassesorder_moderator_set', blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    order_sum = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'glasses_order'


class Lens(models.Model):
    lens_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(unique=True, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lens'


class MToM(models.Model):
    lens = models.ForeignKey(Lens, on_delete=models.DO_NOTHING)
    glasses_order = models.ForeignKey(GlassesOrder, on_delete=models.DO_NOTHING)
    dioptres = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'm_to_m'
        constraints = [
            models.UniqueConstraint(fields=['lens', 'glasses_order'], name='unique_key')
        ]