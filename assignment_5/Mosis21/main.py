import tkinter
import time
from srcgen import physics, system, trolley, motor_control

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yakindu.rx import Observer


class QueueEntry:
    __slots__ = ('timestamp', 'callback', 'canceled', 'debug') # For MAXIMUM performance :)

    def __init__(self, timestamp, callback, debug):
        self.timestamp = timestamp
        self.callback = callback
        self.debug = debug
        self.canceled = False

# Simulation primitive.
# Uses virtualized (simulated) time, instead of looking at the wall clock.
class Controller:
    def __init__(self):
        self.event_queue = []
        self.simulated_time = 0

    def start(self, timestamp):
        self.simulated_time = timestamp
        self.start_time = timestamp

    def add_input(self, timestamp, sc, event, value=None):
        raise_method = getattr(sc, 'raise_' + event)
        if value is not None:
            callback = lambda: raise_method(value)
        else:
            callback = raise_method
        print("add_input", event, value)
        self.add_input_lowlevel(timestamp, callback, event)

    def add_input_lowlevel(self, timestamp, callback, debug):
        e = QueueEntry(timestamp, callback, debug)
        self.event_queue.append(e)
        self.event_queue.sort(key = lambda entry: entry.timestamp, reverse=True)
        return e

    def run_until(self, until):
        while self.have_event() and self.get_earliest() <= until:
            e = self.event_queue.pop();
            if not e.canceled:
                # print("handling", e.debug)
                self.simulated_time = e.timestamp
                e.callback()

    def have_event(self):
        return len(self.event_queue) > 0

    def get_earliest(self):
        return self.event_queue[-1].timestamp

# Our own timer service, used by the statechart.
# Much better than YAKINDU's pathetic timer service.
class TimerService:
    def __init__(self, controller):
        self.controller = controller;
        self.timers = {}

    # Duration: milliseconds
    def set_timer(self, sc, event_id, duration, periodic):
        def callback():
            sc.time_elapsed(event_id)

        self.unset_timer(callback, event_id)

        controller_duration = duration * 1000000 # ms to ns

        # print("set timer"+str(event_id), "duration", duration)
        e = self.controller.add_input_lowlevel(
            self.controller.simulated_time + controller_duration, # timestamp relative to simulated time
            callback,
            "timer"+str(event_id))

        self.timers[event_id] = e

    def unset_timer(self, callback, event_id):
        try:
            e = self.timers[event_id]
            e.canceled = True
        except KeyError:
            pass

# Runs the Controller as close as possible to the wall-clock.
# Depending on how fast your computer is, simulated time will always run a tiny bit behind wall-clock time, but this error will NOT grow over time.
class RealTimeSimulation:
    def __init__(self, Controller, tk, update_callback):
        self.controller = controller
        self.tk = tk
        self.update_callback = update_callback

        self.scheduled_id = None
        self.purposefully_behind = 0

    def add_input(self, sc, event, value=None):
        now = time.perf_counter_ns() + self.purposefully_behind
        self.controller.add_input(now, sc, event, value)
        self.interrupt()

    def interrupt(self):
        if self.scheduled_id is not None:
            self.tk.after_cancel(self.scheduled_id)

        if self.controller.have_event():
            now = time.perf_counter_ns()
            earliest = self.controller.get_earliest()
            sleep_time = earliest - now

            if sleep_time < 0:
                self.purposefully_behind = sleep_time
            else:
                self.purposefully_behind = 0

            def callback():
                # print("run_until...")
                self.controller.run_until(now + self.purposefully_behind)
                self.update_callback()
                self.interrupt()

            # print("sleeping for", int(sleep_time / 1000000))

            self.scheduled_id = self.tk.after(int(sleep_time / 1000000), callback)
        else:
            print("sleeping forever")

