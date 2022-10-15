model PrayHares
  Modelica.Blocks.Interfaces.RealOutput y annotation(
    Placement(visible = true, transformation(origin = {94, -20}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {-4, -10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput x annotation(
    Placement(visible = true, transformation(origin = {82, 18}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {-2, -4}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.Integrator integratorX(y_start = 10)  annotation(
    Placement(visible = true, transformation(origin = {38, 52}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.Integrator integratorY(y_start = 10)  annotation(
    Placement(visible = true, transformation(origin = {36, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant alpha(k = 1.5)  annotation(
    Placement(visible = true, transformation(origin = {-56, 18}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Product ax annotation(
    Placement(visible = true, transformation(origin = {-22, 24}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant beta(k = 0.7)  annotation(
    Placement(visible = true, transformation(origin = {-56, 54}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.MultiProduct bxy(nu = 3)  annotation(
    Placement(visible = true, transformation(origin = {-22, 56}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Math.Add axMinbxy(k1 = -1)  annotation(
    Placement(visible = true, transformation(origin = {8, 52}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.MultiProduct dxy(nu = 3) annotation(
    Placement(visible = true, transformation(origin = {-22, -26}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Math.Product gy annotation(
    Placement(visible = true, transformation(origin = {-22, -58}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant delta(k = 0.2) annotation(
    Placement(visible = true, transformation(origin = {-56, -28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Add dxyMingy(k1 = +1, k2 = -1) annotation(
    Placement(visible = true, transformation(origin = {8, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant gamma(k = 0.2) annotation(
    Placement(visible = true, transformation(origin = {-56, -64}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(beta.y, bxy.u[1]) annotation(
    Line(points = {{-45, 54}, {-29, 54}, {-29, 56}}, color = {0, 0, 127}));
  connect(alpha.y, ax.u2) annotation(
    Line(points = {{-45, 18}, {-35, 18}}, color = {0, 0, 127}));
  connect(bxy.y, axMinbxy.u1) annotation(
    Line(points = {{-14.98, 56}, {-4.98, 56}, {-4.98, 58}}, color = {0, 0, 127}));
  connect(ax.y, axMinbxy.u2) annotation(
    Line(points = {{-11, 24}, {-5, 24}, {-5, 46}}, color = {0, 0, 127}));
  connect(axMinbxy.y, integratorX.u) annotation(
    Line(points = {{19, 52}, {26, 52}}, color = {0, 0, 127}));
  connect(gy.y, dxyMingy.u2) annotation(
    Line(points = {{-11, -58}, {-4, -58}, {-4, -36}}, color = {0, 0, 127}));
  connect(gamma.y, gy.u2) annotation(
    Line(points = {{-45, -64}, {-34, -64}}, color = {0, 0, 127}));
  connect(delta.y, dxy.u[1]) annotation(
    Line(points = {{-45, -28}, {-28, -28}, {-28, -26}}, color = {0, 0, 127}));
  connect(dxy.y, dxyMingy.u1) annotation(
    Line(points = {{-14.98, -26}, {-3.98, -26}, {-3.98, -24}}, color = {0, 0, 127}));
  connect(y, gy.u1) annotation(
    Line(points = {{94, -20}, {94, -86}, {-82, -86}, {-82, -46}, {-38, -46}, {-38, -52}, {-34, -52}}, color = {0, 0, 127}));
  connect(y, dxy.u[2]) annotation(
    Line(points = {{94, -20}, {94, -88}, {-84, -88}, {-84, -8}, {-44, -8}, {-44, -26}, {-28, -26}}, color = {0, 0, 127}));
  connect(x, dxy.u[3]) annotation(
    Line(points = {{82, 18}, {82, -2}, {-36, -2}, {-36, -26}, {-28, -26}}, color = {0, 0, 127}));
  connect(dxyMingy.y, integratorY.u) annotation(
    Line(points = {{20, -30}, {24, -30}}, color = {0, 0, 127}));
  connect(y, bxy.u[2]) annotation(
    Line(points = {{94, -20}, {92, -20}, {92, 86}, {-38, 86}, {-38, 56}, {-28, 56}}, color = {0, 0, 127}));
  connect(integratorX.y, x) annotation(
    Line(points = {{50, 52}, {66, 52}, {66, 18}, {82, 18}}, color = {0, 0, 127}));
  connect(integratorY.y, y) annotation(
    Line(points = {{48, -30}, {74, -30}, {74, -20}, {94, -20}}, color = {0, 0, 127}));
  connect(ax.u1, x) annotation(
    Line(points = {{-34, 30}, {-42, 30}, {-42, 94}, {82, 94}, {82, 18}}, color = {0, 0, 127}));
  connect(bxy.u[3], x) annotation(
    Line(points = {{-28, 56}, {-34, 56}, {-34, 74}, {86, 74}, {86, 18}, {82, 18}}, color = {0, 0, 127}));
  annotation(
    uses(Modelica(version = "4.0.0")));
end PrayHares;
