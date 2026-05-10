"""
Skills 自动注册入口
在应用启动时自动加载所有数据库技能
"""

from app.skills.base import skill_registry
from app.skills.databases.mysql import MySQLSkill
from app.skills.databases.oracle import OracleSkill
from app.skills.databases.postgresql import PostgreSQLSkill
from app.skills.databases.tidb import TiDBSkill
from app.skills.databases.oceanbase import OceanBaseSkill
from app.skills.databases.self_db import SelfDBSkill


def init_skills():
    """初始化所有技能库"""
    skill_registry.register(MySQLSkill())
    skill_registry.register(OracleSkill())
    skill_registry.register(PostgreSQLSkill())
    skill_registry.register(TiDBSkill())
    skill_registry.register(OceanBaseSkill())
    skill_registry.register(SelfDBSkill())
