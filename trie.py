from collections import deque
from state import *

class Trie:
    def __init__(self, keywords=None):
        # 是否建立了failure表
        self.failure_states_constructed = False
        self.root_state = State()

        if keywords is not None:
            self.add_all_keywords(keywords)

    def add_all_keywords(self, keywords):
        for kw in keywords:
            self.add_keyword(kw)

    def add_keyword(self, keyword):
        if keyword is None or len(keyword) == 0:
            return

        current_state = self.root_state
        for char in keyword:
            current_state = current_state.add_state(char)

        current_state.add_emits(keyword)

    def remove_overlaps(self):
        self.allow_overlaps = False

    def remain_longest(self):
        self.remain_longest = True

    def construct_failure_states(self):
        """
        构建failure表
        :return:
        """
        self.root_state.failure = self.root_state

        queue = deque()
        # step1: 将深度为1的结点的failure设为根结点
        states = self.root_state.get_state()
        for stat in states:
            stat.failure = self.root_state
            queue.append(stat)

        self.failure_states_constructed = True

        # step2: 为深度大于1的结点建立failure表，广度优先遍历
        while len(queue) > 0:
            curr_state = queue.popleft()
            transitions = curr_state.get_transitions()
            for tran in transitions:
                target_stat = curr_state.next_state(tran)
                queue.append(target_stat)

                trace_failure_state = curr_state.failure
                while trace_failure_state.next_state(tran) is None:
                    trace_failure_state = trace_failure_state.failure

                new_failure_state = trace_failure_state.next_state(tran)
                target_stat.failure = new_failure_state
                target_stat.add_emits(new_failure_state.emits)

    def check_constructed_failure(self):
        if not self.failure_states_constructed:
            self.construct_failure_states()

    def store_emits(self, pos, curr_stat, emit_lst, word_lst):
        emits = curr_stat.emits
        for emit in emits:
            if emit not in word_lst:
                emit_lst.append(Emit(pos - len(emit) + 1, pos, emit))
                word_lst.append(emit)

    def get_state(self, curr_stat, char):
        """
        获取一个能跳转的state，如果无法跳转，则返回根状态
        :param curr_stat: 当胶状态
        :param char:
        :return:
        """
        new_curr_stat = curr_stat.next_state(char)
        while new_curr_stat is None:
            curr_stat = curr_stat.failure
            new_curr_stat = curr_stat.next_state(char)

        return new_curr_stat

    def parse_text(self, text):
        self.check_constructed_failure()
        pos = 0
        curr_stat = self.root_state
        emit_lst = []
        word_lst = []
        for i in range(0, len(text)):
            curr_stat = self.get_state(curr_stat, text[i])
            self.store_emits(pos, curr_stat, emit_lst, word_lst)
            pos += 1

        return emit_lst

    def tokenize(self, text):
        emit_lst = self.parse_text(text)
        last_emit_end = -1
        word_lst = []
        for emit in emit_lst:
            if emit.start - last_emit_end <= 1:
                # 若当前emit.word是上一次emit.word的后缀，则(emit.start-last_emit_end)<=0
                # 若当前emit.word与上一次emit.word相邻，则(emit.start-last_emit_end)=1
                word_lst.append(emit.word)
                if emit.end > last_emit_end:
                    last_emit_end = emit.end
            else:
                frags = create_fragment(emit, text, last_emit_end)
                word_lst.extend(frags)
                word_lst.append(emit.word)
                last_emit_end = emit.end

        if len(text) - last_emit_end > 1:
            frags = create_fragment(None, text, last_emit_end)
            word_lst.extend(frags)

        return word_lst


def create_fragment(emit, text, last_emit_end):
    if emit is not None:
        frags = text[last_emit_end + 1:emit.start]
    else:
        frags = text[last_emit_end + 1:len(text)]

    return list(frags)


class Emit:
    def __init__(self, start, end, word):
        self.start = start
        self.end = end
        self.word = word


if __name__ == '__main__':
    ac = Trie()
    keywords = ['she', 'he', 'her', 'his']
    ac.add_all_keywords(keywords)
    ac.construct_failure_states()
    emits = ac.parse_text('asheruhis')
