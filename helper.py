from datetime import timedelta
import random
import string
import subprocess


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
    cmd_one = "sed -i '/^TOKEN_SHUFFLE/d' %s" % __file__
    subprocess.call(cmd_one, shell=True)
    cmd_two = r'sed -i "$ a\CRYPTO_AUTH_TOKEN_SHUFFLE = %s" %s' % (str(_shuffled), __file__)
    subprocess.call(cmd_two, shell=True)

    print("Token shuffle for crypto_app was successfully created!")
