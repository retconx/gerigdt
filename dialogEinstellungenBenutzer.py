import configparser, os
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
)

class EinstellungenBenutzer(QDialog):
    def __init__(self, configPath):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.benutzernamen = (configIni["Benutzer"]["namen"]).split("::")
        self.benutzerkuerzel = (configIni["Benutzer"]["kuerzel"]).split("::")

        self.setWindowTitle("Benutzer verwalten")
        self.setMinimumSize(QSize(300,250))
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        dialogLayoutV = QVBoxLayout()
        dialogLayoutG = QGridLayout()

        self.labelNamen = QLabel("Name")
        self.labelKuerzel = QLabel("Kürzel")
        dialogLayoutG.addWidget(self.labelNamen, 0, 0)
        dialogLayoutG.addWidget(self.labelKuerzel, 0, 1)
        self.lineEditNamen = []
        self.lineEditKuerzel = []
        for i in range(5):
            self.lineEditNamen.append(QLineEdit())
            dialogLayoutG.addWidget(self.lineEditNamen[i], i + 1, 0)
        for i in range(5):
            self.lineEditKuerzel.append(QLineEdit())
            self.lineEditKuerzel[i].setFixedWidth(40)
            dialogLayoutG.addWidget(self.lineEditKuerzel[i], i + 1, 1)
        for i in range(len(self.benutzernamen)):
                self.lineEditNamen[i].setText(self.benutzernamen[i])
                self.lineEditKuerzel[i].setText(self.benutzerkuerzel[i])

        dialogLayoutV.addLayout(dialogLayoutG)
        dialogLayoutV.addWidget(self.buttonBox)

        self.setLayout(dialogLayoutV)
        self.lineEditNamen[0].setFocus()
        self.lineEditNamen[0].setFocus()
   
    def accept(self):
        fehlendesKuerzel = -1
        for i in range(5):
            if self.lineEditNamen[i].text() != "" and self.lineEditKuerzel[i].text() == "":
                fehlendesKuerzel = i
                break
        if fehlendesKuerzel != -1:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Für den " + str(fehlendesKuerzel + 1) + ". Benutzer wurde kein Kürzel angegeben.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditKuerzel[fehlendesKuerzel].setFocus()
        else:
            self.done(1)
                    
        
            
            