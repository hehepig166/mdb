import os
import unittest

from memory_base.adapters import TextToNEIAdapter
from memory_base.llm.base import LLMClient
from memory_base.llm.providers import OllamaLLM
from memory_base.llm.providers.ollama_provider import ollama_has_model


class TestTextToNEIQualityOllama(unittest.TestCase):
    """
    Optional quality/integration test for TextToNEIAdapter.

    Enable with:
      RUN_OLLAMA_TESTS=1
    Uses:
      OLLAMA_MODEL (default: qwen2.5:3b)
      OLLAMA_BASE_URL (default: http://localhost:11434)
    """

    def test_life_task_cases_boundaries(self) -> None:
        if os.environ.get("RUN_OLLAMA_TESTS") != "1":
            self.skipTest("Set RUN_OLLAMA_TESTS=1 to run Ollama integration tests.")

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
        if not ollama_has_model(base_url=base_url, model=model):
            self.skipTest(f"Ollama not reachable or model not found: {model!r} at {base_url!r}")

        provider = OllamaLLM(base_url=base_url, timeout_s=120.0)
        llm = LLMClient(llm=provider, model=model)
        adapter = TextToNEIAdapter(llm=llm)

        # A list of more natural, longer, less-structured narratives.
        cases = [
            (
                "下班回家已经挺晚了，我其实有点累，但还是想着把今天的运动补上。"
                "我住的地方器械不多，只有一副哑铃和瑜伽垫，时间也就剩半小时。"
                "我没怎么热身就直接开始做深蹲和推举，前几组还行，后面呼吸乱了、动作也开始变形，"
                "膝盖还隐隐有点不舒服，于是我提前停下来了。"
                "回头看，可能是我把强度拉得太快、而且没把动作做扎实；明天我打算先做 5 分钟热身，"
                "用更轻的重量把动作节奏固定下来，再慢慢加量。"
            ),
            (
                "周末我打算把家里收拾一下，但一想到要整理就有点头大，因为东西堆了挺久。"
                "我从客厅角落那堆杂物开始，想着先挪出来再分类，结果越挪越多，地上到处都是，"
                "两个小时过去，垃圾袋还没装满，反而把自己搞得很烦。"
                "我意识到问题不是手不够快，而是没有一个固定流程：每次拿起一个东西就犹豫要不要留，"
                "于是进度被反复打断。下次我准备把整理拆成更小的范围，比如一次只处理一个抽屉，"
                "并且用“扔/留/归位”三个箱子强制决策，定个 25 分钟闹钟到点就停。"
            ),
            (
                "今天本来计划把一个项目方案写出初稿，但打开文档后总觉得思路不够清晰。"
                "我就去查了一些资料和别人的模板，想着先把背景和结构弄明白再写。"
                "结果一篇文章接一篇文章地看，笔记倒是做了不少，但文档本身几乎没动，"
                "到晚上只写了几行标题和两句背景。"
                "复盘一下，其实我需要的只是一个能开始写的骨架，而不是把所有资料都看完。"
                "明天我会先用 15 分钟写一个目录和每节要点，再用定时器限制检索时间，"
                "只查“写不下去的那一小段”。"
            ),
        ]

        issues: list[str] = []

        def has_any(s: str | None, needles: list[str]) -> bool:
            if not s:
                return False
            return any(n in s for n in needles)

        for idx, text in enumerate(cases, start=1):
            nei = adapter.ingest(text)

            # Basic sanity: we expect these to be populated for these inputs.
            if not nei.situation or not nei.goal or not nei.attempt:
                issues.append(f"case {idx}: missing situation/goal/attempt (got: {nei})")
                continue

            # Heuristic boundary checks: situation shouldn't contain reflection/next-time guidance.
            # (We keep this heuristic coarse; it's a guardrail, not a proof.)
            if has_any(nei.situation, ["反思", "下次", "明天我会", "我打算", "准备"]):
                issues.append(f"case {idx}: situation seems to include non-situation content: {nei.situation!r}")

            # Reflection usually contains next-time guidance; if it's empty, flag it (soft).
            if not nei.reflection:
                issues.append(f"case {idx}: reflection empty")

        if issues:
            self.fail("NEI quality issues:\\n- " + "\\n- ".join(issues))


if __name__ == "__main__":
    unittest.main()


