"""Synthetic predicate/order regressions; no copied vanilla source or ID bypass."""
import copy
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dst_kb.intent_scope import _operations
from dst_kb.predicate_grammar import literal_relations
from dst_kb.task_relevance import _nominal_method_order, _single_request_support


class MixedPredicateOrderTests(unittest.TestCase):
    source = 'Reset() 腐败时先取消task→expiredfn(inst)→再清理旧物。'
    context = {'atom_kind': 'NSF', 'record_pointer': '/claims/0',
        'receivers': ['Perishable'], 'original_content_index': {'synthetic': True},
        'role_bindings': [{'symbol': 'Perishable:Reset', 'receiver': 'Perishable',
                           'role': 'METHOD_SUBJECT'}]}
    query = '审查 Perishable:Reset 的腐败回调与任务清理顺序'

    def test_chinese_predicate_binds_english_resource_objects(self):
        for resource in ('task', 'tasks', 'handle', 'handles', 'callback', 'listeners', 'subscription'):
            with self.subTest(resource=resource):
                self.assertIn('cancel_task', _operations('先取消' + resource + '→再清理旧物', source=True))
        for text in ('取消task的结果', '取消task名称', '取消task状态',
                     '取消完成判定，然后调用task', '取消技能，然后注册task',
                     '调用删除回调的顺序'):
            with self.subTest(text=text):
                self.assertNotIn('cancel_task', _operations(text, source=True))

    def test_arrow_callback_is_an_actual_call(self):
        self.assertTrue({'callback_binding', 'argument_binding'} <= literal_relations(self.source))
        for text in ('先取消task→expiredfn→再清理旧物',
                     'metadata: 先取消task→expiredfn(inst)',
                     '尚未验证先取消task→expiredfn(inst)',
                     '保存字符串 "→expiredfn(inst)"',
                     '保存字符串 "step;→expiredfn(inst)"',
                     '保存字符串 [=[→expiredfn(inst)]=]'):
            with self.subTest(text=text):
                self.assertNotIn('callback_binding', literal_relations(text))

    def test_nominal_order_keeps_whole_original_atom(self):
        result = _single_request_support(self.query, self.source, self.context)
        self.assertTrue(result['whole_atom_delivery_allowed'])
        self.assertEqual(result['relevance_original_pointer'], '/claims/0')
        self.assertEqual(result['support_meaning'], 'TASK_RELEVANCE_ONLY')
        self.assertFalse(result['query_assertion_verified'])
        self.assertFalse(result['method_contract_verified'])

    def test_resolved_referent_can_precede_the_nominal_review(self):
        query = ('我的物品会手动调用 Perishable:Reset。'
                 '请审查该组件的腐败回调与任务清理顺序，限定这个方法的实际路径。')
        result = _single_request_support(query, self.source, self.context)
        self.assertTrue(result['whole_atom_delivery_allowed'])

    def test_unknown_aspects_and_explicit_steps_cannot_borrow_method_head(self):
        for query in ('审查 Perishable:Reset 的碰撞与任务清理顺序',
                      '审查 Perishable:Reset 的存档与任务清理顺序',
                      '审查 Perishable:Reset 的 Other:Apply 与任务清理顺序',
                      '审查 Perishable:Reset 先调用 Other:Apply 再清理任务的顺序',
                      '审查 Combat:Reset 的腐败回调与任务清理顺序'):
            with self.subTest(query=query):
                self.assertFalse(_single_request_support(query, self.source, self.context)
                                 ['whole_atom_delivery_allowed'])

    def test_explicit_method_exclusion_cannot_return_a_supported_strict_result(self):
        for suffix in ('。排除 Perishable:Reset 的实现。', '。不要 Perishable:Reset。'):
            with self.subTest(suffix=suffix):
                result = _single_request_support(self.query + suffix, self.source, self.context)
                self.assertFalse(result['whole_atom_delivery_allowed'])
                self.assertTrue(result['excluded_source_scope'])
        result = _single_request_support(self.query + '。排除 Combat:Hit 的实现。',
                                         self.source, self.context)
        self.assertTrue(result['whole_atom_delivery_allowed'])

    def test_role_owner_and_local_source_boundaries_remain_required(self):
        for change in ('role', 'receiver', 'pointer'):
            context = copy.deepcopy(self.context)
            if change == 'role':
                context['role_bindings'][0]['role'] = 'BOUNDED_CALLEE_CALLSITE'
            elif change == 'receiver':
                context['role_bindings'][0].update(symbol='Combat:Reset', receiver='Combat')
            else:
                context['record_pointer'] = ''
            with self.subTest(change=change):
                self.assertFalse(_nominal_method_order(self.query, self.source, context))
        for source in ('Reset() 腐败时先取消task；Combat:Hit 调用 expiredfn(inst)。',
                       'Reset() 腐败时取消task。Other:Apply 先调用 expiredfn(inst)。',
                       'Reset() 腐败时先取消task→expiredfn→再清理旧物。'):
            with self.subTest(source=source):
                self.assertFalse(_nominal_method_order(self.query, source, self.context))


if __name__ == '__main__':
    unittest.main(verbosity=2)
