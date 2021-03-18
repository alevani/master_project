class RobotMemoryInformation:
    def __init__(self):
        self.task = 0  # Idle
        self.has_to_work = False
        self.time_before_registration = 0
        self.time_since_last_registration = 0

        # Array of size three telling how much a robot as performed on each task
        self.task_processed_resources = [0, 0, 0]
