import dspy

# --- Module 1: Context Enrichment Examples ---
context_examples_zh = [
    dspy.Example(
        input_text="男子咬狗",
        task_type="headline",
        context_analysis="事实：这是新闻界的经典反例。讽刺：自然秩序的颠倒。文化：'热狗'是一种食物。潜在的双关语：吃热狗 vs 咬真狗。"
    ),
    dspy.Example(
        input_text="喷雾, 椅子",
        task_type="words",
        context_analysis="联想：'喷雾'意味着清洁、绘画或猫标记领地。'椅子'是家具。潜在冲突：喷椅子可能是意外（涂鸦）、清洁失败或恶作剧。"
    )
]

# --- Module 2: Humor Theory Examples ---
theory_examples_zh = [
    dspy.Example(
        input_text="男子咬狗",
        context_analysis="事实：这是新闻界的经典反例... 讽刺：自然秩序的颠倒...",
        script_opposition="正常 (狗咬人) vs 异常 (人咬狗)",
        logical_mechanism="角色互换 / 双关语",
        target="热狗 (食物)",
        humor_strategy="铺垫：按字面意思接受前提。触发点：热狗 (食物) 的双关。笑点：暗示热狗终于开始反击人类了。"
    ),
    dspy.Example(
        input_text="喷雾, 椅子",
        context_analysis="联想：'喷雾'意味着清洁... 潜在冲突：喷椅子可能是意外...",
        script_opposition="保养 (好) vs 毁坏 (坏)",
        logical_mechanism="误用 / 意外后果",
        target="自己",
        humor_strategy="铺垫：描述涉及椅子的正常情况。触发点：以意想不到的方式引入'喷雾' (美黑喷雾)。笑点：椅子现在被'晒黑'了 (毁了)。"
    )
]

# --- Module 3: Draft Examples ---
draft_examples_zh = [
    dspy.Example(
        input_text="男子咬狗",
        humor_strategy="铺垫：按字面意思接受前提... 目标：情境的荒谬性。",
        constraints="最多20个字。",
        draft_text="我想热狗终于开始反击了。"
    ),
    dspy.Example(
        input_text="喷雾, 椅子",
        humor_strategy="铺垫：描述涉及椅子的正常情况... 脚本转换：家具维护 -> 个人灾难。",
        constraints="包含'喷雾'和'椅子'。最多20个字。",
        draft_text="我在椅子上用了美黑喷雾。现在它看起来像是在伊维萨岛度过了一周。"
    )
]

# --- Module 4: Formatter Examples ---
formatter_examples_zh = [
    dspy.Example(
        raw_draft="这是一个笑话：我想热狗终于开始反击了。希望你喜欢！",
        constraints="最多20个字。无介绍。",
        final_joke="我想热狗终于开始反击了。"
    )
]
