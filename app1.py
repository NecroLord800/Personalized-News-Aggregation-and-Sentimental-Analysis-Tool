from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.config import Config

# Set the app window size for a fixed mobile screen layout
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

# Login Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Login", font_size='20sp', size_hint=(1, 0.3)))

        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.6))
        self.password = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.6))
        login_btn = Button(text="Login", size_hint=(1, 0.7), background_color=(0.2, 0.5, 1, 1))

        register_btn = Button(text="Register", size_hint=(1, 0.7), background_color=(0.1, 0.3, 0.8, 1))

        login_btn.bind(on_press=self.login_action)
        register_btn.bind(on_press=self.go_to_register)

        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(register_btn)
        self.add_widget(layout)

    def login_action(self, instance):
        # Perform login validation here
        print(f"Username: {self.username.text}, Password: {self.password.text}")
        self.manager.current = 'dashboard'

    def go_to_register(self, instance):
        self.manager.current = 'register'

# Register Screen
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Register", font_size='20sp', size_hint=(1, 0.3)))

        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.6))
        self.email = TextInput(hint_text="Email", multiline=False, size_hint=(1, 0.6))
        self.password = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.6))
        register_btn = Button(text="Register", size_hint=(1, 0.7), background_color=(0.2, 0.5, 1, 1))

        back_btn = Button(text="Back to Login", size_hint=(1, 0.7), background_color=(0.1, 0.3, 0.8, 1))

        register_btn.bind(on_press=self.register_action)
        back_btn.bind(on_press=self.go_to_login)

        layout.add_widget(self.username)
        layout.add_widget(self.email)
        layout.add_widget(self.password)
        layout.add_widget(register_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def register_action(self, instance):
        # Perform registration validation here
        print(f"Registering Username: {self.username.text}, Email: {self.email.text}, Password: {self.password.text}")
        self.manager.current = 'login'

    def go_to_login(self, instance):
        self.manager.current = 'login'

# Dashboard Screen
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Dashboard", font_size='20sp', size_hint=(1, 0.3)))

        feed_label = Label(text="Personalized News Feed", font_size='16sp', size_hint=(1, 0.6))
        layout.add_widget(feed_label)

        stats_label = Label(text="Your Reading Stats", font_size='16sp', size_hint=(1, 0.6))
        layout.add_widget(stats_label)

        logout_btn = Button(text="Logout", size_hint=(1, 0.7), background_color=(1, 0.3, 0.3, 1))
        logout_btn.bind(on_press=self.logout_action)

        layout.add_widget(logout_btn)
        self.add_widget(layout)

    def logout_action(self, instance):
        print("Logging out...")
        self.manager.current = 'login'

# Main App
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    MyApp().run()
