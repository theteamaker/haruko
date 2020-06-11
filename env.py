from dotenv import load_dotenv
import os

load_dotenv()

HARUKO_SERVERS_DB = os.getenv("HARUKO_SERVERS_DB")
HARUKO_TOKEN = os.getenv("HARUKO_TOKEN")
CANADAPOST_AUTHORIZATION = os.getenv("CANADAPOST_AUTHORIZATION")