"""Literal predicate navigation, never API identity, polarity or contract proof.

Callers retain source-role, owner, scope and evidence checks. A returned relation
may describe either a positive behavior or its explicit negation.
"""
import re


def _rx(pattern):
    return re.compile(pattern, re.I | re.ASCII)


_METADATA = _rx(r'^\s*(?:metadata|title|navigation|topics?|tags?|aliases|scope|API names|'
                r'元数据|标题|导航|标签|别名|范围)\s*[:：]')
_EPISTEMIC = _rx(r'\b(?:evidence|proof|unverified|unproven|unknown|uncertain)\b'
                 r'|\bnot\s+(?:verified|proven|confirmed|established)\b'
                 r'|证据|未验证|未证明|未确认|未知|不确定')
_CLAUSE = re.compile(r'[。；;！？\n]+|(?<=[.!?])\s+')
_RETIRE_VERB = r'(?:removes?|removed|removing|cancels?|canceled|cancelled|cancelling|canceling|'
_RETIRE_VERB += r'unregisters?|unregistered|unsubscribes?|unsubscribed|detaches?|detached|clears?|cleared|releases?|released)'
_RESOURCE = r'(?:tasks?|handles?|callbacks?|listeners?|subscriptions?|watchers?)'
_OTHER_PREDICATE = r'(?:register\w*|subscrib\w*|add\w*|creat\w*|initializ\w*|return\w*|calls?|invok\w*|execut\w*|then|after)'
_RETIRE_RESOURCE = _rx(r'\b' + _RETIRE_VERB + r'\b\s+'
    r'(?:(?!' + _OTHER_PREDICATE + r'\b|and\b|but\b|while\b)\S+\s+){0,7}' + _RESOURCE + r'\b')
_RESOURCE_RETIRED = _rx(r'\b' + _RESOURCE + r'\b\s+'
    r'(?:(?:is|are|was|were|gets?|have|has|been|explicitly|first|then)\s+){0,4}'
    + r'(?:removed|cancelled|canceled|unregistered|unsubscribed|detached|cleared|released)\b')
_RETIRE_ZH = re.compile(
    r'(?:解除|移除|解绑|取消|卸除|清理|清除|注销|删除)'
    r'(?:(?:已(?:经)?|所)(?:登记|注册|创建)(?:的)?'
    r'|(?!登记|注册|创建|返回|调用|执行|触发|之后|随后|然后|后|以及|同时|并且)[^，,。；;！？!?\n]){0,18}'
    r'(?:回调|监听(?:器)?|订阅|任务|句柄)')
_RESOURCE_RETIRED_ZH = re.compile(r'(?:任务|句柄|回调|监听(?:器)?|订阅)(?:被|已被|已经|已)?'
                                 r'(?:解除|移除|解绑|取消|清理|清除|注销|删除)')
_RELEASE_OBJECT_ZH = (r'(?:(?:回调|监听器|监听(?!器)|订阅|任务)(?:句柄|(?!句柄))|句柄|\b' + _RESOURCE + r'\b)'
                      r'(?![ \t]*(?:的)?(?:结果|返回值|参数|名称|名字|状态|数量|完成(?:标记|判定)))')
_RELEASE_MODIFIER_ZH = (r'(?:这些|那些|所有|全部|当前|原有|旧|新|其|该|自身|自己的|自己|它的|'
                        r'所?(?:持有|保留|保存|登记|注册|创建)的)')
# “释放”须带资源宾语；不跨过技能/信号等其他受事去借用后文的监听。
_RELEASE_ZH = _rx(r'释放(?:掉)?[ \t]*(?:' + _RELEASE_MODIFIER_ZH + r'[ \t]*)*' + _RELEASE_OBJECT_ZH)
_RESOURCE_RELEASED_ZH = _rx(_RELEASE_OBJECT_ZH +
    r'(?:[ \t]*(?:和|与|及|、)[ \t]*' + _RELEASE_OBJECT_ZH + r')*[ \t]*'
    r'(?:(?:没有|未|不曾)?(?:已(?:经)?)?被|(?:该|应该|需要|应当)?(?:怎样|怎么|如何)|'
    r'(?:是否|要不要)(?:需要|应该)?)[ \t]*释放(?:掉)?')
_STOP_TASK = _rx(
    r'停止[ \t]*(?:(?:这些|那些|所有|全部|当前|该|旧|原有)(?:的)?[ \t]*)*'
    r'(?:更新|周期|定时|延迟|后台)?任务'
    r'(?![ \t]*(?:的)?(?:名称|名字|标签|计数|数量|参数|状态|结果))'
    r'|\b(?:stops?|stopped|stopping)\s+(?:(?:the|its|these|old|previous|existing)\s+)*'
    r'(?:(?:update|updating|periodic|scheduled|delayed|background)\s+)?tasks?\b'
    r'(?!\s+(?:names?|labels?|counts?|results?|arguments?|parameters?|status)\b)')
