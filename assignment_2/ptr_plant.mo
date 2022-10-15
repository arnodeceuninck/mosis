model ptr_plant
  Real v_psgr;
  Real x_trolley;
  parameter Real m_psgr(start=77);
  parameter Real m_trolley(start=2376);
  parameter Real k(start=300);
  parameter Real c(start=150);
  parameter Real c_D(start=0.6);
  parameter Real p(start=1.2);
  parameter Real A(start=9.12);
  Modelica.Blocks.Interfaces.RealInput f_traction annotation(
    Placement(visible = true, transformation(origin = {-96, -2}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-96, -2}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput v_trolley annotation(
    Placement(visible = true, transformation(origin = {90, 14}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {92, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput x_psgr annotation(
    Placement(visible = true, transformation(origin = {90, -14}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {84, -8}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  der(v_psgr) = ((k*(-x_psgr)) + (c*(-v_psgr)) - (m_psgr*(f_traction - (0.5*p*(v_trolley^2)*c_D*A)) / (m_trolley + m_psgr))) / m_psgr;
  der(v_trolley) = (f_traction - (0.5*p*(v_trolley^2)*c_D*A)) / (m_trolley + m_psgr);
  der(x_psgr) = v_psgr;
  der(x_trolley) = v_trolley;
annotation(
    uses(Modelica(version = "3.2.3")));
end ptr_plant;