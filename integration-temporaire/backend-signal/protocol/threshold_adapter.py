class ThresholdAdapter:
    def adapt(self, success_rate, current_threshold):
        if success_rate > 60:
            return current_threshold + 0.5
        elif success_rate < 40:
            return current_threshold - 0.5
        return current_threshold