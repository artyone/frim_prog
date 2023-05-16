import subprocess
import chardet
import os
import configparser
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import tkinter.ttk as ttk


class Config(object):
    """Класс работы с конфиг файлом"""

    def __init__(self):
        self.path_dir = os.path.dirname(__file__)
        self.path = self.path_dir + '\\frm.ini'
        self.config = configparser.ConfigParser()
        if not os.path.isfile(self.path):
            self.__create_config()

    def __config_read(self):
        self.config.read(self.path)

    def get_command1(self):
        """Позволяет получить из конфига первую команду"""
        app_path = '"' + self.get_default_value('app_path') + '"'
        args = self.get_config_section('COMMAND1')['args']
        value = self.get_config_section('COMMAND1')['value']
        if app_path != '' and args != '' and value != '':
            command = ' '.join([app_path, args, value])
            return command
        else:
            return ''

    def get_command2(self):
        """Позволяет получить из конфига вторую команду"""
        app_path = '"' + self.get_default_value(key='app_path') + '"'
        args = self.get_config_section(section='COMMAND2')['args']
        value = self.get_config_section(section='COMMAND2')['value']
        if app_path != '' and args != '' and value != '':
            command = ' '.join([app_path, args, value])
            return command
        else:
            return ''

    def get_config_section(self, section):
        self.__config_read()
        value = self.config[section]
        return value

    def get_default_value(self, key):
        self.__config_read()
        value = self.config.get('DEFAULT', key)
        return value

    def get_frm_path_value(self):
        """Путь к файлу прошивки"""
        self.__config_read()
        value = self.config.get('COMMAND2', 'value')
        return value

    def __create_config(self):
        """Генерация файла конфига, если его нет"""
        if os.path.isfile('C:\\AStudio6\\atbackend\\atprogram.exe'):
            self.config['DEFAULT'] = {
                'app_path': 'C:\\AStudio6\\atbackend\\atprogram.exe'}
        else:
            self.config['DEFAULT'] = {'app_path': ''}
        self.config['COMMAND1'] = {'value': 'E419FF',
                                   'args': '-t jtagicemkii -d 1887BE7T -i JTAG -cl 250khz write -fs --values'}
        self.config['COMMAND2'] = {'value': '',
                                   'args': '-t jtagicemkii -d 1887BE7T -i JTAG -cl 250khz program -fl -f'}
        with open(self.path, 'w') as config_file:
            self.config.write(config_file)

    def set_config_value(self, block, key, value):
        """Запись необходимых значений в конфиг"""
        self.config.set(block, key, value)
        with open(self.path, 'w') as config_file:
            self.config.write(config_file)
        return True

    def check_app_path(self):
        """Проверка, что файл приложения, указанный в конфиге, существует"""
        if os.path.isfile(self.get_default_value(key='app_path')):
            return True
        else:
            return False


class Commander(object):
    """Класс для выполнения команд в командной строке"""

    def __init__(self):
        pass

    def exec_command(self, command):
        """Исполнение команды"""
        try:
            self.process = subprocess.run(
                command, shell=True, capture_output=True, timeout=13)
            self.answer = self.process.stdout + self.process.stderr
        except subprocess.TimeoutExpired:
            self.answer = 'Timeout error'.encode()

    def get_answer(self):
        """Получение ответа после выполнения команды"""
        if self.answer != b'':
            encoding = chardet.detect(self.answer)['encoding']
            encode_answer = self.answer.decode(encoding)
            return encode_answer
        else:
            return 'Wrong command'

    def exec_all_commands(self):
        """Выполнить сразу 2 команды.
        Возвращает сразу результат выполнения двух команд с форматом для вывода в алерт!
        Для чистого получения ответа использовать методы exec_command() и get_answer()!
        """
        self.exec_command(config.get_command1())
        result = self.get_answer()
        self.exec_command(config.get_command2())
        result += '*__*' + self.get_answer()
        return result

