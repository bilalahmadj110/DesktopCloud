from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import styles
from constants import *
from networking import *


class Register(QDialog):
    def __init__(self, parent=None):
        super(Register, self).__init__(parent)

        # textboxes
        self.textFullName = QLineEdit(self)
        self.textEmail = QLineEdit(self)
        self.textPassword = QLineEdit(self)

        # buttons
        self.buttonRegister = QPushButton('Let\'s Create', self)
        # set upper case
        styles.button(self.buttonRegister)
        # self.setFont(QFont('SegoeUI', 10))
        register_link = QLabel('Already have an account? <a href="http://www.example.com"><b>Login</b></a>')

        # set the password to be hidden
        self.textPassword.setEchoMode(QLineEdit.Password)
        self.textConfirmPassword = QLineEdit(self)
        self.textConfirmPassword.setEchoMode(QLineEdit.Password)

        styles.textbox(self.textFullName, self.textEmail, self.textPassword, self.textConfirmPassword)

        register_link.setAlignment(Qt.AlignHCenter)

        # listeners
        self.buttonRegister.clicked.connect(self.handleRegister)
        register_link.linkActivated.connect(self.openLink)

        # main layout
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Full name'))
        layout.addWidget(self.textFullName)
        layout.addWidget(QLabel('Email'))
        layout.addWidget(self.textEmail)
        layout.addWidget(QLabel('Password'))
        layout.addWidget(self.textPassword)
        layout.addWidget(QLabel('Confirm Password'))
        layout.addWidget(self.textConfirmPassword)

        layout.addWidget(self.buttonRegister)

        layout.addWidget(register_link)
        # signal to open the link

        # resize the layout width, height
        # layout.resize(400, 100)
        self.setFixedSize(450, 350)
        self.setFont(QFont('SegoeUI', 10))

        # set the title of the screen
        self.setWindowTitle('Register Cloud Drive')

        # self.fill_all()

    def openLink(self, link):
        self.accept()
        from login import Login
        Login(parent=self).show()

    def receiveResponse(self, resp):
        self.doneLoading()
        print("Response: " + str(resp))
        if 'data' in resp:
            if 'message' in resp['data']:
                if resp['data']['message'] == u'Account created':
                    reply = QMessageBox.question(self, 'Account created',
                                                 'Your account has been created. Would you like to login now?',
                                                 QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.openLink('http://www.example.com')
                else:
                    QMessageBox.information(self, 'Acount creation failed', resp['data']['message'])
            else:
                QMessageBox.information(self, 'Acount creation failed',
                                        'An error occurred, response was invalid, please contact developer.')
        elif 'message' in resp:
            QMessageBox.information(self, 'Acount creation failed', resp['message'])
        else:
            QMessageBox.information(self, 'Acount creation failed', 'Unknown error occured, please try again later.')

    def fill_all(self):
        self.textFullName.setText('John Doe')
        self.textEmail.setText('john@gmail.com')
        self.textPassword.setText('password')
        self.textConfirmPassword.setText('password')

    def handleRegister(self):
        print('registering')
        valid = self.validate()
        if valid == True:
            self.setLoading()
            self.thread1 = ResponseThread(
                SIGN_UP_API,
                form_data={"email": self.textEmail.text(), "password": self.textPassword.text(),
                           "name": self.textFullName.text(), "auth": "FROM_PYTHON_GUI_!@#$%^&*()"}, parent=self)
            self.thread1.start()
            self.thread1.signal.sig.connect(self.receiveResponse)
        else:
            # show a message box
            QMessageBox.information(self, 'Error', valid)
            return

    def setLoading(self):
        self.buttonRegister.setEnabled(False)
        self.buttonRegister.setText('Creating account...')
        # increasing the number of dots while loading

    def doneLoading(self):
        self.buttonRegister.setEnabled(True)
        self.buttonRegister.setText('Let\'s Create')

    def validate(self):
        if self.textFullName.text().strip() == '':
            return 'Please enter your full name'
        if self.textEmail.text() == '' or not styles.validate_email(self.textEmail.text()):
            return 'Please enter a valid email address'
        if self.textPassword.text() == '' or len(self.textPassword.text()) < 6:
            return 'Password is required (min 6 characters)'
        if self.textConfirmPassword.text() == '':
            return 'Please confirm your password'
        if self.textPassword.text() != self.textConfirmPassword.text():
            return 'Passwords do not match'
        return True
