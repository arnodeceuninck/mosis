model PreyPredator
 Real numFoxes(start=10, fixed=true);
 Real numHares(start=10, fixed=true);
equation
 der(numHares) = 1.5*numHares-0.7*numHares*numFoxes;
 der(numFoxes) = 0.2*numHares*numFoxes-0.2*numFoxes;

end PreyPredator;