

M400 ;Finish moves
G4 P1000 ;Wait for no vibrations
M300 S440 P100 ;Playing a beep

M118 //action:pjhTakeSnapshot

G4 P60000 ;Waiting for Camera taken the Snapshot
M300 S440 P100 ;Playing a beep
G28
