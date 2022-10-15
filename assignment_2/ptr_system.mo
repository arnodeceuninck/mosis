model ptr_system
  velocity_lookup look_up annotation(
    Placement(visible = true, transformation(origin = {-98, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Add sum(k1 = -1)  annotation(
    Placement(visible = true, transformation(origin = {-34, 6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  bang_bang_controller Controller(d_max = 1, d_min = -1, g = 2000)  annotation(
    Placement(visible = true, transformation(origin = {10, 6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  ptr_plant Plant annotation(
    Placement(visible = true, transformation(origin = {56, 6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(look_up.velocity_ideal, sum.u2) annotation(
    Line(points = {{-88, 0}, {-46, 0}}, color = {0, 0, 127}));
  connect(sum.y, Controller.u) annotation(
    Line(points = {{-22, 6}, {0, 6}}, color = {0, 0, 127}));
  connect(Controller.f, Plant.f_traction) annotation(
    Line(points = {{20, 6}, {46, 6}}, color = {0, 0, 127}));
  connect(Plant.v_trolley, sum.u1) annotation(
    Line(points = {{66, 8}, {80, 8}, {80, 40}, {-60, 40}, {-60, 12}, {-46, 12}}, color = {0, 0, 127}));

annotation(
    uses(Modelica(version = "3.2.3")));
end ptr_system;