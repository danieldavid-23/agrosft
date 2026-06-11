from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

def create_user_custom(backend, details, response, uid, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}
        
    User = get_user_model()
    
    # Extract email and names from Google profile details
    email = details.get('email') or f"{uid}@google.com"
    first_name = details.get('first_name') or 'Google'
    last_name = details.get('last_name') or 'User'
    
    # Check if a user already exists with this email
    try:
        user = User.objects.get(correo=email)
        return {
            'is_new': False,
            'user': user
        }
    except User.DoesNotExist:
        pass
        
    # Create the user using the custom manager create_user method
    # generate a random password
    random_password = get_random_string(32)
    user = User.objects.create_user(
        correo=email,
        nombres=first_name,
        apellidos=last_name,
        password=random_password,
        telefono=''
    )
    
    return {
        'is_new': True,
        'user': user
    }
