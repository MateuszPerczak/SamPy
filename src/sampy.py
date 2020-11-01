try:
    from typing import ClassVar
    from tkinter import Tk, Frame, Label, Button, ttk, Canvas, Scrollbar, Radiobutton, StringVar, IntVar, Listbox, Toplevel
    from tkinter.filedialog import askdirectory
    from os.path import join, basename, abspath, isfile, isdir, splitext
    from os import listdir, stat, system
    from PIL import Image, ImageTk
    from tkinter.messagebox import showinfo, showerror
    from hashlib import md5
    from webbrowser import open as open_browser
    from random import choice
    from threading import Thread
except ImportError as err:
    exit(err)


class App(Tk):
    def __init__(self) -> None:
        super().__init__()
        # hide window
        self.withdraw()
        # configure window
        self.minsize(450, 500)
        self.title('SamPy')
        self.configure(background='#212121')
        # variables
        self.selected: StringVar = StringVar(value='start')
        self.folders: list = []
        self.files: list = []
        self.random_words: tuple = ('Yeet!', 'Hi')
        self.run: bool = False
        self.scan_subfolders: bool = True
        self.hashes: dict = {}
        self.duplicated_files: dict = {}
        # style
        self.setup_styles()
        # icons
        self.load_icons()
        # layout
        self.main_frame: ClassVar = ttk.Frame(self)
        select_frame: ClassVar = ttk.Frame(self.main_frame, style='second.TFrame')
        ttk.Radiobutton(select_frame, image=self.play_icon[1], variable=self.selected, value='start', command=lambda: self.start_frame.lift()).place(x=0, y=0, width=52, relheight=1)
        ttk.Radiobutton(select_frame, image=self.folder_icon[1], variable=self.selected, value='folder', command=lambda: self.folder_frame.lift()).place(x=52, y=0, width=52, relheight=1)
        ttk.Radiobutton(select_frame, image=self.file_icon, variable=self.selected, value='files', command=lambda: self.files_frame.lift()).place(x=104, y=0, width=52, relheight=1)
        ttk.Radiobutton(select_frame, image=self.info_icon, variable=self.selected, value='about', command=lambda: self.about_frame.lift()).place(relx=1, rely=1, width=52, relheight=1, anchor='se')
        select_frame.pack(side='top', fill='x', ipady=25)
        content_frame: ClassVar = ttk.Frame(self.main_frame)
        self.about_frame: ClassVar = ttk.Frame(content_frame)
        # about frame
        ttk.Label(self.about_frame, image=self.copy_icon[1], text='About SamPy', compound='top', style='fourth.TLabel').pack(anchor='c', fill='x', pady=(60, 0))
        ttk.Label(self.about_frame, text='v1.0.0', style='third.TLabel').pack(anchor='c', fill='x', pady=(0, 5))
        ttk.Label(self.about_frame, text='LUI v2.0.0', style='third.TLabel').pack(anchor='c', fill='x', pady=(0, 15))
        ttk.Label(self.about_frame, text='By Mateusz Perczak', style='third.TLabel').pack(anchor='c', fill='x')
        ttk.Button(self.about_frame, image=self.git_icon, text='Github', compound='left', command=lambda: open_browser('https://github.com/losek1/SamPy')).pack(anchor='c', pady=10)
        ttk.Button(self.about_frame, image=self.bug_icon, text='Report a bug', compound='left', command=lambda: open_browser('https://github.com/losek1/SamPy/issues')).pack(anchor='c')
        ttk.Label(self.about_frame, text=choice(self.random_words), style='fifth.TLabel').pack(side='bottom', fill='x')
        self.about_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # start frame
        self.start_frame: ClassVar = ttk.Frame(content_frame)
        self.start_label: ClassVar = ttk.Label(self.start_frame, image=self.search_icon, text='SamPy', compound='top', style='third.TLabel')
        self.start_label.pack(padx=10, anchor='c', expand=True, fill='both')
        # buttons
        start_buttons_frame: ClassVar = ttk.Frame(self.start_frame)
        self.start_button: ClassVar = ttk.Button(start_buttons_frame, image=self.play_icon[0], text='Start', compound='left', command=self.init_task)
        self.start_button.pack(side='left', fill='x', expand=True, padx=(10, 0), pady=(0, 10))
        self.duplicates_button: ClassVar = ttk.Button(start_buttons_frame, image=self.logs_icon, text='Duplicates', compound='left', command=lambda: self.results_frame.lift())
        self.duplicates_button.pack(side='right', fill='x', expand=True, padx=(10, 10), pady=(0, 10))
        start_buttons_frame.pack(side='bottom', fill='x')
        # progress bars
        progress_frame: ClassVar = ttk.Frame(self.start_frame)
        ttk.Label(progress_frame, text='Overall progress:', style='second.TLabel').pack(side='top', fill='x', padx=10)
        self.overall_progressbar: ClassVar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.overall_progressbar.pack(side='top', fill='x', padx=6)
        self.target_label: ClassVar = ttk.Label(progress_frame, text='Task:', style='second.TLabel')
        self.target_label.pack(side='top', fill='x', padx=10)
        self.target_progressbar: ClassVar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.target_progressbar.pack(side='top', fill='x', padx=6)
        progress_frame.pack(side='bottom', fill='x', pady=(0, 15))
        self.start_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # folder frame
        self.folder_frame: ClassVar = ttk.Frame(content_frame)
        # buttons
        folder_buttons_frame: ClassVar = ttk.Frame(self.folder_frame)
        ttk.Button(folder_buttons_frame, image=self.plus_icon, text='Add folder', compound='left', command=self.add_folder).pack(side='left', fill='x', expand=True, padx=(10, 0), pady=(0, 10))
        ttk.Button(folder_buttons_frame, image=self.delete_icon, text='Remove folder', compound='left', command=self.remove_folder).pack(side='left', fill='x', expand=True, padx=(10, 10), pady=(0, 10))
        folder_buttons_frame.pack(side='bottom', fill='x')
        folder_settings_frame: ClassVar = ttk.Frame(self.folder_frame)
        self.folder_check_button: ClassVar = ttk.Button(folder_settings_frame, image=self.checkmark_icon, command=self.change_folder_settings)
        self.folder_check_button.pack(side='left', padx=(10, 0))
        ttk.Label(folder_settings_frame, text='Scan for subfolders', style='second.TLabel').pack(side='left', fill='x', padx=(10, 0))
        folder_settings_frame.pack(side='bottom', fill='x', pady=10)
        folder_scrollbar: ClassVar = ttk.Scrollbar(self.folder_frame, orient='vertical')
        folder_scrollbar.pack(side='right', fill='y', pady=(0, 10))
        self.folder_listbox: ClassVar = Listbox(self.folder_frame, selectbackground='#111', font=('Bahnschrift 12'), foreground='#fff', takefocus=False, bd=0, background='#212121', activestyle='none', selectmode='extended', highlightthickness=0, yscrollcommand=folder_scrollbar.set, exportselection=0)
        folder_scrollbar.configure(command=self.folder_listbox.yview)
        self.folder_listbox.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        self.folder_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # files frame
        self.files_frame: ClassVar = ttk.Frame(content_frame)
        ttk.Button(self.files_frame, image=self.delete_icon, text='Remove file', compound='left', command=self.remove_file).pack(side='bottom', fill='x', padx=(10, 10), pady=(0, 10))
        files_scrollbar: ClassVar = ttk.Scrollbar(self.files_frame, orient='vertical')
        files_scrollbar.pack(side='right', fill='y', pady=(0, 10))
        self.files_listbox: ClassVar = Listbox(self.files_frame, selectbackground='#111', font=('Bahnschrift 12'), foreground='#fff', takefocus=False, bd=0, background='#212121', activestyle='none', selectmode='extended', highlightthickness=0, yscrollcommand=files_scrollbar.set, exportselection=0)
        files_scrollbar.configure(command=self.files_listbox.yview)
        self.files_listbox.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        self.files_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # results frame
        self.results_frame: ClassVar = ttk.Frame(content_frame)
        ttk.Button(self.results_frame, image=self.left_icon, text='Go back', compound='left', command=lambda: self.start_frame.lift()).pack(side='bottom', fill='x', padx=10, pady=(0, 10))
        results_scrollbar: ClassVar = ttk.Scrollbar(self.results_frame)
        results_scrollbar.pack(side='right', fill='y', pady=10)
        self.results_canvas: ClassVar = Canvas(self.results_frame, background=self['background'], bd=0, highlightthickness=0, yscrollcommand=results_scrollbar.set, takefocus=False)
        results_scrollbar.configure(command=self.results_canvas.yview)
        self.results_panel = ttk.Frame(self.results_canvas)
        self.results_panel.bind('<Configure>', lambda _: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))
        self.results_window: ClassVar = self.results_canvas.create_window((0, 0), window=self.results_panel, anchor="nw")
        self.results_canvas.bind('<Configure>', lambda _: self.results_canvas.itemconfigure(self.results_window, width=self.results_canvas.winfo_width(), height=self.results_panel.winfo_reqheight()))
        self.results_canvas.pack(side='top', anchor='n', fill='both', expand=True, padx=(10, 0), pady=10)
        self.results_frame.place(x=0, y=0, relwidth=1, relheight=1)
        content_frame.pack(side='top', fill='both', expand=True)
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.start_frame.lift()
        self.bind('<MouseWheel>', self.scroll_page)
        self.deiconify()

    def scroll_page(self, event):
        self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def load_icons(self) -> None:
        try:
            self.plus_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'plus.png')).resize((25, 25)))
            self.left_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'left.png')).resize((25, 25)))
            self.logs_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'logs.png')).resize((25, 25)))
            self.delete_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'delete.png')).resize((25, 25)))
            self.folder_icon: ClassVar = (ImageTk.PhotoImage(Image.open(join('Icons', 'folder.png')).resize((25, 25))), ImageTk.PhotoImage(Image.open(join('Icons', 'folder.png')).resize((35, 35))))
            self.file_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'file.png')).resize((35, 35)))
            self.checkmark_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'checkmark.png')).resize((25, 25)))
            self.git_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'github.png')).resize((25, 25)))
            self.bug_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'bug.png')).resize((25, 25)))
            self.stop_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'stop.png')).resize((25, 25)))
            self.play_icon: ClassVar = (ImageTk.PhotoImage(Image.open(join('Icons', 'play.png')).resize((25, 25))), ImageTk.PhotoImage(Image.open(join('Icons', 'play.png')).resize((35, 35))))
            self.info_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'info.png')).resize((35, 35)))
            self.copy_icon: ClassVar = (ImageTk.PhotoImage(Image.open(join('Icons', 'copy.png')).resize((25, 25))), ImageTk.PhotoImage(Image.open(join('Icons', 'copy.png')).resize((60, 60))))
            self.search_icon: ClassVar = ImageTk.PhotoImage(Image.open(join('Icons', 'search.png')).resize((80, 80)))
            self.iconphoto(False, self.copy_icon[1])
        except Exception as err:
            showerror('Error', err)

    def setup_styles(self) -> None:
        self.layout: ClassVar = ttk.Style()
        self.layout.theme_use('clam')
        # label
        self.layout.configure('TLabel', background='#111', relief='flat', font=('Bahnschrift 13'), foreground='#fff', anchor='c')
        self.layout.configure('second.TLabel', background='#212121', anchor='w')
        self.layout.configure('third.TLabel', background='#212121', anchor='c')
        self.layout.configure('fourth.TLabel', background='#212121', anchor='c', font=('Bahnschrift 15'))
        self.layout.configure('fifth.TLabel', background='#212121', font=('Bahnschrift 10'), foreground='#2d2d2d', anchor='w')
        self.layout.configure('sixth.TLabel', background='#111', anchor='w')
        # frame
        self.layout.configure('TFrame', background='#212121', relief='flat')
        self.layout.configure('second.TFrame', background='#111')
        # button
        self.layout.layout('TButton', [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])
        self.layout.configure('TButton', background='#111', relief='flat', font=('Bahnschrift 13'), foreground='#fff')
        self.layout.map('TButton', background=[('pressed', '!disabled', '#212121'), ('active', '#212121'), ('selected', '#212121')])
        self.layout.configure('second.TButton', anchor='w')
        # scrollbar
        self.layout.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
        self.layout.configure('Vertical.TScrollbar', gripcount=0, relief='flat', background='#212121', darkcolor='#212121', lightcolor='#212121', troughcolor='#212121', bordercolor='#212121')
        self.layout.map('Vertical.TScrollbar', background=[('pressed', '!disabled', '#111'), ('disabled', '#212121'), ('active', '#111'), ('!active', '#111')])
        # progressbar
        self.layout.configure('Horizontal.TProgressbar', foreground='#000', background='#111', lightcolor='#212121', darkcolor='#212121', bordercolor='#212121', troughcolor='#212121', thickness=2)
        # radiobutton
        self.layout.layout('TRadiobutton', [('Radiobutton.padding', {'sticky': 'nswe', 'children': [('Radiobutton.label', {'sticky': 'nswe'})]})])
        self.layout.configure('TRadiobutton', background='#111', relief='flat', font=('catamaran 13 bold'), foreground='#fff', anchor='c', padding=5, width=12)
        self.layout.map('TRadiobutton', background=[('pressed', '!disabled', '#212121'), ('active', '#212121'), ('selected', '#212121')])

    def add_folder(self) -> None:
        temp_dir: str = askdirectory()
        if temp_dir and not temp_dir in self.folders:
            self.folders.append(temp_dir)
            self.folder_listbox.insert('end', abspath(temp_dir))
            self.scan_for_folders()
            self.scan_for_files()

    def remove_folder(self) -> None:
        items_to_delete: list = []
        for item in self.folder_listbox.curselection()[::-1]:
            self.folder_listbox.delete(item)
            items_to_delete.append(self.folders[item])
        for item in items_to_delete:
            self.folders.remove(item)
        del items_to_delete
        self.scan_for_files()

    def remove_file(self) -> None:
        items_to_delete: list = []
        for item in self.files_listbox.curselection()[::-1]:
            self.files_listbox.delete(item)
            items_to_delete.append(self.files[item])
        for item in items_to_delete:
            self.files.remove(item)
        del items_to_delete

    def scan_for_folders(self) -> None:
        path: str = ''
        try:
            for folder in self.folders:
                for item in listdir(folder):
                    if item in ('System Volume Information', '$RECYCLE.BIN'):
                        continue
                    path = abspath(join(folder, item))
                    if self.scan_subfolders and isdir(path) and not path in self.folders:
                        self.folders.append(path)
                        self.folder_listbox.insert('end', path)
        except Exception:
            pass

    def scan_for_files(self) -> None:
        self.files = []
        path: str = ''
        self.files_listbox.delete(0, 'end')
        try:
            for folder in self.folders:
                for item in listdir(folder):
                    path = abspath(join(folder, item))
                    if isfile(path) and not splitext(item)[1] in ('.ini'):
                        self.files.append(path)
                        self.files_listbox.insert('end', path)
        except Exception as err:
            print(err)

    def get_mmd5(self, file) -> ClassVar:
        md5_obj: ClassVar = md5()
        with open(file, 'rb') as source:
            self.target_progressbar['maximum'] = stat(file).st_size
            self.target_progressbar['value'] = 0
            while self.run:
                self.target_progressbar['value'] += 65536
                data: bytes = source.read(65536)
                if not data:
                    break
                md5_obj.update(data)
        return md5_obj.hexdigest()

    def generate_hashes(self) -> None:
        self.hashes = {}
        self.start_label['text'] = f'Generating hashes for: {len(self.files)} files'
        for file in self.files:
            if not self.run:
                break
            self.target_label['text'] = f'Generating hash {float(round((self.files.index(file) * 100) / len(self.files), 1))}%'
            self.hashes[file] = self.get_mmd5(file)
            self.overall_progressbar['value'] += 1

    def start_task(self) -> None:
        if self.files and self.folders:
            for card in self.results_panel.winfo_children():
                card.destroy()
            self.update_results(1)
            self.run = True
            self.target_progressbar['value'] = 0
            self.target_progressbar['maximum'] = 100
            self.overall_progressbar['value'] = 0
            self.overall_progressbar['maximum'] = len(self.files) * 2
            self.duplicates_button['text'] = 'Duplicates 0'
            self.start_button.configure(text='Stop', image=self.stop_icon)
            self.start_label['text'] = 'Working ...'
            self.generate_hashes()
            self.compare_files()
            self.end_tasks()

    def end_tasks(self) -> None:
        self.run = False
        self.start_button.configure(text='Start', image=self.play_icon[0])
        self.target_progressbar.stop()
        self.target_progressbar.configure(mode='determinate') 
        self.target_progressbar['value'] = 0
        self.overall_progressbar['value'] = 0
        self.target_label['text'] = 'Task:'
        self.start_label['text'] = 'Done!'

    def init_task(self) -> None:
        if self.files and self.folders and not self.run:
            Thread(target=self.start_task, daemon=True).start()
        elif self.run:
            self.end_tasks()

    def compare_files(self) -> None:
        self.target_progressbar['maximum'] = len(self.files)
        self.target_label['text'] = 'Comparing hashes ...'
        self.start_label['text'] = f'Comparing hashes: {len(self.files)} files'
        ignore_files: list = []
        for file in self.files:
            self.target_progressbar['value'] = 0
            self.duplicated_files[file]: list = []
            if not self.run:
                break
            for compare_files in self.files:
                self.target_progressbar['value'] += 1 
                self.target_label['text'] = f'Comparing hash {float(round((self.files.index(file) * 100) / len(self.files), 1))}%'
                #  or compare_files in self.duplicated_files
                if file == compare_files or file in ignore_files:
                    continue
                if self.hashes[compare_files] == self.hashes[file]:
                    ignore_files.append(compare_files)
                    self.duplicated_files[file].append(compare_files)
                    self.duplicates_button['text'] = f'Duplicates {len(self.duplicated_files)}'

            if not self.duplicated_files[file]:
                del self.duplicated_files[file]
            else:
                self.duplicated_card(file)
                self.update_results(0)
            self.overall_progressbar['value'] += 1
        del ignore_files

    def change_folder_settings(self: ClassVar) -> None:
        if self.scan_subfolders:
            self.folder_check_button.configure(image=self.delete_icon)
            self.scan_subfolders = False
        else:
            self.folder_check_button.configure(image=self.checkmark_icon)
            self.scan_subfolders = True

    def update_results(self: ClassVar, length: int) -> None:
        self.results_canvas.itemconfigure(self.results_window, width=self.results_canvas.winfo_width(), height=length)

    def duplicated_card(self, file: str) -> None:
        card_frame: ClassVar = ttk.Frame(self.results_panel, style='second.TFrame')
        card_title: ClassVar = ttk.Frame(card_frame, style='second.TFrame')
        ttk.Label(card_title, image=self.copy_icon[0], text='Duplicates', compound='left', style='sixth.TLabel').pack(side='left', fill='x', padx=10, pady=10)
        ttk.Label(card_title, text=len(self.duplicated_files[file]), style='sixth.TLabel').pack(side='right', fill='x', padx=10, pady=10)
        card_title.pack(side='top', fill='x')
        ttk.Button(card_frame, text=file, style='second.TButton', command=lambda: self.open_file_location(file)).pack(side='top', padx=10, pady=(10, 10), fill='x', ipady=5)
        for item in self.duplicated_files[file]:
            ttk.Button(card_frame, text=item, style='second.TButton', command=lambda: self.open_file_location(item)).pack(side='top', padx=10, pady=(0, 10), fill='x', ipady=5)
        card_frame.pack(side='top', pady=(10, 0), fill='x')

    def open_file_location(self: ClassVar, file: str) -> None:
        system(r'explorer /select,' + file)


if __name__ == '__main__':
    App().mainloop()