# Adapted from https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):    
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class TrackDisplay:
    def __init__(self, parent, width, height, margin, sep):
        self.width = width
        self.height = height
        self.margin = margin
        self.sep = sep

        self.length = 2*self.width + 2*self.height
        self.w_portion = self.width / self.length
        self.h_portion = self.height / self.length

        self.canvas = tkinter.Canvas(parent, bd=0, bg='#faebd2',
            width=self.width + self.margin * 2,
            height=self.height + self.margin * 2)

        # draw track
        round_rectangle(self.canvas,
            x1=self.margin - self.sep/2,
            y1=self.margin - self.sep/2,
            x2=self.margin + self.width + self.sep/2,
            y2=self.margin + self.height + self.sep/2,
            radius=self.sep*5,
            outline='black', fill='')
        round_rectangle(self.canvas,
            x1=self.margin + self.sep/2,
            y1=self.margin + self.sep/2,
            x2=self.margin + self.width - self.sep/2,
            y2=self.margin + self.height - self.sep/2,
            radius=self.sep*4,
            outline='black', fill='')


    def __rel_to_abs(self, rel_pos):
        def without_margin():
            if rel_pos < self.w_portion:
                return [rel_pos*self.length, 0]
            elif rel_pos < self.w_portion + self.h_portion:
                return [self.width, (rel_pos-self.w_portion)*self.length]
            elif rel_pos < 2*self.w_portion + self.h_portion:
                return [(2*self.w_portion+self.h_portion-rel_pos)*self.length, self.height]
            else:
                return [0, (1-rel_pos)*self.length]
        [x,y] = without_margin()
        return [x+self.margin, y+self.margin]

    def create_point(self, position, color, **options):
        [x, y] = self.__rel_to_abs(position)
        return self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=color, **options)

    def move_point(self, obj, old_position, new_position):
        [old_x, old_y] = self.__rel_to_abs(old_position)
        [new_x,new_y] = self.__rel_to_abs(new_position)
        # Must provide translation vector instead of new position...
        self.canvas.move(obj, new_x - old_x, new_y - old_y)

class PhysicalObject:
    def __init__(self, x, id, color):
        self.x = x
        self.id = id
        self.color = color

class VirtualTrack:
    def __init__(self, track_display, length, stations, train_x):
        self.track_display = track_display
        self.length = length
        self.stations = stations

        self.train_x = train_x

        self.train_shape = self.track_display.create_point(self.train_x / self.length, 'grey', outline='grey')

        for s in self.stations:
            self.track_display.create_point(s.x / self.length, s.color)

    def update(self, train_x, on_cross):
        wrapped_x = train_x % self.length

        self.track_display.move_point(self.train_shape,
            self.train_x / self.length, wrapped_x / self.length)

        if wrapped_x < self.train_x:
            def has_crossed(x):
                return (self.train_x < x
                    and wrapped_x + virtual_track.length >= x
                    or self.train_x - virtual_track.length < x
                    and wrapped_x >= x)
        else:
            def has_crossed(x):
                return (self.train_x < x
                  and wrapped_x >= x)

        for (x, callback) in on_cross:
            if has_crossed(x):
                callback()

        self.train_x = wrapped_x

# def breaking_distance(v_i):
#     # Given an initial speed, what's the breaking distance?

#     # When our trolley breaks, there are 2 'portions' of the breaking:
#     #  The part above 4 m/s is "fast breaking" with acceleration -20m/s^2
#     #  The part below 4 m/s is "slow breaking" with acceleration -1m/s^2

#     def breaking_time(v_f, v_i, a):
#         return (vf - v_i) / a

#     def breaking_distance(v_i, a, t):
#         return v_i * t + 0.5 * a * t^2


#     # The 'fast part'
#     fast_time = max(breaking_time(v_f=4.0, v_i=v_i, a=-20.0), 0.0)
#     slow_time = max(breaking_time(v_f=0.0, v_i=min(4.0, v_i), a=-1.0), 0.0)

#     fast_distance = breaking_distance(v_i=v_i, a=-20, t=fast_time)
#     slow_distance = breaking_distance(v_i=max(4.0, v_i), a=-1, t=slow_time)

#     return fast_distance + slow_distance

