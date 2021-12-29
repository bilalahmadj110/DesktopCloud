from PyQt5.QtWidgets import *
from listItem import Item

class W1(QListWidget):
    def __init__(self, parent=None):
        super(W1, self).__init__(parent)
        for i in range(1, 10):
            itemN = QListWidgetItem() 
            widget = Item() 
            itemN.setSizeHint(widget.sizeHint())    
            self.addItem(itemN)
            self.setItemWidget(itemN, widget)