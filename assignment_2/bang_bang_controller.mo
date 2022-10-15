model bang_bang_controller
  parameter Real d_min(start=-1);
  parameter Real d_max(start=1);
  parameter Real g(start=2000);
  Modelica.Blocks.Interfaces.RealInput u annotation(
    Placement(visible = true, transformation(origin = {-96, 2}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-96, 2}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput f annotation(
    Placement(visible = true, transformation(origin = {100, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {100, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation

  when u > d_max then
    f = g;
  elsewhen u < d_min then
    f = 0;
  end when;
annotation(
    uses(Modelica(version = "3.2.3")));
end bang_bang_controller;