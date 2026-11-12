"""Primary resource bonuses follow declared owners across natural titles."""
import unittest
import test_research_task_navigation as fixtures


class DeclaredOwnerSubjectTests(unittest.TestCase):
    def test_ambiguous_material_title_keeps_builder_owner_priority(self):
        builder = fixtures.record('BUILD', '普通实体处理',
                                  ['处理输入并返回结果。'], symbol='Builder:Consume')
        repair = fixtures.record('REPAIR', '材料维修',
                                 ['处理输入并返回结果。'], symbol='Repairable:Consume')
        for item in (builder, repair):
            item['entry']['api_contracts'][0]['visibility'] = 'Lua component instance method'
        service = fixtures.TaskNavigationTests.service(self, [builder, repair])
        rows = service._research_navigation_rows([], [repair, builder], '制作')
        self.assertEqual(rows[0]['document']['id'], 'BUILD')
        self.assertGreater(rows[0]['score'], rows[1]['score'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
