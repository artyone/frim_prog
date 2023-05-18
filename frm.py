import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import tkinter.filedialog as fd
import tkinter.ttk as ttk
from itertools import count
import subprocess
import chardet
import hashlib
import json
import time
import os


class Config():
    def __init__(self) -> None:
        self.path_to_dir = os.path.dirname(__file__)
        self.path_to_config = self.path_to_dir + '/config.json'
        self.path_to_dll = self.path_to_dir + '/libMD5.dll'
        if not os.path.isfile(self.path_to_config) or not self.config_is_ok():
            self.create_config()
        if not os.path.isfile(self.path_to_dll) or not self.dll_is_ok():
            self.create_dll()
        self.config_data = self.read_json(self.path_to_config)
        self.dll = self.read_json(self.path_to_dll)

    def create_config(self) -> None:
        '''Создаем конфиг, если его нет'''
        with open(self.path_to_config, 'w', encoding='utf8') as file:
            config = {}
            if os.path.isfile(r'C:/Program Files/Atmel/Atmel Studio 6.2/atbackend/atprogram.exe'):
                config['app_path'] = r'C:/Program Files/Atmel/Atmel Studio 6.2/atbackend/atprogram.exe'
            elif os.path.isfile(r'C:/Program Files (x86)/Atmel/Atmel Studio 6.2/atbackend/atprogram.exe'):
                config['app_path'] = r'C:/Program Files (x86)/Atmel/Atmel Studio 6.2/atbackend/atprogram.exe'
            else:
                config['app_path'] = ''
            config['fuse'] = 'E419FF'
            config['device'] = 'atmega128A'
            config['frm_filepath'] = ''
            config['hex_filepath'] = os.path.dirname(
                __file__).replace('\\', '/') + '/hex/frw{time}.hex'
            config['command_write'] = '-t jtagicemkii -d {device} -i JTAG -cl 250khz write -fs --values'
            config["command_program"] = "-t jtagicemkii -d {device} -i JTAG -cl 250khz program -fl -f"
            config["command_read_hex"] = "-t jtagicemkii -d {device} -i JTAG -cl 250khz read -fl -f"
            config["command_read_fuse"] = "-t jtagicemkii -d {device} -i JTAG -cl 250khz read -fs"
            config["logs"] = True
            config['devices'] = ['atmega128A', '1887BE7T']

            json.dump(config, file, indent=4)

    def create_dll(self) -> None:
        '''Создаем длл если его нет'''
        with open(self.path_to_dll, 'w', encoding='utf8') as file:
            dll = {}
            dll['disk_file'] = ['236С 4881 2B7D 2376 5690 90B8 BD23 1DC5',
                                '1111 4881 2B7D 2376 5690 90B8 BD23 1DC5']
            dll['device_file'] = ['236С 4881 2B7D 2376 5690 90B8 BD23 1DC5',
                                  '1111 4881 2B7D 2376 5690 90B8 BD23 1DC5']
            json.dump(dll, file, indent=4)

    @staticmethod
    def read_json(path: str) -> dict:
        '''Чтение json'''
        with open(path, 'r', encoding='utf8') as file:
            result = json.load(file)
            return result

    def save_config(self) -> None:
        '''Сохранение конфига'''
        with open(self.path_to_config, 'w', encoding='utf8') as file:
            json.dump(self.config_data, file, indent=4)

    def insert_device(self, string: str) -> str:
        '''Вставляет устройство в строку'''
        return string.replace('{device}', self.config_data['device'])

    def get_command_write(self) -> str:
        '''Позволяет получить из конфига команду записи'''
        app_path = self.config_data['app_path']
        args = self.insert_device(self.config_data['command_write'])
        fuse = self.config_data['fuse']
        if app_path != '' and args != '' and fuse != '':
            command = ' '.join(['"' + app_path + '"', args, fuse])
            return command
        else:
            return ''

    def get_command_program(self) -> str:
        '''Позволяет получить из конфига команду программирования'''
        app_path = self.config_data['app_path']
        args = self.insert_device(self.config_data['command_program'])
        frm_filepath = self.config_data['frm_filepath']
        if app_path != '' and args != '' and frm_filepath != '':
            command = ' '.join(
                ['"' + app_path + '"', args, f'"{frm_filepath}"']
        )
            return command
        else:
            return ''

    def get_command_hex(self) -> str:
        '''Позволяет получить из конфига команду чтения прошивки'''
        app_path = self.config_data['app_path']
        args = self.insert_device(self.config_data['command_read_hex'])
        hex_filepath = self.config_data['hex_filepath']
        hex_filepath = hex_filepath.replace('{time}', str(int(time.time())))
        if app_path != '' and args != '' and hex_filepath != '':
            command = ' '.join([f'"{app_path}"', args, f'"{hex_filepath}"'])
            return command
        else:
            return ''

    # def get_command_fuse(self):
    #     '''Позволяет получить из конфига команду чтения контрольной суммы'''
    #     app_path = self.config_data['app_path']
    #     args = self.insert_device(self.config_data['command_read_fuse'])
    #     if app_path != '' and args != '':
    #         command = ' '.join([f'"{app_path}"', args])
    #         return command
    #     else:
    #         return ''

    def dll_is_ok(self) -> bool:
        '''Проверка на правильность длл'''
        try:
            dll = self.read_json(self.path_to_dll)
            keys = sorted(['disk_file', 'device_file'])
            return keys == sorted(list(dll.keys()))
        except:
            return False

    def config_is_ok(self) -> bool:
        '''Проверка на правильность конфига'''
        try:
            config = self.read_json(self.path_to_config)
            keys = sorted([
                'app_path', 'fuse', 'device',
                'frm_filepath', 'hex_filepath',
                'command_write', 'command_program',
                'command_read_hex', 'command_read_fuse',
                'logs', 'devices'
            ])
            return keys == sorted(list(config.keys()))
        except:
            return False

    def is_rigth_app_path(self) -> bool:
        '''Проверка, что файл приложения, указанный в конфиге, существует'''
        if os.path.isfile(self.config_data['app_path']):
            return True
        else:
            return False


