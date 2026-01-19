import dspy

# --- Chinese Signatures ---

class DescribeImageZh(dspy.Signature):
    """
    生成图像的详细描述，用作幽默生成的上下文。
    关注视觉细节、动作和情绪。
    """
    image_input = dspy.InputField(desc="要描述的图像。")
    description = dspy.OutputField(desc="图像的详细文字描述。")

class EnrichContextZh(dspy.Signature):
    """
    分析输入并检索相关的事实和文化背景，以辅助笑话生成。
    对于标题，识别核心的讽刺或荒谬之处。
    对于词对，识别常见的联想和潜在的冲突。
    """
    input_text = dspy.InputField(desc="新闻标题、词对或图像描述。")
    task_type = dspy.InputField(desc="任务类型：'headline'（标题）、'words'（词对）或 'image'（图像）。")
    
    context_analysis = dspy.OutputField(desc="事实背景、文化联想和潜在的幽默切入点。")

class DevelopHumorStrategyZh(dspy.Signature):
    """
    应用基于脚本的幽默语义理论 (SSTH) 来开发笑话概念。
    识别两个对立的脚本以及连接它们的逻辑机制。
    """
    input_text = dspy.InputField(desc="原始输入（标题、词语或图像描述）。")
    context_analysis = dspy.InputField(desc="丰富的上下文、联想和事实。")
    
    script_opposition = dspy.OutputField(desc="两个冲突的脚本（例如：真实 vs 虚幻，正常 vs 异常）。")
    logical_mechanism = dspy.OutputField(desc="连接脚本的认知规则（例如：反转、夸张、并置）。")
    target = dspy.OutputField(desc="笑话的目标（人、群体、机构或概念）。")
    humor_strategy = dspy.OutputField(desc="逐步计划：铺垫（脚本 1）-> 触发点 -> 笑点（脚本 2）。")

class DraftJokeZh(dspy.Signature):
    """
    根据提供的幽默策略起草笑话。
    笑话必须简短、有力，并严格遵守限制条件。
    """
    input_text = dspy.InputField(desc="原始输入。")
    humor_strategy = dspy.InputField(desc="笑话的结构计划。")
    constraints = dspy.InputField(desc="具体限制（例如，最大长度，包含的词）。")
    
    draft_text = dspy.OutputField(desc="生成的笑话草稿。")

class FormatJokeZh(dspy.Signature):
    """
    将笑话草稿格式化为最终提交格式。
    确保没有介绍性文字，没有解释，并严格遵守长度限制。
    """
    raw_draft = dspy.InputField(desc="生成的笑话草稿。")
    constraints = dspy.InputField(desc="需要遵守的限制。")
    
    final_joke = dspy.OutputField(desc="干净、格式化后的笑话字符串。")
