model PreyPredator
 parameter Real a(start=1.5);
 parameter Real b(start=0.7);
 parameter Real d(start=0.2);
 parameter Real g(start=0.2);
  Real numFoxes(start=10, fixed=true);
 Real numHares(start=10, fixed=true);
  Modelica.Blocks.Interfaces.RealOutput numFoxes2 annotation(
   Placement(visible = true, transformation(origin = {110, 14}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {108, 28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
 Modelica.Blocks.Interfaces.RealOutput numHares2 annotation(
   Placement(visible = true, transformation(origin = {110, -16}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {106, -8}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
 equation
 der(numHares) = a*numHares-b*numHares*numFoxes;
 der(numFoxes) = d*numHares*numFoxes-g*numFoxes;
  numFoxes2 = numFoxes;
 numHares2 = numHares;

annotation(
   uses(Modelica(version = "4.0.0")));
end PreyPredator;
