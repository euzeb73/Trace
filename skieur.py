from position import Angle

class Skieur():
    def __init__(self,pentemax=15):
        """skieur avec des attributs pour caractériser ses gouts/aptitudes
        en matière de trace"""
        self.pentemax=Angle(pentemax)