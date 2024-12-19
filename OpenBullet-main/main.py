from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
import threading
import time
import os
import random
from datetime import datetime
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from OpenBullet import OpenBullet, proxyType

class ResultRow(BoxLayout):
    def __init__(self, id_text, data_text, proxy_text, status_text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = dp(10)
        self.spacing = dp(10)
        
        with self.canvas.before:
            Color(rgba=get_color_from_hex('#2E2E2E'))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
        
        self.add_widget(Label(
            text=str(id_text),
            size_hint_x=None,
            width=dp(50),
            color=(1, 1, 1, 1)
        ))
        self.add_widget(Label(
            text=str(data_text),
            size_hint_x=0.4,
            color=(1, 1, 1, 1)
        ))
        self.add_widget(Label(
            text=str(proxy_text),
            size_hint_x=0.3,
            color=(1, 1, 1, 0.7)
        ))
        
        status_color = {
            'HIT': '#4CAF50',
            'CUSTOM': '#2196F3',
            'BAD': '#F44336',
            'RETRY': '#FFC107',
            'CHECKING': '#03A9F4'
        }.get(status_text, '#9E9E9E')
        
        self.add_widget(Label(
            text=str(status_text),
            size_hint_x=0.3,
            color=get_color_from_hex(status_color)
        ))

class CheckerRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.running = False
        self.total_checks = 0
        self.hits = 0
        self.custom = 0
        self.bad = 0
        self.retries = 0
        self.start_time = None
        self.proxies = []
        self.setup_directories()
        
        Window.size = (400, 700)
        Window.clearcolor = get_color_from_hex('#121212')

    def setup_directories(self):
        self.app_dir = os.path.join(os.path.expanduser('~'), 'OpenBulletApp')
        self.config_dir = os.path.join(self.app_dir, 'configs')
        self.combo_dir = os.path.join(self.app_dir, 'combos')
        self.hits_dir = os.path.join(self.app_dir, 'hits')
        self.proxy_dir = os.path.join(self.app_dir, 'proxies')
        
        # Crear subdirectorios para diferentes tipos de hits
        self.hits_categories = {
            'SUCCESS': os.path.join(self.hits_dir, 'success'),
            'CUSTOM': os.path.join(self.hits_dir, 'custom'),
            'RETRIES': os.path.join(self.hits_dir, 'retries')
        }
        
        # Crear todos los directorios necesarios
        for directory in [self.app_dir, self.config_dir, self.combo_dir, self.hits_dir, self.proxy_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        for hit_dir in self.hits_categories.values():
            if not os.path.exists(hit_dir):
                os.makedirs(hit_dir)

    def add_result(self, id_text, data_text, proxy_text, status_text):
        row = ResultRow(id_text, data_text, proxy_text, status_text)
        self.ids.data_grid.add_widget(row)
        
        self.total_checks += 1
        if status_text == 'HIT':
            self.hits += 1
        elif status_text == 'CUSTOM':
            self.custom += 1
        elif status_text == 'BAD':
            self.bad += 1
        elif status_text == 'RETRY':
            self.retries += 1
            
        self.update_stats()

    def update_stats(self):
        self.ids.total_label.value = str(self.total_checks)
        self.ids.hits_label.value = str(self.hits)
        self.ids.progress_label.value = f"{int((self.total_checks / 100) * 100)}%"
        
        if self.start_time:
            elapsed_time = (datetime.now() - self.start_time).total_seconds() / 60
            if elapsed_time > 0:
                cpm = int(self.total_checks / elapsed_time)
                self.ids.cpm_label.value = str(cpm)

    def load_proxies(self):
        if not self.ids.proxy_input.text:
            return []
            
        try:
            with open(self.ids.proxy_input.text, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

    def get_proxy_type(self):
        proxy_type_map = {
            'HTTP': proxyType.HTTP,
            'SOCKS4': proxyType.SOCKS4,
            'SOCKS5': proxyType.SOCKS5
        }
        return proxy_type_map.get(self.ids.proxy_type.text, proxyType.HTTP)

    def start_check(self):
        if not self.running:
            if not all([self.ids.config_input.text, self.ids.combo_input.text]):
                return
            
            self.running = True
            self.start_time = datetime.now()
            self.ids.start_button.text = 'Stop'
            self.ids.start_button.background_color = get_color_from_hex('#F44336')
            
            self.ids.data_grid.clear_widgets()
            self.total_checks = 0
            self.hits = 0
            self.custom = 0
            self.bad = 0
            self.retries = 0
            
            self.proxies = self.load_proxies()
            
            threading.Thread(target=self.check_thread).start()
        else:
            self.running = False
            self.ids.start_button.text = 'Start'
            self.ids.start_button.background_color = get_color_from_hex('#4CAF50')

    def check_thread(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            hits_files = {
                'SUCCESS': os.path.join(self.hits_categories['SUCCESS'], f'hits_{timestamp}.txt'),
                'CUSTOM': os.path.join(self.hits_categories['CUSTOM'], f'custom_{timestamp}.txt'),
                'RETRIES': os.path.join(self.hits_categories['RETRIES'], f'retries_{timestamp}.txt')
            }

            with open(self.ids.config_input.text, 'r') as f:
                config = f.read()

            with open(self.ids.combo_input.text, 'r') as f:
                combos = [line.strip() for line in f if line.strip()]

            bots_count = int(self.ids.bots_count.text)

            for i, combo in enumerate(combos, start=1):
                if not self.running:
                    break

                try:
                    user, password = combo.split(':')
                    proxy = random.choice(self.proxies) if self.proxies else None
                    
                    Clock.schedule_once(lambda dt, id=i, data=combo, proxy=proxy: 
                        self.add_result(id, data, proxy or "Direct", "CHECKING"))
                    
                    ob = OpenBullet(
                        config=config,
                        USER=user,
                        PASS=password,
                        PROXY=proxy,
                        PROXY_TYPE=self.get_proxy_type() if proxy else None
                    )
                    
                    ob.run()
                    status = ob.status()
                    
                    if status == "SUCCESS":
                        Clock.schedule_once(lambda dt, id=i, data=combo, proxy=proxy: 
                            self.add_result(id, data, proxy or "Direct", "HIT"))
                        with open(hits_files['SUCCESS'], 'a') as hf:
                            hf.write(f'{combo} | Proxy: {proxy or "Direct"}\n')
                    elif status == "CUSTOM":
                        Clock.schedule_once(lambda dt, id=i, data=combo, proxy=proxy: 
                            self.add_result(id, data, proxy or "Direct", "CUSTOM"))
                        with open(hits_files['CUSTOM'], 'a') as hf:
                            hf.write(f'{combo} | Proxy: {proxy or "Direct"}\n')
                    else:
                        Clock.schedule_once(lambda dt, id=i, data=combo, proxy=proxy: 
                            self.add_result(id, data, proxy or "Direct", "BAD"))
                    
                except Exception as e:
                    Clock.schedule_once(lambda dt, id=i, data=combo, proxy=proxy: 
                        self.add_result(id, data, proxy or "Direct", "RETRY"))
                    with open(hits_files['RETRIES'], 'a') as hf:
                        hf.write(f'{combo} | Proxy: {proxy or "Direct"} | Error: {str(e)}\n')
                    continue

        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: self.reset_check_state())

    def reset_check_state(self):
        self.running = False
        self.ids.start_button.text = 'Start'
        self.ids.start_button.background_color = get_color_from_hex('#4CAF50')

    def show_file_chooser(self, type):
        start_path = {
            'config': self.config_dir,
            'combo': self.combo_dir,
            'proxy': self.proxy_dir
        }.get(type, os.path.expanduser('~'))
        
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(
            path=start_path,
            filters=['*.txt'] if type in ['combo', 'proxy'] else ['*.loli']
        )
        
        def on_submit(*args):
            if args[1]:  # Si hay una selección
                path = args[1][0]  # Tomar el primer archivo seleccionado
                if type == 'config':
                    self.ids.config_input.text = path
                elif type == 'proxy':
                    self.ids.proxy_input.text = path
                else:
                    self.ids.combo_input.text = path
                popup.dismiss()
            
        content.add_widget(file_chooser)
        popup = Popup(
            title=f'Select {type.capitalize()} File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        file_chooser.bind(on_submit=on_submit)
        popup.open()

class CheckerApp(App):
    def build(self):
        return CheckerRoot()

if __name__ == '__main__':
    CheckerApp().run()
