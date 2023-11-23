from typing import List
from ..base_llm_evaluator import BaseLlmEvaluator
from .examples import FAITHFULNESS_EVAL_EXAMPLES


class Faithfulness(BaseLlmEvaluator):
    """
    This evaluator checks if the response can be inferred using the information provided as context.
    """

    REQUIRED_ARGS: List[str] = ["context", "response"]
    EXAMPLES = FAITHFULNESS_EVAL_EXAMPLES

    SYSTEM_MESSAGE_TEMPLATE = f""" 
    You are an expert at evaluating whether the response can be inferred using the information provided as context.
    """

    USER_MESSAGE_TEMPLATE = """
        Let's think step by step.
        1. Consider the following: 
        context: {context}.
        response: {response}.
        2. Make sure to also consider these instructions: {additional_instructions}
        3. Determine if the response can be inferred using ONLY the information provided in the context.
        4. Provide a brief explanation of why the response can or cannot be inferred purely from the context, labeled as 'explanation', leading up to a verdict (Pass/Fail) labeled as 'result'.
        5. Return a JSON object in the following format: "result": 'result', "explanation": 'explanation'.

        ### EXAMPLES ###
        Here's are some examples: 
        {examples}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _user_message(
        self,
        context: str,
        response: str,
        additional_instructions: str = "",
    ) -> str:
        return self.USER_MESSAGE_TEMPLATE.format(
            context=context,
            response=response,
            additional_instructions=additional_instructions,
            examples=self._examples_str(),
        )