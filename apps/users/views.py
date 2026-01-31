from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile
from .serializers import CustomUserDetailsSerializer, UserProfileSerializer

class UserMeView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserDetailsSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        profile = self.request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CustomUserDetailsSerializer(self.request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleFitAuthView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"detail": "Google Fit認証画面へリダイレクト"})

class StepSyncView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"detail": "Google Fitから歩数を取得"})