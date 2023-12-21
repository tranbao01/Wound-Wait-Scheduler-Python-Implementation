from collections import defaultdict


class Action:
    """
    This is the Action class.
    """

    def __init__(self, object_, transaction, type_):
        self.object_ = object_
        self.transaction = transaction
        assert type_ in ("WRITE", "COMMIT", "ROLLBACK", "LOCK", "UNLOCK", "WAIT")
        self.type_ = type_

    def __str__(self):
        return f"Action('{self.object_}', '{self.transaction}', '{self.type_}')"

    __repr__ = __str__

    def __eq__(self, other):
        return ((self.object_ == other.object_) and
                (self.transaction == other.transaction) and
                (self.type_ == other.type_))


# Do not modify any code above this line


def wound_wait_scheduler(actions):
    res = []
    tran_order = {}
    agelist = []
    i = 0
    for action in actions:
        if action.transaction not in tran_order:
            tran_order[action.transaction] = i
            i = i + 1
        if action.transaction not in agelist:
            agelist.insert(0, action.transaction)
    remove_dict = defaultdict(list)
    tran_act = defaultdict(list)

    for action in actions:
        if action.transaction not in tran_act:
            tran_act[action.transaction] = []

    object_dict = {}

    while len(tran_act) > 0:
        if len(actions) > 0:
            action_pop = actions.pop(0)

            tran_act[action_pop.transaction].append(action_pop)

        for transac in sorted(tran_act):
            transac_act_list = tran_act[transac]

            if len(transac_act_list) > 0:

                action = transac_act_list.pop(0)

                if action.type_ == 'WRITE':

                    if action.object_ not in object_dict:
                        object_dict[action.object_] = [True, action.transaction]
                        res.append(Action(action.object_, action.transaction, 'LOCK'))
                        res.append(Action(action.object_, action.transaction, 'WRITE'))

                        remove_dict[action.transaction].append(action)

                    else:

                        if tran_order[action.transaction] < tran_order[object_dict[action.object_][1]]:

                            res.append(Action('NA', object_dict[action.object_][1], 'ROLLBACK'))
                            k = object_dict[action.object_][1]

                            objects_unlock = []
                            for ele in object_dict:
                                if object_dict[ele][1] == object_dict[action.object_][1]:
                                    objects_unlock.append(ele)
                            objects_unlock.sort()
                            count = 0

                            for ele in objects_unlock:

                                res.append(Action(ele, object_dict[ele][1], 'UNLOCK'))
                                z = Action(ele, object_dict[ele][1], 'WRITE')
                                for count2 in range(len(remove_dict)):
                                    if list(remove_dict.keys())[count2] == object_dict[ele][1]:
                                        for y in remove_dict[list(remove_dict.keys())[count2]]:
                                            if y.object_ == ele:
                                                tran_act[object_dict[ele][1]].insert(count,
                                                                                     Action(ele, object_dict[ele][1],
                                                                                            'WRITE'))

                                                count += 1

                                object_dict.pop(ele)
                            remove_dict[k] = []

                            object_dict[action.object_] = [True, action.transaction]
                            res.append(Action(action.object_, action.transaction, 'LOCK'))
                            res.append(Action(action.object_, action.transaction, 'WRITE'))

                            remove_dict[action.transaction].append(action)

                        elif tran_order[action.transaction] == tran_order[object_dict[action.object_][1]]:
                            res.append(Action(action.object_, action.transaction, 'WRITE'))

                            remove_dict[action.transaction].append(action)

                        else:
                            res.append(Action('NA', action.transaction, 'WAIT'))
                            transac_act_list.insert(0, action)

                if action.type_ == 'COMMIT':
                    res.append(Action('NA', action.transaction, 'COMMIT'))

                    objects_unlock = []
                    for ele in object_dict:
                        if object_dict[ele][1] == action.transaction:
                            objects_unlock.append(ele)
                    objects_unlock.sort()
                    for ele in objects_unlock:
                        res.append(Action(ele, action.transaction, 'UNLOCK'))

                        object_dict.pop(ele)

                    tran_act.pop(action.transaction)

                    remove_dict[action.transaction] = []

    return res
