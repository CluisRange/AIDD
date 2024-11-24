from GlassesShop_app.models import AuthUser, GlassesOrder, Lens, MToM
from rest_framework import serializers
from django.contrib.auth import get_user_model

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class GlassesOrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = GlassesOrder
        fields = ['glasses_order_id', 'status', 'date_created', 'creator', 'date_formed', 'moderator', 'order_sum', 'phone', 'date_ended']

class LensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lens
        fields = ['lens_id', 'name', 'description', 'status', 'url', 'price']

class MToMSerializer(serializers.ModelSerializer):
    lens_id = serializers.IntegerField() 
    glasses_order_id = serializers.IntegerField()
    class Meta:
        model = MToM
        fields = ['lens_id', 'glasses_order_id', 'dioptres']

class MToMInsertedSerializer(serializers.ModelSerializer):
    lens = LensSerializer(read_only=True)
    class Meta:
        model = MToM
        fields = ['lens', 'dioptres']

class SingleGlassesOrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    lenses = MToMInsertedSerializer(many=True, read_only=True, source='linked_glasses_order')

    class Meta:
        model = GlassesOrder
        fields = ['glasses_order_id', 'status', 'date_created', 'creator', 'date_formed', 'moderator', 'order_sum', 'phone', 'date_ended', 'lenses']
