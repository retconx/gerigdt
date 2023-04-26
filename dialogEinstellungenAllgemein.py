import configparser, os
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
)

basedir = os.path.dirname(__file__)

class EinstellungenAllgemein(QDialog):
    def __init__(self):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(basedir, "config.ini"))
        self.version = configIni["Allgemein"]["version"]
        self.releasedatum = configIni["Allgemein"]["releasedatum"]
        self.dokuverzeichnis = configIni["Allgemein"]["dokuverzeichnis"]
        self.vorherigeDokuLaden = (configIni["Allgemein"]["vorherigedokuladen"] == "1")

        self.setWindowTitle("Allgemeine Einstellungen")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        dialogLayoutV = QVBoxLayout()
        groupboxLayoutG = QGridLayout()
        # Groupbox Dokumentationsverwaltung
        groupboxDokumentationsverwaltung = QGroupBox("Dokumentationsverwaltung")
        groupboxDokumentationsverwaltung.setStyleSheet("font-weight:bold")
        labelArchivierungsverzeichnis = QLabel("Archivierungsverzeichnis:")
        labelArchivierungsverzeichnis.setStyleSheet("font-weight:normal")
        self.lineEditArchivierungsverzeichnis= QLineEdit(self.dokuverzeichnis)
        self.lineEditArchivierungsverzeichnis.setStyleSheet("font-weight:normal")
        buttonDurchsuchenArchivierungsverzeichnis = QPushButton("Durchsuchen")
        buttonDurchsuchenArchivierungsverzeichnis.setStyleSheet("font-weight:normal")
        buttonDurchsuchenArchivierungsverzeichnis.clicked.connect(self.durchsuchenArchivierungsverzeichnis)
        groupboxLayoutG.addWidget(labelArchivierungsverzeichnis, 0, 0, 1, 2)
        groupboxLayoutG.addWidget(self.lineEditArchivierungsverzeichnis, 1, 0)
        groupboxLayoutG.addWidget(buttonDurchsuchenArchivierungsverzeichnis, 1, 1)
        labelVorherigeDokuLaden = QLabel("Vorherige Dokumentation laden (falls vorhanden)")
        labelVorherigeDokuLaden.setStyleSheet("font-weight:normal")
        self.checkboxVorherigeDokuLaden = QCheckBox()
        groupboxLayoutG.addWidget(labelVorherigeDokuLaden, 2, 0)
        groupboxLayoutG.addWidget(self.checkboxVorherigeDokuLaden, 2, 1)
        self.checkboxVorherigeDokuLaden.setChecked(self.vorherigeDokuLaden)
        groupboxDokumentationsverwaltung.setLayout(groupboxLayoutG)

        dialogLayoutV.addWidget(groupboxDokumentationsverwaltung)
        dialogLayoutV.addWidget(self.buttonBox)
        dialogLayoutV.setContentsMargins(10, 10, 10, 10)
        dialogLayoutV.setSpacing(20)
        self.setLayout(dialogLayoutV)

    def durchsuchenArchivierungsverzeichnis(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.Directory)
        fd.setWindowTitle("Dokumentationsarchivierungsverzeichnis")
        fd.setDirectory(self.dokuverzeichnis)
        fd.setModal(True)
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.dokuverzeichnis = fd.directory()
            self.lineEditArchivierungsverzeichnis.setText(fd.directory().path())

    # def accept(self):
    #     if len(self.lineEditPraxisEdvId.text()) != 8:
    #         mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Die GDT-ID muss aus acht Zeichen bestehen.", QMessageBox.StandardButton.Ok)
    #         mb.exec()
    #         self.lineEditPraxisEdvId.setFocus()
    #         self.lineEditPraxisEdvId.selectAll()
    #     elif len(self.lineEditPraxisEdvKuerzel.text()) != 4:
    #         mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Das Kürzel für Austauschdateien muss aus vier Zeichen bestehen.", QMessageBox.StandardButton.Ok)
    #         mb.exec()
    #         self.lineEditPraxisEdvKuerzel.setFocus()
    #         self.lineEditPraxisEdvKuerzel.selectAll()
    #     else:
    #         self.done(1)