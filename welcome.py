from os import path
from PySide.QtCore import *
from PySide.QtGui import *
from listItem import Item
import styles
import auth
import sys
import re
from constants import *
from networking import *
from listwidgetitem import ListWidgetItem
import styles

class WelcomeScreen(QDialog):
    
    listItems = []
    contentItems = []
    
    def __init__(self, explorer=None, title=None, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        self.explorer = explorer
        print ('init', self.explorer)
        
        self.name, self.email, self.token, self.regdate = auth.load()
        
        self.hori = QHBoxLayout()
        self.titlHor = QHBoxLayout()
        self.vert = QVBoxLayout()
        self.status = QHBoxLayout()
        
        self.pathLbl = QLabel("/home/bilal/Desktop/CloudDrive-desktop--main")
        
        self.backBtn = QPushButton("Back")
        self.logoutBtn = QPushButton("Logout")
        self.logoutBtn.setIcon(QIcon("img/logout.png"))
        # fix the button size
        self.backBtn.setFixedSize(QSize(70, 35))
        self.backBtn.setIcon(QIcon("img/back.png"))
        
        self.uploadBtn = QPushButton("Upload")
        self.uploadBtn.setIcon(QIcon("img/upload.png"))
        self.createBtn = QPushButton("Create")
        # stylsheet button with icon
        self.createBtn.setIcon(QIcon("img/create.png"))
        
        self.reloadBtn = QPushButton("Reload")
        self.reloadBtn.setIcon(QIcon("img/reload.png"))
        
        self.loading = QLabel()
        # set loading gif QMovie
        mov = QMovie("img/spinner.gif")
        # set size
        mov.setScaledSize(QSize(20, 20))
        self.loading.setFixedSize(QSize(20, 20))
        self.loading.setMovie(mov)
        mov.start()
        
        self.loadinglbl = QLabel("Loading...")
        
        self.status.addWidget(self.loading)
        self.status.addWidget(self.loadinglbl)
        self.status.addStretch()
        self.status.addWidget(self.logoutBtn)
             
        # listeners
        self.backBtn.clicked.connect(self.backClicked)
        self.createBtn.clicked.connect(self.displayInputDialog)
        self.uploadBtn.clicked.connect(self.browseFiles)
        self.logoutBtn.clicked.connect(self.handleLogout)
        self.reloadBtn.clicked.connect(self.handleReload)
        self.pathLbl.linkActivated.connect(self.openLink)

        self.listwidget = QListWidget()
        # click event
        self.listwidget.itemClicked.connect(self.itemClicked)
        
        self.titlHor.addWidget(self.backBtn)
        self.titlHor.addWidget(self.pathLbl)
        self.titlHor.addStretch()
        
        
        self.hori.addWidget(self.reloadBtn)
        self.hori.addStretch()
        self.hori.addWidget(self.uploadBtn)
        self.hori.addWidget(self.createBtn)
        
        
        self.vert.addLayout(self.titlHor)
        self.vert.addLayout(self.hori)
        self.vert.addWidget(self.listwidget)
        self.vert.addLayout(self.status)
        # self.vert as the main layout
        self.vert.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.vert)
        
        
        self.setWindowTitle("Welcome")
        
        # delay for loading
        QTimer.singleShot(400, self.downloadExplorer)  
        
        self.setPathTitle()  
   
    
    def backClicked(self):
            # QStackWidget total items
        totalItems = stack_widget.count()
        print totalItems
        # get index
        index = stack_widget.currentIndex()
        if index == 2:
            return
        # if index is 0, then disable back button
        if index == 3:
            self.backBtn.setEnabled(False)
            # remove widget at index
        else:
            self.backBtn.setEnabled(True)
        index -= 1
        stack_widget.setCurrentIndex(index)
        stack_widget.removeWidget(stack_widget.widget(index + 1))
        # add transition animation
    
    def itemClicked(self, item):
        this_item = self.contentItems[self.listItems.index(item)]
        if this_item['type'] != 'DIR':
            return
        main_screen = WelcomeScreen(explorer=this_item['path'])
        stack_widget.addWidget(main_screen)
        stack_widget.setCurrentIndex(stack_widget.count() - 1)
          
    def openLink(self, link):
        index = int(link) + 2
        stack_widget.setCurrentIndex(index)
        # delete all widgets greater than index
        for i in range(stack_widget.count() - 1, index, -1):
            stack_widget.removeWidget(stack_widget.widget(i))

    def setPathTitle(self):
        if self.explorer is None:
            self.pathLbl.setText("Home Page")
            return
        l = self.explorer.split('/')
        # font
        self.pathLbl.setText("<html>")
        self.pathLbl.setText("<a style='font-size:16px;font-family:Segoe UI; font-weight:bold;' href='0'>Home</a>")
        for index, i in enumerate(l, start=1):
            if index == len(l):
                self.pathLbl.setText(self.pathLbl.text() + " / " + "<tag style='font-size:16px;font-family:Segoe UI; font-weight:bold;'>" + i + '</tag>')
            else:
                self.pathLbl.setText(self.pathLbl.text() + ' / ' + "<a style='font-size:16px;font-family:Segoe UI; font-weight:bold;' href='" + str(index) + "'>" + i + "</a>")
        self.pathLbl.setText(self.pathLbl.text() + "</html>")
        # set font size
        self.pathLbl.setFont(QFont("Arial", 12))
       
    def handleLogout(self):
        print ("Logging out...")
        auth.clear()
        for i in range(stack_widget.count() - 1, 1, -1):
            stack_widget.removeWidget(stack_widget.widget(i))
        stack_widget.setCurrentIndex(0)
        
      
    def handleReload(self):
        print ("Refreshing the list...")
        self.downloadExplorer() 
        
    def validateFolderName(self, name):
        # check if name is empty
        if name is None or len(str(name).strip()) == 0 or len(name) > 250:
            return 'Folder name is empty or too long'
        # check if name exists in the list
        for item in self.contentItems:
            if item['name'].strip().lower() == name.strip().lower():
                return 'This folder name already exists, please choose another name.'
        # check if name contains any of the following characters
        # "/\:*?<>|" check if any of the following characters are in the name
        for i in "/\:*?<>|":
            if i in name:
                return 'Invalid folder name, please choose another name.'
        return False
   
    def menuClicked(self, action):
        if action[0] == u'Delete':
            self.removeFromList(action[1])
        elif action[0] == u'Download':
            self.downloadNetworking(action[1])
                  
    def addToList(self, data):   
        itemN = ListWidgetItem(pos=len(self.listItems))
        widget = Item(data, pos=len(self.listItems)) 
        widget.menuSignal.sig.connect(self.menuClicked)
        itemN.setSizeHint(widget.sizeHint())    
        self.listwidget.addItem(itemN)
        self.listwidget.setItemWidget(itemN, widget) 
        
        self.listItems.append(itemN)#] = False
        self.contentItems.append(data)
    
    def displayInputDialog(self, error=False):
            # red tag html
        if error:
            redTag = "<font color='red'>" + error + " </font>"
        else:
            redTag = ''
        text, ok = QInputDialog.getText(self, 'Input Dialog', '<html><h3>Enter the folder name:</h3>Note: A folder name can\'t contain any of the following characters: <center> /\:*?<>| </center>%s</html>' % redTag, QLineEdit.Normal, '')
        if ok:
            # show error message if file name is empty
            error = self.validateFolderName(text)
            if error:
                self.displayInputDialog(error)
                return 
            self.createNetworking(text)
        else:
            return None
           
    def createNetworking(self, name):
        self.setLoading("Creating folder `" + name + "`...")  
        self.thread1 = ResponseThread(
                    CREATE_API + '/' + ('' if self.explorer is None else self.explorer),  
                    header={"email": self.email, "authorization": self.token, "name": name.strip()},
                    parent=self, back=['create', name])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)  
    
    def deleteNetworking(self, pos):
        self.setLoading("Deleting `" + self.contentItems[pos]['name'] + "`, please wait...")    
        self.thread1 = ResponseThread(
                    DELETE_API + '/' + self.contentItems[pos]['path'],  
                    header={"email": self.email, "authorization": self.token},
                    parent=self, back=['delete', pos])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse) 
           
    def removeFromList(self, pos, networking=True):
        if not networking:
            self.listwidget.takeItem(self.listwidget.row(self.listItems[pos]))
            self.listwidget.removeItemWidget(self.listItems[pos])
            self.setSuccess("Deleted `" + self.contentItems[pos][u'name'] + "`!")
        else:
            self.setLoading("Deleting `" + self.contentItems[pos][u'name'] + "`, please wait...")
            self.deleteNetworking(pos)
        
    def receiveResponse(self, resp):
        # {'data': {u'node': [{u'name': u'auth.py', u'cdate': u'2021/12/27 13:10:07', u'link': u'/explorer/auth.py', u'path': u'auth.py', u'icon': u'text', u'type': u'.PY', u'size': u'1.5264 KiB'}
        print (resp)
        self.doneLoading() 
        if 'back' in resp:
            if resp['back'] is None:
                
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':   
                            # iterate over `node` and add to list
                            self.clearList()
                            for i in resp['data']['node']:
                                self.addToList(i) 
                        else:
                            self.setError(resp['data']['message'])  
                self.reloadBtn.setEnabled(True)      
                   
            elif resp['back'][0] == 'delete':
                success = False
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':   
                            self.removeFromList(resp['back'][1], False)
                            success = True
                if not success:
                    self.setError("Error deleting `" + self.contentItems[resp['back'][1]][u'name'] + "`!")
            elif resp['back'][0] == 'create':
                success = False
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':  
                            del resp['data']['message'] 
                            self.addToList(resp['data'])
                            success = True
                if not success:
                    self.setError("Error creating folder `" + resp['back'][1] + "`!")
                else:
                    self.setSuccess("Created folder `" + resp['back'][1] + "`!")
            elif resp['back'][0] == 'download':
                success = False
                if 'message' in resp:
                    if resp['message'] == 'Success':   
                        success = True
                if not success:
                    self.setError("Error downloading `" + resp['back'][1] + "`!")
                else:
                    self.setSuccess("Downloaded `" + resp['back'][1] + "`!")
            elif resp['back'][0] == 'upload':
                success = False
                if 'message' in resp:
                    if type(resp['message']) is dict:  
                        self.addToList(resp['message'])
                        success = True
                if not success:
                    self.setError("Error uploading `" + resp['back'][1] + "`!")
                else:
                    self.setSuccess("Uploaded `" + resp['back'][1] + "`!")
        else:
            self.showErrorDialog('Something went wrong, please try again.')   
            
    def downloadNetworking(self, pos):
        print (EXPLORER_API + '/' + self.contentItems[pos]['path'])
        self.setLoading("Downloading `" + self.contentItems[pos]['name'] + "`, please wait...")
        self.thread1 = DownloadThread(
                    EXPLORER_API + '/' + self.contentItems[pos]['path'],  
                    self.contentItems[pos]['name'],
                    header={"email": self.email, "authorization": self.token},
                    parent=self)
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse) 
        
    def uploadNetworking(self, filePath):
        self.setLoading("Uploading `" + filePath + "`, please wait...")
        self.thread1 = UploadThread(
                    UPLOAD_API + '/' + ('' if self.explorer is None else self.explorer), 
                    header={"email": self.email, "authorization": self.token},
                    parent=self,
                    back=['upload', filePath])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)
        
    def browseFiles(self):
        filePath = QFileDialog.getOpenFileName(self, 'Open file', '', 'All Files (*)')
        if filePath:
            self.uploadNetworking(filePath[0])
        else:
            return None
    
     
    def clearList(self):
        self.listItems = []
        self.contentItems = []
        self.listwidget.clear()   
                        
    def showErrorDialog(self, error):
        self.setError(error)
        QMessageBox.information(self, 'Error', error, QMessageBox.Ok)
        
    def downloadExplorer(self):
        print EXPLORER_API + '' if self.explorer is None else self.explorer
        self.reloadBtn.setEnabled(False)
        # get auth token
        try:
            _, email, token, __ = auth.load()
            print (self.setLoading("Downloading " + ('HomePage' if self.explorer is None else ("`" + self.explorer + "`")) + "..."))
            self.setLoading("Downloading " + ('HomePage' if self.explorer is None else ("`" + self.explorer + "`")) + "...") 
            self.thread1 = ResponseThread(
                    EXPLORER_API + "/" + ('' if self.explorer is None else self.explorer),  
                    header={"email": email, "authorization": token},
                    parent=self)
            self.thread1.start()
            self.thread1.signal.sig.connect(self.receiveResponse) 
             
        except:
            self.showErrorDialog('Something went wrong, please try logging in again.')
            self.reloadBtn.setEnabled(True)
           

    def setLoading(self, text):
        self.loadinglbl.setText(text)
        self.loadinglbl.show()
        self.loading.show()
        
    def setError(self, text):
        # red html text   
        self.loadinglbl.setText("<html><font color='red'>" + text + "</font></html>")
        self.loadinglbl.show()
        self.loading.hide()
        
    def setSuccess(self, text):
        # green html text
        self.loadinglbl.setText("<html><font color='green'>" + text + "</font></html>")
        self.loadinglbl.show()
        self.loading.hide()
        
    def doneLoading(self):
        self.loadinglbl.hide()
        self.loading.hide()
        