if __name__ == "__main__":
    toplevel = tkinter.Tk()
    toplevel.resizable(0,0)

    # For some reason, we have to initialize all 3 statecharts in code (instead of just the 'system' statechart)
    sc_physics = physics.Physics()
    sc_trolley = trolley.Trolley()
    sc_system = system.System()
    sc_motor_control = motor_control.MotorControl()

    sc_system.physics = sc_physics
    sc_system.trolley = sc_trolley
    sc_system.motor_control = sc_motor_control

    controller = Controller()

    sc_physics.timer_service = TimerService(controller)
    sc_motor_control.timer_service = TimerService(controller)
    sc_trolley.timer_service = TimerService(controller)
    sc_system.timer_service = TimerService(controller)

    def update_callback():
        string_simtime.set('{:.3f}'.format((controller.simulated_time - controller.start_time) / 1000000000))
    sim = RealTimeSimulation(controller, toplevel, update_callback)

    toplevel.title("Personal Rapid Transport Simulator")

    track_display = TrackDisplay(toplevel,
        width=820, height=100, margin=20, sep=4)
    track_display.canvas.pack()

    virtual_track = VirtualTrack(
        track_display,
        length=400,
        stations=[
            PhysicalObject(50, 0, '#84b1f5'), # blue
            PhysicalObject(150, 1, '#f58484'), # red
            PhysicalObject(290, 2, '#a1f584'), # green
            PhysicalObject(385, 3, '#f5ef84'), # yellow
        ],
        train_x=sc_physics.x)

    string_simtime = tkinter.StringVar()
    string_a = tkinter.StringVar()
    string_v = tkinter.StringVar()
    string_x = tkinter.StringVar()
    string_doors = tkinter.StringVar(value="OPEN")
    string_signal = tkinter.StringVar(value="NO")
    string_stop = tkinter.StringVar(value="0")

    string_num_passengers = tkinter.StringVar(value="0")
    string_rem_cap = tkinter.StringVar()

    request_stop_frame = tkinter.LabelFrame(toplevel, text="Request stop at")
    station_buttons = []
    def create_station_button(station):
        # closure
        button = tkinter.Button(request_stop_frame, text="Station "+str(station.id), bg=station.color,
            command=lambda: sim.add_input(sc_trolley, "request_stop", station.id))
        button.grid(row=station.id//2, column=station.id%2)
        station_buttons.append(button)
    for station in virtual_track.stations:
        create_station_button(station)
    request_stop_frame.pack(side=tkinter.LEFT)

    passenger_frame = tkinter.LabelFrame(toplevel, text="Passengers")
    tkinter.Label(passenger_frame, text="# passengers").grid(row=0, column=0)
    tkinter.Entry(passenger_frame, state='readonly', width=4, textvariable=string_num_passengers, justify=tkinter.RIGHT).grid(row=0, column=1)
    tkinter.Label(passenger_frame, text="remaining capacity").grid(row=1, column=0)
    tkinter.Entry(passenger_frame, state='readonly', width=4, textvariable=string_rem_cap, justify=tkinter.RIGHT).grid(row=1, column=1)
    board_buttons = tkinter.Frame(passenger_frame)
    tkinter.Button(board_buttons, text="Board",
        command=lambda: sim.add_input(sc_trolley, "board")).pack(side=tkinter.LEFT)
    tkinter.Button(board_buttons, text="Unboard",
        command=lambda: sim.add_input(sc_trolley, "unboard")).pack(side=tkinter.RIGHT)
    board_buttons.grid(row=2, column=0, columnspan=2)
    passenger_frame.pack(side=tkinter.LEFT)

    doors_frame = tkinter.LabelFrame(toplevel,text="Doors and such")
    tkinter.Label(doors_frame, text="doors").grid(row=0, column=0)
    tkinter.Entry(doors_frame, state='readonly', width=10, textvariable=string_doors, justify=tkinter.CENTER).grid(row=0, column=1)
    tkinter.Label(doors_frame, text="signal").grid(row=1, column=0)
    tkinter.Entry(doors_frame, state='readonly', width=10, textvariable=string_signal, justify=tkinter.CENTER).grid(row=1, column=1)
    tkinter.Button(doors_frame, text="Begin emergency", bg='red',
        command=lambda: sim.add_input(sc_trolley, "start_emergency")).grid(row=2, column=0, columnspan=2)
    tkinter.Button(doors_frame, text="End emergency",
        command=lambda: sim.add_input(sc_trolley, "stop_emergency")).grid(row=3, column=0, columnspan=2)
    doors_frame.pack(side=tkinter.LEFT)



    img = tkinter.PhotoImage(file="prt.png")
    tkinter.Label(image=img).pack(side=tkinter.RIGHT)

    sim_frame = tkinter.Frame(toplevel)
    tkinter.Label(sim_frame, text="simulated time").grid(column=0, row=0, columnspan=2)
    tkinter.Entry(sim_frame, state='readonly', width=8, textvariable=string_simtime, justify=tkinter.RIGHT).grid(row=1, column=0)
    tkinter.Label(sim_frame, text="s").grid(row=1, column=1)
    sim_frame.pack(side=tkinter.RIGHT)

    physics_frame = tkinter.LabelFrame(toplevel, text="Physics")
    tkinter.Label(physics_frame, text="a").grid(row=0, column=0)
    tkinter.Entry(physics_frame, state='readonly', width=6, textvariable=string_a, justify=tkinter.RIGHT).grid(row=0, column=1)
    tkinter.Label(physics_frame, text="m/s²").grid(sticky=tkinter.W, row=0, column=2)

    tkinter.Label(physics_frame, text="v").grid(row=1, column=0)
    tkinter.Entry(physics_frame, state='readonly', width=6, textvariable=string_v, justify=tkinter.RIGHT).grid(row=1, column=1)
    tkinter.Label(physics_frame, text="m/s").grid(sticky=tkinter.W, row=1, column=2)

    tkinter.Label(physics_frame, text="x").grid(row=2, column=0)
    tkinter.Entry(physics_frame, state='readonly', width=6, textvariable=string_x, justify=tkinter.RIGHT).grid(row=2, column=1)
    tkinter.Label(physics_frame, text="m").grid(sticky=tkinter.W, row=2, column=2)
    physics_frame.pack(side=tkinter.RIGHT)


    class CallbackObserver(Observer):
        def __init__(self, callback):
            self.callback = callback

        def next(self, value=None):
            if value is None:
                self.callback()
            else:
                self.callback(value)

    class PhysicsObserver(Observer):
        def __init__(self):
            self.on_cross = []
            def create_handler(station):
                # closure
                self.on_cross.append((station.x - 29, lambda: sim.add_input(sc_trolley, "approaching_station", station.id)))
                self.on_cross.append((station.x, lambda: print("Crossed station "+str(station.id))))
            for station in virtual_track.stations:
                create_handler(station)

        def next(self, value=None):
            virtual_track.update(sc_physics.x, on_cross=self.on_cross)
            string_a.set('{:.1f}'.format(sc_physics.a))
            string_v.set('{:.1f}'.format(sc_physics.v))
            string_x.set('{:.1f}'.format(sc_physics.x))

    sc_physics.update_observable.subscribe(PhysicsObserver())

    sc_trolley.close_doors_observable.subscribe(CallbackObserver(lambda: string_doors.set("CLOSED")))
    sc_trolley.open_doors_observable.subscribe(CallbackObserver(lambda: string_doors.set("OPEN")))
    sc_trolley.start_doors_signal_observable.subscribe(CallbackObserver(lambda: string_signal.set("YES")))
    sc_trolley.stop_doors_signal_observable.subscribe(CallbackObserver(lambda: string_signal.set("NO")))

    def refresh_ui():
        string_num_passengers.set(sc_trolley.num_passengers)
        string_rem_cap.set(sc_trolley.remaining_capacity)

        for i in range(len(virtual_track.stations)):
            if (sc_trolley.stops_at & 1<<i) > 0:
                station_buttons[i].config(state=tkinter.DISABLED)
            else:
                station_buttons[i].config(state=tkinter.NORMAL)

    sc_trolley.refresh_ui_observable.subscribe(CallbackObserver(refresh_ui))

    # initialize UI
    refresh_ui()

    # Enter default states
    controller.start(time.perf_counter_ns())

    sc_system.enter()

    sim.interrupt() # schedule first wakeup
    toplevel.mainloop()
