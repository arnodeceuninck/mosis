from assignment_6.prt_system.config_objects import StationConfig

RANDOM_SEED = 0

TROLLEY_DEFAULT_VELOCITY = 50
TROLLEY_MAX_CAPACITY = 10

GENERATOR_AVG_MINUTES = 5
GENERATOR_DEVIATION_MINUTES = 1

TRACK_WAITING_TIME_SECONDS = 60
BOARDING_TIME_SECONDS = 10  # TODO: Not sure about this one, should also contain the word seconds/minutes in it's name

MIN_LOG_LEVEL = 5

MIN_RAIL_TROLLEY_WAIT_SECONDS = 10
TROLLEY_JUNCTION_WAIT_TIME = 50

# Linenumber, StationConfig list
STATIONS = [StationConfig("University Square", lines=[2], generate_trollies=True, velocity=25),
            StationConfig("Forrester Gardens", lines=[2], generate_trollies=True),
            StationConfig("Zeigler Circus", lines=[1, 2, 3]),
            StationConfig("Model Station North", lines=[3], generate_trollies=True, velocity=25),
            StationConfig("Harel Cross", lines=[1, 2, 3]),
            StationConfig("Petris Palace", lines=[3], generate_trollies=True),
            StationConfig("Moores Moor", lines=[2], generate_trollies=True, velocity=25),
            StationConfig("Museum of Informatics", lines=[1], generate_trollies=True),
            StationConfig("Turing Station", lines=[1], generate_trollies=True, velocity=25),
            StationConfig("Model Station South", lines=[1], generate_trollies=True)]

# LineNumber, Railconfig list
RAILS = {
    1: {
        'rails': [("Harel Cross", 1, "Museum of Informatics"),
                  ("Museum of Informatics", 3, "Turing Station"),
                  ("Turing Station", 2.5, "Model Station South")],
        'junctions': [("Zeigler Circus", 1, "Junction 1"),
                      ("Junction 1", 0.5, "Harel Cross"),
                      ("Model Station South", 1, "Junction 2"),
                      ("Junction 2", 1.5, "Zeigler Circus")]
    },
    2: {
        'rails': [("University Square", 5, "Forrester Gardens"),
                  ("Forrester Gardens", 1.1, "Zeigler Circus"),
                  ("Harel Cross", 1, "Moores Moor"),
                  ("Moores Moor", 2, "University Square")],
        'junctions': [("Zeigler Circus", 1, "Junction 1"),
                      ("Junction 1", 0.5, "Harel Cross")]
    },
    3: {
        'rails': [("Zeigler Circus", 0.7, "Model Station North"),
                  ("Harel Cross", 3.5, "Petris Palace"),
                  ],
        'junctions': [("Model Station North", 0.5, "Junction 1"),
                      ("Junction 1", 0.5, "Harel Cross"),
                      ("Petris Palace", 2, "Junction 2"),
                      ("Junction 2", 1.5, "Zeigler Circus")]
    }
}

JUNCTIONS = ['Junction 1', 'Junction 2']

WRONG_STATION_UNBOARD_CHANCE = 0.20  # Should be a number between 0 and 1
#WRONG_STATION_UNBOARD_CHANCE = 0.03

# All below is for the altered model, uncomment if you want this altered version
# TROLLEY_DEFAULT_VELOCITY = 500
# TROLLEY_MAX_CAPACITY = 100
#
# GENERATOR_AVG_MINUTES = 5
# GENERATOR_DEVIATION_MINUTES = 1
#
# TRACK_WAITING_TIME_SECONDS = 30
# BOARDING_TIME_SECONDS = 5
#
# MIN_LOG_LEVEL = 5
#
# MIN_RAIL_TROLLEY_WAIT_SECONDS = 5
# TROLLEY_JUNCTION_WAIT_TIME = 40
#
#
# WRONG_STATION_UNBOARD_CHANCE = 0.00
#
# # Linenumber, StationConfig list
# STATIONS = [StationConfig("University Square", lines=[2], generate_trollies=True),
#             StationConfig("Forrester Gardens", lines=[2], generate_trollies=True),
#             StationConfig("Zeigler Circus", lines=[1, 2, 3]),
#             StationConfig("Model Station North", lines=[3], generate_trollies=True),
#             StationConfig("Harel Cross", lines=[1, 2, 3]),
#             StationConfig("Petris Palace", lines=[3], generate_trollies=True),
#             StationConfig("Moores Moor", lines=[2], generate_trollies=True),
#             StationConfig("Museum of Informatics", lines=[1], generate_trollies=True),
#             StationConfig("Turing Station", lines=[1], generate_trollies=True),
#             StationConfig("Model Station South", lines=[1], generate_trollies=True)]
