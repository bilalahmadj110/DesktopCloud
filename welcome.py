from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import auth
from adminusers import AdminUsers
from constants import *
from listItem import Item
from listwidgetitem import ListWidgetItem
from networking import *


class WelcomeScreen(QDialog):
    flag = False
    currentIndex = 0
    itemsData = [{"list": [], "content": [], "explorer": None, "title": None, "to": None}]

    def __init__(self, explorer=None, title=None, parent=None, to=None, access_admin=None):
        super(WelcomeScreen, self).__init__(parent)

        self.title = title
        self.explorer = explorer
        self.to = to
        self.access_admin = access_admin
        self.parent = parent
        print('init', self.explorer, title, parent, to)

        self.name, self.email, self.token, self.regdate, self.is_admin, self.access = auth.load()

        self.hori = QHBoxLayout()
        self.titlHor = QHBoxLayout()
        self.vert = QVBoxLayout()
        self.status = QHBoxLayout()

        self.pathLbl = QLabel("/home/bilal/Desktop/CloudDrive-desktop--main")

        self.backBtn = QPushButton("Back")

        self.logoutBtn = QPushButton("Logout")
        self.logoutBtn.setIcon(QIcon("img/logout.png"))

        self.changePassBtn = QPushButton("Change Password")
        self.changePassBtn.setIcon(QIcon("img/change-password.png"))

        self.adminUserBtn = QPushButton()

        if self.to or access_admin:
            self.logoutBtn.hide()
            self.changePassBtn.hide()
            self.adminUserBtn.hide()

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
        self.status.addWidget(self.adminUserBtn)
        self.status.addWidget(self.changePassBtn)
        self.status.addWidget(self.logoutBtn)

        # listeners
        self.backBtn.clicked.connect(self.backClicked)
        self.createBtn.clicked.connect(self.displayInputDialog)
        self.uploadBtn.clicked.connect(self.browseFiles)
        self.logoutBtn.clicked.connect(self.handleLogout)
        self.reloadBtn.clicked.connect(self.handleReload)
        self.changePassBtn.clicked.connect(self.handleChangePassword)
        self.pathLbl.linkActivated.connect(self.openLink)
        if self.is_admin is True or self.is_admin == 'true':
            self.adminUserBtn.clicked.connect(self.handleAdminUser)
            self.adminUserBtn.setIcon(QIcon("img/user.png"))
            self.adminUserBtn.setText("Users List")
        elif self.access is True or self.access == 'true' or (isinstance(self.access, int) and self.access > 0):
            self.adminUserBtn.setText("Admin files")
            self.adminUserBtn.setIcon(QIcon("img/icons8-file-100.png"))
            self.adminUserBtn.clicked.connect(self.handleAccessUser)
        else:
            self.adminUserBtn.hide()

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

        self.setWindowTitle("Welcome" if title is None else title)

        # delay for loading
        QTimer.singleShot(400, self.downloadExplorer)

        self.setPathTitle()

        # resize window
        self.resize(QSize(600, 800))

    def backClicked(self):
        if self.currentIndex == 0 or self.flag:
            return
        self.currentIndex -= 1
        self.itemsData.pop()

        self.explorer = self.itemsData[self.currentIndex]['explorer']

        self.itemsData[self.currentIndex]['list'] = []
        self.listwidget.clear()
        for data in self.itemsData[self.currentIndex]['content']:
            if 'deleted' in data and data['deleted']:
                continue
            self.addToList(data, from_item=True)
        self.setPathTitle()

    def itemClicked(self, item):
        if self.flag:
            return
        this_item = self.itemsData[self.currentIndex]['content'][self.itemsData[self.currentIndex]["list"].index(item)]
        if this_item['type'] != 'DIR':
            return
        self.currentIndex += 1

        self.explorer = this_item['path']
        self.itemsData.append(
            {"list": [], "content": [], "explorer": this_item['path'], "title": self.title, "to": self.to})
        self.downloadExplorer()
        self.setPathTitle()

    def openLink(self, link):
        if self.flag:
            return
        index = int(link)
        print(index, len(self.itemsData))
        self.currentIndex = index
        del self.itemsData[index + 1:]
        self.explorer = self.itemsData[self.currentIndex]['explorer']
        self.itemsData[self.currentIndex]['list'] = []
        self.listwidget.clear()
        for data in self.itemsData[self.currentIndex]['content']:
            if 'deleted' in data and data['deleted']:
                continue
            self.addToList(data, from_item=True)
        self.setPathTitle()

    def handleAdminUser(self):
        # make dialog at the top of the window
        admin_users = AdminUsers(title="Users", parent=self)
        admin_users.show()

    def handleAccessUser(self):
        welc = WelcomeScreen(title="Admin Files", parent=self, access_admin='1')
        welc.show()

    def handleChangePassword(self):
        inputDialog = QDialog()
        inputDialog.setWindowTitle("Change password")
        inputDialog.setFixedSize(QSize(400, 250))
        inputDialog.setWindowIcon(QIcon("img/change-password.png"))
        inputDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        inputDialog.setWindowModality(Qt.ApplicationModal)
        inputDialog.setAttribute(Qt.WA_DeleteOnClose)

        # create layout
        layout = QVBoxLayout()
        # create input
        old_pass = QLineEdit()
        new_pass = QLineEdit()
        confirm_pass = QLineEdit()
        old_pass.setEchoMode(QLineEdit.Password)
        new_pass.setEchoMode(QLineEdit.Password)
        confirm_pass.setEchoMode(QLineEdit.Password)
        error_lbl = QLabel()
        error_lbl.setStyleSheet("color: red")
        # create button
        button = QPushButton("Change")
        button.setIcon(QIcon("img/change-password.png"))
        # add to layout
        layout.addWidget(QLabel("Enter old password"))
        layout.addWidget(old_pass)
        layout.addWidget(QLabel("Re-enter the new password to confirm"))
        layout.addWidget(new_pass)
        layout.addWidget(QLabel("Confirm new password"))
        layout.addWidget(confirm_pass)
        layout.addWidget(error_lbl)

        # connect button
        def changePasswordEvent():
            if old_pass.text() == "" or new_pass.text() == "" or confirm_pass.text() == "":
                error_lbl.setText("Please fill all the fields")
                return
            if len(new_pass.text()) < 6 or len(confirm_pass.text()) < 6 or len(old_pass.text()) < 6:
                error_lbl.setText("Password must be at least 6 characters")
                return
            if new_pass.text() != confirm_pass.text():
                error_lbl.setText("New password and confirm password does not match")
                return
            error_lbl.setText("")
            # close
            # inputDialog.close()
            self.changePasswordNetworking(new_pass.text(), old_pass.text(), inputDialog, error_lbl, button)

        button.clicked.connect(changePasswordEvent)

        layout.addWidget(button)
        # set layout
        inputDialog.setLayout(layout)
        # show dialog
        inputDialog.exec_()

    def setPathTitle(self):
        if self.explorer is None:
            self.pathLbl.setText("Home")
            self.pathLbl.setFont(QFont("Arial", 11, QFont.Bold))
            return
        l = self.explorer.split('/')
        # font
        self.pathLbl.setText("<html>")
        self.pathLbl.setText("<a style='font-size:16px;font-family:Segoe UI; font-weight:bold;' href='0'>Home</a>")
        for index, i in enumerate(l, start=1):
            if index == len(l):
                self.pathLbl.setText(
                    self.pathLbl.text() + " / " + "<tag style='font-size:16px;font-family:Segoe UI; font-weight:bold;'>" + i + '</tag>')
            else:
                self.pathLbl.setText(
                    self.pathLbl.text() + ' / ' + "<a style='font-size:16px;font-family:Segoe UI; font-weight:bold;' "
                                                  "href='" + str(
                        index) + "'>" + i + "</a>")
        self.pathLbl.setText(self.pathLbl.text() + "</html>")
        # set font size
        self.pathLbl.setFont(QFont("Arial", 12))

    def handleLogout(self):
        print("Logging out...")
        auth.clear()
        self.accept()
        from login import Login
        Login(parent=self).show()

    def handleReload(self):
        print("Refreshing the list...")
        self.downloadExplorer()

    def validateFolderName(self, name):
        # check if name is empty
        if name is None or len(str(name).strip()) == 0 or len(name) > 250:
            return 'Folder name is empty or too long'
        # check if name exists in the list
        for item in self.itemsData[self.currentIndex]['content']:
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

    def addToList(self, data, from_item=False):
        itemN = ListWidgetItem(pos=len(self.itemsData[self.currentIndex]["list"]))
        widget = Item(data, pos=len(self.itemsData[self.currentIndex]["list"]))
        widget.menuSignal.sig.connect(self.menuClicked)
        itemN.setSizeHint(widget.sizeHint())

        self.listwidget.addItem(itemN)
        self.listwidget.setItemWidget(itemN, widget)

        self.itemsData[self.currentIndex]['list'].append(itemN)
        if not from_item:
            self.itemsData[self.currentIndex]['content'].append(data)

        # self.listItems.append(itemN)  # ] = False
        # self.contentItems.append(data)

    def displayInputDialog(self, error=False):
        # red tag html
        if error:
            redTag = "<font color='red'>" + error + " </font>"
        else:
            redTag = ""
        text, ok = QInputDialog.getText(self, 'Input Dialog',
                                        '<html><h3>Enter the folder name:</h3>Note: A folder name can\'t contain any of the following characters: <center> /\:*?<>| </center>%s</html>' % redTag,
                                        QLineEdit.Normal, '')
        if ok:
            # show error message if file name is empty
            error = self.validateFolderName(text)
            if error:
                self.displayInputDialog(error)
                return
            self.createNetworking(text)
        else:
            return None

    def changePasswordNetworking(self, new, pwd, dialog, err, btn):
        btn.setEnabled(False)
        btn.setText('Changing... ')
        self.setLoading("Changing password...")
        print({"email": self.email, "authorization": self.token, "new_password": new, "password": pwd})
        self.thread1 = ResponseThread(
            CHANGE_PASSWORD_API,
            header={"email": self.email, "authorization": self.token, "new": new, "password": pwd},
            parent=self, back=['change', dialog, err, btn]
        )
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def createNetworking(self, name):
        self.setLoading("Creating folder `" + name + "`...")
        self.thread1 = ResponseThread(
            CREATE_API + '/' + ('' if self.explorer is None else self.explorer),
            header={"email": self.email, "authorization": self.token, "name": name.strip(), "to": self.to,
                    "isadminfiles": self.access_admin},
            parent=self, back=['create', name])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def deleteNetworking(self, pos):
        self.setLoading("Deleting `" + self.itemsData[self.currentIndex]["content"][pos]['name'] + "`, please wait...")
        self.thread1 = ResponseThread(
            DELETE_API + '/' + self.itemsData[self.currentIndex]["content"][pos]['path'],
            header={"email": self.email, "authorization": self.token, "to": self.to,
                    "isadminfiles": self.access_admin},
            parent=self, back=['delete', pos])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def removeFromList(self, pos, networking=True):
        # pos -= self.deleted
        try:
            if not networking:
                self.listwidget.takeItem(self.listwidget.row(self.itemsData[self.currentIndex]["list"][pos]))
                self.listwidget.removeItemWidget(self.itemsData[self.currentIndex]["list"][pos])
                self.setSuccess("Deleted `" + self.itemsData[self.currentIndex]["content"][pos][u'name'] + "`!")
                self.itemsData[self.currentIndex]["content"][pos]["deleted"] = True

            else:
                self.setLoading(
                    "Deleting `" + self.itemsData[self.currentIndex]["content"][pos][u'name'] + "`, please wait...")
                self.deleteNetworking(pos)
        except Exception as e:
            print(e)

    def receiveResponse(self, resp):
        print(resp)
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
                self.flag = False

            elif resp['back'][0] == 'delete':
                success = False
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':
                            self.removeFromList(resp['back'][1], False)
                            success = True
                if not success:
                    self.setError("Error deleting `" + self.itemsData[self.currentIndex]['content'][resp['back'][1]][
                        u'name'] + "`!")
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
            elif resp['back'][0] == 'change':
                resp['back'][-1].setEnabled(True)
                resp['back'][-1].setText("Change")

                success = False
                if 'data' in resp and 'message' in resp['data']:
                    if resp['data']['message'] == u'Success':
                        resp['back'][1].close()
                        self.setSuccess("Password changed successfully.")
                        success = True
                    else:
                        resp['back'][2].setText(resp['data']['message'])
                        self.setError(resp['data']['message'])
                        success = None
                if success is not None and success is not True:
                    resp['back'][2].setText("Error changing password")
                    self.setError("Error changing password.")

        else:
            self.showErrorDialog('Something went wrong, please try again.')

    def downloadNetworking(self, pos):
        print({"email": self.email, "authorization": self.token, "to": self.to})
        print(EXPLORER_API + '/' + self.itemsData[self.currentIndex]["content"][pos]['path'])
        self.setLoading(
            "Downloading `" + self.itemsData[self.currentIndex]["content"][pos]['name'] + "`, please wait...")
        self.thread1 = DownloadThread(
            EXPLORER_API + '/' + self.itemsData[self.currentIndex]["content"][pos]['path'],
            self.itemsData[self.currentIndex]["content"][pos]['name'],
            header={"email": self.email, "authorization": self.token, "to": self.to,
                    "isadminfiles": self.access_admin},
            parent=self)
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def uploadNetworking(self, filePath):
        self.setLoading("Uploading `" + filePath + "`, please wait...")
        self.thread1 = UploadThread(
            UPLOAD_API + '/' + ('' if self.explorer is None else self.explorer),
            header={"email": self.email, "authorization": self.token, "to": self.to,
                    "isadminfiles": self.access_admin},
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
        # self.listItems = []
        # self.contentItems = []
        self.listwidget.clear()
        self.itemsData[self.currentIndex]["list"].clear()
        self.itemsData[self.currentIndex]["content"].clear()

    def showErrorDialog(self, error):
        self.setError(error)
        QMessageBox.information(self, 'Error', error, QMessageBox.Ok)

    def downloadExplorer(self):
        if self.flag:
            return
        print(EXPLORER_API + '' if self.explorer is None else self.explorer)
        self.reloadBtn.setEnabled(False)
        self.flag = True
        # get auth token
        try:
            _, email, token, __, ___, ____ = auth.load()
            print(self.setLoading(
                "Downloading " + ('Home' if self.explorer is None else ("`" + self.explorer + "`")) + "..."))
            self.setLoading(
                "Downloading " + ('Home' if self.explorer is None else ("`" + self.explorer + "`")) + "...")
            self.thread1 = ResponseThread(
                EXPLORER_API + "/" + ('' if self.explorer is None else self.explorer),
                header={"email": email, "authorization": token, "to": self.to,
                        "isadminfiles": self.access_admin},
                parent=self)
            self.thread1.start()
            self.thread1.signal.sig.connect(self.receiveResponse)

        except Exception as e:
            self.showErrorDialog('Something went wrong, please try logging in again.\nError: ' + str(e))
            self.reloadBtn.setEnabled(True)
            self.flag = False

    def setLoading(self, text):
        text = self.shortLongText(text)
        self.loadinglbl.setText(text)
        self.loadinglbl.show()
        self.loading.show()

    def setError(self, text):
        # red html text
        text = self.shortLongText(text)
        self.loadinglbl.setText("<html><font color='red'>" + text + "</font></html>")
        self.loadinglbl.show()
        self.loading.hide()

    def shortLongText(self, text):
        if len(text) > 20:
            return text[:20] + "..."
        else:
            return text

    def setSuccess(self, text):
        # green html text
        text = self.shortLongText(text)
        self.loadinglbl.setText("<html><font color='green'>" + text + "</font></html>")
        self.loadinglbl.show()
        self.loading.hide()

    def doneLoading(self):
        self.loadinglbl.hide()
        self.loading.hide()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    if not auth.load():
        from login import Login

        login = Login()
        login.show()
    else:
        main_screen = WelcomeScreen()
        main_screen.show()
    sys.exit(app.exec_())
