import configparser, os, gdttoolsL, re, sys
from PySide6.QtGui import QFont, Qt, QDesktopServices
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
    QMessageBox
)

class EinstellungenAllgemein(QDialog):
    def __init__(self, configPath):
        super().__init__()

        self.fontNormal = QFont()
        self.fontNormal.setBold(False)
        self.fontBold = QFont()
        self.fontBold.setBold(True)

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.version = configIni["Allgemein"]["version"]
        self.releasedatum = configIni["Allgemein"]["releasedatum"]
        self.dokuverzeichnis = configIni["Allgemein"]["dokuverzeichnis"]
        self.vorherigeDokuLaden = configIni["Allgemein"]["vorherigedokuladen"] == "1"
        self.pdferstellen = configIni["Allgemein"]["pdferstellen"] == "1"
        self.bmiuebernehmen = configIni["Allgemein"]["bmiuebernehmen"] == "1"
        self.pdfbezeichnung = configIni["Allgemein"]["pdfbezeichnung"] 
        self.benutzerUebernehmen = configIni["Allgemein"]["benutzeruebernehmen"] == "1"
        self.einrichtungUebernehmen = configIni["Allgemein"]["einrichtunguebernehmen"] == "1"
        self.autoupdate = configIni["Allgemein"]["autoupdate"] == "True"
        self.updaterpfad = configIni["Allgemein"]["updaterpfad"]
        self.trendverzeichnis = configIni["Allgemein"]["trendverzeichnis"]

        self.setWindowTitle("Allgemeine Einstellungen")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        # Prüfen, ob Lizenzschlüssel verschlüsselt in config.ini
        lizenzschluessel = configIni["Erweiterungen"]["lizenzschluessel"]
        if len(lizenzschluessel) != 29:
            lizenzschluessel = gdttoolsL.GdtToolsLizenzschluessel.dekrypt(lizenzschluessel)

        dialogLayoutV = QVBoxLayout()
        # Groupbox Dokumentationsverwaltung
        groupboxDokumentationsverwaltung = QGroupBox("Dokumentationsverwaltung")
        groupboxDokumentationsverwaltung.setFont(self.fontBold)
        labelKeineRegistrierung = QLabel("Für diese Funktion ist eine gültige LANR/Lizenzschlüsselkombination erforderlich.")
        labelKeineRegistrierung.setStyleSheet("font-weight:normal;color:rgb(0,0,200)")
        labelKeineRegistrierung.setVisible(False)
        labelArchivierungsverzeichnis = QLabel("Archivierungsverzeichnis:")
        labelArchivierungsverzeichnis.setFont(self.fontNormal)
        self.lineEditArchivierungsverzeichnis= QLineEdit(self.dokuverzeichnis)
        self.lineEditArchivierungsverzeichnis.setFont(self.fontNormal)
        buttonDurchsuchenArchivierungsverzeichnis = QPushButton("Durchsuchen")
        buttonDurchsuchenArchivierungsverzeichnis.setFont(self.fontNormal)
        buttonDurchsuchenArchivierungsverzeichnis.clicked.connect(self.durchsuchenArchivierungsverzeichnis) # type: ignore
        groupboxLayoutArchivierungsverzeichnis = QGridLayout()
        groupboxLayoutArchivierungsverzeichnis.addWidget(labelKeineRegistrierung, 0, 0, 1, 2)
        groupboxLayoutArchivierungsverzeichnis.addWidget(labelArchivierungsverzeichnis, 1, 0, 1, 2)
        groupboxLayoutArchivierungsverzeichnis.addWidget(self.lineEditArchivierungsverzeichnis, 2, 0)
        groupboxLayoutArchivierungsverzeichnis.addWidget(buttonDurchsuchenArchivierungsverzeichnis, 2, 1)
        labelVorherigeDokuLaden = QLabel("Vorherige Dokumentation laden (falls vorhanden)")
        labelVorherigeDokuLaden.setFont(self.fontNormal)
        self.checkboxVorherigeDokuLaden = QCheckBox()
        self.checkboxVorherigeDokuLaden.setChecked(self.vorherigeDokuLaden)
        # Dokumenationsverwaltung daktivieren, falls nicht lizensiert
        if not gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(lizenzschluessel, configIni["Erweiterungen"]["lanr"], gdttoolsL.SoftwareId.GERIGDT):
            labelKeineRegistrierung.setVisible(True)
            self.checkboxVorherigeDokuLaden.setEnabled(False)
            self.checkboxVorherigeDokuLaden.setChecked(False)
        groupboxLayoutArchivierungsverzeichnis.addWidget(labelVorherigeDokuLaden, 3, 0)
        groupboxLayoutArchivierungsverzeichnis.addWidget(self.checkboxVorherigeDokuLaden, 3, 1)
        groupboxDokumentationsverwaltung.setLayout(groupboxLayoutArchivierungsverzeichnis)
        # Groupbox PDF-Erstellung
        groupboxPdfErstellung = QGroupBox("PDF-Erstellung")
        groupboxPdfErstellung.setFont(self.fontBold)
        labelKeineRegistrierung = QLabel("Für diese Funktion ist eine gültige LANR/Lizenzschlüsselkombination erforderlich.")
        labelKeineRegistrierung.setStyleSheet("font-weight:normal;color:rgb(0,0,200)")
        labelKeineRegistrierung.setVisible(False)
        labelPdfErstellen = QLabel("PDF erstellen und per GDT übertragen")
        labelPdfErstellen.setFont(self.fontNormal)
        self.checkboxPdfErstellen = QCheckBox()
        self.checkboxPdfErstellen.setChecked(self.pdferstellen)
        self.checkboxPdfErstellen.stateChanged.connect(self.checkboxPdfErstellenChanged) # type: ignore
        labelBmiUebernehmen = QLabel("Größe/Gewicht zur BMI-Berechnung übernehmen")
        labelBmiUebernehmen.setFont(self.fontNormal)
        self.checkboxBmiUebernehmen = QCheckBox()
        self.checkboxBmiUebernehmen.setChecked(self.bmiuebernehmen)
        self.checkboxBmiUebernehmen.stateChanged.connect(self.checkboxBmiUebernehmenChanged) # type: ignore
        labelBenutzerUebernehmen = QLabel("Benutzername übernehmen")
        labelBenutzerUebernehmen.setFont(self.fontNormal)
        labelEinrichtungUebernehmen = QLabel("Einrichtungsname übernehmen")
        labelEinrichtungUebernehmen.setFont(self.fontNormal)
        self.checkboxBenutzerUebernehmen = QCheckBox()
        self.checkboxBenutzerUebernehmen.setChecked(self.benutzerUebernehmen)
        self.checkboxBenutzerUebernehmen.stateChanged.connect(self.checkboxBenutzerUebernehmenChanged) # type: ignore
        self.checkboxEinrichtungUebernehmen = QCheckBox()
        self.checkboxEinrichtungUebernehmen.setChecked(self.einrichtungUebernehmen)
        self.checkboxEinrichtungUebernehmen.stateChanged.connect(self.checkboxEinrichtungUebernehmenChanged) # type: ignore
        labelPdfBezeichnung = QLabel("PDF-Bezeichnung in Karteikarte:")
        labelPdfBezeichnung.setFont(self.fontNormal)
        self.lineEditPdfBezeichnung = QLineEdit(self.pdfbezeichnung)
        self.lineEditPdfBezeichnung.setFont(self.fontNormal)
        self.lineEditPdfBezeichnung.setPlaceholderText("Geriatrisches Basisassessment")
        # PDF-Erstellung daktivieren, falls nicht lizensiert
        if not gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(lizenzschluessel, configIni["Erweiterungen"]["lanr"], gdttoolsL.SoftwareId.GERIGDT):
            labelKeineRegistrierung.setVisible(True)
            self.checkboxPdfErstellen.setEnabled(False)
            self.checkboxPdfErstellen.setChecked(False)
            self.checkboxBmiUebernehmen.setEnabled(False)
            self.checkboxBmiUebernehmen.setChecked(False)
            self.lineEditPdfBezeichnung.setText("")
            self.checkboxBenutzerUebernehmen.setEnabled(False)
            self.checkboxBenutzerUebernehmen.setChecked(False)

        groupboxLayoutPdfErstellung = QGridLayout()
        groupboxLayoutPdfErstellung.addWidget(labelKeineRegistrierung, 0, 0, 1, 2)
        groupboxLayoutPdfErstellung.addWidget(labelPdfErstellen, 1, 0)
        groupboxLayoutPdfErstellung.addWidget(self.checkboxPdfErstellen, 1, 1)
        groupboxLayoutPdfErstellung.addWidget(labelBmiUebernehmen, 2, 0)
        groupboxLayoutPdfErstellung.addWidget(self.checkboxBmiUebernehmen, 2, 1)
        groupboxLayoutPdfErstellung.addWidget(labelBenutzerUebernehmen, 3, 0)
        groupboxLayoutPdfErstellung.addWidget(self.checkboxBenutzerUebernehmen, 3, 1)
        groupboxLayoutPdfErstellung.addWidget(labelEinrichtungUebernehmen, 4, 0)
        groupboxLayoutPdfErstellung.addWidget(self.checkboxEinrichtungUebernehmen, 4, 1)
        groupboxPdfErstellung.setLayout(groupboxLayoutPdfErstellung)
        groupboxLayoutPdfErstellung.addWidget(labelPdfBezeichnung, 5, 0)
        groupboxLayoutPdfErstellung.addWidget(self.lineEditPdfBezeichnung, 6, 0)

        # GroupBox Trenderstellung
        groupboxTrenderstellungLayoutG = QGridLayout()
        groupboxTrenderstellung = QGroupBox("Trenderstellung\u002a")
        groupboxTrenderstellung.setFont(self.fontBold)
        labelTrendverzeichnis = QLabel("Trendverzeichnis")
        labelTrendverzeichnis.setFont(self.fontNormal)
        self.lineEditTrendverzeichnis = QLineEdit(self.trendverzeichnis)
        self.lineEditTrendverzeichnis.setFont(self.fontNormal)
        self.pushButtonTrendverzeichnis = QPushButton("...")
        self.pushButtonTrendverzeichnis.setFont(self.fontNormal)
        self.pushButtonTrendverzeichnis.setToolTip("Trendverzeichnis auswählen")
        self.pushButtonTrendverzeichnis.clicked.connect(self.pushButtonTrendverzeichnisClicked)
        labelScoreGdt = QLabel("<table><tr><td>&#x2a;</td><td><span style='font-weight:normal'>Die Trenderstellung des Barthel-Index und des Timed \"Up and Go\"-Tests<br />ist eine Funktion von <a style='color:rgb(0,0,200)' href='https://gdttools.de/scoregdt.php'>ScoreGDT</a>.</td></tr></table")
        labelScoreGdt.setTextFormat(Qt.TextFormat.RichText)
        labelScoreGdt.linkActivated.connect(self.gdtToolsLinkGeklickt)
        groupboxTrenderstellungLayoutG.addWidget(labelTrendverzeichnis, 0, 0)
        groupboxTrenderstellungLayoutG.addWidget(self.lineEditTrendverzeichnis, 0, 1)
        groupboxTrenderstellungLayoutG.addWidget(self.pushButtonTrendverzeichnis, 0, 2)
        groupboxTrenderstellungLayoutG.addWidget(labelScoreGdt, 1, 0, 1, 3)
        groupboxTrenderstellung.setLayout(groupboxTrenderstellungLayoutG)

        # GroupBox Updates
        groupBoxUpdatesLayoutG = QGridLayout()
        groupBoxUpdates = QGroupBox("Updates")
        groupBoxUpdates.setFont(self.fontBold)
        labelUpdaterPfad = QLabel("Updater-Pfad")
        labelUpdaterPfad.setFont(self.fontNormal)
        self.lineEditUpdaterPfad= QLineEdit(self.updaterpfad)
        self.lineEditUpdaterPfad.setFont(self.fontNormal)
        self.lineEditUpdaterPfad.setToolTip(self.updaterpfad)
        if not os.path.exists(self.updaterpfad):
            self.lineEditUpdaterPfad.setStyleSheet("background:rgb(255,200,200)")
        self.pushButtonUpdaterPfad = QPushButton("...")
        self.pushButtonUpdaterPfad.setFont(self.fontNormal)
        self.pushButtonUpdaterPfad.setToolTip("Pfad zum GDT-Tools Updater auswählen")
        self.pushButtonUpdaterPfad.clicked.connect(self.pushButtonUpdaterPfadClicked)
        self.checkBoxAutoUpdate = QCheckBox("Automatisch auf Update prüfen")
        self.checkBoxAutoUpdate.setFont(self.fontNormal)
        self.checkBoxAutoUpdate.setChecked(self.autoupdate)
        groupBoxUpdatesLayoutG.addWidget(labelUpdaterPfad, 0, 0)
        groupBoxUpdatesLayoutG.addWidget(self.lineEditUpdaterPfad, 0, 1)
        groupBoxUpdatesLayoutG.addWidget(self.pushButtonUpdaterPfad, 0, 2)
        groupBoxUpdatesLayoutG.addWidget(self.checkBoxAutoUpdate, 1, 0)
        groupBoxUpdates.setLayout(groupBoxUpdatesLayoutG)

        dialogLayoutV.addWidget(groupboxDokumentationsverwaltung)
        dialogLayoutV.addWidget(groupboxPdfErstellung)
        dialogLayoutV.addWidget(groupboxTrenderstellung)
        dialogLayoutV.addWidget(groupBoxUpdates)
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
            self.lineEditArchivierungsverzeichnis.setText(os.path.abspath(fd.directory().path()))
            self.lineEditArchivierungsverzeichnis.setToolTip(os.path.abspath(fd.directory().path()))

    def checkboxPdfErstellenChanged(self, newState):
        if not newState:
            self.checkboxBmiUebernehmen.setChecked(False)
            self.lineEditPdfBezeichnung.setText("")
            self.checkboxBenutzerUebernehmen.setChecked(False)
            self.checkboxEinrichtungUebernehmen.setChecked(False)

    def checkboxBmiUebernehmenChanged(self, newState):
        if newState:
            self.checkboxPdfErstellen.setChecked(True)

    def checkboxBenutzerUebernehmenChanged(self, newState):
        if newState:
            self.checkboxPdfErstellen.setChecked(True)
    def checkboxEinrichtungUebernehmenChanged(self, newState):
        if newState:
            self.checkboxPdfErstellen.setChecked(True)

    def pushButtonTrendverzeichnisClicked(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.Directory)
        fd.setModal(True)
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Ok")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            pfad = fd.directory().absolutePath()
            self.lineEditTrendverzeichnis.setText(pfad)
            self.trendverzeichnis = pfad

    def pushButtonUpdaterPfadClicked(self):
        fd = QFileDialog(self)
        fd.setFileMode(QFileDialog.FileMode.ExistingFile)
        if os.path.exists(self.lineEditUpdaterPfad.text()):
            fd.setDirectory(os.path.dirname(self.lineEditUpdaterPfad.text()))
        fd.setWindowTitle("Updater-Pfad auswählen")
        fd.setModal(True)
        if "win32" in sys.platform:
            fd.setNameFilters(["exe-Dateien (*.exe)"])
        elif "darwin" in sys.platform:
            fd.setNameFilters(["app-Bundles (*.app)"])
        fd.setLabelText(QFileDialog.DialogLabel.Accept, "Auswählen")
        fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
        if fd.exec() == 1:
            self.lineEditUpdaterPfad.setText(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditUpdaterPfad.setToolTip(os.path.abspath(fd.selectedFiles()[0]))
            self.lineEditUpdaterPfad.setStyleSheet("background:rgb(255,255,255)")

    def gdtToolsLinkGeklickt(self, link):
        QDesktopServices.openUrl(link)

    def accept(self):
        regexPattern = "[/.,]"
        test = re.search(regexPattern, self.lineEditPdfBezeichnung.text())
        if test != None:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Die PDF-Bezeichnung enthält unerlaubte Zeichen (" + regexPattern[1:-1] + ")", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditPdfBezeichnung.setFocus()
            self.lineEditPdfBezeichnung.selectAll()
        else:
            if self.lineEditPdfBezeichnung.text() == "":
                self.lineEditPdfBezeichnung.setText(self.lineEditPdfBezeichnung.placeholderText())
            self.done(1)
