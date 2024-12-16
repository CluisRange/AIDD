from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class GlassesOrder(models.Model):
    glasses_order_id = models.AutoField(primary_key=True)
    status = models.TextField()
    date_created = models.DateTimeField()
    creator = models.ForeignKey(get_user_model(), models.DO_NOTHING, db_column='creator', related_name='glassesorder_creator')
    date_formed = models.DateTimeField(blank=True, null=True)
    moderator = models.ForeignKey(get_user_model(), models.DO_NOTHING, db_column='moderator', related_name='glassesorder_moderator_set', blank=True, null=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    order_sum = models.IntegerField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'glasses_order'


class Lens(models.Model):
    lens_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(unique=True, blank=True, null=True)
    status = models.TextField(blank=True, null=True, default='active')
    url = models.TextField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lens'


class MToM(models.Model):
    lens = models.ForeignKey(Lens, on_delete=models.DO_NOTHING, related_name='linked_lens')
    glasses_order = models.ForeignKey(GlassesOrder, on_delete=models.DO_NOTHING, related_name='linked_glasses_order')
    dioptres = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'm_to_m'
        constraints = [
            models.UniqueConstraint(fields=['lens', 'glasses_order'], name='unique_key')
        ]