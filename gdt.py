import gdtzeile
import csv
from enum import Enum

class GdtSatzarten():
    zeilen = []
    def __init__(self, pfadGdtSatzartenCsv:str):
        try:
            with open(pfadGdtSatzartenCsv, newline="") as csvfile:
                r = csv.reader(csvfile, delimiter=";")
                for zeile in r:
                    self.zeilen.append(zeile)
        except Exception:
            raise
    def getBedingung(self, satzart:str, feldkennung:str):
        """
        Gibt die Bedingung eines Feldes zurück
        Parameter:
            satzart: str
            feldkennung: str
        Return:
            M (Muss), K (Kann) oder None (Feldkennung unbekannt)
        """
        for zeile in self.zeilen:
            if zeile[0] == satzart:
                for x in zeile:
                    if x[0:4] == feldkennung:
                        return x[4]
        return None

class GdtZeichensatz(Enum):
    BIT_7 = 1
    IBM_CP437 = 2
    ANSI_CP1252 = 3

class Satzart(Enum):
    STAMMDATEN_ANFORDERN_6300 = "6300"
    STAMMDATEN_UEBERMITTELN_6301 = "6301"
    NEUE_UNTERSUCHUNG_ANFORDERN_6302 = "6302"
    DATEN_EINER_UNTERSUCHUNG_UEBERMITTELN_6310 = "6310"
    DATEN_EINER_UNTERSUCHUNG_ZEIGEN_6311 = "6311"

class SatzHeader:
    def __init__(self, satzart:Satzart, gdtIdEmpfaenger:str, gdtIdSender:str, zeichensatz:GdtZeichensatz, version:str, softwareVerantwortlicher:str, software:str, softwareReleasestand:str, patientennummer:str):
        self.satzheader = {
            "8000" : str(satzart.value),
            "8315" : gdtIdEmpfaenger,
            "8316" : gdtIdSender,
            "9206" : str(zeichensatz.value),
            "9218" : version,
            "0102" : softwareVerantwortlicher,
            "0103" : software,
            "0132" : softwareReleasestand,
            "3000" : patientennummer
        }

    def getSatzheader(self):
        return self.satzheader
    
class GdtTest:
    def __init__(self, testIdent:str, testBezeichnung:str, testErgebnis:str, testEinheit:str):
        self.test = {
        "8410_testIdent" : testIdent,
        "8411_testBezeichnung" : testBezeichnung,
        "8420_testErgebnis" : testErgebnis,
        "8421_testEinheit" : testEinheit,
        "8418_testStatus" : "",
        "8428_probenmaterialIdent" : "",
        "8429_probenmaterialIndex" : "",
        "8430_probenmaterialBezeichnung" : "",
        "8431_probenmaterialSpezifikation" : "",
        "8432_abnahmeDatum" : "",
        "8437_einheitFuerDatenstrom" : "",
        "8438_datenstrom" : "",
        "8439_abnahmeZeit" : "",
        "8460_normalwertText" : "",
        "8461_normalwertUntereGrenze" : "",
        "8462_normalwertObereGrenze" : "",
        "8470_testbezogeneHinweise" : "",
        "8480_ergebnisText" : ""
    }
    def addTestfeld(self, fk:str, inhalt:str):
        for testfeld in self.test:
            if fk in testfeld[0:4]:
                self.test[testfeld] = inhalt
                return True
        return False
    def getTest(self):
        return self.test
    
