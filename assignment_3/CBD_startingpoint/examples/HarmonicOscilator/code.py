if __name__ == '__main__':
	outputs = []
	signals = []
	for dt in [0.1, 0.01, 0.001]:
		cbd = ErrorB("ErrorB", dt=dt)
		# Run the simulation
		sim = Simulator(cbd)
		sim.setDeltaT(dt)
		sim.run(int(50/dt))
		tvpl = cbd.getSignal("e")
		outputs.append(tvpl)
		signals.append(str(dt))
		plot_signals(cbd, ['real', 'B'], f'Value B ({dt})')

	plt.figure()
	plt.title("Error B")
	plt.xlabel('time')
	plt.ylabel('N')
	for i in range(3):
		time = [x for x, _ in outputs[i]]
		value = [x for _, x in outputs[i]]
		plt.plot(time, value, label=signals[i])
	plt.legend()
	plt.show()
