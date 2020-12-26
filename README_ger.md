[README in English](https://github.com/RichardGoerler/ZwiftWorkouts/blob/master/README.md)

# ZwiftWorkouts

#### Ein Programm zum Erstellen von Zwift-Workouts mit einem intuitiven, textbasierten Editor.

![main_window](https://beachomize.de/zwift_image/WindowGer1.JPG)

## Syntax

**Intervalle Zeile für Zeile aufschreiben** (max. ein Intervall pro Zeile).

Ein Intervall besteht aus
- einer Dauer (```1:30``` oder ```2 min``` oder ```10s```, etc.)
- einer Intensitätsangabe (```112%``` oder ```0.68```, etc.)

Falls das Intervall ein Aufwärmen- / Abkühlen-Intervall ist, kann es zwei Intensitätsangaben beinhalten, getrennt durch ein Minus oder einen Pfeil: z.B. ```25%-75%```.

Wiederholung von Intervallen, indem Klammern ```()``` oder ```[]``` oder ```{}``` darum geschrieben werden
 und ein Multiplikator ```3x``` oder ```4X``` oder ```5*```, etc. direkt vor die öffnende Klammer. 

Wiederholungen können verschachtelt sein, wie z.B. ```2x { 3x ( ... ) ... }``` (hier fehlen die notwendigen Zeilenumbrüche).

## Funktionen
**Konvertieren** des textbasierten Workouts in Zwift's xml-Format und Berechnen der Dauer des Workouts.

**Speichern** des Workouts in dem Ordner, wo Zwift es findet.

**Laden** eines zuvor erstellten Workouts, um es zu editieren oder zu kopieren.

## Installation
Auf Windows, einfach die [exe](https://github.com/RichardGoerler/ZwiftWorkouts/raw/main/dist/gui.exe) herunterladen und ausführen.

Auf anderen Betribssystemen muss das Repository heruntergeladen werden. *Python3* und die Bibliothek *lxml* müssen installiert sein. Dann kann *gui.py* ausgeführt werden.