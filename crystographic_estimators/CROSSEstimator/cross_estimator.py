from ..helper import ComplexityType
from ..base_algorithm import BaseAlgorithm, optimal_parameter
from ..cross_problem import CROSSProblem
from math import log2, inf, comb


class CROSSAlgorithm(BaseAlgorithm):
    def __init__(self, problem: CROSSProblem, **kwargs):
        """Base class for CROSS algorithms complexity estimator.
        
        Covers both RSDP and RSDPG variants of the CROSS signature scheme.

        Args:
            problem (CROSSProblem): CROSSProblem object including all necessary parameters.
            var_ranges (bool, optional): Allow parameter optimization to adapt ranges if necessary. Defaults to True.
            hmap (bool, optional): Indicates if hashmap is being used for linear time sorting. Defaults to True.
        """
        super(CROSSAlgorithm, self).__init__(problem, **kwargs)
        self._name = "CROSS_base"
        self._variable_parameter_ranges = kwargs.get("var_ranges", 1)
        self._hmap = kwargs.get("hmap", 1)
        self._adjust_radius = kwargs.get("adjust_radius", 10)
        self.workfactor_accuracy = kwargs.get("workfactor_accuracy", 1)
        self.scipy_model = None
        self.full_domain = kwargs.get("full_domain", False)
        self._current_minimum_for_early_abort = inf
        
        n, k, w, t, m, variant = self.problem.get_parameters()
        
        # Set parameter ranges for window size l
        self.set_parameter_ranges("l", 0, n - k)
        
        # Set parameter ranges for weight distribution p
        self.set_parameter_ranges("p", 0, w)

    def problem_expected_solutions(self):
        """Expected number of solutions for the RSDP/RSDPG problem.
        
        For RSDP: Solutions correspond to error vectors with regular weight structure.
        For RSDPG: Additional Gaussian structure constrains the solution space.
        """
        n = self.problem.parameters["code length"]
        w = self.problem.parameters["error weight"]
        
        if self.problem.parameters["variant"] == "RSDP":
            return max(1, comb(n, w))
        else:  # RSDPG
            m = self.problem.parameters["m_parameter"]
            return max(1, comb(n, w) / (2 ** m))

    @optimal_parameter
    def l(self):
        """Returns the optimal parameter `l` (window size) used in ISD algorithms."""
        if self._optimal_parameters.get("l") is None:
            n = self.problem.parameters["code length"]
            k = self.problem.parameters["code dimension"]
            if self.complexity_type == ComplexityType.ESTIMATE.value:
                return (n - k) // 3
            elif self.complexity_type == ComplexityType.TILDEO.value:
                return 0
        return self._optimal_parameters.get("l")

    @optimal_parameter
    def p(self):
        """Returns the optimal parameter `p` (weight distribution) used in ISD algorithms."""
        if self._optimal_parameters.get("p") is None:
            w = self.problem.parameters["error weight"]
            if self.complexity_type == ComplexityType.ESTIMATE.value:
                return w // 2
            elif self.complexity_type == ComplexityType.TILDEO.value:
                return 1
        return self._optimal_parameters.get("p")

    def reset(self):
        """Reset the algorithm state."""
        super().reset()
        try:
            self.initialize_parameter_ranges()
        except AttributeError:
            pass
        except ValueError:
            pass

    def _are_parameters_invalid(self, parameters: dict):
        """Returns whether the provided parameter set is invalid.

        Args:
            parameters (dict): Dictionary of parameters to validate.

        Returns:
            bool: True if `parameters` is an invalid parameter set.
        """
        n = self.problem.parameters["code length"]
        k = self.problem.parameters["code dimension"]
        w = self.problem.parameters["error weight"]
        
        l = parameters.get("l", 0)
        p = parameters.get("p", 0)
        
        # Window size must be valid
        if l < 0 or l > n - k:
            return True
            
        # Weight distribution must be valid
        if p < 0 or p > w:
            return True
            
        # Parameters for the specific algorithm
        if p > (k + l) / 2:  # p must fit in first half of window
            return True
            
        if (w - p) > (k + l) / 2:  # w-p must fit in second half
            return True
            
        return False

    def _find_optimal_parameters(self):
        """Enumerates over all valid parameter configurations within the ranges
        of the optimization and saves the best result in `self._optimal_parameters`."""
        _ = self.l()
        time = inf
        
        while True:
            stop = True
            for params in self._valid_choices():
                if self._are_parameters_invalid(params):
                    continue
                    
                tmp_time, tmp_memory = self._time_and_memory_complexity(params)

                if self.bit_complexities:
                    tmp_memory = self.problem.to_bitcomplexity_memory(tmp_memory)

                tmp_time += self.memory_access_cost(tmp_memory)

                if tmp_time < time and tmp_memory < self.problem.memory_bound:
                    time, memory = tmp_time, tmp_memory
                    self._current_minimum_for_early_abort = tmp_time

                    for i in params:
                        self._optimal_parameters[i] = params[i]

            if self._variable_parameter_ranges and len(self._optimal_parameters) > 1:
                stop = self._adjust_parameter_ranges()

            if stop:
                break
                
        self._current_minimum_for_early_abort = inf

    def _find_optimal_tilde_o_parameters(self):
        """Enumerates all valid parameters within the given ranges to find 
        the optimal one asymptotically."""
        self._tilde_o_time_and_memory_complexity(self._optimal_parameters)

    def _adjust_parameter_ranges(self):
        """Readjust the boundaries of the ESTIMATE optimization routine if 
        the optimization detects that it runs into one or more of the boundaries."""
        kept_old_ranges = True
        r = self._adjust_radius

        for i in self._optimal_parameters_methods:
            ranges = self._parameter_ranges[i.__name__]
            current_min = ranges["min"]
            current_max = ranges["max"]
            val = i()
            
            if val > ranges["max"] - r:
                ranges["max"] += r
                ranges["min"] = max(0, min(val - r, ranges["min"] + r))
                kept_old_ranges = False

            if i() < ranges["min"] + r:
                ranges["min"] -= r
                ranges["min"] = max(0, ranges["min"])
                ranges["max"] = max(val + r, ranges["max"] - r)
                kept_old_ranges = False

            if current_min == ranges["min"] and current_max == ranges["max"]:
                kept_old_ranges = True
                
        return kept_old_ranges

    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        """Computes time and memory complexity for given parameters.

        Args:
            parameters (dict): Dictionary of parameters.
            verbose_information (dict, optional): Dictionary for verbose output.

        Returns:
            tuple: (time_complexity, memory_complexity)
        """
        raise NotImplementedError

    def _compute_time_complexity(self, parameters: dict):
        """Compute and return the time complexity either in the asymptotic 
        case or for real parameters.

        Args:
            parameters (dict): Dictionary of parameters used for time complexity computation.
        """
        return self._time_and_memory_complexity(parameters)[0]

    def _compute_tilde_o_time_complexity(self, parameters: dict):
        """Compute and return the time complexity of the algorithm for a 
        given set of parameters.

        Args:
            parameters (dict): A dictionary containing the parameters.
        """
        return self._tilde_o_time_and_memory_complexity(parameters)[0]

    def _compute_memory_complexity(self, parameters: dict):
        """Compute and return the memory complexity of the algorithm for 
        the given parameter set.

        Args:
            parameters (dict): A dictionary of parameters used for the memory complexity computation.
        """
        return self._time_and_memory_complexity(parameters)[1]

    def _compute_tilde_o_memory_complexity(self, parameters: dict):
        """Compute and return the memory complexity of the algorithm for 
        the given parameter set.

        Args:
            parameters (dict): A dictionary of parameters used for the memory complexity computation.
        """
        return self._tilde_o_time_and_memory_complexity(parameters)[1]

    def _tilde_o_time_and_memory_complexity(self, parameters: dict):
        """Computes and returns the time and memory complexity of the 
        algorithm for the given parameter set.

        Args:
            parameters (dict): Dictionary of parameters used for the time complexity computation.
        """
        pass
        if self.scipy_model is None:
            raise NotImplementedError("For " + self._name + " TildeO complexity is not yet implemented")
        
        model = self.scipy_model(
            self.parameter_names(),
            self.problem,
            iterations=self.workfactor_accuracy * 10,
            accuracy=1e-7,
        )
        wf_time, wf_memory, par = model.get_time_memory_and_parameters(parameters=parameters)
        self._optimal_parameters.update(par)
        n = self.problem.parameters["code length"]
        return wf_time * n, wf_memory * n

    def set_parameters(self, parameters: dict):
        """Set optimal parameters to predefined values, then do not allow 
        optimization to modify the ranges again.

        Args:
            parameters (dict): A dictionary including parameters to set.
        """
        BaseAlgorithm.set_parameters(self, parameters)
        self._variable_parameter_ranges = 0

    def _get_verbose_information(self):
        """Get extra information about the algorithm's state.

        Returns:
            dict: Containing 
                LISTS: Size of lists used
                COLLISIONS: Number of expected collisions
                CONSTRAINTS: Information about constraints
        """
        verb = {}
        _ = self._time_and_memory_complexity(self.optimal_parameters(), verbose_information=verb)
        return verb