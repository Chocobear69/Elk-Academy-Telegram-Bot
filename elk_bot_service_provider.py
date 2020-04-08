import pygsheets


class ServiceProvider:
    def __init__(self):
        self.gsheets = pygsheets.authorize(service_file='client_secret.json')
