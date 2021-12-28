from PySide.QtCore import *
from PySide.QtGui import *

class ListWidgetItem(QListWidgetItem):
    
    def __init__(self, pos=0, parent = None):
        super(ListWidgetItem, self).__init__(parent)
        self.pos = pos
        
    # in override
    def __eq__(self, other):
        return self.pos == other.pos
    