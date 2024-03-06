import time
from typing import List

from athina.interfaces.model import Model
from athina.interfaces.result import EvalResult, EvalResultMetric
from athina.evals.llm.llm_evaluator import LlmEvaluator
from athina.evals.eval_type import ConversationEvalTypeId
from athina.metrics.metric_type import MetricType
from .prompt import SYSTEM_MESSAGE, USER_MESSAGE


class ConversationResolution(LlmEvaluator):
    """
    This evaluator checks if the conversation was resolved or not.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._system_message_template = SYSTEM_MESSAGE
        self._user_message_template = USER_MESSAGE
        self._failure_threshold = 0.75  # 75% of the messages must be resolved to pass

    @property
    def name(self):
        return ConversationEvalTypeId.CONVERSATION_RESOLUTION.value

    @property
    def display_name(self):
        return "Conversation Resolution"

    @property
    def metric_ids(self) -> List[str]:
        return [MetricType.CONVERSATION_RESOLUTION.value]

    @property
    def default_model(self):
        return Model.GPT35_TURBO.value

    @property
    def required_args(self):
        return [
            "conversation_messages"
        ]  # messages is an array of strings representing the conversation

    @property
    def examples(self):
        return []

    def _user_message(self, **kwargs) -> str:
        return self._user_message_template.format(**kwargs)

    def reason(self, messages_with_resolution_status: List[dict]) -> str:
        unresolved_messages = [
            f"\n-\"{item['message']}\" (Resolution: {item['resolution']})\n: {item['explanation']}\n"
            for item in messages_with_resolution_status
            if item["resolution"] != "Resolved"
        ]

        if not unresolved_messages:
            return "All messages were resolved"

        return "The following messages were not resolved:\n" + "\n".join(
            unresolved_messages
        )

    def _evaluate(self, conversation_messages: List[str]) -> EvalResult:
        """
        Run the LLM evaluator.
        """
        start_time = time.perf_counter()

        # Construct Prompt
        prompt_messages = self._prompt_messages(
            messages="\n".join(conversation_messages)
        )

        # Run the LLM Completion
        chat_completion_response_json: dict = self.llm_service.json_completion(
            model=self._model,
            messages=prompt_messages,
            temperature=self.TEMPERATURE,
        )

        metrics = []
        try:
            messages_with_resolution_status = chat_completion_response_json["details"]

            number_resolved_messages = 0
            reasons = []
            for message in messages_with_resolution_status:
                if message["resolution"] == "Resolved":
                    number_resolved_messages += 1
                elif message["resolution"] == "Partial":
                    number_resolved_messages += 0.5
                else:
                    number_resolved_messages += 0
                    reasons.append(message)
            score = number_resolved_messages / len(messages_with_resolution_status)
            reason = self.reason(messages_with_resolution_status)
            failure = score < self._failure_threshold

            metrics.append(
                EvalResultMetric(
                    id=MetricType.CONVERSATION_RESOLUTION.value, value=score
                )
            )

        except Exception as e:
            logger.error(f"Error occurred during eval: {e}")
            raise e

        end_time = time.perf_counter()
        eval_runtime_ms = int((end_time - start_time) * 1000)
        llm_eval_result = EvalResult(
            name=self.name,
            display_name=self.display_name,
            data={"messages": conversation_messages},
            failure=failure,
            reason=reason,
            runtime=eval_runtime_ms,
            model=self._model,
            metrics=metrics,
            datapoint_field_annotations=None,
        )
        return {k: v for k, v in llm_eval_result.items() if v is not None}