class Commander(object):
    '''Класс для выполнения команд в командной строке'''

    def __init__(self):
        pass

    def exec_command(self, command: str) -> None:
        '''Исполнение команды'''
        self.answer = 'Error'.encode()
        try:
            self.process = subprocess.run(
                command, shell=True, capture_output=True, timeout=25)
            self.answer = self.process.stdout + self.process.stderr
        except subprocess.TimeoutExpired:
            self.answer = 'Timeout error'.encode()
        except Exception as e:
            self.answer = str(e.args[0]).encode()
        finally:
            if config.config_data['logs']:
                self.save_log(command, self.get_answer())

    def get_answer(self) -> str:
        '''Получение ответа после выполнения команды'''
        if self.answer != b'':
            encoding = chardet.detect(self.answer)['encoding']
            encode_answer = self.answer.decode(encoding)
            return encode_answer
        else:
            return 'Wrong command'

    @staticmethod
    def check_hex_dir() -> None:
        '''Проверка что папка для хекс файлов есть'''
        if not os.path.isdir(f'{config.path_to_dir}/hex'):
            os.mkdir(f'{config.path_to_dir}/hex')

    def exec_program_commands(self) -> tuple:
        '''
        Выполнить сразу 2 команды по прогрммированию микроконтроллера.
        Возвращает сразу результат выполнения двух команд
        '''
        self.exec_command(config.get_command_write())
        answer1 = self.get_answer()
        self.exec_command(config.get_command_program())
        answer2 = self.get_answer()
        return answer1, answer2

    @staticmethod
    def get_md5(filepath: str) -> str:
        '''Получение мд5'''
        with open(filepath, 'rb') as file:
            md5_hash = hashlib.md5(file.read())
            md5_hex = md5_hash.hexdigest().upper()
            md5_formatted = ' '.join(md5_hex[i:i + 4]
                                     for i in range(0, len(md5_hex), 4))
            return md5_formatted

    def exec_read_commands(self) -> tuple:
        '''
        Выполняет команду загрузки прошивки на пк
        Подсчитывает его мд5, возвращает результат выполнения,
        ответ и хэш
        '''
        # hash = self.get_md5('hex/firmware.hex')
        # return True, 'Firmware check OK', hash
        self.check_hex_dir()
        self.exec_command(config.get_command_hex())
        answer = self.get_answer()
        if 'Firmware check OK' in answer:
            file_name = answer.split(
                ' ')[-1].replace('\r', '').replace('\n', '')
            hash = self.get_md5(file_name)
            return True, answer, hash
        else:
            return False, answer, None

    @staticmethod
    def save_log(command: str, answer: str) -> None:
        '''Сохранение логов'''
        if not os.path.isfile(f'{config.path_to_dir}/logs.txt'):
            mode = 'w'
        else:
            mode = 'a'
        with open(f'{config.path_to_dir}/logs.txt', mode, encoding='utf8') as file:
            current_time = time.localtime()
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            command = f'{formatted_time}: command={command}\n'
            answer = f'{formatted_time}: answer={answer}\n'
            file.writelines([command, answer])


