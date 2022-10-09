class FaasFunc:
    def __init__(self, invocation, node=-1):
        self.invocation = invocation
        self.node = node

    def set_invocation(self, new_invocation):
        self.invocation = new_invocation

    def get_invocation(self):
        return self.invocation

    def set_node(self, node):
        self.node = node

    def get_node(self):
        return self.node


class NodeInfo:
    def __init__(
        self,
        total_mem: float,
        current_cpu_usage: float = -1,
        current_mem_usage: float = -1,
        score: int = 0,
        critical: bool = False,
    ):
        self.total_mem = total_mem
        self.current_cpu_usage = current_cpu_usage
        self.current_mem_usage = current_mem_usage
        self.critical = critical
        self.score = score

    def set_current_cpu_usage(self, current_cpu_usage):
        self.current_cpu_usage = current_cpu_usage

    def get_current_cpu_usage(self):
        return self.current_cpu_usage

    def set_current_mem_usage(self, current_mem_usage):
        self.current_mem_usage = current_mem_usage

    def get_current_mem_usage(self):
        return self.current_mem_usage

    def set_to_critical(self):
        self.critical = True

    def get_critical(self):
        return self.critical

    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score

    def clearNode(self):
        self.current_cpu_usage = -1
        self.current_mem_usage = -1
        self.score = 0
        self.critical = False
