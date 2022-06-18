# from PySide.QtCore import *
# from PySide.QtGui import *
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import styles


class ObjectMenuClicked(QObject):
    sig = pyqtSignal(list)


class Item(QWidget):
    def __init__(self, data, pos=0, parent=None, admin_users=None):
        super(Item, self).__init__(parent)

        self.admin_users = admin_users
        self.data = data
        self.position = pos
        self.menuSignal = ObjectMenuClicked()

        self.hori = QHBoxLayout()
        self.hori2 = QHBoxLayout()
        self.vert = QVBoxLayout()

        self.icon = QLabel()
        # set icon from path png styletml

        sz = ""
        if 'size' in data:
            sz = data['size']
        else:
            if data['is_admin']:
                sz = "admin"
            elif data['access']:
                sz = "access granted"

        self.titleLbl = QLabel(data['name'])
        self.sizeLbl = QLabel(sz)

        styles.heading(self.titleLbl)

        self.bulletLbl = QLabel("\u2022")
        # html bullet tag
        self.bulletLbl.setTextFormat(Qt.RichText)
        self.bulletLbl.setText("&#x2022")
        # set font size
        self.bulletLbl.setFont(QFont("Arial", 16))
        self.dateLbl = QLabel(self.changeDateFormat(data['cdate']) if 'cdate' in data else data['regdate'])

        styles.subheading(self.dateLbl, self.bulletLbl, self.sizeLbl)

        # more button with a dropdown menu
        self.moreBtn = QPushButton()
        menu = QMenu()
        self.moreBtn.setMenu(menu)

        # menu icon size
        menu.setStyleSheet("QMenu {icon-size: 32px;}")
        # menu.addAction("Download")
        if not admin_users:
            if data['type'] != 'DIR':
                self.moreBtn.menu().addAction("Download")
            self.moreBtn.menu().addAction("Delete")
        else:
            self.moreBtn.menu().addAction("remove admin" if data['is_admin'] else "make admin")
            self.moreBtn.menu().addAction("grant access" if data['access'] == 0 else "remove access")
            self.moreBtn.menu().addAction("edit")
            self.moreBtn.menu().addAction("delete")

        # menu click event
        self.moreBtn.menu().triggered.connect(self.menuClicked)

        # vertical layout
        self.vert.addWidget(self.titleLbl)
        if self.admin_users:
            self.emaillbl = QLabel(data['email'])
            self.vert.addWidget(self.emaillbl)
            # italic font
            self.emaillbl.setFont(QFont("Arial", 10, QFont.StyleItalic))
        self.vert.addLayout(self.hori2)
        # horizontal layout 2

        if self.admin_users:
            self.hori2.addWidget(self.sizeLbl)
            # set sizelbl bold
            self.sizeLbl.setFont(QFont("Arial", 10, QFont.Bold))
            self.hori2.addWidget(self.bulletLbl)
            if sz == "admin":
                self.sizeLbl.setStyleSheet("QLabel {color: #ff0000;}")
            else:
                # green
                self.sizeLbl.setStyleSheet("QLabel {color: #00b100;}")
            if sz == "":
                self.sizeLbl.hide()
                self.bulletLbl.hide()
        elif data['type'] != 'DIR':
            self.hori2.addWidget(self.sizeLbl)
            self.hori2.addWidget(self.bulletLbl)
        self.hori2.addWidget(self.dateLbl)

        # main layout
        self.hori.addSpacing(10)
        self.hori.addWidget(self.icon)
        self.hori.addSpacing(20)
        self.hori.addLayout(self.vert)
        # match layout to available space
        # add space
        # add tab spacing
        # self.hori.addSpacing(150)
        # self.hori.setStretch(1, 1)
        # align space to right

        self.hori.addStretch()
        self.hori.addWidget(self.moreBtn)

        # draw border around the layout
        self.hori.setContentsMargins(10, 10, 10, 10)

        self.hori.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.hori)

        self.setIcon()

        # layout click event

    def test(self):
        print(f"test {self.position}")

    def change_access(self, should=False):
        if should:
            self.sizeLbl.show()
            self.bulletLbl.show()
        else:
            self.sizeLbl.hide()
            self.bulletLbl.hide()

    def change(self, name=None, is_admin=None, access=None):
        print(f"change {name} {is_admin} {access}")
        if name:
            self.titleLbl.setText(name)
        is_set = None
        if is_admin is not None:
            if is_admin == "true" or is_admin is True:
                # change menu text
                self.moreBtn.menu().actions()[0].setText("remove admin")
                self.sizeLbl.setText("admin")
                # color to red
                self.sizeLbl.setStyleSheet("QLabel {color: #ff0000;}")
                is_set = True
            else:
                self.moreBtn.menu().actions()[0].setText("make admin")
                is_set = False
        if access is not None:
            if access == "true" or access is True or (isinstance(access, int) and access > 0):
                # change menu text to remove access
                self.moreBtn.menu().actions()[1].setText("remove access")
                self.sizeLbl.setText("access granted")
                # color to green
                self.sizeLbl.setStyleSheet("QLabel {color: #00b100;}")
                is_set = True
            else:
                # change menu text to grant access
                self.moreBtn.menu().actions()[1].setText("grant access")
                is_set = is_set or False
        if is_set:
            self.change_access(True)
        elif is_set is False:
            self.change_access(False)

    def setIcon(self):
        if self.admin_users:
            ext = "USERS"
        else:
            ext = self.data['type']
        if ext == 'USERS':
            self.icon.setPixmap(QPixmap("img/icons8-user-40.png"))
        elif ext == '.PY':
            self.icon.setPixmap(QPixmap("img/python.png"))
        elif ext == '.HTML':
            self.icon.setPixmap(QPixmap("img/html.png"))
        elif ext == '.CSS':
            self.icon.setPixmap(QPixmap("img/css.png"))
        elif ext == '.TXT' or ext == '.JS' or ext == '.JSON' or ext == '.MD' or ext == '.RST':
            self.icon.setPixmap(QPixmap("img/txt.png"))
        elif ext == '.PNG' or ext == '.JPG' or ext == '.GIF' or ext == '.BMP' or ext == '.TIF' or ext == '.JPEG':
            self.icon.setPixmap(QPixmap("img/picture.png"))
        elif ext == 'DIR':
            self.icon.setPixmap(QPixmap("img/folder.png"))
        # excel
        elif ext == '.XLS' or ext == '.XLSX':
            self.icon.setPixmap(QPixmap("img/xls.png"))
        elif ext == '.XML' or ext == '.YML':
            self.icon.setPixmap(QPixmap("img/xml.png"))
        elif ext == '.CSV':
            self.icon.setPixmap(QPixmap("img/csv.png"))
        # video
        elif ext == '.MP4' or ext == '.AVI' or ext == '.MOV' or ext == '.WMV' or ext == '.MPG' or ext == '.MPEG' or ext == '.FLV' or ext == '.M4V' or ext == '.3GP':
            self.icon.setPixmap(QPixmap("img/video.png"))
        elif ext == '.PDF':
            self.icon.setPixmap(QPixmap("img/pdf.png"))
        elif ext == '.ZIP' or ext == '.RAR' or ext == '.7Z' or ext == '.GZ' or ext == '.TGZ' or ext == '.TAR' or ext == '.ZIPX':
            self.icon.setPixmap(QPixmap("img/zip.png"))
        else:
            self.icon.setPixmap(QPixmap("img/txt.png"))
        # set size
        self.icon.setFixedSize(QSize(44, 44))
        # scale inside
        self.icon.setScaledContents(True)

    def menuClicked(self, action):
        self.menuSignal.sig.emit([action.text(), self.position])

    # byte to human readable size comma seperated
    def humanSize(self, size):
        if size < 1024:
            return str(size) + " Bytes"
        elif size < 1024 ** 2:
            return str(round(size / 1024, 2)) + " KB"
        elif size < 1024 ** 3:
            return str(round(size / 1024 ** 2, 2)) + " MB"
        elif size < 1024 ** 4:
            return str(round(size / 1024 ** 3, 2)) + " GB"
        elif size < 1024 ** 5:
            return str(round(size / 1024 ** 4, 2)) + " TB"
        elif size < 1024 ** 6:
            return str(round(size / 1024 ** 5, 2)) + " PB"
        elif size < 1024 ** 7:
            return str(round(size / 1024 ** 6, 2)) + " EB"
        elif size < 1024 ** 8:
            return str(round(size / 1024 ** 7, 2)) + " ZB"
        elif size < 1024 ** 9:
            return str(round(size / 1024 ** 8, 2)) + " YB"
        else:
            return str(round(size / 1024 ** 9, 2)) + " BB"

    def changeDateFormat(self, date):
        # '2021/12/27 13:10:07'
        # parse date and convert to 12 hour format
        format_24 = datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
        # month name day, year hour:minute:second am/pm
        format_12 = format_24.strftime('%B %d, %Y %I:%M:%S %p')
        return format_12