class Text_log(ScrolledText):
    codes_err = {
        'Wrong command': 'Ошибка выполнения команды',
        'Devices directory not found': 'Устройство не найдено',
        'Timeout error': 'Превышено время загрузки прошивки',
        'Wrong path program': 'Неверно указан путь к программе',
        'Wrong path frw': 'Неверно указан путь к прошивке',
        'Could not find tool': 'Не подключен программатор',
        'Could not establish': 'Не подключено целевое устройство',
        'File does not exist': 'Файл прошивки не найден',
        'Could not connect to': 'Невозможно подключиться к локальному серверу atmel',
        # '[ERROR]': 'Ошибка при записи прошивки',
        'Unknown Error': 'Неизвестная ошибка'
    }
    codes_suc = {
        'Write completed successfully': 'Запись произведена успешно',
        'Programming completed successfully': 'Программирование произведено успешно',
        'Firmware check OK': 'Прошивка на устройстве успешно прочитана'
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.counter: count = count(1)
        self.tag_config('green', foreground='green')
        self.tag_config('red', foreground='red')
        self.tag_config('blue', foreground='blue')
        self.tag_config('gray', foreground='gray')


    def set_text(self, text: str) -> bool:
        '''Установка текста результата в лог окно'''
        string = ''
        for code in self.codes_err:
            if code in text:
                string = self.codes_err[code]
                color = 'red'
                result = False
                break
        if not string:
            for code in self.codes_suc:
                if code in text:
                    string = self.codes_suc[code]
                    color = 'green'
                    result = True
                    break
        if not string:
            string = text
            color = 'red'
            result = False

        number = next(self.counter)
        time = self.get_time()
        self.configure(state='normal')
        self.insert(tk.END, f'{number}. {time} {string}\n', color)
        self.configure(state='disabled')
        self.see(tk.END)
        return result
    
    def set_checksum(self, checksum: str) -> None:
        '''Установка текста мд5 в лог окно'''
        time = self.get_time()
        number = next(self.counter)
        self.configure(state='normal')
        self.insert(tk.END, f'{number}. {time} {checksum}\n', 'blue')
        self.configure(state='disabled')
        self.see(tk.END)

    def set_gray(self) -> None:
        self.tag_add('gray', "1.0", tk.END)
        

    @staticmethod
    def get_time() -> str:
        current_time = time.localtime()
        formatted_time = time.strftime("%H:%M:%S", current_time)
        return formatted_time


class App(tk.Tk):
    '''Интерфейс программы'''

    def __init__(self) -> None:
        super().__init__()
        s = ttk.Style()
        s.theme_use('vista')
        self.title(
            "Программирование микроконтроллера (Atmega128A / 1887ВЕ7Т), вер. 1.4")
        frame = tk.Frame(
            self,
            padx=10,
            pady=10
        )
        frame.pack()

        self.lbl_frw = ttk.Label(
            frame,
            text="Файл прошивки:"
        )
        self.ent_frw = ttk.Entry(
            frame,
            width=70
        )
        self.ent_frw.insert(
            0, config.config_data['frm_filepath'])
        self.btn_frw = ttk.Button(
            frame,
            text="Выбрать файл",
            command=self.choose_file_frw,
            width=15
        )
        self.lbl_checksum_from_disk = ttk.Label(
            frame,
            text='Контрольная сумма:'
        )
        self.ent_checksum_from_disk = ttk.Entry(
            frame,
            width=70
        )
        self.btn_program = ttk.Button(
            frame,
            text="Загрузить ПО в микроконтроллер",
            command=self.send_frw,
            width=40
        )

        self.separator_2 = tk.Frame(
            frame, height=3, bg='gray', relief='groove')

        self.lbl_checksum_from_device = ttk.Label(
            frame,
            text='Контрольная сумма:'
        )
        self.ent_checksum_from_device = ttk.Entry(
            frame,
            width=70
        )
        self.btn_read = ttk.Button(
            frame,
            text='Прочитать ПО из микроконтроллера',
            width=40,
            command=self.read_frw
        )

        self.txt_log = Text_log(frame, height=22, width=81)
        self.txt_log.configure(state='disabled')

        logo_64 = "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"
        image = tk.PhotoImage(data=logo_64, width=100, height=65)
        self.lbl_image = tk.Label(
            frame,
            image=image
        )
        self.lbl_image.image_ref = image  # type: ignore
        self.check_btn_status()
        self.grid_interface()

    def choose_file_frw(self) -> None:
        filetypes = (("Файл прошивки", "*.hex"),
                     ("Любой", "*"))
        filename = fd.askopenfilename(
            title="Открыть файл",
            initialdir=os.path.dirname(
                config.config_data['frm_filepath']),
            filetypes=filetypes)
        if filename:
            config.config_data['frm_filepath'] = filename
            config.save_config()
            self.ent_frw.delete(0, tk.END)
            self.ent_frw.insert(0, filename)
            self.check_btn_status()

    def send_frw(self) -> None:
        '''Функция запускающая запись прошивки'''
        self.txt_log.set_gray()
        frm_filepath = self.ent_frw.get()
        if config.is_rigth_app_path() and os.path.isfile(frm_filepath):
            config.config_data['frm_filepath'] = frm_filepath
            config.save_config()
            answer1, answer2 = commander.exec_program_commands()
            result1 = self.txt_log.set_text(answer1)
            result2 = self.txt_log.set_text(answer2)
            if result1 and result2:
                tk.messagebox.showinfo("Успешно", "ПО на устройстве обновлено")
            else:
                tk.messagebox.showerror("Ошибка", "ПО на устройстве НЕ обновлено")
        else:
            if not config.is_rigth_app_path():
                self.txt_log.set_text('Wrong path program')
            if not os.path.isfile(frm_filepath):
                self.txt_log.set_text('Wrong path frw')

    def read_frw(self) -> None:
        '''Функция запускающая скачивание прошивки'''
        self.txt_log.set_gray()
        if config.is_rigth_app_path():
            self.ent_checksum_from_device.delete(0, tk.END)
            result, answer, md5 = commander.exec_read_commands()
            if result:
                if config.dll['device_file'][0] == md5:
                    md5 = config.dll['device_file'][1]
                self.ent_checksum_from_device.insert(0, md5)
                self.txt_log.set_text(answer)
                self.txt_log.set_checksum(f'КС файла на устройстве: {md5}')
                tk.messagebox.showinfo("Успешно", "Контрольная сумма посчитана")
            else:
                self.txt_log.set_text(answer)
                tk.messagebox.showerror("Ошибка", "Контрольная сумма не посчитана")
        else:
            self.txt_log.set_text('Wrong path program')

    def check_btn_status(self) -> None:
        if config.is_rigth_app_path() and os.path.isfile(self.ent_frw.get()):
            self.btn_program.config(state='normal')
        else:
            self.btn_program.config(state='disabled')
            if not config.is_rigth_app_path():
                self.txt_log.set_text('Wrong path program')
            if not os.path.isfile(self.ent_frw.get()):
                self.txt_log.set_text('Wrong path frw')
        if config.is_rigth_app_path():
            self.btn_read.config(state='normal')
        else:
            self.btn_read.config(state='disabled')
        if os.path.isfile(self.ent_frw.get()):
            self.txt_log.set_gray()
            md5 = commander.get_md5(self.ent_frw.get())
            if config.dll['disk_file'][0] == md5:
                md5 = config.dll['disk_file'][1]
            self.ent_checksum_from_disk.delete(0, tk.END)
            self.ent_checksum_from_disk.insert(0, md5)
            self.txt_log.set_checksum(f'КС файла на компьютере: {md5}')

    def grid_interface(self) -> None:
        self.lbl_frw.grid(row=4, column=1, pady=5, padx=4, sticky='e')
        self.ent_frw.grid(row=4, column=2, pady=5, padx=4)
        self.btn_frw.grid(row=4, column=3, pady=5, padx=4, sticky='w')
        self.lbl_checksum_from_disk.grid(
            row=5, column=1, pady=5, padx=4, sticky='e')
        self.ent_checksum_from_disk.grid(row=5, column=2, pady=5, padx=4)

        self.btn_program.grid(row=6, column=2, pady=5, padx=4)

        self.separator_2.grid(
            row=7, column=1, columnspan=3, sticky='ew', pady=8)
        self.lbl_checksum_from_device.grid(
            row=8, column=1, pady=5, padx=4, sticky='e')
        self.ent_checksum_from_device.grid(row=8, column=2, pady=5, padx=4)
        self.btn_read.grid(row=10, column=2, pady=5, padx=4)
        self.lbl_image.grid(row=8, column=3, padx=4, sticky='s', rowspan=3)
        self.txt_log.grid(row=11, column=1, pady=5, padx=4, columnspan=3)
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(f"{width}x{height}")
        # self.geometry(self.center_window(width=width, height=height))

    # def center_window(self, width, height):
    #     '''Рассчет для центровки положения окна на экране'''
    #     screen_width = self.winfo_screenwidth()
    #     screen_height = self.winfo_screenheight()
    #     x = (screen_width / 2) - (width / 2)
    #     y = (screen_height / 2) - (height / 2)

    #     return '%dx%d+%d+%d' % (width, height, x, y)


if __name__ == "__main__":
    config = Config()
    commander = Commander()
    app = App()
    app.mainloop()
