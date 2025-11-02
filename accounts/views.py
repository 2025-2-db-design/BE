from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, ProfileUpdateSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


#---------------------------------------------------------------------------------------
# 회원가입
#---------------------------------------------------------------------------------------
class RegisterView(APIView):
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            user = s.save()
            return Response({
                'message': '회원가입 성공',
                'user': {
                    'email': user.email,
                    'name': user.name,
                    'nickname': user.nickname
                }
            }, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


#---------------------------------------------------------------------------------------
# 로그인
#---------------------------------------------------------------------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


#---------------------------------------------------------------------------------------
# 로그아웃
#---------------------------------------------------------------------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({'message': 'logout success'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


#---------------------------------------------------------------------------------------
# 내 정보 수정
#---------------------------------------------------------------------------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'id': u.id,
            'email': u.email,
            'name': u.name,
            'nickname': u.nickname
        })

    def patch(self, request):
        s = ProfileUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if s.is_valid():
            u = s.save()
            return Response({
                'message': 'update success',
                'user': {
                    'email': u.email,
                    'name': u.name,
                    'nickname': u.nickname
                }
            })
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

#---------------------------------------------------------------------------------------
# 비밀번호 변경(ChangePasswordView)
#---------------------------------------------------------------------------------------
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '비밀번호 변경 완료'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
