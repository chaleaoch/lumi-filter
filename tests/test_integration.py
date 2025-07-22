"""
Integration tests - test complete workflows

This file tests:
- End-to-end data filtering workflows
- Real-world usage scenarios
- Integration of multiple data types
"""

import datetime
import decimal

from lumi_filter.field import BooleanField, DateField, DecimalField, IntField, StrField
from lumi_filter.model import Model


class UserFilterModel(Model):
    """User filter model - simulates real business scenarios"""

    id = IntField()
    username = StrField()
    email = StrField()
    age = IntField()
    is_active = BooleanField()
    salary = DecimalField()
    join_date = DateField()


class TestIntegrationScenarios:
    """Integration test scenarios"""

    @property
    def sample_users(self):
        """Mock user data"""
        return [
            {
                "id": 1,
                "username": "alice_smith",
                "email": "alice@example.com",
                "age": 28,
                "is_active": True,
                "salary": decimal.Decimal("75000.00"),
                "join_date": datetime.date(2020, 1, 15),
            },
            {
                "id": 2,
                "username": "bob_jones",
                "email": "bob@example.com",
                "age": 32,
                "is_active": True,
                "salary": decimal.Decimal("85000.00"),
                "join_date": datetime.date(2019, 6, 10),
            },
            {
                "id": 3,
                "username": "charlie_brown",
                "email": "charlie@company.com",
                "age": 26,
                "is_active": False,
                "salary": decimal.Decimal("65000.00"),
                "join_date": datetime.date(2021, 3, 22),
            },
            {
                "id": 4,
                "username": "diana_prince",
                "email": "diana@example.com",
                "age": 35,
                "is_active": True,
                "salary": decimal.Decimal("95000.00"),
                "join_date": datetime.date(2018, 11, 5),
            },
            {
                "id": 5,
                "username": "eve_wilson",
                "email": "eve@company.com",
                "age": 29,
                "is_active": False,
                "salary": decimal.Decimal("70000.00"),
                "join_date": datetime.date(2020, 8, 18),
            },
        ]

    def test_hr_search_active_employees(self):
        """HR 场景：搜索活跃员工"""
        # 查找所有活跃的员工，按薪资降序排列
        request_args = {"is_active": "true", "ordering": "-salary"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # 验证结果
        assert len(results) == 3  # 只有3个活跃员工
        assert all(user["is_active"] for user in results)

        # 验证排序：薪资降序
        salaries = [user["salary"] for user in results]
        assert salaries == sorted(salaries, reverse=True)

        # 验证具体结果
        assert results[0]["username"] == "diana_prince"  # 最高薪资
        assert results[-1]["username"] == "alice_smith"  # 最低薪资（在活跃员工中）

    def test_recruitment_age_filter(self):
        """招聘场景：按年龄范围筛选候选人"""
        # 查找年龄在 25-30 之间的用户
        request_args = {"age__gte": "25", "age__lte": "30", "ordering": "age"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # 验证年龄范围
        assert len(results) == 3
        for user in results:
            assert 25 <= user["age"] <= 30

        # 验证排序
        ages = [user["age"] for user in results]
        assert ages == [26, 28, 29]  # 升序排列

    def test_payroll_salary_analysis(self):
        """薪资分析场景：高薪员工统计"""
        # 查找薪资超过 80000 的活跃员工
        request_args = {
            "salary__gte": "80000",
            "is_active": "true",
            "ordering": "username",
        }

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # 验证结果
        assert len(results) == 2
        for user in results:
            assert user["salary"] >= decimal.Decimal("80000")
            assert user["is_active"] is True

        # 验证排序：按用户名字母顺序
        usernames = [user["username"] for user in results]
        assert usernames == ["bob_jones", "diana_prince"]

    def test_email_domain_search(self):
        """邮箱域名搜索场景"""
        # 查找使用 company.com 域名的用户
        request_args = {"email__in": "company.com", "ordering": "join_date"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # 验证结果
        assert len(results) == 2
        for user in results:
            assert "company.com" in user["email"]

        # 验证排序：按加入日期
        join_dates = [user["join_date"] for user in results]
        assert join_dates[0] < join_dates[1]  # 日期升序

    def test_complex_multi_filter_scenario(self):
        """复杂多条件过滤场景"""
        # 业务需求：查找30岁以下的活跃员工，薪资在70000-90000之间，按年龄升序排列
        request_args = {
            "age__lt": "30",
            "is_active": "true",
            "salary__gte": "70000",
            "salary__lte": "90000",
            "ordering": "age",
        }

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # 验证所有条件
        assert len(results) == 1
        user = results[0]

        assert user["age"] < 30
        assert user["is_active"] is True
        assert decimal.Decimal("70000") <= user["salary"] <= decimal.Decimal("90000")
        assert user["username"] == "alice_smith"

    def test_no_results_scenario(self):
        """无结果场景：过于严格的筛选条件"""
        # 查找年龄超过50的用户（在我们的测试数据中不存在）
        request_args = {"age__gt": "50"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().result())

        assert len(results) == 0

    def test_invalid_input_handling(self):
        """处理无效输入的场景"""
        # 包含无效的年龄值和无效字段
        request_args = {
            "age": "invalid_age",  # 无效年龄
            "nonexistent_field": "value",  # 不存在的字段
            "username": "alice_smith",  # 有效过滤条件
            "ordering": "username",
        }

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # 应该忽略无效输入，只应用有效的过滤条件
        assert len(results) == 1
        assert results[0]["username"] == "alice_smith"

    def test_performance_with_large_dataset(self):
        """大数据集性能测试（模拟）"""
        # 创建更大的数据集
        large_dataset = []
        for i in range(100):
            large_dataset.append(
                {
                    "id": i,
                    "username": f"user_{i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + (i % 40),  # 年龄 20-59
                    "is_active": i % 3 != 0,  # 大约 2/3 的用户活跃
                    "salary": decimal.Decimal(
                        str(50000 + (i % 50) * 1000)
                    ),  # 薪资 50000-99000
                    "join_date": datetime.date(2020, 1, 1) + datetime.timedelta(days=i),
                }
            )

        # 执行复杂查询
        request_args = {
            "age__gte": "25",
            "age__lt": "35",
            "is_active": "true",
            "salary__gte": "60000",
            "ordering": "-salary",  # 简化排序，只按薪资降序
        }

        model = UserFilterModel(large_dataset, request_args)
        results = list(model.filter().order().result())

        # 验证结果的正确性（不关注性能，只验证逻辑）
        for user in results:
            assert 25 <= user["age"] < 35
            assert user["is_active"] is True
            assert user["salary"] >= decimal.Decimal("60000")

        # 验证排序：按薪资降序
        if len(results) > 1:
            salaries = [user["salary"] for user in results]
            assert salaries == sorted(salaries, reverse=True)
