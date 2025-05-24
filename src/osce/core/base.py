class OSCEModule:
    """Minimal base class for OSCE core modules."""
    def __init__(self, config=None):
        self.config = config or {}
        self.env = None

    async def initialize(self):
        """Optional async initialization hook"""
        pass
