from pathlib import Path
import os
import tkinter as tk
from tkinter import font
from tkinter import messagebox

import line_parser
import xml_writer

EXAMPLE_NAME = '3 x 3 x 2 Min PFPI'
EXAMPLE_DESCRIPTION = '3 x 3 x 2 Min PFPI\n"FTP" = 1,15 x FTP'
EXAMPLE_TEXT = '10 minuten 25 -70%\n 1 min 90% \n 5 m 0.6 \n3x (\n3x ( 10 Sekunden 200%\n 1:50 100%\n 2:00 0.4)\n 6 Min 40%)\n2 Minuten 40-20%'


class GUI:
    def __init__(self):
        wdir = Path.home() / 'Documents' / 'Zwift' / 'Workouts'
        self.workout_path = next(wdir.iterdir())

        self.data_path = Path('./data/')
        self.data_path.mkdir(exist_ok=True)

        self.author_file = self.data_path / 'author.txt'
        if self.author_file.exists():
            with open(self.author_file, 'r') as f:
                self.author = f.readline()
        else:
            self.author = ''

        self.bg = "#EDEEF3"
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.screen_resolution = [self.screenwidth, self.screenheight]
        self.hdfactor = self.screenheight / 1080.
        self.default_size = int(round(15 * self.hdfactor))
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=self.default_size)
        self.bold_font = self.default_font.copy()
        self.bold_font.configure(weight="bold")
        try:
            self.root.iconbitmap("favicon.ico")
        except:
            pass
        self.root.title('Zwift Workout erstellen')
        self.root.configure(bg=self.bg)

        tk.Label(self.root, text='Autor', bg=self.bg, font=self.default_font).grid(row=0, column=0, padx=int(self.default_size/2))
        self.author_entry = tk.Entry(self.root, bg=self.bg, font=self.default_font, width=30)
        self.author_entry.grid(row=1, column=0, padx=int(self.default_size/2))
        self.author_entry.insert(0, self.author)
        tk.Label(self.root, text='Name', bg=self.bg, font=self.default_font).grid(row=2, column=0, padx=int(self.default_size/2))
        self.name_entry = tk.Entry(self.root, bg=self.bg, font=self.default_font, width=30)
        self.name_entry.grid(row=3, column=0, padx=int(self.default_size/2))
        tk.Label(self.root, text='Beschreibung', bg=self.bg, font=self.default_font).grid(row=4, column=0, padx=int(self.default_size/2))
        self.description_entry = tk.Text(self.root, bg=self.bg, font=self.default_font, height=4, width=30)
        self.description_entry.grid(row=5, column=0, padx=int(self.default_size/2))

        self.button_frame = tk.Frame(self.root, bg=self.bg)
        self.button_frame.grid(row=6, column=0, padx=int(self.default_size/2), pady=self.default_size)
        tk.Button(self.button_frame, text='Umwandeln', bg=self.bg, font=self.bold_font, command=self.generate_workout).grid(row=0, column=0, padx=int(self.default_size/2), pady=self.default_size)
        tk.Button(self.button_frame, text='Speichern', bg=self.bg, font=self.bold_font, command=self.save_workout_files).grid(row=0, column=1, padx=int(self.default_size / 2), pady=self.default_size)
        tk.Button(self.button_frame, text='Beispiel laden', bg=self.bg, font=self.default_font, command=self.load_example).grid(row=1, column=0, columnspan=2, padx=int(self.default_size / 2),
                                                                                                                                pady=int(self.default_size / 2))
        tk.Button(self.button_frame, text='Workouts', bg=self.bg, font=self.default_font, command=self.open_workouts).grid(row=2, column=0, padx=int(self.default_size / 2),
                                                                                                                           pady=int(self.default_size / 2))
        tk.Button(self.button_frame, text='Daten', bg=self.bg, font=self.default_font, command=self.open_data).grid(row=2, column=1, padx=int(self.default_size/2), pady=int(self.default_size / 2))

        self.duration_label = tk.Label(self.button_frame, text='', bg=self.bg, font=self.bold_font)
        self.duration_label.grid(row=3, column=0, columnspan=2, padx=int(self.default_size/2), pady=int(self.default_size / 2))

        self.text = tk.Text(self.root, bg=self.bg, font=self.default_font, height=20, width=30)
        self.text.grid(row=0, column=1, rowspan=20, padx=int(self.default_size/2), pady=self.default_size)

        self.xml_data = None
        self.filename = ''
        self.workout_lines_raw = ''

        tk.mainloop()

    def generate_workout(self):
        new_author = self.author_entry.get()
        if new_author != self.author:
            self.author = new_author
            with open(self.author_file, 'w') as f:
                f.write(self.author)

        name = self.name_entry.get()
        if len(name) == 0:
            messagebox.showerror(title='Fehler', message='Kein Name eingegeben')
            return
        self.filename = name.replace(" ", "_")

        description = self.description_entry.get(1.0, 'end-1c')

        self.workout_lines_raw = self.text.get(1.0, 'end-1c')
        if len(self.workout_lines_raw) <= 1:
            messagebox.showerror(title='Fehler', message='Kein Workout eingegeben')
            return
        workout_lines = self.workout_lines_raw.splitlines()

        try:
            parsed_lines = line_parser.parse_lines(workout_lines)
        except SyntaxError as e:
            # print('Syntax error in line {}: {}'.format(e.lineno, e.text))
            error_start = self.workout_lines_raw.find(e.text)
            error_end = error_start + len(e.text)
            self.text.tag_add('sel', '1.0+{}c'.format(error_start), '1.0+{}c'.format(error_end))
            self.text.mark_set('insert', '1.0+{}c'.format(error_start))
            # self.text.see('insert')
            self.text.focus_set()
            messagebox.showerror(title='Syntax Error', message='Syntax error in line {}: {}'.format(e.lineno, e.text))
            return
        self.xml_data, workout_duration = xml_writer.to_xml(parsed_lines, author=self.author, workout_name=name, workout_description=description)
        hours = 0
        minutes = int(workout_duration/60)
        seconds = int(workout_duration - minutes*60)
        if minutes >= 60:
            hours = int(minutes/60)
            minutes = int(minutes - hours*60)
        self.duration_label['text'] = 'Workout duration: {:d}:{:d}:{:d}'.format(hours, minutes, seconds)
        # print('Workout duration: {}:{}'.format(minutes, seconds))


    def save_workout_files(self):
        if self.xml_data is None:
            messagebox.showerror(title='Fehler', message='Zuerst "Umwandeln"!')
        else:
            write_path = self.workout_path / (self.filename + '.zwo')
            xml_writer.xml_to_file(self.xml_data, write_path)

            write_path_data = self.data_path / (self.filename + '.txt')
            with open(write_path_data, 'w') as f:
                f.write(self.workout_lines_raw)

            self.xml_data = None

            messagebox.showinfo(title='Speichern erfolgreich', message='Speichern war erfolgreich')

    def open_workouts(self):
        os.startfile(self.workout_path)

    def open_data(self):
        os.startfile(self.data_path)

    def load_example(self):
        self.text.delete(1.0, "end")
        self.text.insert(1.0, EXAMPLE_TEXT)
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, EXAMPLE_NAME)
        self.description_entry.delete(1.0, "end")
        self.description_entry.insert(1.0, EXAMPLE_DESCRIPTION)


if __name__ == '__main__':
    gui = GUI()
