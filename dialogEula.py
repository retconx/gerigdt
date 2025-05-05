import os, requests
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
        response = requests.get("https://api.github.com/repos/retconx/dosisgdt/releases/latest")
        body = response.json()["body"]
        aenderungen = str.split(body, "###")[1]
        aenderungenListe = str.split(aenderungen, "\r\n- ")
        datum = aenderungenListe[0].strip()
        aenderungenText = ""
        for i in range(len(aenderungenListe)):
            if i > 0:
                aenderungenText += "\u00b7 " + aenderungenListe[i]
                if i < len(aenderungenListe) - 1:
                    aenderungenText += "\n"
        aenderungenText = aenderungenText.replace("_", "\"")
        labelAenderungen = QLabel("Änderungen vom " + datum + ":")
        labelAenderungen.setStyleSheet("font-weight:bold")
        self.labelAenderungenListe = QLabel(aenderungenText)
        labelBestaetigung = QLabel("Bitte bestätigen Sie, dass Sie die folgende Lizenzvereinbarung gelesen haben und dieser zustimmen.")
        iconsPfad = os.path.join(basedir, "icons/alleIcons200.png")
        labelAndereGdtTools = QLabel("Vielleicht sind auch die anderen GDT-Tools interessant für Sie: <a href='https://gdttools.de' style='border:none;vertical-align:middle'><img width='200' src='" + iconsPfad + "' /></a>")
        labelAndereGdtTools.setTextFormat(Qt.TextFormat.RichText)
        labelAndereGdtTools.linkActivated.connect(self.linkGeklickt)
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
            dialogLayoutV.addWidget(labelAenderungen)
            dialogLayoutV.addWidget(self.labelAenderungenListe)
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
