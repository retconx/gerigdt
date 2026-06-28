import configparser, os
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QWidget,
    QPushButton
)

class EinstellungenBenutzer(QDialog):
    def __init__(self, configPath):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"), encoding="utf-8")
        self.benutzernamen = (configIni["Benutzer"]["namen"]).split("::")
        self.benutzerkuerzel = (configIni["Benutzer"]["kuerzel"]).split("::")
        self.anzahlBenutzerzeilen = len(self.benutzernamen) + 1
        if self.anzahlBenutzerzeilen < 11:
            self.anzahlBenutzerzeilen = 11

        self.setWindowTitle("BenutzerInnen verwalten")
        self.setMinimumSize(QSize(300,250))
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        dialogLayoutV = QVBoxLayout()
        self.dialogLayoutG = QGridLayout()
        self.scrollArea = QScrollArea()
        scrollWidget = QWidget()
        
        self.labelNummern = QLabel("Nr.")
        self.labelNamen = QLabel("Name")
        self.labelKuerzel = QLabel("Kürzel")
        self.dialogLayoutG.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.dialogLayoutG.addWidget(self.labelNummern, 0, 0)
        self.dialogLayoutG.addWidget(self.labelNamen, 0, 1)
        self.dialogLayoutG.addWidget(self.labelKuerzel, 0, 2)
        self.labelBenutzerNummer = []
        self.lineEditNamen = []
        self.lineEditKuerzel = []
        self.pushButtonEntfernen = []
        self.pushButtonWiederherstellen = []
        for i in range(self.anzahlBenutzerzeilen):
            self.labelBenutzerNummer.append(QLabel(str(i + 1)))
            self.dialogLayoutG.addWidget(self.labelBenutzerNummer[i], i + 1, 0)
            self.lineEditNamen.append(QLineEdit())
            self.lineEditNamen[i].setFixedWidth(250)
            self.dialogLayoutG.addWidget(self.lineEditNamen[i], i + 1, 1)
            self.lineEditKuerzel.append(QLineEdit())
            self.lineEditKuerzel[i].setFixedWidth(40)
            self.dialogLayoutG.addWidget(self.lineEditKuerzel[i], i + 1, 2)
            self.pushButtonEntfernen.append(QPushButton("\u232b"))
            self.pushButtonEntfernen[i].setFixedWidth(30)
            self.pushButtonEntfernen[i].clicked.connect(lambda clicked = False, benutzerNr = i:self.pushButtonEntfernenClicked(clicked, benutzerNr))
            self.dialogLayoutG.addWidget(self.pushButtonEntfernen[i], i + 1, 3)
        self.lineEditNamen[0].setPlaceholderText("Dr. med. XY")
        for i in range(len(self.benutzernamen)):
                self.lineEditNamen[i].setText(self.benutzernamen[i])
                self.lineEditKuerzel[i].setText(self.benutzerkuerzel[i])
                if self.lineEditNamen[i].text() != "":
                    self.pushButtonEntfernen[i].setToolTip("BenutzerIn " + str(i + 1) + " " + self.lineEditNamen[i].text() + " (" + self.lineEditKuerzel[i].text() + ") entfernen")

        scrollWidget.setLayout(self.dialogLayoutG)
        self.scrollArea.setWidget(scrollWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.verticalScrollBar().rangeChanged.connect(self.verticalScrollBarRangeChanged)
        
        # Hinzufügen-Button
        self.pushButtonBenutzerHinzufuegen = QPushButton("BenutzerIn hinzufügen")
        self.pushButtonBenutzerHinzufuegen.clicked.connect(self.pushButtonBenutzerHinzufuegenClicked)

        dialogLayoutV.addWidget(self.scrollArea)
        dialogLayoutV.addWidget(self.pushButtonBenutzerHinzufuegen)
        dialogLayoutV.addWidget(self.buttonBox)

        self.setLayout(dialogLayoutV)
        self.setFixedHeight(int(self.dialogLayoutG.sizeHint().height()) + 180)
        self.lineEditNamen[0].setFocus()
        self.lineEditNamen[0].setFocus()
    
    def pushButtonBenutzerHinzufuegenClicked(self):
        self.labelBenutzerNummer.append(QLabel(str(self.anzahlBenutzerzeilen + 1)))
        self.lineEditNamen.append(QLineEdit())
        self.lineEditKuerzel.append(QLineEdit())
        self.dialogLayoutG.addWidget(self.labelBenutzerNummer[self.anzahlBenutzerzeilen], self.anzahlBenutzerzeilen + 2, 0)
        self.dialogLayoutG.addWidget(self.lineEditNamen[self.anzahlBenutzerzeilen], self.anzahlBenutzerzeilen + 2, 1)
        self.lineEditNamen[self.anzahlBenutzerzeilen].setFixedWidth(250)
        self.dialogLayoutG.addWidget(self.lineEditKuerzel[self.anzahlBenutzerzeilen], self.anzahlBenutzerzeilen + 2, 2)
        self.lineEditKuerzel[self.anzahlBenutzerzeilen].setFixedWidth(40)
        self.lineEditNamen[self.anzahlBenutzerzeilen].setFocus()
        self.anzahlBenutzerzeilen += 1

    def pushButtonEntfernenClicked(self, clicked, nr):
        self.lineEditNamen[nr].setText("")
        self.lineEditKuerzel[nr].setText("")
    
    def verticalScrollBarRangeChanged(self):
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
   
    def accept(self):
        fehlendesKuerzel = -1
        for i in range(self.anzahlBenutzerzeilen):
            if self.lineEditNamen[i].text() != "" and self.lineEditKuerzel[i].text() == "":
                fehlendesKuerzel = i
                break
        if fehlendesKuerzel != -1:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Für den " + str(fehlendesKuerzel + 1) + ". Benutzer wurde kein Kürzel angegeben.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditKuerzel[fehlendesKuerzel].setFocus()
        else:
            self.done(1)
                    
        
            
            