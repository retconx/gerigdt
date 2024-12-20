import os
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QTextEdit
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt

basedir = os.path.dirname(__file__)

class Eula(QDialog):
    def __init__(self, neueVersion=""):
        super().__init__()

        self.setWindowTitle("Endnutzer-Lizenzvereinbarung (EULA)")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)

        dialogLayoutV = QVBoxLayout()
        labelAktualisiert = QLabel("GeriGDT wurde erfolgreich auf Version " + neueVersion + " aktualisiert.")
        labelAktualisiert.setStyleSheet("font-weight:bold")
        labelSpende = QLabel("Falls GeriGDT Ihren Praxisalltag erleichtert, würde ich mich über eine kleine Anerkennung freuen.<br /><a href='https://gdttools.de/gerigdt.php#spende'>Hier</a> finden Sie Informationen über die Möglichkeit einer <a href='https://gdttools.de/gerigdt.php#spende' style='text-decoration:none;color(rgb(0,0,0))'><b>Spende</b></a>. Dankeschön! &#x1f609;")
        labelSpende.setTextFormat(Qt.TextFormat.RichText)
        labelSpende.linkActivated.connect(self.linkGeklickt)
        labelBestaetigung = QLabel("Bitte bestätigen Sie, dass Sie die folgende Lizenzvereinbarung gelesen haben und dieser zustimmen.")
        iconsPfad = os.path.join(basedir, "icons/alleIcons200.png")
        labelAndereGdtTools = QLabel("Vielleicht sind auch die anderen GDT-Tools interessant für Sie: <a href='https://gdttools.de' style='border:none;vertical-align:middle'><img width='200' src='" + iconsPfad + "' /></a>")
        labelAndereGdtTools.setTextFormat(Qt.TextFormat.RichText)
        labelAndereGdtTools.linkActivated.connect(self.linkGeklickt)
        #labelAndereGdtTools.setStyleSheet("background:rgb(255,255,255);border-style:solid;border-color:rgb(0,0,200);border-width:2px;border-radius:4%;padding:4px")
        text = ""
        self.textEditEula = QTextEdit()
        self.textEditEula.setReadOnly(True)
        with open(os.path.join(basedir, "eula.txt"), "r", encoding="utf_8") as f:  
            for zeile in f:
                text += zeile
        self.textEditEula.setText(text)
        self.textEditEula.setFixedHeight(300)

        self.checkBoxZustimmung = QCheckBox("Gelesen und zugestimmt")
        if neueVersion != "":
            dialogLayoutV.addWidget(labelAktualisiert)
            dialogLayoutV.addWidget(labelSpende)
            dialogLayoutV.addWidget(labelAndereGdtTools)
            dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(labelBestaetigung, alignment=Qt.AlignmentFlag.AlignCenter)
        dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(self.textEditEula)
        dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(self.checkBoxZustimmung, alignment=Qt.AlignmentFlag.AlignCenter)
        dialogLayoutV.addSpacing(10)
        dialogLayoutV.addWidget(self.buttonBox, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(dialogLayoutV)

    def linkGeklickt(self, link):
        QDesktopServices.openUrl(link)
