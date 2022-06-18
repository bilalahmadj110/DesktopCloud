from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import auth
import register
import styles
from constants import *
from networking import *


class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.textEmail = QLineEdit(self)
        self.textPassword = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)

        self.textPassword.setEchoMode(QLineEdit.Password)

        # settins style on all texbox
        styles.textbox(self.textEmail, self.textPassword)
        styles.button(self.buttonLogin)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.textEmail)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.textPassword)
        layout.addWidget(self.buttonLogin)
        # Don't have an account, register link label
        register_link = QLabel('Don\'t have an account yet? <a href="http://www.example.com"><b>Create</b></a> it.')
        # match width to the parent widget
        register_link.setAlignment(Qt.AlignHCenter)
        layout.addWidget(register_link)

        # signal to open the link
        register_link.linkActivated.connect(self.openLink)

        self.buttonLogin.clicked.connect(self.handleLogin)

        # resize the layout width, height
        # layout.resize(400, 100)
        self.setFixedSize(450, 220)
        self.setFont(QFont('SegoeUI', 10))
        # layout.setSizeConstraint(QLayout.SetFixedSize)

        self.setWindowTitle('Login Cloud Drive')

        # self.fill_all()

    def receiveResponse(self, resp):
        self.doneLoading()
        print("Response: " + str(resp))
        if 'data' in resp:
            if 'message' in resp['data']:
                if resp['data']['message'] == u'Login successful':
                    # login success, now save the token
                    print("Saving token...")
                    auth.save(resp['data']['name'], resp['data']['regdate'], resp['data']['token'],
                              resp['data']['email'], resp['data']['is_admin'], resp['data']['access'])
                    self.openWindow()
                else:
                    QMessageBox.information(self, 'Acount creation failed', resp['data']['message'])
            else:
                QMessageBox.information(self, 'Acount creation failed',
                                        'An error occurred, response was invalid, please contact developer.')
        elif 'message' in resp:
            QMessageBox.information(self, 'Acount creation failed', resp['message'])
        else:
            QMessageBox.information(self, 'Acount creation failed', 'Unknown error occured, please try again later.')

    def openLink(self, link):
        self.accept()
        from register import Register
        r = Register(parent=self)
        r.show()

    def openWindow(self):
        self.accept()
        from welcome import WelcomeScreen
        main_screen = WelcomeScreen(parent=self)
        main_screen.show()

    def handleLogin(self):
        valid = self.validate()
        if valid == True:
            self.setLoading()
            self.thread1 = ResponseThread(
                SIGN_IN_API,
                form_data={"email": self.textEmail.text(), "password": self.textPassword.text()}, parent=self)
            self.thread1.start()
            self.thread1.signal.sig.connect(self.receiveResponse)
        else:
            # show a message box
            QMessageBox.information(self, 'Error', valid)
            return

    def validate(self):
        if self.textEmail.text() == '' or not styles.validate_email(self.textEmail.text()):
            return 'Please enter a valid email address'
        if self.textPassword.text() == '' or len(self.textPassword.text()) < 6:
            return 'Password is required (min 6 characters)'
        return True

    def setLoading(self):
        self.buttonLogin.setText('Signing in...')
        self.buttonLogin.setEnabled(False)

    def doneLoading(self):
        self.buttonLogin.setText('Login')
        self.buttonLogin.setEnabled(True)

    def fill_all(self):
        self.textEmail.setText('john@gmail.com')
        self.textPassword.setText('password.')
