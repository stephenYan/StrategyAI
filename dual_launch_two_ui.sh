#!/bin/bash

# Start two AI each with a UI-debug.
python ../UI-Debug/main.py config/field/sim.cfg blue \
| python ../UI-Debug/main.py config/field/sim.cfg yellow \
| python main.py config/sim.cfg \
| python main.py config/sim_yellow.cfg --on_negative_side

