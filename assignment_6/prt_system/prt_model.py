from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *
from assignment_6.prt_system.rail import Rail
from assignment_6.prt_system.station import Station
from assignment_6.prt_system.junction import Junction

from matplotlib import pyplot as plt


class PRTModel(CoupledDEVS):
    """
    Coupled DEVS model that contains a Generator, a Collector, a Platform, a Track, a Light and possibly a Split. The
    Station serves a set of n lines. For simplicity, there is a single input and n outputs (see the Split logic above).
    The figure below shows a shematic overview of how a Station is created with the given list of components.
    """

    def __init__(self, name="Station"):
        CoupledDEVS.__init__(self, name)

        # First distance is always ignored
        # Don't forget to repeat the first name at the end if you want to make it a cycle
        # TODO: Implement logic for junction

        self.stations = dict()
        self.rails = dict()
        self.junctions = dict()
        self.trollies = set()

        for station_config in STATIONS:
            station_name = station_config.name
            if station_name not in self.stations:
                new_trolley = None
                if station_config.generate_trollies:
                    # Place the trolley in a station that supports only one line to be sure that it gets placed on the
                    #  right line
                    new_trolley = Trolley(line=station_config.lines[0], velocity=station_config.velocity)
                    self.trollies.add(new_trolley)
                new_station = self.addSubModel(
                    Station(station_name, station_config.lines, initial_trolley=new_trolley))
                self.stations[station_name] = new_station

        for junction_config in JUNCTIONS:
            junction_name = junction_config
            if junction_name not in self.junctions:
                new_junction = self.addSubModel(Junction(junction_name))
                self.junctions[junction_name] = new_junction

        # TODO: Junction between Zeigler Circus and Harel Cross
        for line_nr in range(1, 4):

            for rail_description in RAILS[line_nr]['rails']:
                from_name = rail_description[0]
                distance = rail_description[1]
                to_name = rail_description[2]

                rail_name = f"Rail {from_name} -> {to_name} Line: {line_nr}"
                rail = self.addSubModel(Rail(rail_name, distance, line_nr, from_name, to_name))
                self.rails[rail_name] = rail

                from_station = self.stations[from_name]
                to_station = self.stations[to_name]
                if line_nr == 1:
                    self.connectPorts(from_station.out1, rail.in1)
                if line_nr == 2:
                    self.connectPorts(from_station.out2, rail.in1)
                if line_nr == 3:
                    self.connectPorts(from_station.out3, rail.in1)
                self.connectPorts(rail.out, to_station.entry)

            for junction_description in RAILS[line_nr]['junctions']:
                from_name = junction_description[0]
                distance = junction_description[1]
                to_name = junction_description[2]

                if from_name in self.junctions:
                    rail_name = f"Rail {from_name} -> {to_name} Line: Junction"
                else:
                    rail_name = f"Rail {from_name} -> {to_name} Line: {line_nr}"
                if rail_name not in self.rails:
                    rail = self.addSubModel(Rail(rail_name, distance, line_nr, from_name, to_name))
                    self.rails[rail_name] = rail

                if from_name in self.junctions:
                    from_junction = self.junctions[from_name]
                    self.connectPorts(from_junction.out, self.rails[rail_name].in1)
                else:
                    from_station = self.stations[from_name]
                    if line_nr == 1:
                        self.connectPorts(from_station.out1, self.rails[rail_name].in1)
                    if line_nr == 2:
                        self.connectPorts(from_station.out2, self.rails[rail_name].in1)
                    if line_nr == 3:
                        self.connectPorts(from_station.out3, self.rails[rail_name].in1)

                if to_name in self.junctions:
                    to_junction = self.junctions[to_name]
                    if line_nr == 1:
                        self.connectPorts(self.rails[rail_name].out, to_junction.in1)
                    if line_nr == 2:
                        self.connectPorts(self.rails[rail_name].out, to_junction.in2)
                    if line_nr == 3:
                        self.connectPorts(self.rails[rail_name].out, to_junction.in3)
                else:
                    to_station = self.stations[to_name]
                    self.connectPorts(self.rails[rail_name].out, to_station.entry)

        pass

    def get_all_trollies(self):
        # return self.trollies
        result = []
        for station in self.stations.values():

            if station.light.state.queue:
                if station.light.state.queue.len() > 0:
                    result.extend(station.light.state.queue.contents)
            if station.track.state.trolley:
                result.append(station.track.state.trolley)
        for rail in self.rails.values():
            if rail.state.trolley_queue.len() > 0:
                result.extend(rail.state.trolley_queue.contents)

        for junction in self.junctions.values():
            if junction.state.queue.len() > 0:
                result.extend(junction.state.queue.contents)

        return result
        # Old method, depreciated since trolley_generator isn't used anymore and this doesn't keep all the info of the trollies
        # trolley_list = []
        # for station_name in self.stations:
        #     station = self.stations[station_name]
        #     trolley_generator = station.trolley_gen
        #     if trolley_generator is not None:
        #         for trolley in trolley_generator.state["generated_trollies"]:
        #             trolley_list.append(trolley)
        # return trolley_list

    def get_avg_travel_time(self):
        # Average travel time for users
        total_time = 0
        total_passengers = 0
        for station_name in self.stations:
            station = self.stations[station_name]
            collector_state = station.collector.state
            for passenger in collector_state.get_passenger():
                total_time += passenger.get_travel_time()
                total_passengers += 1
        if total_passengers == 0:
            return 0, 0
        avg_travel_time = total_time / total_passengers
        return total_passengers, avg_travel_time

    def get_average_trolley_capacity(self, samples):
        previous_time = 0
        total_time = 0
        total_capacity = 0
        for time, capacity in samples:
            total_time += time - previous_time  # Adding the passed time interval
            total_capacity += capacity
            previous_time = time
        if total_time == 0:
            return 0
        return total_capacity / total_time

    def get_trolley_capacity_stats(self):
        # TODO: How can I acces the trolley? Those trolley only contain the initial state of the trollies
        trollies = self.get_all_trollies()
        print("2. (see generated output graphs)")
        print("3. time-average trolley capacity:")
        for trolley in trollies:
            samples = trolley.capacity_log
            print(f" {trolley}: {self.get_average_trolley_capacity(samples)}")
            times, capacity = zip(*samples)
            plt.plot(times, capacity)
            plt.show()
        # TODO: Also determine the average capacity of trollies over time
        # TODO: When I have all trolies, also determine total number of people still commuting when the experiment terminates

    def get_station_stats(self):
        stats = dict()
        total_succesful_arrivals = 0
        for station_name in self.stations:
            station = self.stations[station_name]
            collector_state = station.collector.state
            stats[station_name] = (collector_state.total_passengers, collector_state.total_passengers_wrong_destination,
                                   collector_state.get_avg_time())
            total_succesful_arrivals += collector_state.get_total_succesful_arrivals()
        return stats, total_succesful_arrivals

    def statistics(self):
        total_passengers, avg_travel_time = self.get_avg_travel_time()
        print(f"7. Total number of people arrived at a destination: {total_passengers}")
        print(f"1. Avg. travel time: {avg_travel_time}s")
        self.get_trolley_capacity_stats()
        station_stats, total_succesful_arrivals = self.get_station_stats()
        for station in station_stats:
            stats = station_stats[station]
            total_psgr = stats[0]
            total_wrong = stats[1]
            avg_time = stats[2]
            print(
                f"4+5+6. {station}: {total_psgr} exited, of which {total_wrong} at the wrong destination, with avg time of {avg_time}s")
        print(f"8. Total successful arrivals: {total_succesful_arrivals}")
        print(f"9. TODO")
        # TODO: Number of people with a destination that equals their origin station, but this is always 0 in our case
        print("10. Number of people with a destination that equals their origin station: 0")
