from ..base_algorithm import BaseAlgorithm
from ..cross_problem import CROSSProblem


class CROSSAlgorithm(BaseAlgorithm):
    """Base class for CROSS algorithms complexity estimator.

    Args:
        problem (CROSSProblem): CROSSProblem object including all necessary parameters
    """
    
    def __init__(self, problem: CROSSProblem, **kwargs):
        """Base class for CROSS algorithms complexity estimator.

        Args:
            problem (CROSSProblem): CROSSProblem object including all necessary parameters
        """
        super(CROSSAlgorithm, self).__init__(problem, **kwargs)
        self._name = "sample_name"
        self.problem = problem

    def _compute_time_and_memory_complexity(self, parameters: dict):
        """Returns the time and memory complexity of the algorithm for a given set of parameters.
    
        Args:
            parameters (dict): Dictionary including the parameters.
        """
        raise NotImplementedError

    def _compute_time_complexity(self, parameters: dict):
        """Return the time complexity of the algorithm for a given set of parameters.
    
        Args:
            parameters (dict): Dictionary including the parameters.
        """
        return self._compute_time_and_memory_complexity(parameters)[0]

    def _compute_memory_complexity(self, parameters: dict):
        """Return the memory complexity of the algorithm for a given set of parameters.
    
        Args:
            parameters (dict): Dictionary including the parameters.
        """
        return self._compute_time_and_memory_complexity(parameters)[1]