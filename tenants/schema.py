from drf_spectacular.extensions import OpenApiAuthenticationExtension

class JWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'tenants.authentication.JWTAuthentication'
    name = 'JWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }