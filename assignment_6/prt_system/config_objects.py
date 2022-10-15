class StationConfig:
    def __init__(self, name, lines, generate_trollies=False, velocity=None):
        self.name = name
        self.lines = lines # The lines the station operates on, e.g. [0, 1]
        self.generate_trollies = generate_trollies
        self.velocity = velocity