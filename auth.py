import configparser
from constants import *

def save(name, regdate, token, email):
    clear()
    config = configparser.ConfigParser()
    config.add_section(SECTION)
    config[SECTION]['name'] = name
    config[SECTION]['regdate'] = regdate
    config[SECTION]['token'] = token
    config[SECTION]['email'] = email
    with open(CREDENTIAL_FILE, 'w') as configfile:
        config.write(configfile)
                
def load():
    config = configparser.ConfigParser()
    config.read(CREDENTIAL_FILE)
    # check if has section
    if not config.has_section(SECTION):
        return False
    name = None
    if config.has_option(SECTION, 'name'):
        name = config[SECTION]['name']
    regdate = None
    if config.has_option(SECTION, 'regdate'):
        regdate = config[SECTION]['regdate']
    token = None
    if config.has_option(SECTION, 'token'):
        token = config[SECTION]['token']
    email = None
    if config.has_option(SECTION, 'email'):
        email = config[SECTION]['email']
    if name and regdate and token and email:
        return name, email, token, regdate
    else:
        return False

def clear():
    config = configparser.ConfigParser()
    config.read(CREDENTIAL_FILE)
    # check if has section
    if not config.has_section(SECTION):
        return False
    config.remove_section(SECTION)
    with open(CREDENTIAL_FILE, 'w') as configfile:
        config.write(configfile)