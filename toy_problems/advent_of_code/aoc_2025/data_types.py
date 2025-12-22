



class SmallInt(int):
    MOD = 100
    zero_counter = 0
    passed_zeroes = 0
    previous_value = 0

    def __new__(cls, value):

        if value < 0:
            dial_value = value #+ cls.MOD
            if cls.previous_value == 0:
                dial_value += cls.MOD
            while dial_value < 0:
                dial_value += cls.MOD
                cls.passed_zeroes += 1
        elif value == 0:
            dial_value = value
        else: # value > 0
            dial_value = value 
            while dial_value > cls.MOD:
                dial_value -= cls.MOD
                cls.passed_zeroes += 1
        final_state = dial_value % cls.MOD
        if final_state == 0:
            cls.zero_counter += 1
        cls.previous_value = final_state
        return super().__new__(cls, final_state)

    # addition
    def __add__(self, other):
        return SmallInt(int(self) + int(other))

    # subtraction
    def __sub__(self, other):
        return SmallInt(int(self) - int(other))

    # radd and rsub allow things like 5 + SmallInt(40)
    def __radd__(self, other):
        return SmallInt(int(other) + int(self))

    def __rsub__(self, other):
        return SmallInt(int(other) - int(self))