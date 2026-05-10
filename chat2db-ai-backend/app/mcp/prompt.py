"""
MCP - Prompt 层
负责用户问题理解、意图识别、Query增强、输出格式化
"""

import re
from typing import Dict, List, Optional, Tuple

from app.core.logger import logger


class IntentType:
    TROUBLESHOOT = "troubleshoot"
    TIPS = "tips"
    PARAMETERS = "parameters"
    SOLUTION = "solution"
    SQL = "sql"
    GENERAL = "general"


class PromptEngine:
    """提示词引擎"""

    INTENT_KEYWORDS = {
        IntentType.TROUBLESHOOT: [
            "排查", "故障", "报错", "错误", "crash", "挂掉", "无法连接",
            "慢", "卡顿", "延迟", "宕机", "oom", "死锁", "锁等待", "抖动", "满了"
        ],
        IntentType.TIPS: [
            "技巧", "trick", "优化", "最佳实践", "常用", "快捷",
            "怎么查看", "如何快速", "命令", "语句", "查看"
        ],
        IntentType.PARAMETERS: [
            "参数", "配置", "设置", "调优", "tune", "buffer", "cache",
            "内存", "连接数", "并发", "线程", "调整"
        ],
        IntentType.SOLUTION: [
            "方案", "解决", "怎么处理", "怎么办", "修复", "恢复",
            "迁移", "升级", "备份", "容灾", "重建"
        ],
        IntentType.SQL: [
            "sql", "语句", "查询", "select", "insert", "update", "delete",
            "建表", "索引", "执行计划"
        ],
    }

    def analyze(self, query: str) -> Tuple[str, str]:
        """分析用户query，返回增强后的query和意图"""
        intent = self._detect_intent(query)
        enhanced = self._enhance_query(query, intent)
        logger.info("prompt_analyzed", intent=intent, original=query[:50])
        return enhanced, intent

    def _detect_intent(self, query: str) -> str:
        q = query.lower()
        scores = {k: 0 for k in self.INTENT_KEYWORDS}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in q:
                    scores[intent] += 1

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else IntentType.GENERAL

    def _enhance_query(self, query: str, intent: str) -> str:
        templates = {
            IntentType.TROUBLESHOOT: f"故障排查: {query} (请提供排查思路、根因分析、解决步骤、风险避坑)",
            IntentType.TIPS: f"实用技巧: {query} (请提供具体操作命令、SQL语句和注意事项)",
            IntentType.PARAMETERS: f"参数配置: {query} (请推荐参数值、说明影响范围、是否需要重启、风险点)",
            IntentType.SOLUTION: f"解决方案: {query} (请提供完整方案、风险点、回滚预案、变更窗口建议)",
            IntentType.SQL: f"SQL相关: {query} (请提供SQL语句、执行计划分析、索引建议和性能影响)",
        }
        return templates.get(intent, query)

    def format_answer(self, raw_answer: str, intent: str, sources: List[str] = None, model_used: str = None) -> Dict:
        """格式化最终返回给前端的数据结构"""
        sections = self._parse_sections(raw_answer)

        return {
            "type": intent,
            "sections": sections,
            "sources": sources or [],
            "suggestion": self._generate_suggestion(intent),
            "model_used": model_used,
        }

    def _parse_sections(self, text: str) -> List[Dict[str, str]]:
        sections = []
        lines = text.split("\n")
        current_title = "回答"
        current_content = []

        for line in lines:
            stripped = line.strip()
            if re.match(r"^(\d+[\.、]|#+\s|【.+?】|[一二三四五六七八九十]+[、\.])", stripped):
                if current_content:
                    sections.append({
                        "title": current_title,
                        "content": "\n".join(current_content).strip(),
                    })
                current_title = re.sub(r"^[\d#\.、【】\s]+", "", stripped)
                current_content = []
            else:
                current_content.append(stripped)

        if current_content:
            sections.append({
                "title": current_title,
                "content": "\n".join(current_content).strip(),
            })

        if not sections:
            sections.append({"title": "回答", "content": text.strip()})

        return sections

    def _generate_suggestion(self, intent: str) -> str:
        suggestions = {
            IntentType.TROUBLESHOOT: "如果以上排查无法定位问题，建议收集错误日志、监控截图和堆栈信息进一步分析。",
            IntentType.TIPS: "建议在生产环境验证前，先在测试环境演练相关命令，并确保有备份。",
            IntentType.PARAMETERS: "参数修改前请确保已做好配置备份，选择业务低峰期执行，并准备回滚方案。",
            IntentType.SOLUTION: "执行方案前请确认已制定回滚预案，在变更窗口期操作，并通知相关干系人。",
            IntentType.SQL: "建议在测试环境验证SQL执行计划，确认无全表扫描和笛卡尔积后再上生产。",
        }
        return suggestions.get(intent, "如有疑问，欢迎继续提问。")
