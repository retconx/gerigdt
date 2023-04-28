import sys, configparser, os, datetime, shutil
import gdt, gdtzeile
import dialogEinstellungenGdt, dialogEinstellungenBenutzer, dialogEinstellungenAllgemein

from PySide6.QtCore import Qt, QSize, QDate, QTime, QTranslator, QLibraryInfo, QLocale
from PySide6.QtGui import QFont, QAction, QKeySequence, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QRadioButton,
    QWidget,
    QLabel, 
    QDateEdit,
    QComboBox,
    QMessageBox,
    QLineEdit
)

basedir = os.path.dirname(__file__)

def versionVeraltet(versionAktuell:str, versionVergleich:str):
    """
    Vergleicht zwei Versionen im Format x.x.x
    Parameter:
        versionAktuell:str
        versionVergleich:str
    Rückgabe:
        True, wenn versionAktuell veraltet
    """
    versionVeraltet= False
    hunderterBase = int(versionVergleich.split(".")[0])
    zehnerBase = int(versionVergleich.split(".")[1])
    einserBase = int(versionVergleich.split(".")[2])
    hunderter = int(versionAktuell.split(".")[2])
    zehner = int(versionAktuell.split(".")[1])
    einser = int(versionAktuell.split(".")[2])
    if hunderterBase > hunderter:
        versionVeraltet = True
    elif hunderterBase == hunderter:
        if zehnerBase >zehner:
            versionVeraltet = True
        elif zehnerBase == zehner:
            if einserBase > einser:
                versionVeraltet = True
    return versionVeraltet

# Sicherstellen, dass Icon in Windows angezeigt wird
try:
    from ctypes import windll # type: ignore
    mayappid = "gdttools.gerigdt"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(mayappid)
except ImportError:
    pass

