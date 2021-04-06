import datetime 
import uuid

from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .serializers import AddFavoriteSerializer, RemoveFavoriteSerializer, ListBeerSerializer
from .models import Beer, Malts, Hops

from user.models import User

# Create your views here.

class BeerCreateListDestroy(APIView):

    parser_classes = [FormParser, JSONParser, MultiPartParser]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self, request):
        user_id = request.user.public_id
        return Beer.objects.filter(user__public_id=user_id, is_active=True)

    def post(self, request, *args, **kwargs):
        user_id = request.user.public_id
        serializer = AddFavoriteSerializer(context={"user_id": user_id}, data=request.data)

        if serializer.is_valid():

            data = request.data
            beer = Beer.objects.create(
                user=request.user,
                api_id=data.get("beer_id"),
            )

            beer.save()
            
            for data in eval(request.data.get("malts")):
                    
                malt = Malts.objects.create(
                    beer=beer,
                    name=data,
                )

                malt.save()
            
            for data in eval(request.data.get("hops")):
                    
                hop = Hops.objects.create(
                    beer=beer,
                    name=data,
                )

                hop.save()

            return JsonResponse({'response': 'Beer as been add to favorite'}, status=201)

        return JsonResponse({
            'errors': serializer.errors,
        }, status=404)

    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = ListBeerSerializer(queryset, many=True)
        return JsonResponse(list(serializer.data), safe=False, status=200)
        
        return JsonResponse({
            'errors': serializer.errors
        }, status=400)
    

    def delete(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]

        user_id = request.user.public_id
        serializer = RemoveFavoriteSerializer(context={'user_id': user_id}, data=request.data)

        if serializer.is_valid():

            data = request.data
            beer = Beer.objects.get(user=request.user, api_id=data.get("beer_id"), is_active=True)
            beer.is_active = False
            beer.save()

            return JsonResponse({'response': 'Beer as been removed from your favorite'})

        return JsonResponse({
            'errors': serializer.errors
        }, status=400)
