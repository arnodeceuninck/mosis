# Commands used to run generate reachability / coverability / invariant analysis

# Show the help page
python3 RC.py -h

# Generate the reachability graph
python3 RC.py tapaal_codes/ptr_petri_light_v3.tapn reachability.dot reachability

# Generate the coverability graph
python3 RC.py tapaal_codes/ptr_petri_light_v3.tapn coverability.dot coverability

# Invariant analysis
python3 RC.py -p tapaal_codes/ptr_petri_light_v3.tapn deleteme.dot coverability | head -n 6 > invariants.txt
#P-Invariants:
#        M(track.P6) + M(track.P7) = 1
#        M(track.P1) + M(track.P2) = 1
#        M(track.Green) + M(track.Red) = 1
#        M(track.Enter) + M(track.Exit) + M(track.P0) + M(track.P1) + M(track.P3) + M(track.P4) + M(track.P5) + M(track.P6) + M(track.Red) = 3
