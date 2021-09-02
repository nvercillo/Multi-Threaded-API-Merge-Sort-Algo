import os
from binascii import hexlify

key = hexlify(os.urandom(40))
f = open(".env", "a+")
f.write(f"\nAPI_KEY={key.decode()}\n")
f.close()
