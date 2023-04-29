import configparser, os, lizenzschluessel
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

class EinstellungenAllgemein(QDialog):
    def __init__(self, configPath):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.version = configIni["Allgemein"]["version"]
        self.releasedatum = configIni["Allgemein"]["releasedatum"]
        self.dokuverzeichnis = configIni["Allgemein"]["dokuverzeichnis"]
        self.vorherigeDokuLaden = (configIni["Allgemein"]["vorherigedokuladen"] == "1")

        self.setWindowTitle("Allgemeine Einstellungen")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        dialogLayoutV = QVBoxLayout()
        # Groupbox Dokumentationsverwaltung
        groupboxDokumentationsverwaltung = QGroupBox("Dokumentationsverwaltung (Lizenz erforderlich)")
        groupboxDokumentationsverwaltung.setStyleSheet("font-weight:bold")
        labelArchivierungsverzeichnis = QLabel("Archivierungsverzeichnis:")
        labelArchivierungsverzeichnis.setStyleSheet("font-weight:normal")
        self.lineEditArchivierungsverzeichnis= QLineEdit(self.dokuverzeichnis)
        self.lineEditArchivierungsverzeichnis.setStyleSheet("font-weight:normal")
        buttonDurchsuchenArchivierungsverzeichnis = QPushButton("Durchsuchen")
        buttonDurchsuchenArchivierungsverzeichnis.setStyleSheet("font-weight:normal")
        buttonDurchsuchenArchivierungsverzeichnis.clicked.connect(self.durchsuchenArchivierungsverzeichnis) # type: ignore
        groupboxLayoutArchivierungsverzeichnis = QGridLayout()
        groupboxLayoutArchivierungsverzeichnis.addWidget(labelArchivierungsverzeichnis, 0, 0, 1, 2)
        groupboxLayoutArchivierungsverzeichnis.addWidget(self.lineEditArchivierungsverzeichnis, 1, 0)
        groupboxLayoutArchivierungsverzeichnis.addWidget(buttonDurchsuchenArchivierungsverzeichnis, 1, 1)
        labelVorherigeDokuLaden = QLabel("Vorherige Dokumentation laden (falls vorhanden)")
        labelVorherigeDokuLaden.setStyleSheet("font-weight:normal")
        self.checkboxVorherigeDokuLaden = QCheckBox()
        self.checkboxVorherigeDokuLaden.setChecked(self.vorherigeDokuLaden)
        if not lizenzschluessel.GdtToolsLizenzschluessel.lizenzErteilt(configIni["Erweiterungen"]["lizenzschluessel"], configIni["Erweiterungen"]["lanr"], lizenzschluessel.SoftwareId.GERIGDT):
            groupboxDokumentationsverwaltung.setEnabled(False)
            self.lineEditArchivierungsverzeichnis.setText("")
            self.checkboxVorherigeDokuLaden.setChecked(False)
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        groupboxLayoutArchivierungsverzeichnis.addWidget(labelVorherigeDokuLaden, 2, 0)
        groupboxLayoutArchivierungsverzeichnis.addWidget(self.checkboxVorherigeDokuLaden, 2, 1)
        groupboxDokumentationsverwaltung.setLayout(groupboxLayoutArchivierungsverzeichnis)

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