class State:
    def __init__(self, depth=0):
        # 状态深度
        self.depth = depth
        # output表
        self.emits = []
        # goto表
        self.success = {}
        # fail表
        self.failure = None

    def add_emits(self, keyword):

        if type(keyword).__name__ == 'list':
            self.emits.extend(keyword)
        else:
            self.emits.append(keyword)

    def next_state(self, char, ignoreRootState=False):
        """
        转移到下一个状态
        :param char:
        :param ignoreRootState: 是否忽略根节点，如果是根节点调用这个方法则应该设为false，否则为true
        :return:
        """
        next_stat = self.success.get(char)
        # 如果ignoreRootState==False，且next state是根结点，就返回根结点
        if not ignoreRootState and next_stat is None and self.depth == 0:
            next_stat = self

        return next_stat

    def next_state_ignore_rootstate(self, char):
        next_stat = self.next_state(char, True)
        return next_stat

    def add_state(self, char):
        next_stat = self.next_state_ignore_rootstate(char)
        if next_stat is None:
            next_stat = State(self.depth + 1)
            self.success[char] = next_stat

        return next_stat

    def get_state(self):
        return self.success.values()

    def get_transitions(self):
        return self.success.keys()
