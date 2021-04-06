import os
from django.contrib.auth.hashers import check_password
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from user.models import User
from .models import Malts, Hops, Beer



from rest_framework import serializers 

# Create the form class.
#_AddFavoriteSerializer
class AddFavoriteSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        serializers.Serializer.__init__(self, *args, **kwargs)

    beer_id = serializers.CharField(max_length=10, error_messages={
        'required': "Please enter the beer id",
    })

    hops = serializers.CharField(max_length=3000,error_messages={
        'required': "Please enter beer hops",
    })

    malts = serializers.CharField(max_length=3000, error_messages={
        'required': "Please enter beer malts",
    })

    def __init__(self, *args, **kwargs):
        serializers.Serializer.__init__(self, *args, **kwargs)

    def validate_hops(self, value):
        
        try:
            eval(value)
        except:
            raise ValidationError("Hops must be a valid list of hops. Exemple: ['Fuggles', 'First Gold']")

        return value

    def validate_malts(self, value):

        try:
            eval(value)
        except:
            raise ValidationError("Malts must be a valid list of malts. Exemple: ['Maris Otter Extra Pale', 'Caramalt']")
    
    def validate_beer_id(self, value):

        beer = Beer.objects.filter(
            user__public_id = self.context['user_id'],
            api_id = value,
            is_active = True
        ).all()

        print(beer)
        if len(beer) > 0:
            raise ValidationError("Beer is already in your favorite")


#_RemoveFavoriteSerializer
class RemoveFavoriteSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        serializers.Serializer.__init__(self, *args, **kwargs)
        self.user_id = self.context['user_id']

    beer_id = serializers.CharField(max_length=10, error_messages={
        'required': "Please enter the beer id",
    })

    def validate_beer_id(self, value):

        try:
            beer = Beer.objects.get(
                api_id = value,
                user__public_id = self.user_id,
                is_active = True
            )
        except:
            raise ValidationError("Beer not found")

        return value

class ListMaltsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Malts
        fields = ['name']

class ListHopsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hops
        fields = ['name']

class ListBeerSerializer(serializers.ModelSerializer):
    
    malts = serializers.StringRelatedField(many=True)
    hops = serializers.StringRelatedField(many=True)

    class Meta:
        model = Beer
        fields = ['api_id', 'malts', 'hops']