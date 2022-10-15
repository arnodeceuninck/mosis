model CostFunction
  Modelica.Blocks.Interfaces.RealInput v_ideal annotation(
    Placement(visible = true, transformation(origin = {-100, 28}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-94, 28}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput x_psgr annotation(
    Placement(visible = true, transformation(origin = {100, 70}, extent = {{20, -20}, {-20, 20}}, rotation = 0), iconTransformation(origin = {74, 40}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput cost annotation(
    Placement(visible = true, transformation(origin = {0, -98}, extent = {{-10, -10}, {10, 10}}, rotation = -90), iconTransformation(origin = {10, -88}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput v_trolley annotation(
    Placement(visible = true, transformation(origin = {100, -70}, extent = {{20, -20}, {-20, 20}}, rotation = 0), iconTransformation(origin = {102, -66}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Real speed_diff;
equation
  // v_ideal - v_trolley must be small (in order to attain the ideal velocity as fast as possible)
  speed_diff = v_ideal - v_trolley;
  // x_psgr must be small (to not let the passenger fall)
  
    // If the passenger falls
  if abs(x_psgr) > 0.35 then
    // discard
    cost = 100000;
  else
    // 2nd part has lower weight because displacement doesn't matter that much as long as the passenger doesn't fall
    cost = speed_diff*speed_diff + 0.5 * x_psgr*x_psgr;
    // cost = speed_diff + 0.5 * x_psgr;
  end if;
  annotation(
    uses(Modelica(version = "4.0.0")),
    experiment(StartTime = 0, StopTime = 1, Tolerance = 1e-06, Interval = 0.002));
end CostFunction;
