import plyer
from kivy.app import App

class Messager():
    def messager(self, msg):
        the = App().get_running_app()
        plyer.notification.notify(title=msg, message=msg, app_name=the.name,
                                  timeout=1,
                                  ticker='New Incoming Notification', toast=True)