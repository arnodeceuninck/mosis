model ptr_pid_system
  parameter Real Kp(start=350);
  parameter Real Ki(start=1.5);
  parameter Real Kd(start=0);
  velocity_lookup look_up annotation(
    Placement(visible = true, transformation(origin = {-90, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Add sum(k1 = -1)  annotation(
    Placement(visible = true, transformation(origin = {-34, 6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  ptr_plant Plant annotation(
    Placement(visible = true, transformation(origin = {58, 6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  custom_pid pid_controller(Kd = Kd, Ki = Ki, Kp = Kp)  annotation(
    Placement(visible = true, transformation(origin = {6, 6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  CostFunction costFunction annotation(
    Placement(visible = true, transformation(origin = {0, -34}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(look_up.velocity_ideal, sum.u2) annotation(
    Line(points = {{-81, 0}, {-46, 0}}, color = {0, 0, 127}));
  connect(Plant.v_trolley, sum.u1) annotation(
    Line(points = {{67, 8}, {80, 8}, {80, 40}, {-60, 40}, {-60, 12}, {-46, 12}}, color = {0, 0, 127}));
  connect(sum.y, pid_controller.u) annotation(
    Line(points = {{-22, 6}, {-4, 6}}, color = {0, 0, 127}));
  connect(pid_controller.f_traction, Plant.f_traction) annotation(
    Line(points = {{16, 6}, {48, 6}}, color = {0, 0, 127}));
  connect(Plant.x_psgr, costFunction.x_psgr) annotation(
    Line(points = {{66, 6}, {72, 6}, {72, -30}, {8, -30}}, color = {0, 0, 127}));
  connect(Plant.v_trolley, costFunction.v_trolley) annotation(
    Line(points = {{68, 8}, {82, 8}, {82, -40}, {10, -40}}, color = {0, 0, 127}));
  connect(look_up.velocity_ideal, costFunction.v_ideal) annotation(
    Line(points = {{-80, 0}, {-66, 0}, {-66, -32}, {-10, -32}}, color = {0, 0, 127}));
protected
  annotation(
    uses(Modelica(version = "3.2.3")),
    experiment(StartTime = 0, StopTime = 300, Tolerance = 1e-6, Interval = 0.5));
end ptr_pid_system;