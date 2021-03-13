class RobotMemoryInformation:
    def __init__(self):
        self.task = 0  # Idle
        self.has_to_work = False

        # Array of size three telling how much a robot as performed on each task
        self.task_processed_resources = [0, 0, 0]
