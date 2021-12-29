
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import requests
import os
import constants

class JSONObject(QObject):
    sig = pyqtSignal(dict)
    
class JSONArray(QObject):
    sig = pyqtSignal(list)

    
class ResponseThread(QThread):
    def __init__(self, url, header=None, form_data=None, parent=None, signal='json', back=None):
        QThread.__init__(self, parent)
        if signal == 'json':
            self.signal = JSONObject()
        else:
            self.signal = JSONArray()
        self.url = url
        self.header = header
        self.form_data = form_data
        self.back = back
        
    def run(self):
        # send FORM data
        print ("sent data: ", self.form_data)
        try:
            if self.form_data:
                r = requests.post(self.url, headers=self.header, data=self.form_data)
            elif self.header:
                r = requests.get(self.url, headers=self.header)
            self.send(r.json())
        except Exception as e:
            self.signal.sig.emit({"back" : self.back, "error": True, "message": str(e)})
            
    def send(self, data):
        try:
            a = {"back" : self.back, 'error': False, 'data': data}
            self.signal.sig.emit(a)
        except Exception as e:
            a = {"back" : self.back, 'error': True, 'message': str(e)}
            self.signal.sig.emit(a)

    def stop(self):
        self.terminate()
        
class DownloadThread(QThread):
    def __init__(self, url, name, header=None, parent=None):
        QThread.__init__(self, parent)
        self.signal = JSONObject()
        self.url = url
        self.name = name
        self.header = header
        
    def run(self):
        try:
            # download file to path
            print (constants.DOWNLOAD_DIRECTORY + '/' + self.name)
            r = requests.get(self.url, headers=self.header, stream=True)
            # create directory if not exists
            if not os.path.exists(constants.DOWNLOAD_DIRECTORY):
                os.makedirs(constants.DOWNLOAD_DIRECTORY)
            # get path separator
            sep = "/"
            with open(constants.DOWNLOAD_DIRECTORY + sep + self.name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            self.signal.sig.emit({"back" : ['download', self.name], 'error': False, 'message': "Success"})
        except Exception as e:
            self.signal.sig.emit({"back" : ['download', self.name], "error": True, "message": str(e)})
          
    def stop(self):
        self.terminate()
        
class UploadThread(QThread):
    def __init__(self, url, header=None, parent=None, back=None):
        QThread.__init__(self, parent)
        self.signal = JSONObject()
        self.url = url
        self.filePath = back[1]
        self.back = back
        self.header = header
        
    def run(self):
        try:
            r = requests.post(self.url, headers=self.header, files={'file': open(self.filePath, 'rb')})
            self.signal.sig.emit({"back" : self.back, 'error': False, 'message': r.json()})
        except Exception as e:
            self.signal.sig.emit({"back" : self.back, "error": True, "message": str(e)})
            
    def stop(self):
        self.terminate()