class MainWindow(QMainWindow):
    barthelEssen = ["Unfähig, alleine zu essen (0)", "Braucht etwas Hilfe (5)", "Selbstständig, benötigt keine Hilfe (10)"]
    barthelBaden = ["Abhängig von fremder Hilfe (0)", "Selbstständig, benötigt keine Hilfe (5)"]
    barthelKoerperpflege = ["Abhängig von fremder Hilfe (0)", "Selbstständig, benötigt keine Hilfe (5)"]
    barthelAnAuskleiden = ["Unfähig, sich allein an- und Auszuziehen (0)", "Benötigt etwas Hilfe, kann aber ca. 50% allein durchführen (5)", "Selbstständig, benötigt keine Hilfe (10)"]
    barthelStuhlkontrolle = ["Inkontinent (0)", "Gelegentlich inkontinent (max. 1x pro Woche) (5)", "Ständig kontinent (10)"]
    barthelUrinkontrolle = ["Inkontinent (0)", "Gelegentlich inkontinent (max. 1x pro Tag) (5)", "Ständig kontinent (10)"]
    barthelToilettenbenutzung = ["Abhängig von fremder Hilfe (0)", "Benötigt Hilfe wegen fehlenden Gleichgewichts oder beim Ausziehen (5)", "Selbstständig, benötigt keine Hilfe (10)"]
    barthelBettRollstuhltransfer = ["Abhängig von fremder Hilfe, fehlende Sitzbalance (0)", "Erhebliche physische Hilfe beim Transfer erforderlich, Sitzen selbstständig (5)", "Geringe physische bzw. verbale Hilfe oder Beaufsichtigung erforderlich (10)", "Selbstständig, benötigt keine Hilfe (15)"]
    barthelMobilitaet = ["Immobil bzw. Strecke < 50 m (0)", "Unabhängig mit Rollstuhl inklusive Ecken, Strecke > 50 m (5)", "Unterstütztes Gehen möglich, Strecke > 50 m (10)", "Selbstständiges Gehen möglich (Hilfsmittel erlaubt), Strecke > 50 m (15)"]
    barthelTreppensteigen = ["Unfähig, allein Treppe zu steigen (0)", "Benötigt Hilfe oder Überwachung beim Treppensteigen (5)", "Selbstständiges Treppensteigen möglich (10)"]
    timedUpGo = ["< 10 Sekunden - keine Mobilitätseinschränkung", "11-19 Sekunden - leichte, i. d. R. irrelevante Mobilitätseinschränkung", "20-29 Sekunden - abklärungsbedürftige, relevante Mobilitätseinschränkung", "> 30 Sekunden - starke Mobilitätseinschränkung"]
    kognitiveFunktion = ["Keine oder leichte Einschränkung", "Mittlere Einschränkung", "Schwere Einschränkung"]
    pflegegrad = ["1", "2", "3", "4", "5", "Nicht vorhanden/unbekannt", "Beantragt"]

    # Mainwindow zentrieren
    def resizeEvent(self, e):
        mainwindowBreite = e.size().width()
        mainwindowHoehe = e.size().height()
        ag = self.screen().availableGeometry()
        screenBreite = ag.size().width()
        screenHoehe = ag.size().height()
        left = screenBreite / 2 - mainwindowBreite / 2
        top = screenHoehe / 2 - mainwindowHoehe / 2
        self.setGeometry(left, top, mainwindowBreite, mainwindowHoehe)

    # Statusmeldungen ändern
    def changeStatus(self, statusnummer:int, statustext:str, rot = False):
        """
            Ändert eine Statusmeldung
            Parameter:
                statusnummer:int
                statustext:str
                rot:boolean (optional)
        """
        self.statusanzeigeLabel[statusnummer].setText(self.statusanzeigeLabelTexte[statusnummer] + ": " + statustext)
        if rot:
            self.statusanzeigeLabel[statusnummer].setStyleSheet("font-weight:normal; color:rgb(200,0,0)")

    def __init__(self):
        super().__init__()

        # config.ini lesen
        updateSafePath = ""
        if sys.platform == "win32":
            updateSafePath = os.path.expanduser("~/appdata/local/gerigdt")
        else:
            updateSafePath = os.path.expanduser("~/.config/gerigdt")
        self.configPath = updateSafePath
        self.configIni = configparser.ConfigParser()
        if os.path.exists(os.path.join(updateSafePath, "config.ini")):
            self.onfigPath = updateSafePath
        elif os.path.exists(os.path.join(basedir, "config.ini")):
            try:
                if (not os.path.exists(updateSafePath)):
                    os.makedirs(updateSafePath, 0o777)
                shutil.copy(os.path.join(basedir, "config.ini"), updateSafePath)
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "Die Konfigurationsdatei config.ini wurde nach " + updateSafePath + " kopiert um sie vor Überschreiben bei einem Update zu schützen.", QMessageBox.StandardButton.Ok)
                mb.exec()
                self.configPath = updateSafePath
            except:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "Problem beim Kopieren der Konfigurationsdatei. GeriGDT wird mit Standardeinstellungen gestartet.", QMessageBox.StandardButton.Ok)
                mb.exec()
                self.configPath = basedir
        else:
            mb = QMessageBox(QMessageBox.Icon.Critical, "Hinweis", "Die Konfigurationsdatei config.ini fehlt. GeriGDT kann nicht gestartet werden.", QMessageBox.StandardButton.Ok)
            mb.exec()
            app.quit()
        self.configIni.read(os.path.join(self.configPath, "config.ini"))
        self.gdtImportVerzeichnis = self.configIni["Verzeichnisse"]["gdtimport"]
        if self.gdtImportVerzeichnis == "":
            self.gdtImportVerzeichnis = os.getcwd()
        self.gdtExportVerzeichnis = self.configIni["Verzeichnisse"]["gdtexport"]
        if self.gdtExportVerzeichnis == "":
            self.gdtExportVerzeichnis = os.getcwd()
        self.benutzernamen = self.configIni["Benutzer"]["namen"].split("::")
        self.benutzerkuerzel = self.configIni["Benutzer"]["kuerzel"].split("::")
        self.aktuelleBenuztzernummer = 0
        self.version = self.configIni["Allgemein"]["version"]
        self.dokuVerzeichnis = self.configIni["Allgemein"]["dokuverzeichnis"]
        self.vorherigeDokuLaden = (self.configIni["Allgemein"]["vorherigedokuladen"] == "1")
        z = self.configIni["GDT"]["zeichensatz"]
        self.zeichensatz = gdt.GdtZeichensatz.IBM_CP437
        if z == "1":
            self.zeichensatz = gdt.GdtZeichensatz.BIT_7
        elif z == "3":
            self.zeichensatz = gdt.GdtZeichensatz.ANSI_CP1252

        # Version vergleichen und gegebenenfalls aktualisieren
        configIniBase = configparser.ConfigParser()
        try:
            configIniBase.read(os.path.join(basedir, "config.ini"))
            if versionVeraltet(self.version, configIniBase["Allgemein"]["version"]):
                self.configIni["Allgemein"]["version"] = configIniBase["Allgemein"]["version"]
                with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                    self.configIni.write(configfile)
                    self.version = self.configIni["Allgemein"]["version"]
        except:
            raise

        jahr = datetime.datetime.now().year
        copyrightJahre = "2023"
        if jahr > 2023:
            copyrightJahre = "2023-" + str(jahr)
        self.setWindowTitle("GeriGDT V" + self.version + " (\u00a9 Fabian Treusch - GDT-Tools " + copyrightJahre + ")")
        font = QFont()
        font.setBold(False)
        fontBold = QFont()
        fontBold.setBold(True)
        fontBoldGross = QFont()
        fontBoldGross.setBold(True)
        fontBoldGross.setPixelSize(16)
        # GDT-Datei laden
        gd = gdt.GdtDatei()
        self.patId = "-"
        name = "-"
        mbErg = QMessageBox.StandardButton.Yes
        try:
            gd.laden(self.gdtImportVerzeichnis + "/GERIT2MD.gdt", self.zeichensatz)
            self.patId = str(gd.getInhalt("3000"))
            name = str(gd.getInhalt("3102")) + " " + str(gd.getInhalt("3101"))
        except (IOError, gdtzeile.GdtFehlerException) as e:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Fehler beim Laden der GDT-Datei:\n" + str(e) + "\n\nSoll GeriGDT dennoch geöffnet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
            mb.button(QMessageBox.StandardButton.No).setText("Nein")
            mb.setDefaultButton(QMessageBox.StandardButton.No)
            mbErg = mb.exec()
        if mbErg == QMessageBox.StandardButton.Yes:
            widget = QWidget()
            mainLayout = QVBoxLayout()
            kopfLayout= QHBoxLayout()
            kopfLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
            titelLabel = QLabel("Geriatrisches Basisassessment")
            titelLabel.setStyleSheet("font-weight:bold;font-size:26px")
            kopfLayout.addWidget(titelLabel)
            # Statusanzeige aufbauen
            self.statusanzeigeLabelTexte = ["Von PVS erzeugte GDT-Datei", "Vorherige Dokumentation geladen vom"]
            self.statusanzeigeStatustext = []
            for statustext in range(len(self.statusanzeigeLabelTexte)):
                self.statusanzeigeStatustext.append("")
            self.statusanzeigeLabel = []
            groupboxStatusanzeigeLayout = QGridLayout()
            groupboxStatusanzeige = QGroupBox(title="Statusanzeige")
            groupboxStatusanzeige.setStyleSheet("font-weight:bold")
            i = 0
            for text in self.statusanzeigeLabelTexte:
                if i == 1:
                    self.buttonAlteUntersuchung = QPushButton()
                    reloadIcon = QIcon(os.path.join(basedir, "icons/reload.png"))
                    self.buttonAlteUntersuchung.setIcon(reloadIcon)
                    self.buttonAlteUntersuchung.setEnabled(False)
                    self.buttonAlteUntersuchung.setToolTip("Funktion nicht verfügbar")
                    self.buttonAlteUntersuchung.clicked.connect(self.vorherigeUntersuchungWiederherstellen) # type: ignore
                    groupboxStatusanzeigeLayout.addWidget(self.buttonAlteUntersuchung, i, 0)
                self.statusanzeigeLabel.append(QLabel(text + ": -"))
                self.statusanzeigeLabel[i].setStyleSheet("font-weight:normal")
                groupboxStatusanzeigeLayout.addWidget(self.statusanzeigeLabel[i], i, 1)
                i += 1
            groupboxStatusanzeige.setLayout(groupboxStatusanzeigeLayout)
            kopfLayout.addStretch()
            kopfLayout.addWidget(groupboxStatusanzeige)
            if self.patId !="-":
                self.changeStatus(0, "geladen")
            else:
                self.changeStatus(0, "nicht geladen", True)
            testLayout = QGridLayout()
            barthelLabel = QLabel(text="Barthel-Index")
            barthelLabel.setFont(fontBoldGross)
            groupboxLayout = QVBoxLayout()
            groupboxBarthelEssen = QGroupBox(title="Essen")
            self.radiobuttonBarhelEssen = []
            for radio in self.barthelEssen:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelEssen.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelEssen[len(self.barthelEssen) - 1].setChecked(True)
            groupboxBarthelEssen.setLayout(groupboxLayout)
            groupboxBarthelEssen.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelBaden = QGroupBox(title="Baden")
            self.radiobuttonBarhelBaden = []
            for radio in self.barthelBaden:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelBaden.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelBaden[len(self.barthelBaden) - 1].setChecked(True)
            groupboxBarthelBaden.setLayout(groupboxLayout)
            groupboxBarthelBaden.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelKoerperpflege = QGroupBox(title="Körperpflege (Rasieren, Zähneputzen)")
            self.radiobuttonBarhelKoerperpflege = []
            for radio in self.barthelKoerperpflege:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelKoerperpflege.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelKoerperpflege[len(self.barthelKoerperpflege) - 1].setChecked(True)
            groupboxBarthelKoerperpflege.setLayout(groupboxLayout)
            groupboxBarthelKoerperpflege.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelAnAuskleiden = QGroupBox(title="An- und Auskleiden")
            self.radiobuttonBarhelAnAuskleiden = []
            for radio in self.barthelAnAuskleiden:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelAnAuskleiden.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelAnAuskleiden[len(self.barthelAnAuskleiden) - 1].setChecked(True)
            groupboxBarthelAnAuskleiden.setLayout(groupboxLayout)
            groupboxBarthelAnAuskleiden.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelStuhlkontrolle = QGroupBox(title="Stuhlkontrolle")
            self.radiobuttonBarhelStuhlkontrolle = []
            for radio in self.barthelStuhlkontrolle:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelStuhlkontrolle.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelStuhlkontrolle[len(self.barthelStuhlkontrolle) - 1].setChecked(True)
            groupboxBarthelStuhlkontrolle.setLayout(groupboxLayout)
            groupboxBarthelStuhlkontrolle.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelUrinkontrolle = QGroupBox(title="Urinkontrolle")
            self.radiobuttonBarhelUrinkontrolle = []
            for radio in self.barthelUrinkontrolle:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelUrinkontrolle.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelUrinkontrolle[len(self.barthelUrinkontrolle) - 1].setChecked(True)
            groupboxBarthelUrinkontrolle.setLayout(groupboxLayout)
            groupboxBarthelUrinkontrolle.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelToilettenbenutzung = QGroupBox(title="Toilettenbenutzung")
            self.radiobuttonBarhelToilettenbenutzung = []
            for radio in self.barthelToilettenbenutzung:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelToilettenbenutzung.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelToilettenbenutzung[len(self.barthelToilettenbenutzung) - 1].setChecked(True)
            groupboxBarthelToilettenbenutzung.setLayout(groupboxLayout)
            groupboxBarthelToilettenbenutzung.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelBettRollstuhltransfer = QGroupBox(title="Bett-/ (Roll-)-Stuhltransfer")
            self.radiobuttonBarhelBettRollstuhltransfer = []
            for radio in self.barthelBettRollstuhltransfer:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelBettRollstuhltransfer.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelBettRollstuhltransfer[len(self.barthelBettRollstuhltransfer) - 1].setChecked(True)
            groupboxBarthelBettRollstuhltransfer.setLayout(groupboxLayout)
            groupboxBarthelBettRollstuhltransfer.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelMobilitaet = QGroupBox(title="Mobilität")
            self.radiobuttonBarhelMobilitaet = []
            for radio in self.barthelMobilitaet:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelMobilitaet.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelMobilitaet[len(self.barthelMobilitaet) - 1].setChecked(True)
            groupboxBarthelMobilitaet.setLayout(groupboxLayout)
            groupboxBarthelMobilitaet.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelTreppensteigen = QGroupBox(title="Treppensteigen")
            self.radiobuttonBarhelTreppensteigen = []
            for radio in self.barthelTreppensteigen:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonBarhelTreppensteigen.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelTreppensteigen[len(self.barthelTreppensteigen) - 1].setChecked(True)
            groupboxBarthelTreppensteigen.setLayout(groupboxLayout)
            groupboxBarthelTreppensteigen.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxTimedUpGo = QGroupBox(title="Timed \"Up and Go\"")
            self.radiobuttonTimedUpGo = []
            for radio in self.timedUpGo:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonTimedUpGo.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonTimedUpGo[0].setChecked(True)
            groupboxTimedUpGo.setLayout(groupboxLayout)
            groupboxTimedUpGo.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxKognitiveFunktion = QGroupBox("Kognitive Funktion")
            self.radiobuttonKognitiveFunktion = []
            for radio in self.kognitiveFunktion:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonKognitiveFunktion.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonKognitiveFunktion[0].setChecked(True)
            groupboxKognitiveFunktion.setLayout(groupboxLayout)
            groupboxKognitiveFunktion.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxPflegegrad = QGroupBox("Pflegegrad")
            self.radiobuttonPflegegrad = []
            for radio in self.pflegegrad:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                self.radiobuttonPflegegrad.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonPflegegrad[len(self.pflegegrad) - 2].setChecked(True)
            groupboxPflegegrad.setLayout(groupboxLayout)
            groupboxPflegegrad.setFont(fontBold)

            testLayout.addWidget(barthelLabel, 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)
            testLayout.addWidget(groupboxBarthelEssen, 1, 0)
            testLayout.addWidget(groupboxBarthelBaden, 2, 0)
            testLayout.addWidget(groupboxBarthelKoerperpflege, 3, 0)
            testLayout.addWidget(groupboxBarthelAnAuskleiden, 4, 0)
            testLayout.addWidget(groupboxBarthelStuhlkontrolle, 5, 0)
            testLayout.addWidget(groupboxBarthelUrinkontrolle, 1, 1)
            testLayout.addWidget(groupboxBarthelToilettenbenutzung, 2, 1)
            testLayout.addWidget(groupboxBarthelBettRollstuhltransfer, 3, 1)
            testLayout.addWidget(groupboxBarthelMobilitaet, 4, 1)
            testLayout.addWidget(groupboxBarthelTreppensteigen, 5, 1)
            testLayout.addWidget(groupboxTimedUpGo, 1, 2)
            testLayout.addWidget(groupboxKognitiveFunktion, 2, 2)
            testLayout.addWidget(groupboxPflegegrad, 3, 2, 2, 1)
            datenLayoutH = QHBoxLayout()
            datenLayoutG = QGridLayout()
            labelName = QLabel("Name:")
            labelPatId = QLabel("Pat.-ID:")
            labelUntDat = QLabel("Untersuchungsdatum:")
            labelDokuVon = QLabel("Dokumentiert von:")
            labelNameGdt = QLabel()
            labelPatIdGdt = QLabel()
            labelNameGdt.setText(name)
            labelPatIdGdt.setText(self.patId)
            untdat = QDate()
            self.untdatEdit = QDateEdit()
            self.untdatEdit.setDate(untdat.currentDate())
            self.untdatEdit.setDisplayFormat("dd.MM.yyyy")
            self.untdatEdit.setCalendarPopup(True)
            self.untdatEdit.userDateChanged.connect(self.datumGeaendert) # type: ignore
            self.dokuvonComboBox = QComboBox()
            self.dokuvonComboBox.currentIndexChanged.connect(self.benutzerGewechselt)# type: ignore
            benutzernamen = self.configIni["Benutzer"]["namen"].split("::")
            benutzerkuerzel = self.configIni["Benutzer"]["kuerzel"].split("::")
            for i in range(len(benutzernamen)):
                self.dokuvonComboBox.addItem(benutzernamen[i] + " (" + benutzerkuerzel[i] + ")")
            datenLayoutG.addWidget(labelName, 0, 0)
            datenLayoutG.addWidget(labelNameGdt, 0, 1)
            datenLayoutG.addWidget(labelPatId, 1, 0)
            datenLayoutG.addWidget(labelPatIdGdt, 1, 1)
            datenLayoutG.addWidget(labelUntDat, 2, 0)
            datenLayoutG.addWidget(self.untdatEdit, 2, 1)
            datenLayoutG.addWidget(labelDokuVon, 3, 0)
            datenLayoutG.addWidget(self.dokuvonComboBox, 3, 1)
            pushbuttonDatenSenden = QPushButton("Daten senden")
            pushbuttonDatenSenden.setFixedSize(QSize(160, 80))
            if self.patId == "-":
                pushbuttonDatenSenden.setEnabled(False)
                pushbuttonDatenSenden.setToolTip("Senden nicht möglich, da keine GDT-Datei vom PVS geladen")
            pushbuttonDatenSenden.clicked.connect(self.datenSendenClicked) # type: ignore
            datenLayoutH.addLayout(datenLayoutG)
            datenLayoutH.addSpacing(20)
            datenLayoutH.addWidget(pushbuttonDatenSenden)
            testLayout.addLayout(datenLayoutH, 5, 2)
            mainLayout.addLayout(kopfLayout)
            mainLayout.addLayout(testLayout)
            widget.setLayout(mainLayout)

            self.setCentralWidget(widget)

            # Gegebenenfalls vorheriges Untersuchungsergebnis verwenden
            if self.vorherigeDokuLaden:
                self.mitVorherigerUntersuchungAusfuellen()

            # Menü
            menu = self.menuBar()
            einstellungenMenu = menu.addMenu("Einstellungen")
            einstellungenAllgemeinAction = QAction("Allgemeine Einstellungen", self)
            einstellungenAllgemeinAction.triggered.connect(self.einstellungenAllgemein) # type: ignore
            einstellungenAllgemeinAction.setShortcut(QKeySequence("Ctrl+E"))
            einstellungenGdtAction = QAction("GDT-Einstellungen", self)
            einstellungenGdtAction.triggered.connect(self.einstellungenGdt) # type: ignore
            einstellungenGdtAction.setShortcut(QKeySequence("Ctrl+G"))
            einstellungenBenutzerAction = QAction("Benutzer verwalten", self)
            einstellungenBenutzerAction.triggered.connect(self.einstellungenBenutzer) # type: ignore
            einstellungenBenutzerAction.setShortcut(QKeySequence("Ctrl+B"))
            einstellungenMenu.addAction(einstellungenAllgemeinAction)
            einstellungenMenu.addAction(einstellungenGdtAction)
            einstellungenMenu.addAction(einstellungenBenutzerAction)
        else:
            sys.exit()

    def mitVorherigerUntersuchungAusfuellen(self):
        pfad = self.dokuVerzeichnis + "/" + self.patId
        doku = ""
        if os.path.exists(pfad) and len(os.listdir(pfad)) > 0:
            dokus = [d for d in os.listdir(pfad) if os.path.isfile(pfad + "/" + d)]
            dokus.sort()
            try:
                with open(pfad + "/" + dokus[len(dokus) - 1], "r") as d:
                    doku = d.read()
            except IOError as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "Fehler beim Lesen der vorherigen Dokumentation\n" + str(e), QMessageBox.StandardButton.Ok)
                mb.exec()
        if doku != "":
            # Untersuchungsdatum
            untdat = self.dokuZusammenfassungLesen(doku)[0]
            self.changeStatus(1, untdat.toString("dd.MM.yyyy"))
            self.buttonAlteUntersuchung.setEnabled(True)
            self.buttonAlteUntersuchung.setToolTip("Vorheriges Untersuchungsergebnis wiederherstellen")
            # Barthel ausfüllen
            barthelGesamt = self.dokuZusammenfassungLesen(doku)[1]
            self.radiobuttonBarhelEssen[int(barthelGesamt[0] / 5)].setChecked(True)
            self.radiobuttonBarhelBaden[int(barthelGesamt[1] / 5)].setChecked(True)
            self.radiobuttonBarhelKoerperpflege[int(barthelGesamt[2] / 5)].setChecked(True)
            self.radiobuttonBarhelAnAuskleiden[int(barthelGesamt[3] / 5)].setChecked(True)
            self.radiobuttonBarhelStuhlkontrolle[int(barthelGesamt[4] / 5)].setChecked(True)
            self.radiobuttonBarhelUrinkontrolle[int(barthelGesamt[5] / 5)].setChecked(True)
            self.radiobuttonBarhelToilettenbenutzung[int(barthelGesamt[6] / 5)].setChecked(True)
            self.radiobuttonBarhelBettRollstuhltransfer[int(barthelGesamt[7] / 5)].setChecked(True)
            self.radiobuttonBarhelMobilitaet[int(barthelGesamt[8] / 5)].setChecked(True)
            self.radiobuttonBarhelTreppensteigen[int(barthelGesamt[9] / 5)].setChecked(True)
            # Rest ausfüllen
            tug = int(self.dokuZusammenfassungLesen(doku)[2])
            pg = int(self.dokuZusammenfassungLesen(doku)[3])
            kf = int(self.dokuZusammenfassungLesen(doku)[4])
            if pg == 0:
                pg = 5
            elif pg == 5:
                pg = 6
            else:
                pg -= 1
            self.radiobuttonTimedUpGo[tug].setChecked(True)
            self.radiobuttonPflegegrad[pg].setChecked(True)
            self.radiobuttonKognitiveFunktion[kf].setChecked(True)
        else:
            self.changeStatus(1, "-")
            self.buttonAlteUntersuchung.setEnabled(False)
            self.buttonAlteUntersuchung.setToolTip("Funktion nicht verfügbar")


    def vorherigeUntersuchungWiederherstellen(self):
        if self.vorherigeDokuLaden:
            self.mitVorherigerUntersuchungAusfuellen()

    def datumGeaendert(self, datum):
        gewaehltesDatum = QDate(datum)
        if gewaehltesDatum.daysTo(QDate().currentDate()) < 0:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "Das Untersuchungsdatum darf nicht in der Zukunft liegen.", QMessageBox.StandardButton.Ok)
            mb.exec()

    def benutzerGewechselt(self):
        self.aktuelleBenuztzernummer = self.dokuvonComboBox.currentIndex()

    def einstellungenAllgemein(self):
        de = dialogEinstellungenAllgemein.EinstellungenAllgemein(self.configPath)
        if de.exec() == 1:
            if de.checkboxVorherigeDokuLaden.isChecked():
                self.configIni["Allgemein"]["vorherigedokuladen"] = "1"
            else:
                self.configIni["Allgemein"]["vorherigedokuladen"] = "0"
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis", "Damit die Änderungen der GDT-Einstellungen wirksam werden, sollte GeriGDT beendet werden.\nSoll GeriGDT jetzt beendet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    app.quit()

    def einstellungenGdt(self):
        de = dialogEinstellungenGdt.EinstellungenGdt(self.configPath)
        if de.exec() == 1:
            self.configIni["GDT"]["idgerigdt"] = de.lineEditGeriGdtId.text()
            self.configIni["GDT"]["idpraxisedv"] = de.lineEditPraxisEdvId.text()
            self.configIni["Verzeichnisse"]["gdtimport"] = de.lineEditImport.text()
            self.configIni["Verzeichnisse"]["gdtexport"] = de.lineEditExport.text()
            self.configIni["GDT"]["kuerzelgerigdt"] = de.lineEditGeriGdtKuerzel.text()
            self.configIni["GDT"]["kuerzelpraxisedv"] = de.lineEditPraxisEdvKuerzel.text()
            self.configIni["GDT"]["zeichensatz"] = str(de.aktuelleZeichensatznummer + 1)
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis", "Damit die Änderungen der GDT-Einstellungen wirksam werden, sollte GeriGDT beendet werden.\nSoll GeriGDT jetzt beendet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    app.quit()

    def einstellungenBenutzer(self):
        de = dialogEinstellungenBenutzer.EinstellungenBenutzer(self.configPath)
        if de.exec() == 1:
            namen = []
            kuerzel = []
            for i in range(5):
                if de.lineEditNamen[i].text() != "":
                    namen.append(de.lineEditNamen[i].text())
                    kuerzel.append(de.lineEditKuerzel[i].text())
            self.configIni["Benutzer"]["namen"] = "::".join(namen)
            self.configIni["Benutzer"]["kuerzel"] = "::".join(kuerzel)
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis", "Damit die Änderungen in der Benutzerverwaltung wirksam werden, sollte GeriGDT beendet werden.\nSoll GeriGDT jetzt beendet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    app.quit()

    def datenSendenClicked(self):
        # Barthel berechnen
        barthelTests = [self.radiobuttonBarhelEssen, self.radiobuttonBarhelBaden, self.radiobuttonBarhelKoerperpflege, self.radiobuttonBarhelAnAuskleiden, self.radiobuttonBarhelStuhlkontrolle, self.radiobuttonBarhelUrinkontrolle, self.radiobuttonBarhelToilettenbenutzung, self.radiobuttonBarhelBettRollstuhltransfer, self.radiobuttonBarhelMobilitaet, self.radiobuttonBarhelTreppensteigen]
        barthelEinzel = []
        barthelGesamt = 0
        for barthelTest in barthelTests:
            zaehler = 0
            for punkt in barthelTest:
                if punkt.isChecked():
                    barthelGesamt += zaehler * 5
                    barthelEinzel.append(zaehler * 5)
                zaehler += 1

        # GDT-Datei erzeugen
        sh = gdt.SatzHeader(gdt.Satzart.DATEN_EINER_UNTERSUCHUNG_UEBERMITTELN_6310, self.configIni["GDT"]["idpraxisedv"], self.configIni["GDT"]["idgerigdt"], self.zeichensatz, "2.10", "Fabian Treusch - GDT-Tools", "GeriGDT", "1.0.0", self.patId)
        gd = gdt.GdtDatei()
        gd.erzeugeGdtDatei(sh.getSatzheader())
        self.datum = "{:>02}".format(str(self.untdatEdit.date().day())) + "{:>02}".format(str(self.untdatEdit.date().month())) + str(self.untdatEdit.date().year())
        jetzt = QTime().currentTime()
        uhrzeit = "{:>02}".format(str(jetzt.hour())) + "{:>02}".format(str(jetzt.minute())) + str(jetzt.second())
        gd.addZeile("6200", self.datum)
        gd.addZeile("6201", uhrzeit)
        gd.addZeile("8402", "ALLG00")
        # Barthel
        testBarthelEssen = gdt.GdtTest("ESSEN", "Essen", str(barthelEinzel[0]), "von 10 Punkten")
        gd.addTest(testBarthelEssen)
        testBarthelBaden = gdt.GdtTest("BADEN", "Baden", str(barthelEinzel[1]), "von 5 Punkten")
        gd.addTest(testBarthelBaden)
        testBarthelKoerperpflege = gdt.GdtTest("KOERPERPFLEGE", "Körperpflege (Rasieren, Zähneputzen)", str(barthelEinzel[2]), "von 5 Punkten")
        gd.addTest(testBarthelKoerperpflege)
        testBarthelAnAuskleiden = gdt.GdtTest("ANAUSKLEIDEN", "An- und Auskleiden", str(barthelEinzel[3]), "von 10 Punkten")
        gd.addTest(testBarthelAnAuskleiden)
        testBarthelStuhlkontrolle = gdt.GdtTest("STUHLKONTROLLE", "Stuhlkontrolle", str(barthelEinzel[4]), "von 10 Punkten")
        gd.addTest(testBarthelStuhlkontrolle)
        testBarthelUrinkontrolle = gdt.GdtTest("URINKONTROLLE", "Urinkontrolle", str(barthelEinzel[5]), "von 10 Punkten")
        gd.addTest(testBarthelUrinkontrolle)
        testBarthelToilettenbenutzung = gdt.GdtTest("TOILETTENBENUTZUNG", "Toilettenbenutzung", str(barthelEinzel[6]), "von 10 Punkten")
        gd.addTest(testBarthelToilettenbenutzung)
        testBarthelBettRolstuhlTransfer = gdt.GdtTest("BETTROLLSTUHLTRANSFER", "Bett-/ (Roll)-Stuhltransfer", str(barthelEinzel[7]), "von 15 Punkten")
        gd.addTest(testBarthelBettRolstuhlTransfer)
        testBarthelMobilitaet = gdt.GdtTest("MOBILITAET", "Mobilität", str(barthelEinzel[8]), "von 15 Punkten")
        gd.addTest(testBarthelMobilitaet)
        testBarthelTreppensteigen = gdt.GdtTest("TREPPENSTEIGEN", "Treppensteigen", str(barthelEinzel[9]), "von 10 Punkten")
        gd.addTest(testBarthelTreppensteigen)
        # Timed Up and Go
        tugErgebnis = ""
        tugErgebnisInt = 0
        for rb in self.radiobuttonTimedUpGo:
            if rb.isChecked():
                tugErgebnis = rb.text()
                break
            else:
                tugErgebnisInt += 1
        testTimedUpGo = gdt.GdtTest("TIMEDUPGO", "Times \"Up and Go\"", tugErgebnis, "")
        gd.addTest(testTimedUpGo)
        # Kognitive Funktion
        kfErgebnis = ""
        kfErgebnisInt = 0
        for rb in self.radiobuttonKognitiveFunktion:
            if rb.isChecked():
                kfErgebnis = rb.text()
                break
            else:
                kfErgebnisInt += 1
        testKognitiveFunktion = gdt.GdtTest("KOGNITIVEFUNKTION", "Kognitive Funktion", kfErgebnis, "")
        gd.addTest(testKognitiveFunktion)
        # Pflegegrad
        pgErgebnis = ""
        pgErgebnisInt = 0
        for rb in self.radiobuttonPflegegrad:
            if rb.isChecked():
                pgErgebnis = rb.text()
                break
            else:
                pgErgebnisInt += 1
        testPflegegrad = gdt.GdtTest("PFLEGEGRAD", "Pflegegrad", pgErgebnis, "")
        gd.addTest(testPflegegrad)
        # Benutzer
        ak = self.aktuelleBenuztzernummer
        gd.addZeile("6227", "Dokumentiert von " + self.benutzerkuerzel[int(self.aktuelleBenuztzernummer)])
        # Befund
        gd.addZeile("6220", "Barthel-Index: " + str(barthelGesamt) + " Punkte")
        gd.addZeile("6221", "Timed \"Up and Go\": " + str(tugErgebnis))
        gd.addZeile("6221", "Kognitive Funktion: " + str(kfErgebnis))
        gd.addZeile("6221", "Pflegegrad: " + str(pgErgebnis))
                    
        # GDT-Datei exportieren
        if not gd.speichern(self.gdtExportVerzeichnis + "/T2MDGERI.gdt", self.zeichensatz):
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "GDT-Export nicht möglich.\nBitte überprüfen Sie die Angabe des Exportverzeichnisses.", QMessageBox.StandardButton.Ok)
            mb.exec()
        else:
            dokuZusammenfassung = self.dokuZusammenfassen(barthelEinzel, tugErgebnisInt, kfErgebnisInt, pgErgebnisInt)
            if self.dokuVerzeichnis != "":
                if os.path.exists(self.dokuVerzeichnis):
                    speicherdatum = str(self.untdatEdit.date().year()) + "{:>02}".format(str(self.untdatEdit.date().month())) + "{:>02}".format(str(self.untdatEdit.date().day()))
                    try:
                        if not os.path.exists(self.dokuVerzeichnis + "/" + self.patId):
                            os.mkdir(self.dokuVerzeichnis + "/" + self.patId, 0o777)
                        with open(self.dokuVerzeichnis + "/" + self.patId + "/" + speicherdatum + "_" + self.patId + ".gba", "w") as zf:
                            zf.write(dokuZusammenfassung)
                    except IOError as e:
                        mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "Fehler beim Speichern der Dokumentation\n" + str(e), QMessageBox.StandardButton.Ok)
                        mb.exec()
                    except:
                        raise
                else:
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis", "Speichern der Dokumentation nicht möglich\nBitte überprüfen Sie die Angabe des Dokumentations-Speicherverzeichnisses.", QMessageBox.StandardButton.Ok)
                    mb.exec()

        app.quit()

    def dokuZusammenfassen(self, barthel:list, timedUpGo:int, kognitiveFunktion:int, pflegegrad:int):
        #Untersuchungsdatum TTMMJJJJ + 10x Barthel hexadezimal + TUG 0-3 + PG 0-6 (unbekannt = 0) + KF 0-2
        zusammenfassung = self.datum
        for b in barthel:
            punkte = int(b)
            punkteHex = hex(punkte).upper()
            zusammenfassung += punkteHex[2]
        pflegegrad += 1
        if pflegegrad == 6:
            pflegegrad = 0
        elif pflegegrad == 7:
            pflegegrad = 6
        zusammenfassung += str(timedUpGo) + str(pflegegrad) + str(kognitiveFunktion)
        return zusammenfassung
    
    def dokuZusammenfassungLesen(self, zusammenfassung:str):
        jahr = int(zusammenfassung[4:8])
        monat = int(zusammenfassung[2:4])
        tag = int(zusammenfassung[0:2])
        datum = QDate(jahr, monat, tag)
        barthelGesamt = []
        for bt in zusammenfassung[8:18]:
            barthelGesamt.append(int(bt, 16))
        tug = zusammenfassung[18]
        pg = zusammenfassung[19]
        kf = zusammenfassung[20]
        return (datum, barthelGesamt, tug, pg, kf)
    
app = QApplication(sys.argv)
qt = QTranslator()
filename = "qtbase_de"
directory = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
qt.load(filename, directory)
app.installTranslator(qt)
app.setWindowIcon(QIcon(os.path.join(basedir, "icons/program.png")))
window = MainWindow()
window.show()

app.exec()