from const import RESOURCE_STATE_FORAGING


class PointOfInterest:
    def __init__(self, position, decay_time, t, value=None, index=None, is_visible=True):
        self.is_visible = is_visible
        self.decay_time = decay_time
        self.position = position
        self.value = value
        self.index = index
        self.type = t
        self.state = RESOURCE_STATE_FORAGING

    def encode(self):
        return {
            'position': self.position.__dict__,
            'type': self.type
        }
