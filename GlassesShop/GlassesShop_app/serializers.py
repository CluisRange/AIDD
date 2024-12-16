from GlassesShop_app.models import GlassesOrder, Lens, MToM
from rest_framework import serializers
from django.contrib.auth import get_user_model
from collections import OrderedDict

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = get_user_model()
        fields = ['email', 'is_staff', 'is_superuser', 'username']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class GlassesOrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = GlassesOrder
        fields = ['glasses_order_id', 'status', 'date_created', 'creator', 'date_formed', 'moderator', 'order_sum', 'phone', 'date_ended']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class LensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lens
        fields = ['lens_id', 'name', 'description', 'status', 'url', 'price']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class MToMSerializer(serializers.ModelSerializer):
    lens_id = serializers.IntegerField() 
    glasses_order_id = serializers.IntegerField()
    class Meta:
        model = MToM
        fields = ['lens_id', 'glasses_order_id', 'dioptres']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class MToMInsertedSerializer(serializers.ModelSerializer):
    lens = LensSerializer(read_only=True)
    class Meta:
        model = MToM
        fields = ['lens', 'dioptres']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class SingleGlassesOrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    lenses = MToMInsertedSerializer(many=True, read_only=True, source='linked_glasses_order')

    class Meta:
        model = GlassesOrder
        fields = ['glasses_order_id', 'status', 'date_created', 'creator', 'date_formed', 'moderator', 'order_sum', 'phone', 'date_ended', 'lenses']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields
