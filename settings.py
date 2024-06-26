from os import environ

ATS_ID = environ.get("ATS_ID", "5209")
ATS_IP = environ.get("ATS_IP", "192.168.40.230")
ATS_PORT = environ.get("ATS_PORT", 33333)

# DB_SERVER = environ.get("DB_SERVER", "agat-pdb117")
DB_SERVER = environ.get("DB_SERVER", "192.168.0.209")
DB_USER = environ.get("DB_USER", "")
DB_PWD = environ.get("DB_PWD", "")

NUMBER_PREF = environ.get("NUMBER_PREF", "52")
PREF_MAKECALL = environ.get("PREF_MAKECALL", "9")

DEBUG = environ.get("DEBUG", 0)