_RESOURCE_NOT_TARGET = _rx(r'^\s*(?:return\s+values?|results?|arguments?|parameters?|names?|labels?|counts?|status|metadata)\b|^\s*(?:的\s*)?(?:结果|返回值|参数|名称|名字|标签|计数|数量|状态)')
_CANCEL_RESOURCE_SHORTHAND = _rx(
    r'\bCancel(?:[ \t]*/[ \t]*nil)?[ \t]*(?:更新|周期|定时|延迟|后台)?'
    r'(?:(?:self|inst)\.)?(?:task|tasks|handle|handles)\b')
_RETIRE_CALL = _rx(
    r'\b(?:RemoveEventCallback|RemoveAllEventCallbacks|CancelAllPendingTasks)\s*\('
    r'|\b[A-Za-z_]*?(?:task|handle)[A-Za-z_]*\s*:\s*Cancel\s*\('
    r'|\bStopUpdating\s*\(')
_BARE_CANCEL = _rx(r'^\s*(?:please\s+)?(?:cancel|stopupdating|unsubscribe)'
                   r'(?:\s+(?:it|them))?\s*[.!?。！？]*\s*$')
_REGISTER = _rx(
    r'\b(?:registers?|registered|subscribes?|subscribed|binds?|attaches?|installs?)\b\s+'
    r'(?:(?!and\b|but\b)\S+\s+){0,6}(?:callbacks?|listeners?|subscriptions?|watchers?)\b'
    r'|\bListenForEvent\s*\(|(?:登记|注册|订阅|绑定).{0,14}(?:回调|监听|订阅)')
_PASSIVE_UPDATE = _rx(
    r'\b(?:is|are|was|were|has been|have been)\s+(?:not\s+)?updated\s+by\s+'
    r'(?:the\s+)?[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*\b')


def _clauses(text):
    return [value.strip() for value in _CLAUSE.split(text) if value.strip()]


_LIFECYCLE_CALLBACK_NAME_ZH = re.compile(r'(?:删除|移除|销毁)(?:回调|监听器?)')
_NOMINAL_CALLBACK_USE_ZH = re.compile(r'(?:调用|执行|触发|覆盖|包装|设置|注册|添加|定义|配置)\s*$')
_NOMINAL_CALLBACK_TAIL_ZH = re.compile(
    r'^\s*(?:当作|视为|等同|(?:的\s*)?(?:契约|语义|签名|参数|返回值|名称|名字|结果))'
    r'|^\s*(?:与|和|及|、|/)[^，,。；;！？!?\n]{0,60}(?:契约|语义|签名|参数|返回值|差异|区别|当作|视为|等同)'
    r'|^\s*(?:在[^，,。；;！？!?\n]{1,40})?的\s*'
    r'(?:事件|调用|执行|触发)?(?:顺序|先后|次数|时机|参数|返回值|语义|契约)')


def _retirement_predicate_text(clause):
    # A lifecycle callback name can contain a deletion verb without requesting
    # retirement of that callback. Mask only that nominal occurrence, keeping a
    # later independent cleanup predicate and explicit resource modifiers.
    spans = []
    for match in _LIFECYCLE_CALLBACK_NAME_ZH.finditer(clause):
        before, after = clause[:match.start()], clause[match.end():]
        if (_NOMINAL_CALLBACK_USE_ZH.search(before) or _NOMINAL_CALLBACK_TAIL_ZH.search(after)
                or re.search(r'在\s*$', before) and re.match(r'\s*(?:中|内|里)', after)):
            spans.append((match.start(), match.end()))
    for start, end in reversed(spans):
        clause = clause[:start] + ' ' * (end - start) + clause[end:]
    return clause


def _retires_resource(clause):
    clause = _retirement_predicate_text(clause)
    if _RETIRE_CALL.search(clause) or _BARE_CANCEL.fullmatch(clause):
        return True
    for pattern in (_RETIRE_RESOURCE, _RESOURCE_RETIRED, _RETIRE_ZH, _RESOURCE_RETIRED_ZH,
                    _RELEASE_ZH, _RESOURCE_RELEASED_ZH, _STOP_TASK, _CANCEL_RESOURCE_SHORTHAND):
        for match in pattern.finditer(clause):
            if not _RESOURCE_NOT_TARGET.search(clause[match.end():]):
                return True
    return False


