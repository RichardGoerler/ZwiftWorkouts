[README auf Deutsch](https://github.com/RichardGoerler/ZwiftWorkouts/blob/master/README_ger.md)

# ZwiftWorkouts

#### A tool for creating Zwift Workouts featuring an an intuitive, text-based editor.

![main_window](https://beachomize.de/zwift_image/WindowEng1.JPG)

## Syntax

**Write down intervals line by line** (max. one interval per line).

An Interval consist of
- a time duration (```1:30``` or ```2 min``` or ```10s```, etc.)
- a power specification (```112%``` or ```0.68```, etc.)

If the interval is a warmup / cooldown interval, it can have two power specifications, separated by a hyphen or an arrow: ```25%-75%```, for instance.

Repeat intervals by putting brackets ```()``` or ```[]``` or ```{}``` around them and
 add a multiplyer ```3x``` or ```4X``` or ```5*```, etc. directly in front of the opening bracket.

Repeats can be nested, like ```2x { 3x ( ... ) ... }``` (here the required line breaks are omitted).

## Functions
**Convert** your text-based workout into Zwift's xml format and calculate duration of your workout.

**Save** your workout directly into the folder where Zwift will find it.

**Load** a previously created workout to edit or copy it.

## Installation
On Windows, just download the [exe](https://github.com/RichardGoerler/ZwiftWorkouts/raw/main/dist/gui.exe) and run it.

On other operating systems the repository must be downloaded. *Python3* and the library *lxml* need to be installed. Run *gui.py*.