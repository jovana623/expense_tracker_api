from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User=get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string=scope.get('query_string', b'').decode()
        query_params=parse_qs(query_string)
        token=query_params.get('token',[None])[0]

        user=AnonymousUser()

        if token:
            try:
                accessToken=AccessToken(token) 
                user_id=accessToken['user_id']
                user=await self.get_user(user_id)
            except Exception as e:
                print(f"JWT auth failed: {e}")
        
        scope['user']=user

        return await super().__call__(scope,receive,send)
    
    @database_sync_to_async
    def get_user(self,user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()