def refine_operations(text, operations, source=False):
    """Bind cleanup to its resource, preserving all unrelated operation labels.

    cancel_task remains the compatibility label for task/subscription retirement.
    Bare cancel commands keep their existing anaphoric meaning; named buff detach
    and cancellation of completion do not establish a task or subscription.
    """
    result = set(operations)
    clauses = _clauses(text)
    usable = [clause for clause in clauses
              if not _METADATA.search(clause) and not (source and _EPISTEMIC.search(clause))]
    retiring = any(_retires_resource(clause) for clause in usable)
    if any(_PASSIVE_UPDATE.search(clause) for clause in usable):
        result.add('update_state')
    if retiring:
        result.add('cancel_task')
        if not any(_REGISTER.search(clause) for clause in usable):
            result.discard('subscribe_event')
    else:
        result.discard('cancel_task')
        if source and not usable:
            result.discard('subscribe_event')
    return result


_FALLBACK = _rx(
    r'\bfalls?\s+back\b'
    r'|\b(?:has|have|had|provides?|uses?|enters?|offers?)\b'
    r'\s+(?:(?!evidence\b|proof\b)[\w-]+\s+){0,7}fallback\b'
    r'|\b(?:does?|did)\s+not\s+(?:provide|use|enter|offer|have)\b'
    r'\s+(?:[\w-]+\s+){0,7}fallback\b'
    r'|(?:进入|采用|走|提供|没有|不提供|不采用).{0,40}(?:回退|fallback)')
_PARAM_VERB = _rx(r'\b(?:takes?|accepts?|receives?)\b|(?:接受|接收|传入|形参为|参数为|签名为)')
_PARAM_NOUN = _rx(r'\b(?:arguments?|parameters?|inputs?|signature)\b|参数|实参|形参|签名')
_FORMAL_HEAD = _rx(r'^\s*(?:the\s+)?(?:helper|function|method)\b'
                   r'|^\s*(?:[A-Za-z_]\w*[.:]\w+|(?:[A-Z][a-z0-9]+){2,}\w*)\b')
_PARAM_LIST = _rx(r'\b[A-Za-z_]\w*\s*,\s*[A-Za-z_]\w*\b')
_PARAM_CODE = _rx(r'`[A-Za-z_]\w*`|\b[A-Za-z_]\w*_[A-Za-z_]\w*\b|\([A-Za-z_]\w*\s*,')
_CALLBACK_NAME = r'(?:[A-Za-z_]\w*[.:])*(?:callback|[A-Za-z_]\w*(?:fn|callback))'
_CALLBACK_CALL = _rx(
    r'\b(?:calls?|invokes?)\s+(?:the\s+)?' + _CALLBACK_NAME + r'\b'
    r'|(?:调用|执行|触发)\s*(?:所保存的|现有的|该|此)?(?:回调(?:函数)?|'
    + _CALLBACK_NAME + r'(?![A-Za-z0-9_]))')
_CALLBACK_INVOCATION = _rx(
    r'(?:' + _CALLBACK_CALL.pattern + r')(?:\s+as\s+(?:a\s+)?method)?'
    r'\s*(?:with\b|\(|（|并传入|，传入|传入)')
_EVENT_FINITE = (r'(?:emits?|emitted|push(?:es|ed)?|sends?|sent|dispatch(?:es|ed)?|'
                 r'fires?|fired|deliver(?:s|ed)?|receives?|received)')
_EVENT_ING = r'(?:emitting|pushing|sending|dispatching|firing|delivering|receiving)'
_EVENT_PARTICIPLE = r'(?:emitted|pushed|sent|dispatched|fired|delivered|received)'
_NOT_EVENT_ARGUMENT = (r'(?!\s+as\s+(?:(?:an?|the|its|their|that|this|named)\s+){0,3}'
                       r'(?:arguments?|parameters?|inputs?)\b)')
_EVENT_VERB = (r'(?<![\'\"`])\b(?:' + _EVENT_FINITE + r'|'
    r'(?:without|while|when|before|after|by|upon|is|are|was|were|be|been|being|keeps?|continues?|starts?|stops?)'
    r'\s+(?:(?:not|never|already|still|explicitly)\s+){0,2}' + _EVENT_ING + r')\b')
_EVENT_OBJECT = (r'(?:(?:no|not|an?|the|its|that|this|named|completion|ordinary|explicit)\s+){0,5}'
    r'(?:events?|notifications?|messages?)\b'
    r'(?!\s+(?:arguments?|parameters?|names?|identifiers?|symbols?|fields?|handlers?|callbacks?|types?|data|payload|metadata)\b)'
    + _NOT_EVENT_ARGUMENT)
