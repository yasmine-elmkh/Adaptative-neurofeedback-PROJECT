class PalierManager:
    def get_palier(self, session_number):
        if session_number <= 3:
            return "P1"
        elif session_number <= 7:
            return "P2"
        elif session_number <= 12:
            return "P3"
        else:
            return "P4"