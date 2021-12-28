# {'data': {u'node': [], u'name': u'John Doe', u'regdate': u'2021/12/26', u'token': u'6gKFKqPPgLQ3X0asUsWE_gvCjFGt4L7MWGf7ptNXoKUX5nCRIrQvVm996gdboRkOAp43CBAOQ8F1YFcxMLejjZEQl-rbW9b86IdTGMExE_t-vcaoH7Hgya9es-6q_g7-otVi4g', u'message': u'Login successful', u'email': u'john@gmail.com'}, 'back': None, 'error': False}
import ConfigParser

CONFIG_FILE = 'config.ini'
SECTION = 'LoginDetails'

def save(name, regdate, token, email):
    # save the token to the config file
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)
    # check if section exists delete it
    if config.has_section(SECTION):
        config.remove_section(SECTION)
        # with open(CONFIG_FILE, 'wb') as configfile:
        #     config.write(configfile)
    config.add_section(SECTION)
    config.set(SECTION, 'token', token)
    config.set(SECTION, 'name', name)
    config.set(SECTION, 'regdate', regdate)
    config.set(SECTION, 'email', email)
    with open(CONFIG_FILE, 'wb') as configfile:
        config.write(configfile)
        
def load():
    config = ConfigParser.RawConfigParser()
    # check if config file exists
    config.read(CONFIG_FILE)
    if not config.has_section(SECTION):
        return False
    token = config.get(SECTION, 'token')
    name = config.get(SECTION, 'name')
    regdate = config.get(SECTION, 'regdate')
    email = config.get(SECTION, 'email')
    if not token or not name or not regdate or not email:
        return False
    return name, email, token, regdate

def clear():
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)
    config.remove_section(SECTION)
    with open(CONFIG_FILE, 'wb') as configfile:
        config.write(configfile)