from common.common import get_secret


VERSION = get_secret("VERSION")
API_KEY = get_secret("API_KEY")
REDIS_TTL = 8600
REDIS_HOST = get_secret("REDIS_HOST")
REDIS_PORT = get_secret("REDIS_PORT")
REDIS_DB= get_secret("REDIS_DB")
POSTGRES_USER = get_secret("POSTGRES_USER")
POSTGRES_PASSWORD = get_secret("POSTGRES_PASSWORD")
POSTGRES_PORT = get_secret("POSTGRES_PORT")
POSTGRES_DB = get_secret("POSTGRES_DB")
SNIPPET_DIR = "./gleam_snippets"