class Alert(tk.Toplevel):
    """Класс вывода сообщений на экран и их расшифровке, создается обязательно с message"""

    def __init__(self, message):
        super().__init__()
        self.message = message
        self.unpack_codes_error = {'Wrong command': 'Ошибка выполнения команды',
                                   'Devices directory not found': 'Устройство не найдено',
                                   'Timeout error': 'Превышено время загрузки прошивки',
                                   'Wrong path': 'Неверно указан путь к файлу \nпрошивки или программе',
                                   'Could not find tool': 'Не подключен программатор',
                                   'Could not establish': 'Не подключено целевое устройство',
                                   'File does not exist': 'Файл прошивки не найден',
                                   '[ERROR]': 'Ошибка при записи прошивки'}
        self.unpack_codes_success = {'Write completed successfully': 'Запись произведена успешно',
                                     'Programming completed successfully': 'Программирование произведено успешно'}
        self.message_rus1 = ''
        self.message_rus2 = ''
        self.message_eng1 = ''
        self.message_eng2 = ''
        self.status = 'error'
        self.__unpack_message()

    def __unpack_message(self):
        """Распаковывает сообщение на 4 составляющие по словарям. 
        Обязательно должен быть разделитель *__*
        """
        if len(self.message.split('*__*')) > 1:
            message1 = self.message.split('*__*')[0]
            message2 = self.message.split('*__*')[1]
        else:
            message1 = self.message
            message2 = self.message
        for key in self.unpack_codes_error:
            if key in message1 and self.message_rus1 == '':
                self.message_rus1 = self.unpack_codes_error[key]
                self.status = 'error'
            if key in message2 and self.message_rus2 == '':
                self.message_rus2 = self.unpack_codes_error[key]
                self.status = 'error'
        if self.message_rus1 == '' and self.message_rus2 == '':
            for key in self.unpack_codes_success:
                if key in message1 and self.message_rus1 == '':
                    self.message_rus1 = self.unpack_codes_success[key]
                    self.status = 'information'
                if key in message2 and self.message_rus2 == '':
                    self.message_rus2 = self.unpack_codes_success[key]
                    self.status = 'information'
        if self.message_rus1 == '' or self.message_rus2 == '':
            self.status = 'error'
        self.message_eng1 = message1
        self.message_eng2 = message2

    def get_alert(self):
        """Выводит соообщение на экран"""
        self.title("Предупреждение")
        self.frame = tk.Frame(
            self,
            padx=10,
            pady=10
        )
        self.frame.pack()
        self.__get_label()
        self.__set_center_window()

    def __get_label(self):
        # warning, error, information, question - возможные статусы для иконок
        if self.status == 'error':
            color = 'red'
        elif self.status == 'information':
            color = 'green'
        else:
            color = 'black'
        self.l1 = tk.Label(self.frame, image="::tk::icons::" + self.status)
        if self.message_rus1 != '':
            self.l2 = tk.Label(self.frame,
                               text=self.message_rus1,
                               justify='left',
                               wraplength=470,
                               fg=color,
                               font=('Arial', 15))
        if self.message_eng1 != '':
            self.l3 = tk.Label(self.frame,
                               text=self.message_eng1,
                               justify='left',
                               wraplength=470,
                               fg='black',
                               font=('Arial', 8))
        if self.message_rus2 != '':
            self.l4 = tk.Label(self.frame,
                               text=self.message_rus2,
                               justify='left',
                               wraplength=470,
                               fg=color,
                               font=('Arial', 15))
        if self.message_eng2 != '':
            self.l5 = tk.Label(self.frame,
                               text=self.message_eng2,
                               justify='left',
                               wraplength=470,
                               fg='black',
                               font=('Arial', 8))
        self.b1 = ttk.Button(self.frame, text="OK",
                             command=self.destroy, width=10)
        self.__grid_label()

    def __grid_label(self):
        self.l1.grid(row=0, column=0, padx=10, pady=10, sticky='n', rowspan=4)
        if self.message_rus1 != '':
            self.l2.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        if self.message_eng1 != '':
            self.l3.grid(row=1, column=1, padx=5, sticky='w')
        if self.message_rus2 != '':
            self.l4.grid(row=2, column=1, padx=5, sticky='w')
        if self.message_eng2 != '':
            self.l5.grid(row=3, column=1, padx=5, sticky='w')
        self.b1.grid(row=4, column=0, padx=10,
                     pady=5, sticky='n', columnspan=2)

    def __set_center_window(self):
        """Помещение на центр экрана созданногого алерта"""
        self.update_idletasks()
        s = self.geometry()
        s = s.split('+')
        s = s[0].split('x')
        width = int(s[0])
        height = int(s[1])
        self.geometry(app.center_window(width, height))


