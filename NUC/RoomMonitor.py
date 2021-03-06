from statemachine import StateMachine, State

BED_ROOM = "bedroom"
LIVING_ROOM = "livingroom"
KITCHEN = "Kitchen"
OUTSIDE = "exit"
TOILET = "toilet"

ROOM_TYPES = [BED_ROOM, LIVING_ROOM, KITCHEN, TOILET, OUTSIDE]
ROOM_TYPES_DICT = {i: ROOM_TYPES[i] for i in range(len(ROOM_TYPES))}

class RoomMonitor(StateMachine):
    # Define areas of presence
    living  = State(LIVING_ROOM, initial = True)
    bedroom = State(BED_ROOM)
    kitchen = State(KITCHEN)
    toilet  = State(TOILET)
    out     = State(OUTSIDE)

    # Define transition states

    # Transitions
    liv2bed    = living.to(bedroom)
    bed2liv = bedroom.to(living)

    liv2toilet = living.to(toilet)
    toilet2liv = toilet.to(living)

    liv2kitch  = living.to(kitchen)
    kitch2liv  = kitchen.to(living)

    liv2out    = living.to(out)
    out2liv    = out.to(living)

    toilet2bed = toilet.to(bedroom)
    bed2toilet = bedroom.to(toilet)
    
    liv2x = liv2bed | liv2toilet | liv2kitch | liv2out
    
    def get_all_transitions(self):
        return [t.identifier for t in self.transitions]

    def get_all_states(self):
        return [s.identifier for s in self.states]
    
    def on_liv2x(self):
        print("leaving the living room, going to ", self.current_state.name)