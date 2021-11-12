import os

if os.getenv("LEVEL") == "PRODUCTION":
    print('RUN PRODUCTION MODE')
    from .production import *

else:
    print('RUN LOCAL MODE')
    from .local import *
