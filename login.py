# -*- coding: utf-8 -*-

import re
from PySide import QtGui, QtCore
from constants import *
from networking import ResponseThread
import styles
import auth
import sys

    
class Login(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.textEmail = QtGui.QLineEdit(self)
        self.textPassword = QtGui.QLineEdit(self)
        self.buttonLogin = QtGui.QPushButton('Login', self)
        
        # settins style on all texbox
        styles.textbox(self.textEmail, self.textPassword)
        styles.button(self.buttonLogin)
        
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(QtGui.QLabel('Email:'))
        layout.addWidget(self.textEmail)
        layout.addWidget(QtGui.QLabel('Password:'))
        layout.addWidget(self.textPassword)
        layout.addWidget(self.buttonLogin)
        # Don't have an account, register link label
        register_link = QtGui.QLabel('Don\'t have an account yet? <a href="http://www.example.com"><b>Create</b></a> it.')
        # match width to the parent widget
        register_link.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(register_link)
        
        
        # signal to open the link
        register_link.linkActivated.connect(self.openLink)
        
        self.buttonLogin.clicked.connect(self.handleLogin)
        
        # resize the layout width, height
        #layout.resize(400, 100)
        self.setFixedSize(450, 220)
        self.setFont(QtGui.QFont('SegoeUI', 10))
        #layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        
        self.setWindowTitle('Login Cloud Drive')
        
        self.fill_all()
        
        
    def receiveResponse(self, resp):
        self.doneLoading()
        print ("Response: " + str(resp))
        if 'data' in resp:
            if 'message' in resp['data']:
                if resp['data']['message'] == u'Login successful':
                    # login success, now save the token
                    print ("Saving token...")
                    auth.save(resp['data']['name'], resp['data']['regdate'], resp['data']['token'], resp['data']['email'])
                    self.openWindow()
                else:
                    QtGui.QMessageBox.information(self, 'Acount creation failed', resp['data']['message'])
            else:
                QtGui.QMessageBox.information(self, 'Acount creation failed', 'An error occurred, response was invalid, please contact developer.')
        elif 'message' in resp:
            QtGui.QMessageBox.information(self, 'Acount creation failed', resp['message'])
        else:
            QtGui.QMessageBox.information(self, 'Acount creation failed', 'Unknown error occured, please try again later.')           
    
                    
    def openLink(self, link):
        self.accept()
        stack_widget.setCurrentIndex(1)
            
    def openWindow(self): 
        print stack_widget 
        self.accept()
        stack_widget.addWidget(main_screen)
        stack_widget.setCurrentIndex(2)
        stack_widget.show()
        sys.exit(app.exec_())
        
        
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
            QtGui.QMessageBox.information(self, 'Error', valid)
            return
            
    def validate_email(self, email):
        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
                return True
        return False
        
    def validate(self):
        if self.textEmail.text() == '' or self.validate_email(self.textEmail.text()) == False:
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


if __name__ == '__main__':

     import sys
     app = QtGui.QApplication(sys.argv)
     login = Login()

     if login.exec_() == QtGui.QDialog.Accepted:
         window = Window()
         window.show()
         sys.exit(app.exec_())
