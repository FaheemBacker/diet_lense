from django.shortcuts import render
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView
from diet_app.serializers import *
from diet_app.models import *
from diet_app.permissions import IsOwner
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from diet_app.utility_func import calculate_bmr
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Aggregate

# Create your views here.
class SignupUser(CreateAPIView):
    serializer_class = UserSerializer


class ProfileView(CreateAPIView):
    serializer_class = UserProfileSerilizer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_object = self.request.user
        # data =serializer.validated_data
        # bmr = calculate_bmr(
        #     age = data.get('age'),
        #     height = data.get('height'),
        #     weight = data.get('weight'),
        #     gender = data.get('gender'),
        #     activity_level = data.get('activity_level')
        # )
        return serializer.save(owner = user_object)

class ProfileRetriveView(RetrieveAPIView,UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwner]
    serializer_class = UserProfileSerilizer
    queryset = UserProfile.objects.all()

class UserRetriveView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwner]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


class Foodlogcreateview(CreateAPIView,ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = Foodlogserializer
    queryset = FoodLog.objects.all()
    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)  
    
    def get_queryset(self):
        return self.queryset.filter(owner = self.request.user)  

class FoodlogFunctions(RetrieveAPIView,DestroyAPIView,UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwner]
    serializer_class = Foodlogserializer
    queryset =FoodLog.objects.all()   

class DietSummaryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwner]
    def get(self,request,*args,**kwargs):
        cur_date = timezone.now()
        queryset = FoodLog.objects.filter(created_at__date = cur_date,owner = request.user)
        calories_consumed = queryset.values("calories").aggregate(sum('calories'))
        print(calories_consumed)
        print(request.user.profile.bmr)
        context ={
            "total_calories_consumed":calories_consumed.get('calories__sum'),
            "daily_target":request.user.profile.bmr,
            "balance":request.user.profile.bmr.calories_consumed,
        }
        return Response(context)
    