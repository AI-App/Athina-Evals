from athina.interfaces.model import Model
from ..ragas_evaluator import RagasEvaluator
from athina.evals.eval_type import RagasEvalTypeId
from athina.metrics.metric_type import MetricType
from ragas.metrics.critique import coherence
from typing import List

"""
RAGAS Coherence Docs: https://docs.ragas.io/en/latest/concepts/metrics/critique.html
RAGAS Coherence Github: https://github.com/explodinggradients/ragas/blob/main/src/ragas/metrics/critique.py
"""
class RagasCoherence(RagasEvaluator):
    """
    This evaluates if the generated llm response presents ideas, information, or arguments in a logical and organized manner
    """
    @property
    def name(self):
        return RagasEvalTypeId.RAGAS_COHERENCE.value

    @property
    def display_name(self):
        return "Maliciousness"

    @property
    def metric_ids(self) -> List[str]:
        return [MetricType.RAGAS_COHERENCE.value]
    
    @property
    def ragas_metric(self):
        return coherence
    
    @property
    def ragas_metric_name(self):
        return "coherence"

    @property
    def default_model(self):
        return Model.GPT4_1106_PREVIEW.value

    @property
    def required_args(self):
        return ["query", "contexts", "response", "expected_response"]

    @property
    def examples(self):
        return None
    
    @property
    def grade_reason(self) -> str:
        return "This is calculated by how much potential generated response has to harm, deceive, or exploit users"

    def generate_data_to_evaluate(self, contexts, query, response, expected_response, **kwargs) -> dict:
        """
        Generates data for evaluation.

        :param context: list of strings of retrieved context
        :param query: user query
        :param response: llm response
        :param expected_response: expected output
        :return: A dictionary with formatted data for evaluation.
        """
        data = {
            "contexts": [contexts],
            "question": [query],
            "answer": [response],
            "ground_truths": [[expected_response]]
        }
        return data
