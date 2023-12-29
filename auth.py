from config import ADMIN_USERNAME, ADMIN_PASSWORD

def authenticate(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD
