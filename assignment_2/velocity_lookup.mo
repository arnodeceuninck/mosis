model velocity_lookup
  Modelica.Blocks.Interfaces.RealOutput velocity_ideal annotation(
    Placement(visible = true, transformation(origin = {90, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {90, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
initial equation
  velocity_ideal = 0;
equation  
  if time < 10 then
    velocity_ideal = 0;
  elseif time < 170 then
    velocity_ideal = 10;
  elseif time < 200 then
    velocity_ideal = 8;
  elseif time < 260 then
    velocity_ideal = 18;
  else
    velocity_ideal = 12;
   end if;
      
annotation(
    uses(Modelica(version = "3.2.3")));
end velocity_lookup;