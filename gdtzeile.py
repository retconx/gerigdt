import re
reZeilenlaenge = r"^\d{3}$"
reFeldkennung = r"^\d{4}$"
reGdtZeile = r"^\d{7}.*\r\n$"

class GdtFehlerException(Exception):
    def __init__(self, meldung):
        self.Meldung = meldung
    def __str__(self):
        return "GDT-Fehler: " + self.Meldung

def istGdtZeile(zeile:str, laengenpruefung = False):
    """Prüft, ob es sich um eine gültige GDT-Zeile handelt."""
    if re.match(reGdtZeile, zeile):
        laenge = int(zeile[0:3])
        inhalt = zeile[7:len(zeile) - 2]
        if laengenpruefung and laenge != (3 + 4 + len(inhalt)+ 2):
            raise GdtFehlerException("Zeilenlänge falsch: " + str(laenge) + " statt " + str(3 + 4 + len(inhalt) + 2))
        else:
            return True
    elif not re.match(reZeilenlaenge, zeile[0:3]):
        raise GdtFehlerException("Zeilenlängenformat falsch: " + zeile[0:3])
    elif not re.match(reFeldkennung, zeile[3:7]):
        raise GdtFehlerException("Ungültige Feldkennung: " + zeile[3:7])
    elif str(zeile)[len(zeile) - 3:len(zeile)] != "\r\n":
        raise GdtFehlerException("Kein CRLF am Ende der Zeile: " + zeile)    
    else:
        raise GdtFehlerException("Ungültiges Zeilenformat: " + zeile)

def erzeugeZeile(feldkennung, inhalt):
    """Erzeugt eine GDT-Zeile und gibt diese zurück."""
    if not re.match(reFeldkennung, feldkennung):
        raise GdtFehlerException("Feldkennung ungültig: " + feldkennung)
    else:
        laengeString = 3 + 4 + len(inhalt) + 2
        return "{laenge:>03}".format(laenge = laengeString) + feldkennung + inhalt + "\r\n"

def getFeldkennung(zeile: str):
    """Gibt die Feldkennung einer GDT-Zeile zurück."""
    try:
        if (istGdtZeile(zeile)):
            return zeile[3:7]
    except GdtFehlerException:
        raise

def getInhalt(zeile: str):
    """Gibt den Inhalt einer GDT-Zeile zurück."""
    try:
        if (istGdtZeile(zeile)):
            return zeile[7:len(zeile) - 2]
    except GdtFehlerException:
        raise

def getZeileMitneuemInhalt(zeile, inhalt):
    """Ändert den Inhalt einer GDT-Zeile und gibt diese zürück."""
    try:
        if (istGdtZeile(zeile)):
            return erzeugeZeile(zeile[3:7], inhalt)
    except GdtFehlerException:
        raise