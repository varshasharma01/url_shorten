import string
import secrets

def generate_short_code(length: int = 6)->str:
    
    # this will include the combination of ascii letters and digits
    
    code = string.ascii_letters + string.digits
    # merge the secure 6 characters
    
    return "".join(secrets.choice(code) for i in range (length))