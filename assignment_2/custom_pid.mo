block custom_pid "PID-controller in additive description form"
  parameter Real Kp(unit="1")=1 "Proportional";
  parameter Real Ki(unit="1")=0 "Integral";
  parameter Real Kd(unit="1")=0 "Derivative";
  Modelica.Blocks.Continuous.PID pid(k = Kp, Ti = Kp / Ki, Td = Kd / Kp) annotation(
    Placement(visible = true, transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput u annotation(
    Placement(visible = true, transformation(origin = {-96, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-96, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput f_traction annotation(
    Placement(visible = true, transformation(origin = {96, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {96, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(u, pid.u) annotation(
    Line(points = {{-96, 0}, {-12, 0}}, color = {0, 0, 127}));
  connect(pid.y, f_traction) annotation(
    Line(points = {{12, 0}, {96, 0}}, color = {0, 0, 127}));  
annotation(
    uses(Modelica(version = "3.2.3")),
    Icon);
end custom_pid;