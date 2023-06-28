from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
)
from PySide6.QtGui import Qt, QDesktopServices

class UeberGeriGdt(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Über GeriGDT")
        self.setFixedWidth(400)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept) # type: ignore

        dialogLayoutV = QVBoxLayout()
        labelBeschreibung = QLabel("<span style='color:rgb(0,0,200);font-weight:bold'>Programmbeschreibung:</span><br>GeriGDT ist eine eigenständig lauffähige Software zur elektronischen Dokumentation des geriatrischen Basisassessments via GDT-Schnittstelle in ein beliebiges Praxisverwaltungssystem.")
        labelBeschreibung.setAlignment(Qt.AlignmentFlag.AlignJustify)
        labelBeschreibung.setWordWrap(True)
        labelBeschreibung.setTextFormat(Qt.TextFormat.RichText)
        labelEntwickelsVon = QLabel("<span style='color:rgb(0,0,200);font-weight:bold'>Entwickelt von:</span><br>Fabian Treusch<br><a href='http://www.gdttools.de'>www.gdttools.de</a>")
        labelEntwickelsVon.setTextFormat(Qt.TextFormat.RichText)
        labelEntwickelsVon.linkActivated.connect(self.gdtToolsLinkGeklickt) # type: ignore
        labelHilfe = QLabel("<span style='color:rgb(0,0,200);font-weight:bold'>Hilfe:</span><br><a href='http://www.github.com/retconx/gerigdt/wiki'>GeriGDT Wiki</a>")
        labelHilfe.setTextFormat(Qt.TextFormat.RichText)
        labelHilfe.linkActivated.connect(self.githubWikiLinkGeklickt) # type: ignore
        labelSpende = QLabel("<span style='color:rgb(0,0,200);font-weight:bold'>Spende:</span><ul style='margin:0px'><li style='margin-left:-20px'i>Bankverbindung:<ul style='margin:0px'><li style='margin-left:-20px'>Kontoinhaber: Fabian Treusch</li><li style='margin-left:-20px'>IBAN: DE45 3006 0601 0507 5146 97</li><li style='margin-left:-20px'>BIC:DAAEDEDDXXX<br />(Deutsche Apotheker- und Ärztebank)</li></ul></li><li style='margin-left:-20px'>Gerne werden auch <a href='http://www.gdttools.de/#spende'>Spenden in Bitcoin</a> akzeptiert.</li></ul>")
        labelSpende.setTextFormat(Qt.TextFormat.RichText)
        labelSpende.linkActivated.connect(self.gdtToolsLinkGeklickt) # type: ignore

        dialogLayoutV.addWidget(labelBeschreibung)
        dialogLayoutV.addWidget(labelEntwickelsVon)
        dialogLayoutV.addWidget(labelHilfe)
        dialogLayoutV.addWidget(labelSpende)
        dialogLayoutV.addWidget(self.buttonBox)
        self.setLayout(dialogLayoutV)

    def gdtToolsLinkGeklickt(self, link):
        QDesktopServices.openUrl(link)

    def githubWikiLinkGeklickt(self, link):
        QDesktopServices.openUrl(link)