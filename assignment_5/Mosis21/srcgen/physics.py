"""Implementation of statechart physics.
Generated by YAKINDU Statechart Tools code generator.
"""

import queue
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yakindu.rx import Observable

class Physics:
	"""Implementation of the state machine Physics.
	"""

	class State:
		""" State Enum
		"""
		(
			physics_physics,
			physics_physics_r1default,
			physics_physics_r2default,
			null_state
		) = range(4)
	
	
	def __init__(self):
		""" Declares all necessary variables including list of states, histories etc. 
		"""
		
		self.a = None
		self.v = None
		self.x = None
		self.set_acceleration = None
		self.set_acceleration_value = None
		self.update = None
		self.update_observable = Observable()
		
		self.in_event_queue = queue.Queue()
		# enumeration of all states:
		self.__State = Physics.State
		self.__state_conf_vector_changed = None
		self.__state_vector = [None] * 2
		for __state_index in range(2):
			self.__state_vector[__state_index] = self.State.null_state
		
		# for timed statechart:
		self.timer_service = None
		self.__time_events = [None] * 1
		
		# initializations:
		self.a = 0
		self.v = 0
		self.x = 50
		self.__is_executing = False
		self.__state_conf_vector_position = None
	
	def is_active(self):
		"""Checks if the state machine is active.
		"""
		return self.__state_vector[0] is not self.__State.null_state or self.__state_vector[1] is not self.__State.null_state
	
	def is_final(self):
		"""Checks if the statemachine is final.
		Always returns 'false' since this state machine can never become final.
		"""
		return False
			
	def is_state_active(self, state):
		"""Checks if the state is currently active.
		"""
		s = state
		if s == self.__State.physics_physics:
			return (self.__state_vector[0] >= self.__State.physics_physics)\
				and (self.__state_vector[0] <= self.__State.physics_physics_r2default)
		if s == self.__State.physics_physics_r1default:
			return self.__state_vector[0] == self.__State.physics_physics_r1default
		if s == self.__State.physics_physics_r2default:
			return self.__state_vector[1] == self.__State.physics_physics_r2default
		return False
		
	def time_elapsed(self, event_id):
		"""Add time events to in event queue
		"""
		if event_id in range(1):
			self.in_event_queue.put(lambda: self.raise_time_event(event_id))
			self.run_cycle()
	
	def raise_time_event(self, event_id):
		"""Raise timed events using the event_id.
		"""
		self.__time_events[event_id] = True
	
	def __execute_queued_event(self, func):
		func()
	
	def __get_next_event(self):
		if not self.in_event_queue.empty():
			return self.in_event_queue.get()
		return None
	
	def raise_set_acceleration(self, value):
		"""Raise method for event set_acceleration.
		"""
		self.in_event_queue.put(lambda: self.__raise_set_acceleration_call(value))
		self.run_cycle()
	
	def __raise_set_acceleration_call(self, value):
		"""Raise callback for event set_acceleration.
		"""
		self.set_acceleration = True
		self.set_acceleration_value = value
	
	def __entry_action_physics_physics_r2_default(self):
		"""Entry action for state 'Default'..
		"""
		self.timer_service.set_timer(self, 0, 10, False)
		
	def __exit_action_physics_physics_r2_default(self):
		"""Exit action for state 'Default'..
		"""
		self.timer_service.unset_timer(self, 0)
		
	def __enter_sequence_physics_physics_default(self):
		"""'default' enter sequence for state Physics.
		"""
		self.__enter_sequence_physics_physics_r1_default()
		self.__enter_sequence_physics_physics_r2_default()
		
	def __enter_sequence_physics_physics_r1_default_default(self):
		"""'default' enter sequence for state Default.
		"""
		self.__state_vector[0] = self.State.physics_physics_r1default
		self.__state_conf_vector_position = 0
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_physics_physics_r2_default_default(self):
		"""'default' enter sequence for state Default.
		"""
		self.__entry_action_physics_physics_r2_default()
		self.__state_vector[1] = self.State.physics_physics_r2default
		self.__state_conf_vector_position = 1
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_physics_default(self):
		"""'default' enter sequence for region Physics.
		"""
		self.__react_physics__entry_default()
		
	def __enter_sequence_physics_physics_r1_default(self):
		"""'default' enter sequence for region r1.
		"""
		self.__react_physics_physics_r1__entry_default()
		
	def __enter_sequence_physics_physics_r2_default(self):
		"""'default' enter sequence for region r2.
		"""
		self.__react_physics_physics_r2__entry_default()
		
	def __exit_sequence_physics_physics_r1_default(self):
		"""Default exit sequence for state Default.
		"""
		self.__state_vector[0] = self.State.null_state
		self.__state_conf_vector_position = 0
		
	def __exit_sequence_physics_physics_r2_default(self):
		"""Default exit sequence for state Default.
		"""
		self.__state_vector[1] = self.State.null_state
		self.__state_conf_vector_position = 1
		self.__exit_action_physics_physics_r2_default()
		
	def __exit_sequence_physics(self):
		"""Default exit sequence for region Physics.
		"""
		state = self.__state_vector[0]
		if state == self.State.physics_physics_r1default:
			self.__exit_sequence_physics_physics_r1_default()
		state = self.__state_vector[1]
		if state == self.State.physics_physics_r2default:
			self.__exit_sequence_physics_physics_r2_default()
		
	def __react_physics_physics_r1__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		self.__enter_sequence_physics_physics_r1_default_default()
		
	def __react_physics_physics_r2__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		self.__enter_sequence_physics_physics_r2_default_default()
		
	def __react_physics__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		self.__enter_sequence_physics_physics_default()
		
	def __react(self, transitioned_before):
		"""Implementation of __react function.
		"""
		return transitioned_before
	
	
	def __physics_physics_react(self, transitioned_before):
		"""Implementation of __physics_physics_react function.
		"""
		transitioned_after = transitioned_before
		#If no transition was taken then execute local reactions
		if transitioned_after == transitioned_before:
			transitioned_after = self.__react(transitioned_before)
		return transitioned_after
	
	
	def __physics_physics_r1_default_react(self, transitioned_before):
		"""Implementation of __physics_physics_r1_default_react function.
		"""
		transitioned_after = transitioned_before
		if transitioned_after < 0:
			if self.set_acceleration:
				self.__exit_sequence_physics_physics_r1_default()
				self.a = self.set_acceleration_value
				self.__enter_sequence_physics_physics_r1_default_default()
				transitioned_after = 0
		return transitioned_after
	
	
	def __physics_physics_r2_default_react(self, transitioned_before):
		"""Implementation of __physics_physics_r2_default_react function.
		"""
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[0]:
				self.__exit_sequence_physics_physics_r2_default()
				self.v = self.v + (self.a / 100)
				self.v = 0 if self.v < 0 else self.v
				self.x = self.x + (self.v / 100)
				self.update_observable.next()
				self.__enter_sequence_physics_physics_r2_default_default()
				self.__physics_physics_react(0)
				transitioned_after = 1
		#If no transition was taken then execute local reactions
		if transitioned_after == transitioned_before:
			transitioned_after = self.__physics_physics_react(transitioned_before)
		return transitioned_after
	
	
	def __clear_in_events(self):
		"""Implementation of __clear_in_events function.
		"""
		self.set_acceleration = False
		self.__time_events[0] = False
	
	
	def __micro_step(self):
		"""Implementation of __micro_step function.
		"""
		transitioned = -1
		self.__state_conf_vector_position = 0
		state = self.__state_vector[0]
		if state == self.State.physics_physics_r1default:
			transitioned = self.__physics_physics_r1_default_react(transitioned)
		if self.__state_conf_vector_position < 1:
			state = self.__state_vector[1]
			if state == self.State.physics_physics_r2default:
				transitioned = self.__physics_physics_r2_default_react(transitioned)
	
	
	def run_cycle(self):
		"""Implementation of run_cycle function.
		"""
		if self.timer_service is None:
			raise ValueError('Timer service must be set.')
		
		if self.__is_executing:
			return
		self.__is_executing = True
		next_event = self.__get_next_event()
		if next_event is not None:
			self.__execute_queued_event(next_event)
		condition_0 = True
		while condition_0:
			self.__micro_step()
			self.__clear_in_events()
			next_event = self.__get_next_event()
			if next_event is not None:
				self.__execute_queued_event(next_event)
			condition_0 = self.set_acceleration or self.__time_events[0]
		self.__is_executing = False
	
	
	def enter(self):
		"""Implementation of enter function.
		"""
		if self.timer_service is None:
			raise ValueError('Timer service must be set.')
		
		if self.__is_executing:
			return
		self.__is_executing = True
		self.__enter_sequence_physics_default()
		self.__is_executing = False
	
	
	def exit(self):
		"""Implementation of exit function.
		"""
		if self.__is_executing:
			return
		self.__is_executing = True
		self.__exit_sequence_physics()
		self.__is_executing = False
	
	
	