class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.textEmail = QLineEdit(self)
        self.textPassword = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        
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
        #layout.resize(400, 100)
        self.setFixedSize(450, 220)
        self.setFont(QFont('SegoeUI', 10))
        #layout.setSizeConstraint(QLayout.SetFixedSize)
        
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
                    QMessageBox.information(self, 'Acount creation failed', resp['data']['message'])
            else:
                QMessageBox.information(self, 'Acount creation failed', 'An error occurred, response was invalid, please contact developer.')
        elif 'message' in resp:
            QMessageBox.information(self, 'Acount creation failed', resp['message'])
        else:
            QMessageBox.information(self, 'Acount creation failed', 'Unknown error occured, please try again later.')           
    
                    
    def openLink(self, link):
        self.accept()
        stack_widget.setCurrentIndex(1)
            
    def openWindow(self): 
        print stack_widget 
        self.accept()
        try:
            stack_widget.addWidget(main_screen)
        except NameError as e:
            main_screen = WelcomeScreen()
            stack_widget.addWidget(main_screen)
        stack_widget.setCurrentIndex(2)
        # stack_widget.show()
        # sys.exit(app.exec_())
        
        
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
        #layout.resize(400, 100)
        self.setFixedSize(450, 350)
        self.setFont(QFont('SegoeUI', 10))
        
        # set the title of the screen
        self.setWindowTitle('Register Cloud Drive')
        
        self.fill_all()

    def openLink(self, link):
        self.accept()
        stack_widget.setCurrentIndex(0)
                    
    def receiveResponse(self, resp):
        self.doneLoading()
        print ("Response: " + str(resp))
        if 'data' in resp:
            if 'message' in resp['data']:
                if resp['data']['message'] == u'Account created':
                    reply = QMessageBox.question(self, 'Account created', 'Your account has been created. Would you like to login now?', QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.openLink('http://www.example.com')
                else:
                    QMessageBox.information(self, 'Acount creation failed', resp['data']['message'])
            else:
                QMessageBox.information(self, 'Acount creation failed', 'An error occurred, response was invalid, please contact developer.')
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
        valid = self.validate()
        if valid == True:
            self.setLoading()
            self.thread1 = ResponseThread(
                    SIGN_UP_API,  
                    form_data={"email": self.textEmail.text(), "password": self.textPassword.text(), "name": self.textFullName.text()}, parent=self)
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
        
    def validate_email(self, email):
        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
                return True
        return False
        
    def validate(self):
        if self.textFullName.text().strip() == '':
            return 'Please enter your full name'
        if self.textEmail.text() == '' or self.validate_email(self.textEmail.text()) == False:
            return 'Please enter a valid email address'
        if self.textPassword.text() == '' or len(self.textPassword.text()) < 6:
            return 'Password is required (min 6 characters)'
        if self.textConfirmPassword.text() == '':
            return 'Please confirm your password'
        if self.textPassword.text() != self.textConfirmPassword.text():
            return 'Passwords do not match'
        return True

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
# from login import Login
# from register import Register
# stacks = Stacks()
# stacks.add(WelcomeScreen())

    stack_widget = QStackedWidget()
    
    login = Login()
    register = Register()
    # main_screen2 = WelcomeScreen()
    # main_screen.show()

    stack_widget.addWidget(login)
    stack_widget.addWidget(register)
    
    # stack_widget.addWidget(Login())
    # stack_widget.addWidget(Register())
    # # stack_widget.addWidget(main_screen2)
    # only call class on setting index
    print (auth.load())
    if auth.load() == False:
        stack_widget.setCurrentIndex(0)
    else:
        main_screen = WelcomeScreen()
        stack_widget.addWidget(main_screen)
    stack_widget.setCurrentIndex(2)
    stack_widget.show()
    sys.exit(app.exec_())
    
