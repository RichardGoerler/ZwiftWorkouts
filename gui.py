from pathlib import Path
import os
import sys
import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter import filedialog

import line_parser
import xml_writer
import lang_ger
import lang_eng

EXAMPLE_NAME = ['3 x 3 x 2 Min PFPI', '3 x 3 x 2 min PFPI']
EXAMPLE_DESCRIPTION = ['3 x 3 x 2 Min PFPI\n"FTP" = 1,15 x FTP', '3 x 3 x 2 min PFPI\n"FTP" = 1,15 x FTP']
EXAMPLE_TEXT = ['10 minuten 25 -70%\n 1 min 90% \n 5 m 0.6 \n3x (\n3x ( 10 Sekunden 200%\n 1:50 100%\n 2:00 0.4)\n 6 Min 40%)\n2 Minuten 40-20%',
                '10 minutes 25 -70%\n 1 min 90% \n 5 m 0.6 \n3x (\n3x ( 10 seconds 200%\n 1:50 100%\n 2:00 0.4)\n 6 Min 40%)\n2 Minutes 40-20%']

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(".")

    return base_path / relative_path

class GUI:
    def __init__(self):
        wdir = Path.home() / 'Documents' / 'Zwift' / 'Workouts'
        self.workout_path = next(wdir.iterdir())

        self.data_path = Path('./data/')
        self.data_path.mkdir(exist_ok=True)

        self.author_file = self.data_path / '.author'
        if self.author_file.exists():
            with open(self.author_file, 'r') as f:
                self.author = f.readline()
        else:
            self.author = ''

        self.duration_hours = 0
        self.duration_minutes = 0
        self.duration_seconds = 0

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

        self.lang = lang_ger
        self.languages = [lang_ger, lang_eng]
        self.lang_index = 0
        sub_factor = int(500 / (2*self.default_size))
        ger_flag = tk.PhotoImage(file=resource_path('img/ger_flag.png')).subsample(sub_factor, sub_factor)
        eng_flag = tk.PhotoImage(file=resource_path('img/eng_flag.png')).subsample(sub_factor, sub_factor)
        self.lang_flags = [ger_flag, eng_flag]

        self.open_icon = tk.PhotoImage(file=resource_path('img/open.png')).subsample(sub_factor, sub_factor)

        self.root.title(self.lang.ROOT_TITLE)
        self.root.configure(bg=self.bg)

        self.widgets_with_text = []
        self.widget_texts = []

        self.widgets_with_text.append(tk.Label(self.root, text=self.lang.LABEL_AUTHOR, bg=self.bg, font=self.default_font))
        self.widget_texts.append('self.lang.LABEL_AUTHOR')
        self.widgets_with_text[-1].grid(row=0, column=0, padx=int(self.default_size/2))
        self.author_entry = tk.Entry(self.root, bg=self.bg, font=self.default_font, width=30)
        self.author_entry.grid(row=1, column=0, padx=int(self.default_size/2))
        self.author_entry.insert(0, self.author)
        self.widgets_with_text.append(tk.Label(self.root, text=self.lang.LABEL_NAME, bg=self.bg, font=self.default_font))
        self.widget_texts.append('self.lang.LABEL_NAME')
        self.widgets_with_text[-1].grid(row=2, column=0, padx=int(self.default_size / 2))
        self.name_entry = tk.Entry(self.root, bg=self.bg, font=self.default_font, width=30)
        self.name_entry.grid(row=3, column=0, padx=int(self.default_size/2))
        self.widgets_with_text.append(tk.Label(self.root, text=self.lang.LABEL_DESCRIPTION, bg=self.bg, font=self.default_font))
        self.widget_texts.append('self.lang.LABEL_DESCRIPTION')
        self.widgets_with_text[-1].grid(row=4, column=0, padx=int(self.default_size/2))
        self.description_entry = tk.Text(self.root, bg=self.bg, font=self.default_font, height=4, width=30)
        self.description_entry.grid(row=5, column=0, padx=int(self.default_size/2))

        self.button_frame = tk.Frame(self.root, bg=self.bg)
        self.button_frame.grid(row=6, column=0, padx=int(self.default_size/2), pady=self.default_size)
        self.widgets_with_text.append(tk.Button(self.button_frame, text=self.lang.BUTTON_CONVERT, bg=self.bg, font=self.bold_font, command=self.generate_workout))
        self.widget_texts.append('self.lang.BUTTON_CONVERT')
        self.widgets_with_text[-1].grid(row=0, column=0, padx=int(self.default_size/2), pady=self.default_size)
        self.widgets_with_text.append(tk.Button(self.button_frame, text=self.lang.BUTTON_SAVE, bg=self.bg, font=self.bold_font, command=self.save_workout_files))
        self.widget_texts.append('self.lang.BUTTON_SAVE')
        self.widgets_with_text[-1].grid(row=0, column=1, padx=int(self.default_size / 2), pady=self.default_size)
        tk.Button(self.button_frame, text='', bg=self.bg, image=self.open_icon, font=self.default_font,
                  command=self.open_file).grid(row=0, column=2, padx=int(self.default_size / 2), pady=self.default_size, sticky=tk.E)
        self.widgets_with_text.append(tk.Button(self.button_frame, text=self.lang.BUTTON_EXAMPLE, bg=self.bg, font=self.default_font, command=self.load_example))
        self.widget_texts.append('self.lang.BUTTON_EXAMPLE')
        self.widgets_with_text[-1].grid(row=1, column=0, columnspan=2, padx=int(self.default_size / 2), pady=int(self.default_size / 2))
        self.widgets_with_text.append(tk.Button(self.button_frame, text=self.lang.BUTTON_WORKOUTS_FOLDER, bg=self.bg, font=self.default_font, command=self.open_workouts))
        self.widget_texts.append('self.lang.BUTTON_WORKOUTS_FOLDER')
        self.widgets_with_text[-1].grid(row=2, column=0, padx=int(self.default_size / 2), pady=int(self.default_size / 2))
        self.widgets_with_text.append(tk.Button(self.button_frame, text=self.lang.BUTTON_DATA_FOLDER, bg=self.bg, font=self.default_font, command=self.open_data))
        self.widget_texts.append('self.lang.BUTTON_DATA_FOLDER')
        self.widgets_with_text[-1].grid(row=2, column=1, padx=int(self.default_size/2), pady=int(self.default_size / 2))

        self.language_button = tk.Button(self.button_frame, text='', bg=self.bg, image=self.lang_flags[(self.lang_index + 1) % len(self.languages)], font=self.default_font,
                                         width=2*self.default_size, height=2*self.default_size, command=self.toggle_language)
        self.language_button.grid(row=2, column=2, padx=int(self.default_size / 2), pady=self.default_size, sticky=tk.E)

        self.duration_label = tk.Label(self.button_frame, text='', bg=self.bg, font=self.bold_font)
        self.duration_label.grid(row=3, column=0, columnspan=3, padx=int(self.default_size/2), pady=int(self.default_size / 2))

        self.text = tk.Text(self.root, bg=self.bg, font=self.default_font, height=20, width=30)
        self.text.grid(row=0, column=1, rowspan=20, padx=int(self.default_size/2), pady=self.default_size)

        self.xml_data = None
        self.filename = ''
        self.workout_lines_raw = ''

        tk.mainloop()

    def toggle_language(self):
        self.lang_index = (self.lang_index + 1) % len(self.languages)
        self.lang = self.languages[self.lang_index]
        for widget, eval_text in zip(self.widgets_with_text, self.widget_texts):
            widget['text'] = eval(eval_text)
        self.root.title(self.lang.ROOT_TITLE)
        if len(self.duration_label['text']) > 0:
            self.duration_label['text'] = self.lang.WORKOUT_DURATION_OUTPUT.format(self.duration_hours, self.duration_minutes, self.duration_seconds)

        self.language_button['image'] = self.lang_flags[(self.lang_index + 1) % len(self.languages)]

    def open_file(self):
        filename = filedialog.askopenfilename(initialdir=self.data_path, title=self.lang.FILE_DIALOG_TITLE, filetypes=(("txt files", "*.txt"), ))
        if not filename:
            return
        txt_path = Path(filename)
        zwo_path = self.workout_path / (txt_path.stem + '.zwo')
        try:
            name, description = xml_writer.get_name_and_description_from_xml(zwo_path)
        except OSError:
            name, description = '', ''
        with open(txt_path, 'r') as f:
            workout_text = f.read()
        self.text.delete(1.0, "end")
        self.text.insert(1.0, workout_text)
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, name)
        self.description_entry.delete(1.0, "end")
        self.description_entry.insert(1.0, description)

    def generate_workout(self):
        new_author = self.author_entry.get()
        if new_author != self.author:
            self.author = new_author
            with open(self.author_file, 'w') as f:
                f.write(self.author)

        name = self.name_entry.get()
        if len(name) == 0:
            messagebox.showerror(title=self.lang.ERROR_TITLE, message=self.lang.ERROR_NAME_EMPTY)
            return
        self.filename = name.replace(" ", "_")

        description = self.description_entry.get(1.0, 'end-1c')

        self.workout_lines_raw = self.text.get(1.0, 'end-1c')
        if len(self.workout_lines_raw) <= 1:
            messagebox.showerror(title=self.lang.ERROR_TITLE, message=self.lang.ERROR_WORKOUT_EMPTY)
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
            messagebox.showerror(title=self.lang.ERROR_TITLE, message=self.lang.ERROR_SYNTAX.format(e.lineno, e.text))
            return
        self.xml_data, workout_duration = xml_writer.to_xml(parsed_lines, author=self.author, workout_name=name, workout_description=description)
        self.duration_hours = 0
        self.duration_minutes = int(workout_duration/60)
        self.duration_seconds = int(workout_duration - self.duration_minutes*60)
        if self.duration_minutes >= 60:
            self.duration_hours = int(self.duration_minutes/60)
            self.duration_minutes = int(self.duration_minutes - self.duration_hours*60)
        self.duration_label['text'] = self.lang.WORKOUT_DURATION_OUTPUT.format(self.duration_hours, self.duration_minutes, self.duration_seconds)
        # print('Workout duration: {}:{}'.format(minutes, seconds))

    def save_workout_files(self):
        if self.xml_data is None:
            messagebox.showerror(title=self.lang.ERROR_TITLE, message=self.lang.ERROR_CONVERT_FIRST)
        else:
            write_path = self.workout_path / (self.filename + '.zwo')
            if write_path.exists():
                if messagebox.askokcancel(self.lang.ASK_OVERWRITE_TITLE, self.lang.ASK_OVERWRITE.format(write_path.name)):
                    xml_writer.xml_to_file(self.xml_data, write_path)

                    write_path_data = self.data_path / (self.filename + '.txt')
                    with open(write_path_data, 'w') as f:
                        f.write(self.workout_lines_raw)

                    self.xml_data = None

                    messagebox.showinfo(title=self.lang.SAVE_SUCCESS_TITLE, message=self.lang.SAVE_SUCCESS)

    def open_workouts(self):
        os.startfile(self.workout_path)

    def open_data(self):
        os.startfile(self.data_path)

    def load_example(self):
        self.text.delete(1.0, "end")
        self.text.insert(1.0, EXAMPLE_TEXT[self.lang_index])
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, EXAMPLE_NAME[self.lang_index])
        self.description_entry.delete(1.0, "end")
        self.description_entry.insert(1.0, EXAMPLE_DESCRIPTION[self.lang_index])


if __name__ == '__main__':
    gui = GUI()