_EVENT_PREDICATE = _rx(
    _EVENT_VERB + r'\s+' + _EVENT_OBJECT
    + r'|' + _EVENT_VERB + r'\s+(?:`[^`]+`|[\'\"][^\'\"]+[\'\"])' + _NOT_EVENT_ARGUMENT
    + r'|(?<![\'\"`])\b' + _EVENT_OBJECT
    + r'\s+(?:is|are|was|were|be|been|gets?|has|have|had)\s+'
    r'(?:(?:not|never|being|been|already|still|explicitly|yet)\s+){0,4}' + _EVENT_PARTICIPLE + r'\b' + _NOT_EVENT_ARGUMENT
    + r'|\bPushEvent\s*\('
    r'|(?:推送|派发|分派|发出|发送|触发|接收|收到)\s*'
    r'(?:(?!参数|实参|形参|然后|之后|再|并|后)[^，,。；;!?！？\n]){0,12}(?:事件|通知|消息)'
    r'|(?:推送|派发|分派|发出|发送)\s*[A-Za-z_]\w*\b')
_EVENT_NEGATIVE = _rx(
    r'\b(?:does?|did|will)\s+not\s+(?:emit|push|send|dispatch|fire|deliver)\b\s+'
    + _EVENT_OBJECT)
_QUEUE = _rx(
    r'\b(?:enqueues?|enqueued)\s+\S+'
    r'|\b(?:data|packet|payload|record|item|sender)\s+(?:is|are|was|were)\s+enqueued\b'
    r'|\b(?:places?|push(?:es)?|puts?|adds?)\s+[^.;!?\n]{1,90}\s+(?:in|into|on|onto)\s+(?:the\s+|a\s+)?queue\b'
    r'|(?:把|将)[^。；;！？!?\n]{1,80}(?:入队|放入队列|加入队列)'
    r'|\S.{0,60}(?:被)?入队')


def literal_relations(text):
    """Return existing relation names supported by an actual local predicate.

    There is no owner resolution or positive/negative truth conversion here.
    Titles, symbol lists and epistemic statements cannot supply these predicates.
    """
    found = set()
    for clause in _clauses(text):
        if _METADATA.search(clause) or _EPISTEMIC.search(clause):
            continue
        if _FALLBACK.search(clause):
            found.add('result_behavior')
        if _PASSIVE_UPDATE.search(clause):
            found.add('field_mutation')
        if _retires_resource(clause):
            found.add('task_cancellation')
        if _CALLBACK_CALL.search(clause):
            found.add('callback_binding')
        if _CALLBACK_INVOCATION.search(clause):
            found.add('argument_binding')
        parameter = _PARAM_VERB.search(clause)
        if parameter:
            tail = clause[parameter.end():]
            if (_PARAM_NOUN.search(tail) or _PARAM_NOUN.search(clause[:parameter.start()])
                    or _FORMAL_HEAD.search(clause) and (_PARAM_LIST.search(tail) or _PARAM_CODE.search(tail))):
                found.add('argument_binding')
        if _EVENT_PREDICATE.search(clause) or _EVENT_NEGATIVE.search(clause) or _QUEUE.search(clause):
            found.add('event_delivery')
    return found


_ABSENCE_MARKER = _rx(r'(?:has|have|had)\s+no|没有|尚无|缺少|absent')
_RUNTIME_OBJECT = _rx(
    r'\b(?:arguments?|parameters?|handlers?|handles?|listeners?|callbacks?|tasks?|fields?|keys?|slots?|'
    r'data|values?|payload|records?|components?|references?|entities|entity|targets?)\b'
    r'|参数|实参|形参|句柄|回调|监听|任务|字段|键|槽位|数据|数值|组件|引用|实体|目标对象')


def is_factual_absence(text, marker_start, marker_end):
    """Recognize absence of a runtime object/parameter, never absence of proof."""
    if (type(marker_start) is not int or type(marker_end) is not int
            or not 0 <= marker_start < marker_end <= len(text)):
        return False
    if not _ABSENCE_MARKER.fullmatch(text[marker_start:marker_end]):
        return False
    boundaries = list(_CLAUSE.finditer(text))
    start = max((match.end() for match in boundaries if match.end() <= marker_start), default=0)
    end = min((match.start() for match in boundaries if match.start() >= marker_end), default=len(text))
    clause = text[start:end]
    if _METADATA.search(clause) or _EPISTEMIC.search(clause):
        return False
    following = text[marker_end:end]
    if re.match(r'\s*(?:verified|proven|confirmed|documented)\b|\s*(?:已验证|已证明|已确认)', following, re.I):
        return False
    head = re.split(r'[，,。.!?！？;；\n]', following, maxsplit=1)[0]
    target = _RUNTIME_OBJECT.search(head[:80])
    if not target:
        return False
    modifiers = head[:target.start()]
    if re.search(r'\b(?:fallback|contract|interface|guarantee|of|about|for|which|that)\b'
                 r'|回退|合同|契约|接口|保证|调用|创建|证明|是否|会|但|而', modifiers, re.I):
        return False
    return True
