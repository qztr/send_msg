"""
Пусть мы получаем список часовых поясов, в форме словаря
из некоторого класса
"""


class Timezones:
    def __init__(self, timezones={3: 3, 7: 9}):
        self.timezones = timezones
