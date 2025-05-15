import random
import string
from datetime import timedelta

alphabet = string.ascii_lowercase


expired_time = {
    "seconds": lambda x: timedelta(seconds=x),
    "minutes": lambda x: timedelta(minutes=x),
    "hours": lambda x: timedelta(hours=x),
    "days": lambda x: timedelta(days=x),
    "weeks": lambda x: timedelta(weeks=x)
}

def create_token_shuffle():
    _shuffled = ["%s" % i for i in alphabet[:10]]
    random.shuffle(_shuffled)
    
    print(f"Token shuffle for crypto_app was successfully created! - {str(_shuffled)}")