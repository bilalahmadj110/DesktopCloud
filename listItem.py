from PySide.QtCore import *
from PySide.QtGui import *

from datetime import datetime
import styles

class ObjectMenuClicked(QObject):
    sig = Signal(list)
    
class Item(QWidget):
    def __init__(self, data, pos=0, parent = None):
        super(Item, self).__init__(parent)
        # data
        # {u'name': u'auth.py', u'cdate': u'2021/12/27 13:10:07', u'link': u'/explorer/auth.py', u'path': u'auth.py', u'icon': u'text', u'type': u'.PY', u'size': u'1.5264 KiB'}
        self.data = data
        self.position = pos
        self.menuSignal = ObjectMenuClicked()

        self.hori = QHBoxLayout()
        self.hori2 = QHBoxLayout()
        self.vert = QVBoxLayout()
        
        self.icon = QLabel()
        # set icon from path png styletml
        
        self.titleLbl = QLabel(data['name'])
        self.sizeLbl = QLabel(data['size'])
        
        styles.heading(self.titleLbl)
        
        self.bulletLbl = QLabel("\u2022")
        # html bullet tag
        self.bulletLbl.setTextFormat(Qt.RichText)
        self.bulletLbl.setText("&#x2022")
        # set font size
        self.bulletLbl.setFont(QFont("Arial", 16))
        self.dateLbl = QLabel(self.changeDateFormat(data['cdate']))
        
        styles.subheading(self.dateLbl, self.bulletLbl, self.sizeLbl)
        
            
        # more button with a dropdown menu
        self.moreBtn = QPushButton()
        # self.moreBtn.setIcon(QIcon("img/more.png"))
        # self.moreBtn.setIconSize(QSize(64, 64))
        # self.moreBtn.setFlat(True)
        # self.moreBtn.setStyleSheet("QPushButton {border: none; padding: 0px;}")
        menu = QMenu()
        self.moreBtn.setMenu(menu)
        # menu icon size
        menu.setStyleSheet("QMenu {icon-size: 32px;}")
        # menu.addAction("Download")
        if data['type'] != 'DIR':
            self.moreBtn.menu().addAction("Download")
        self.moreBtn.menu().addAction("Delete")
        
        # menu click event
        self.moreBtn.menu().triggered.connect(self.menuClicked)
        
        
        # vertical layout
        self.vert.addWidget(self.titleLbl)
        self.vert.addLayout(self.hori2)
        # horizontal layout 2
        if data['type'] != 'DIR':
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
        
    def setIcon(self):
        ext = self.data['type']
        if ext == '.PY':
            self.icon.setPixmap(QPixmap("img/python.png"))
        elif ext == '.HTML':
            self.icon.setPixmap(QPixmap("img/html.png"))
        elif ext == '.CSS':
            self.icon.setPixmap(QPixmap("img/css.png"))
        elif ext == '.TXT' or ext == '.JS' or ext == '.JSON' or ext == '.MD' or ext == '.RST':
            self.icon.setPixmap(QPixmap("img/txt.png"))
        elif ext == '.PNG' or  ext == '.JPG' or ext == '.GIF' or ext == '.BMP' or ext == '.TIF' or ext == '.JPEG':
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
        if action.text() == "Download": 
            print("Download " + str(self.position))
        elif action.text() == "Delete":
            print("Delete " + str(self.position))
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