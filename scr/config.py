import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY    = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX         = os.getenv("GOOGLE_CX")
DEFAULT_NUM_LINKS = int(os.getenv("DEFAULT_NUM_LINKS", 4))