class GdtDatei: 
    # tests = []
    def __init__(self):
        self.gdtDatei=[]
    def erzeugeGdtDatei(self, satzheader:dict):
        """
        Erzeugt eine GDT-Zeilenliste
            Parameter:
                satzheader: dict
        """
        self.gdtDatei.clear()
        try:
            for feldkennung, inhalt in satzheader.items():
                self.gdtDatei.append(gdtzeile.erzeugeZeile(feldkennung, inhalt))
            laenge = 0
            for zeile in self.gdtDatei:
                laenge += len(zeile)
            laenge += 9 + 5
            self.gdtDatei.insert(1, gdtzeile.erzeugeZeile("8100", "{:>05}".format(str(laenge))))
        except gdtzeile.GdtFehlerException:
            raise
    def addZeile(self, feldkennung:str, inhalt:str):
        """Fügt eine GDT-Zeile hinzu"""
        self.gdtDatei.append(gdtzeile.erzeugeZeile(feldkennung, inhalt))
    def addTest(self, gdtTest:GdtTest):
        """
        Fügt einen GDT-Test hinzu
        Parameter:
            Test: GdtTest        
        """
        # self.tests.append(gdtTest)
        test = gdtTest.getTest()
        for testfeld in test:
            fk = ""
            if test[testfeld] != "":
                fk = testfeld[0:4]
                self.addZeile(fk, test[testfeld])
    def deleteTest(self, testIdent:str):
        """
        Löscht einen GDT-Test
        Parameter:
            testIdent
        Rückgabe:
            True oder False (falls Test-Ident nicht vorhanden)
        """
        #Test löschen
        # testIdentVorhanden = False
        # index = 0
        # for test in self.tests:
        #     if test.getTest()["8410_testIdent"] == testIdent:
        #         del self.tests[index]
        #         testIdentVorhanden = True
        #     else:
        #         index += 1
        # if testIdentVorhanden:
        #Test aus GDT-Datei entfernen
        index = 0
        while gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" or gdtzeile.getInhalt(self.gdtDatei[index]) != testIdent:
            index += 1
        if index < len(self.gdtDatei):
            del self.gdtDatei[index]
            while index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" and str(gdtzeile.getFeldkennung(self.gdtDatei[index]))[0:2] == "84":
                del self.gdtDatei[index]
            return True
        return False
    def changeTestIdent(self, testIdentAlt:str, testIdentNeu:str):
        """
        Ändert ein Testident
        Parameter:
            testIdentAlt:str
            testIdentNeu:str
        Rückgabe:
            True oder False, falls Testident nicht vorhanden
        """
        index = 0
        while gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" or gdtzeile.getInhalt(self.gdtDatei[index]) != testIdentAlt:
            index += 1
        if index < len(self.gdtDatei):
            self.gdtDatei[index] = gdtzeile.erzeugeZeile("8410", testIdentNeu)
            return True
        return False
    def changeTestBezeichnung(self, testIdent:str, testBezeichnungNeu:str):
        """
        Ändert eine Testbezeichnung
        Parameter:
            testIdent:str
            testBezeichnungNeu:str
        Rückgabe:
            True oder False, falls Testident nicht vorhanden
        """
        index = 0
        while gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" or gdtzeile.getInhalt(self.gdtDatei[index]) != testIdent:
            index += 1
        index += 1
        while index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8411":
            index += 1
        if index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) == "8411":
            self.gdtDatei[index] = gdtzeile.erzeugeZeile("8411", testBezeichnungNeu)
            return True
        return False
    def changeTestErgebnis(self, testIdent:str, testErgebnisNeu:str):
        """
        Ändert eines Testergebnisses
        Parameter:
            testIdent:str
            testErgebnisNeu:str
        Rückgabe:
            True oder False, falls Testident nicht vorhanden
        """
        index = 0
        while gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" or gdtzeile.getInhalt(self.gdtDatei[index]) != testIdent:
            index += 1
        index += 1
        while index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8420":
            index += 1
        if index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) == "8420":
            self.gdtDatei[index] = gdtzeile.erzeugeZeile("8420", testErgebnisNeu)
            return True
        return False
    def changeTestEinheit(self, testIdent:str, testEinheitNeu:str):
        """
        Ändert einer Testeinheit
        Parameter:
            testIdent:str
            testEinheitNeu:str
        Rückgabe:
            True oder False, falls Testident nicht vorhanden
        """
        index = 0
        while gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" or gdtzeile.getInhalt(self.gdtDatei[index]) != testIdent:
            index += 1
        index += 1
        while index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8410" and gdtzeile.getFeldkennung(self.gdtDatei[index]) != "8421":
            index += 1
        if index < len(self.gdtDatei) and gdtzeile.getFeldkennung(self.gdtDatei[index]) == "8421":
            self.gdtDatei[index] = gdtzeile.erzeugeZeile("8421", testEinheitNeu)
            return True
        return False    
    def getInhalt(self, feldkennung:str):
        """
        Gibt den Inhalt des ersten Auftretens einer Feldkennung zurück
        Parameter:
            feldkennung: str
        Return:
            Inhalt: str oder None (falls Feldkennung nicht vorhanden)
        """
        for zeile in self.gdtDatei:
            if gdtzeile.getFeldkennung(zeile) == feldkennung:
                return gdtzeile.getInhalt(zeile)
        return None
    def getAlleInhalte(self, feldkennung:str):
        """
        Gibt eine Liste aller Inhalte einer Feldkennung zurück
        Parameter:
            feldkennung:str
        Return:
            Liste aller gefundenen Inhalte: list
        """
        inhaltsliste = []
        for zeile in self.gdtDatei:
            if gdtzeile.getFeldkennung(zeile) == feldkennung:
                inhaltsliste.append(gdtzeile.getInhalt(zeile))
        return inhaltsliste
    def getSatzart(self):
        """
        Gibt die Satzart zurück
        Return:
            Satzart oder None, falls nicht definiert
        """
        satzart = self.getInhalt("8000")
        if satzart in Satzart._value2member_map_:
            return Satzart(satzart)
        return None
    def speichern(self, pfad:str, zeichensatz:GdtZeichensatz):
        """
        Speichert die GDT-Datei
            Return: True bei Erfolg, False bei Misserfolg
        """
        if zeichensatz == GdtZeichensatz.BIT_7:
            enc = "utf_7"
        elif zeichensatz == GdtZeichensatz.IBM_CP437:
            enc = "cp437"
        else:
            enc = "cp1252"

        try:
            with open(pfad, "w", encoding=enc) as fobj:
                for zeile in self.gdtDatei:
                    fobj.write(zeile)
            return True
        except:
            return False
    def laden(self, pfad:str, zeichensatz:GdtZeichensatz, senderId = None):
        """
        Lädt eine GDT-Datei
        Parameter:
            pfad:str
            zeichensatz:GdtZeichensatz
            senderId:str (Optional)
        Exception:
            IOError bei Ladefehler
        Exception:
            GdtFehlerException, wenn keine gültige GDT-Datei
        Exception:
            GdtFehlerException, wenn senderId nicht übereinstimmt
        """
        self.gdtDatei.clear()
        if zeichensatz == GdtZeichensatz.BIT_7:
            enc = "utf_7"
        elif zeichensatz == GdtZeichensatz.IBM_CP437:
            enc = "cp437"
        else:
            enc = "cp1252"

        try:
            with open(pfad, "r", encoding=enc) as fobj:
                for zeile in fobj:
                    self.gdtDatei.append(zeile.strip() + "\r\n")
            if not self.getSatzart():
                raise gdtzeile.GdtFehlerException("Keine gültige GDT-Datei")
            elif senderId and self.getInhalt("8316") != senderId:
                raise gdtzeile.GdtFehlerException("Sender-ID ungültig")
        except IOError:
            raise
