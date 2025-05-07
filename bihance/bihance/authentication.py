import jwt
import os
import requests

from applications.models import User
from django.core.cache import cache
from dotenv import load_dotenv
from jwt.algorithms import RSAAlgorithm
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


load_dotenv()
CLERK_API_URL='https://api.clerk.com/v1'
CACHE_KEY = "jwks_data"


class JWTAuthenticationMiddleware(BaseAuthentication): 
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header: 
            return None 
        
        try: 
            # [0] is `Bearer`
            token = auth_header.split(" ")[1]
        except IndexError:
            raise AuthenticationFailed("Bearer token not provided.")
        
        user = self.decode_jwt(token)
        if not user: 
            return None
        
        clerk = ClerkSDK()
        info, found = clerk.fetch_user_info(user.id)
        if found: 
            user.email = info["email"]
            user.first_name = info["first_name"]
            user.last_name = info["last_name"]
            user.save()
        
        # Returns the authenticated user
        # Along with the credentials used for authentication (None, cuz not needed anymore)
        return user, None 
        

    def decode_jwt(self, token): 
        clerk = ClerkSDK()
        jwks_data = clerk.get_jwks()

        # Public key used to verify the JWT token
        public_key = RSAAlgorithm.from_jwk(jwks_data["keys"][0])

        try: 
            payload = jwt.decode(
                token, 
                public_key,
                algorithms=["RS256"],
                options={"verify_signature": True}, 
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.DecodeError:
            raise AuthenticationFailed("Token decode error.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.") 

        user_id = payload.get("sub")
        if user_id: 
            # Even if user was created
            # Other compulsory fields will be set later
            user, created = User.objects.get_or_create(id=user_id)
            return user 
        
        return None


class ClerkSDK: 
    # Returns a tuple 
    # First element -> user info, as an dictionary
    # Second element -> boolean found, if user info was found or not
    def fetch_user_info(self, user_id: str): 
        api_endpoint = f'{CLERK_API_URL}/users/{user_id}'
        headers = {"Authorization": f"Bearer {os.getenv('CLERK_SECRET_KEY')}"}
        response = requests.get(api_endpoint, headers=headers)

        # 200 OK
        if response.status_code == 200: 
            data = response.json() 
            return {
                "email": data["email_addresses"][0]["email_address"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
            }, True
        else:
            return {
                "email": "",
                "first_name": "",
                "last_name": "",
            }, False


    def get_jwks(self): 
        jwks_data = cache.get(CACHE_KEY)
        if not jwks_data:
            api_endpoint = f"{os.getenv('CLERK_FRONTEND_API_URL')}/.well-known/jwks.json"
            response = requests.get(api_endpoint)
            
            # 200 OK
            if response.status_code == 200: 
                jwks_data = response.json()
                cache.set(CACHE_KEY, jwks_data)
            else: 
                raise AuthenticationFailed("Failed to fetch JWKS.")
        
        return jwks_data