class App(tk.Tk):
    """Интерфейс программы"""

    def __init__(self):
        super().__init__()
        s = ttk.Style()
        s.theme_use('vista')
        self.title(
            "Программирование микроконтроллера Atmega (1887ВЕ7Т), вер. 1.2.1")
        frame = tk.Frame(
            self,
            padx=10,
            pady=10
        )
        frame.pack()
        self.lbl_app = ttk.Label(
            frame,
            text="Путь к программе:  "
        )
        self.ent_app = ttk.Entry(
            frame,
            width=40)
        self.ent_app.insert(0, config.get_default_value('app_path'))
        self.btn_app = ttk.Button(
            frame,
            text="Выбрать файл",
            command=self.__choose_file_app
        )
        self.lbl_frw = ttk.Label(
            frame,
            text="Файл прошивки:  "
        )
        self.ent_frw = ttk.Entry(
            frame,
            width=40
        )
        self.ent_frw.insert(0, config.get_frm_path_value())
        self.btn_frw = ttk.Button(
            frame,
            text="Выбрать файл",
            command=self.__choose_file_frw
        )
        self.btn_mgc = ttk.Button(
            frame,
            text="Загрузить ПО в микроконтроллер",
            command=self.__magic
        )
        logo_64 = "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"
        image = tk.PhotoImage(data=logo_64, width=100, height=100)
        self.lbl_image = tk.Label(
            frame,
            image=image
        )
        self.lbl_image.image_ref = image  # type: ignore
        self.__check_btn_status()
        self.__grid_interface()

    def __choose_file_app(self):
        filetypes = (("Исполняемый файл", "atprogram.exe"),
                     ("Любой", "*"))
        filename = fd.askopenfilename(
            title="Открыть файл",
            initialdir=os.path.dirname(config.get_default_value('app_path')),
            filetypes=filetypes)
        if filename:
            self.ent_app.delete(0, tk.END)
            self.ent_app.insert(0, filename)
            self.__check_btn_status()

    def __choose_file_frw(self):
        filetypes = (("Файл прошивки", "*.hex"),
                     ("Любой", "*"))
        filename = fd.askopenfilename(
            title="Открыть файл",
            initialdir=os.path.dirname(config.get_frm_path_value()),
            filetypes=filetypes)
        if filename:
            self.ent_frw.delete(0, tk.END)
            self.ent_frw.insert(0, filename)
            self.__check_btn_status()

    def __magic(self):
        """Основная функция запускающая функционал программы"""
        if os.path.isfile(self.ent_app.get()) and os.path.isfile(self.ent_frw.get()):
            config.set_config_value(
                block='DEFAULT', key='app_path', value=self.ent_app.get())
            config.set_config_value(
                block='COMMAND2', key='value', value=self.ent_frw.get())
            answer = commander.exec_all_commands()
            self.alert(answer)
        else:
            self.alert('Wrong path')

    def alert_old(self, message):
        mb.showinfo('Предупреждение', message)

    def alert(self, message):
        """Прослойка для удобного вызова алерта"""
        alert = Alert(message)
        alert.get_alert()

    def __check_btn_status(self):
        if self.ent_app.get() != '' and self.ent_frw.get() != '':
            self.btn_mgc.config(state='normal')
        else:
            self.btn_mgc.config(state='disabled')

    def __grid_interface(self):
        self.lbl_frw.grid(row=4, column=1, pady=5, padx=4, sticky='w')
        self.ent_frw.grid(row=4, column=2, pady=5, padx=4)
        self.btn_frw.grid(row=4, column=3, pady=5, padx=4, sticky='w')
        self.btn_mgc.grid(row=6, column=2, pady=5, padx=4)
        self.lbl_image.grid(row=6, column=3, pady=15, padx=4)
        self.geometry(self.center_window(width=550, height=150))
        if not config.check_app_path():
            self.lbl_app.grid(row=3, column=1, pady=5, padx=4, sticky='w')
            self.ent_app.grid(row=3, column=2, pady=5, padx=4)
            self.btn_app.grid(row=3, column=3, pady=5, padx=4, sticky='w')
            self.geometry(self.center_window(width=550, height=180))
        self.resizable(False, False)

    def center_window(self, width, height):
        """Рассчет для центровки положения окна на экране"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)

        return '%dx%d+%d+%d' % (width, height, x, y)


if __name__ == "__main__":
    config = Config()
    commander = Commander()
    app = App()
    app.mainloop()
