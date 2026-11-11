"""Research topic navigation bridges task nouns and declared API owners."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dst-kb-service'))
from dst_kb import native_mechanism


class ResearchOwnerPriorityTests(unittest.TestCase):
    def test_native_owner_topics_bridge_chinese_tasks_and_declarations(self):
        for task, declaration, topic in (
            ('从背包取物品', 'Inventory:RemoveItem', 'inventory'),
            ('拆堆后物品数量', 'Stackable:Get', 'stack'),
            ('跟随者退出时释放关系', 'Follower:SetLeader', 'follower'),
            ('骑乘退出', 'Rider:Dismount', 'rider'),
            ('护甲扣耐久', 'Armor:TakeDamage', 'armor'),
            ('血量变化', 'Health:DoDelta', 'health'),
        ):
            with self.subTest(topic=topic):
                self.assertIn(topic, native_mechanism.navigation_topics(task))
                self.assertIn(topic, native_mechanism.navigation_topics(declaration))
        self.assertNotIn('follower', native_mechanism.navigation_topics('FX symbol跟随偏移'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
