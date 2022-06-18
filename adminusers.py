from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import auth
import styles
from constants import *
from listItem import Item
from listwidgetitem import ListWidgetItem
from networking import *


class AdminUsers(QDialog):
    listItems = []
    contentItems = []
    listClasses = []

    def __init__(self, explorer=None, title=None, parent=None):
        super(AdminUsers, self).__init__(parent)
        self.explorer = explorer
        print('init', self.explorer)

        self.name, self.email, self.token, self.regdate, _, __ = auth.load()

        self.hori = QHBoxLayout()
        self.vert = QVBoxLayout()
        self.status = QHBoxLayout()

        self.createBtn = QPushButton("Create User")
        # stylsheet button with icon
        self.createBtn.setIcon(QIcon("img/user.png"))

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

        # listeners
        self.createBtn.clicked.connect(self.displayCreateUserDialog)

        self.listwidget = QListWidget()
        # click event
        self.listwidget.itemClicked.connect(self.itemClicked)

        self.hori.addWidget(self.createBtn)

        self.vert.addLayout(self.hori)
        self.vert.addWidget(self.listwidget)
        self.vert.addLayout(self.status)
        # self.vert as the main layout
        self.vert.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.vert)

        self.setWindowTitle("Users List")

        # set window size (400x200)
        self.setFixedSize(600, 800)

        # delay for loading
        QTimer.singleShot(400, self.downloadUsers)

    def displayCreateUserDialog(self, pos=-1, error=False, name_=None, email=None, is__admin=False,
                                has__access=False):
        print(pos)
        try:
            if name_:
                regTag = "Note: Leave the fields blank if you don't want to change them"
            elif error:
                redTag = f"<font style='color:red;'>{error}</font>"

            # two input lineedits
            name = QLineEdit()
            if name_:
                name.setText(name_)
            email_ = QLineEdit()
            if email:
                email_.setText(email)
                email_.setEnabled(False)
            password = QLineEdit()
            # set placeholder

            error_lbl = QLabel()
            # color red
            error_lbl.setStyleSheet("color: red")
            is_admin = QCheckBox("Make this user an admin")
            has_access = QCheckBox("Grant this user access")
            if is__admin == "true" or is__admin is True:
                is_admin.setChecked(True)
            if has__access == "true" or has__access is True or (isinstance(has__access, int) and has__access > 0):
                has_access.setChecked(True)

            password.setEchoMode(QLineEdit.Password)
            # create button
            button = QPushButton('Edit' if pos is False else 'Create')
            button.setIcon(QIcon("img/create-user.png"))
            # add to layout
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Enter name"))
            layout.addWidget(name)
            layout.addWidget(QLabel("Enter username"))
            layout.addWidget(email_)
            layout.addWidget(QLabel("Enter password"))
            layout.addWidget(password)
            layout.addWidget(has_access)
            layout.addWidget(is_admin)
            layout.addWidget(error_lbl)

            layout.addWidget(button)
            # set layout
            inputDialog = QDialog(self)
            inputDialog.setWindowTitle('Edit User' if pos is not False else 'Create User')
            inputDialog.setLayout(layout)

            # connect button

            def createUserEvent():
                n = name.text().strip()
                e = email_.text().strip()
                h = "true" if has_access.isChecked() else "false"
                i = "true" if is_admin.isChecked() else "false"

                p = password.text()
                if n.strip() == "" or len(n) < 3:
                    error_lbl.setText("Name must be at least 3 characters")
                    return
                if not styles.validate_email(e):
                    error_lbl.setText("Invalid email")
                    return
                if pos is not False:
                    if len(p) < 6:
                        error_lbl.setText("Password must be at least 6 characters")
                else:
                    if len(p) > 0:
                        if len(p) < 6:
                            error_lbl.setText("Password must be at least 6 characters")
                            return
                if pos is not False:
                    # (self, pos, name=None, to=None, is_admin=None, access=None)
                    self.editNetworking(pos=pos, name=n.strip() or None, to=e, is_admin=i, access=h, password=p or None)
                else:
                    self.createNetworking(n, e, i, h, p)
                # close dialog
                inputDialog.close()

            button.clicked.connect(createUserEvent)
            inputDialog.exec_()
        except Exception as e:
            print(e)

    def handleAdminUser(self):
        pass

    def itemClicked(self, item):

        from welcome import WelcomeScreen
        stack_widget = QStackedWidget()
        this_item = self.contentItems[self.listItems.index(item)]
        new_welcome_screen = WelcomeScreen(title=this_item["name"], to=this_item["email"], parent=self)
        new_welcome_screen.show()
        # stack_widget.addWidget(new_welcome_screen)
        # stack_widget.setCurrentIndex(0)
        # stack_widget.show()

    def menuClicked(self, action: list):
        item: dict = self.contentItems[action[1]]
        print(action, item['email'])
        if action[0] == "edit":
            print("Editing", item)
            self.displayCreateUserDialog(pos=action[1], name_=item['name'], email=item['email'],
                                         is__admin=item['is_admin'],
                                         has__access=item['access'])
        elif action[0] == "delete":
            try:
                self.deleteNetworking(action[1], item['email'])
            except Exception as e:
                print(e)
        elif action[0] == 'make admin':
            self.editNetworking(action[1], is_admin=True, to=item['email'])
        elif action[0] == 'grant access':
            self.editNetworking(action[1], access=True, to=item['email'])
        elif action[0] == 'remove admin':
            self.editNetworking(action[1], is_admin="false", to=item['email'])
        elif action[0] == 'remove access':
            self.editNetworking(action[1], access="false", to=item['email'])

    def addToList(self, data):
        itemN = ListWidgetItem(pos=len(self.listItems))
        widget = Item(data, pos=len(self.listItems), admin_users=True)
        widget.menuSignal.sig.connect(self.menuClicked)
        itemN.setSizeHint(widget.sizeHint())
        self.listwidget.addItem(itemN)
        self.listwidget.setItemWidget(itemN, widget)

        self.listClasses.append(widget)
        self.listItems.append(itemN)  # ] = False
        self.contentItems.append(data)

    def removeFromList(self, pos):
        self.listwidget.takeItem(self.listwidget.row(self.listItems[pos]))
        self.listwidget.removeItemWidget(self.listItems[pos])
        self.setSuccess("Deleted `" + self.contentItems[pos][u'name'] + "`!")

    def edit_list(self, pos, name=None, access=None, is_admin=None):
        if name:
            self.contentItems[pos]['name'] = name
        if access:
            self.contentItems[pos]['access'] = access
        if is_admin:
            self.contentItems[pos]['is_admin'] = is_admin

    def receiveResponse(self, resp):
        print(resp)
        self.doneLoading()
        if 'back' in resp:
            if resp['back'] is None:
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':
                            # iterate over `node` and add to list
                            # self.clearList()
                            for i in resp['data']['node']:
                                self.addToList(i)
                        else:
                            self.setError(resp['data']['message'])
                        return
            elif resp['back'][0] == 'edit':
                pos = resp['back'][1]
                success = False
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':
                            # ['edit', pos, [name, to, is_admin, access]]

                            self.listClasses[pos].change(name=resp['back'][2][0], is_admin=resp['back'][2][2],
                                                         access=resp['back'][2][3])
                            self.edit_list(pos, name=resp['back'][2][0], is_admin=resp['back'][2][2],
                                           access=resp['back'][2][3])
                            success = True
                if not success:
                    self.setError("Error editing user `" + self.contentItems[pos][u'name'] + "`")
                else:
                    self.setSuccess("Edited `" + self.contentItems[pos][u'name'] + "`!")
                return
            elif resp['back'][0] == 'delete':
                success: bool = False
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':
                            self.removeFromList(resp['back'][1])
                            success = True
                if not success:
                    self.setError("Error deleting `" + self.contentItems[resp['back'][1]][u'name'] + "`!")
                return
            elif resp['back'][0] == 'create':
                success: bool = False
                if 'data' in resp:
                    if 'message' in resp['data']:
                        if resp['data']['message'] == u'Success':
                            del resp['data']['message']
                            self.addToList(resp['data'])
                            success = True
                if not success:
                    self.setError("Error creating user")
                else:
                    self.setSuccess("User created")
                return
        self.showErrorDialog('Something went wrong, please try again.')

    def downloadUsers(self):
        print(f"{LIST_USERS_API}...")
        # get auth token
        try:
            _, email, token, __, ___, ____ = auth.load()
            self.setLoading("Downloading users, please wait...")
            self.thread1 = ResponseThread(
                LIST_USERS_API,
                header={"email": email, "authorization": token},
                parent=self)
            self.thread1.start()
            self.thread1.signal.sig.connect(self.receiveResponse)

        except Exception as e:
            self.showErrorDialog('Something went wrong, please try logging in again. ' + str(e))
            self.reloadBtn.setEnabled(True)

    def deleteNetworking(self, pos, to):
        self.setLoading(f"Deleting `{to}`, please wait...")
        self.thread1 = ResponseThread(
            DELETE_USERS_API,
            header={"email": self.email, "authorization": self.token, "to": to},
            parent=self, back=['delete', pos])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def editNetworking(self, pos, name=None, to=None, is_admin=None, access=None, password=None):
        self.setLoading(f"Editing user")
        header = {"email": self.email, "authorization": self.token, "name": name, "to": to, "admin": is_admin,
                  "access": access, "password": password}
        # filter dict where values are None
        header = {k: "true" if v is True else v for k, v in header.items() if v is not None}
        print("Editing header: ", header)
        self.thread1 = ResponseThread(
            EDIT_USERS_API,
            header=header,
            parent=self,
            back=['edit', pos, [name, to, is_admin, access]])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def createNetworking(self, name, to, is_admin, access, password):
        self.setLoading(f"Creating user")
        self.thread1 = ResponseThread(
            CREATE_USERS_API,
            header={"email": self.email, "authorization": self.token, "username": name, "useremail": to,
                    "admin": is_admin,
                    "access": access, "userpassword": password},
            parent=self,
            back=['create', [name, to, is_admin, access]])
        self.thread1.start()
        self.thread1.signal.sig.connect(self.receiveResponse)

    def clearList(self):
        self.listItems = []
        self.contentItems = []
        self.listwidget.clear()

    def showErrorDialog(self, error):
        self.setError(error)
        QMessageBox.information(self, 'Error', error, QMessageBox.Ok)

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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    main_screen = AdminUsers()
    main_screen.show()
    sys.exit(app.exec_())
