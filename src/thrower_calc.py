from scipy.interpolate import interp1d as func_approx
import config

class Thrower:
    def __init__(self):
        measurements = config.load("throw_dist")
        self.distances = measurements["distances"]
        print(self.distances)
        
        self.throw_speeds = measurements["speeds"]
        print(self.throw_speeds)

        # quit()
        self.throw_speed_func = func_approx(self.distances, self.throw_speeds, fill_value="extrapolate")

        self.measure_list = []

    def calc_throw_speed(self, basket_distance):
        # if basket_distance > some_threshold:
        #     return None
        # if basket_distance < some_threshold:
        #     return None
        throw_speed = int(self.throw_speed_func(basket_distance))
        if len(self.measure_list) < 10:
            self.measure_list.append(throw_speed)
            return None
        else:
            final = int(self.get_average()) # average of ten measurements
            self.measure_list = [] # clear for next measure
            return final

    def get_average(self):
        return sum(self.measure_list) / len(self.measure_list)
