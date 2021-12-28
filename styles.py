def button(*buttons):
    for b in buttons:
        b.setStyleSheet("text-transform: uppercase;font-size:10pt;font-family:Segoe UI;font-weight:bold;")
    
def textbox(*textboxes):
    for t in textboxes:
        t.setStyleSheet('QLineEdit{padding:2,2,1,12;border:1px solid silver; font-size:10pt;font-family:Segoe UI Semibold;}'
                        'QLineEdit:focus{padding:2,2,1,12;border:1px solid #686868; font-size:10pt}'
                        'QLineEdit:hover:!focus{padding:2,2,1,12;border:1px solid #898989; font-size:10pt}')
        
def heading(*widgets):
    for w in widgets:
        w.setStyleSheet('font-size:10pt;font-family:Segoe UI;font-weight:bold;')
        
def icon(widget, path):
    widget.setStyleSheet('QPushButton{border:none;background-color:transparent;background-image:url('+path+');background-position:center;background-repeat:no-repeat;background-attachment:fixed;background-clip:padding;border-style:flat;border-width:0px;border-color:transparent;padding:0px;margin:0px;}')
        
def subheading(*widgets):
    for w in widgets:
        w.setStyleSheet('font-size:9pt;font-family:Segoe UI Semibold;')
        
def border(*widgets):
    for w in widgets:
        w.setStyleSheet('border:1px solid silver;')