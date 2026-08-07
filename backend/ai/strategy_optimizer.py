from __future__ import annotations

import itertools
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ==========================================================
# OPTIMIZATION METHOD
# ==========================================================

class OptimizationMethod(Enum):
    GRID_SEARCH = "GRID_SEARCH"
    RANDOM_SEARCH = "RANDOM_SEARCH"
    GENETIC = "GENETIC"
    BAYESIAN = "BAYESIAN"
    AI = "AI"


# ==========================================================
# OPTIMIZATION TARGET
# ==========================================================

class OptimizationTarget(Enum):
    TOTAL_RETURN = "total_return"
    PROFIT_FACTOR = "profit_factor"
    SHARPE = "sharpe_ratio"
    SORTINO = "sortino_ratio"
    WIN_RATE = "win_rate"
    EXPECTANCY = "expectancy"
    ROBUSTNESS = "robustness_score"


# ==========================================================
# PARAMETER
# ==========================================================

@dataclass(slots=True)
class StrategyParameter:
    name: str
    minimum: float
    maximum: float
    step: float
    parameter_type: type = float
    default: Any = None


# ==========================================================
# OPTIMIZATION RESULT
# ==========================================================

@dataclass(slots=True)
class OptimizationResult:
    parameters: Dict[str, Any]
    score: float
    statistics: Dict
    created_at: datetime = field(
        default_factory=datetime.now
    )


# ==========================================================
# OPTIMIZATION CONFIG
# ==========================================================

@dataclass(slots=True)
class OptimizerConfig:
    method: OptimizationMethod = (
        OptimizationMethod.GENETIC
    )
    target: OptimizationTarget = (
        OptimizationTarget.ROBUSTNESS
    )
    population_size: int = 50
    generations: int = 30
    mutation_rate: float = 0.15
    crossover_rate: float = 0.80
    elite_count: int = 5
    random_seed: int = 42
    max_workers: int = 8


# ==========================================================
# STRATEGY OPTIMIZER
# ==========================================================

class StrategyOptimizer:

    def __init__(self):
        self.lock = threading.RLock()
        self.config = OptimizerConfig()
        self.parameters: List[
            StrategyParameter
        ] = []
        self.strategy_factory: Optional[
            Callable
        ] = None
        self.backtest_engine = None
        self.population = []
        self.results: List[
            OptimizationResult
        ] = []
        self.best_result: Optional[
            OptimizationResult
        ] = None
        self.running = False
        self.progress = 0.0

        random.seed(
            self.config.random_seed
        )

    # ==========================================================
    # CONFIGURE
    # ==========================================================

    def configure(
        self,
        config: OptimizerConfig,
    ) -> None:
        self.config = config
        random.seed(
            config.random_seed
        )

    # ==========================================================
    # REGISTER PARAMETER
    # ==========================================================

    def register_parameter(
        self,
        parameter: StrategyParameter,
    ) -> None:
        self.parameters.append(
            parameter
        )

    # ==========================================================
    # REGISTER MULTIPLE PARAMETERS
    # ==========================================================

    def register_parameters(
        self,
        parameters: List[StrategyParameter],
    ) -> None:
        for parameter in parameters:
            self.register_parameter(
                parameter
            )

    # ==========================================================
    # CLEAR PARAMETERS
    # ==========================================================

    def clear_parameters(
        self,
    ) -> None:
        self.parameters.clear()

    # ==========================================================
    # VALIDATE PARAMETERS
    # ==========================================================

    def validate_parameters(
        self,
    ) -> bool:
        if not self.parameters:
            raise ValueError(
                "No optimization parameters registered."
            )
        for parameter in self.parameters:
            if parameter.minimum > parameter.maximum:
                raise ValueError(
                    f"Invalid range for '{parameter.name}'."
                )
            if parameter.step <= 0:
                raise ValueError(
                    f"Step size must be greater than zero for '{parameter.name}'."
                )
        return True

    # ==========================================================
    # SET STRATEGY FACTORY
    # ==========================================================

    def set_strategy_factory(
        self,
        factory: Callable,
    ) -> None:
        self.strategy_factory = factory

    # ==========================================================
    # SET BACKTEST ENGINE
    # ==========================================================

    def set_backtest_engine(
        self,
        engine,
    ) -> None:
        self.backtest_engine = engine

    # ==========================================================
    # READY CHECK
    # ==========================================================

    def is_ready(
        self,
    ) -> bool:
        return (
            self.strategy_factory is not None
            and
            self.backtest_engine is not None
            and
            len(self.parameters) > 0
        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(
        self,
    ) -> None:
        self.population.clear()
        self.results.clear()
        self.best_result = None
        self.progress = 0.0
        self.running = False

    # ==========================================================
    # RANDOM VALUE
    # ==========================================================

    def random_value(
        self,
        parameter: StrategyParameter,
    ):
        values = []
        value = parameter.minimum
        while value <= parameter.maximum:
            values.append(
                value
            )
            value += parameter.step
        choice = random.choice(
            values
        )
        if parameter.parameter_type is int:
            return int(
                choice
            )
        if parameter.parameter_type is bool:
            return bool(
                random.randint(
                    0,
                    1,
                )
            )
        return float(
            choice
        )

    # ==========================================================
    # RANDOM CHROMOSOME
    # ==========================================================

    def random_chromosome(
        self,
    ) -> Dict[str, Any]:
        chromosome = {}
        for parameter in self.parameters:
            chromosome[
                parameter.name
            ] = self.random_value(
                parameter
            )
        return chromosome

    # ==========================================================
    # INITIAL POPULATION
    # ==========================================================

    def initialize_population(
        self,
    ) -> List[Dict]:
        self.population = [
            self.random_chromosome()
            for _ in range(
                self.config.population_size
            )
        ]
        return self.population

    # ==========================================================
    # POPULATION SIZE
    # ==========================================================

    def get_population_size(
        self,
    ) -> int:
        return len(
            self.population
        )

    # ==========================================================
    # PARAMETER NAMES
    # ==========================================================

    def parameter_names(
        self,
    ) -> List[str]:
        return [
            parameter.name
            for parameter in self.parameters
        ]

    # ==========================================================
    # PARAMETER DEFAULTS
    # ==========================================================

    def parameter_defaults(
        self,
    ) -> Dict[str, Any]:
        defaults = {}
        for parameter in self.parameters:
            defaults[
                parameter.name
            ] = parameter.default
        return defaults

    # ==========================================================
    # FITNESS SCORE
    # ==========================================================

    def fitness_score(
        self,
        statistics: Dict,
    ) -> float:
        target = self.config.target.value
        return float(
            statistics.get(
                target,
                0.0,
            )
        )

    # ==========================================================
    # EVALUATE CHROMOSOME
    # ==========================================================

    def evaluate(
        self,
        chromosome: Dict[str, Any],
    ) -> OptimizationResult:
        strategy = self.strategy_factory(
            **chromosome
        )
        self.backtest_engine.clear_results()
        self.backtest_engine.set_strategy(
            strategy
        )
        self.backtest_engine.run()
        statistics = (
            self.backtest_engine.performance_dashboard()
        )
        score = self.fitness_score(
            statistics
        )
        result = OptimizationResult(
            parameters=dict(
                chromosome
            ),
            score=score,
            statistics=statistics,
        )
        return result

    # ==========================================================
    # EVALUATE POPULATION
    # ==========================================================

    def evaluate_population(
        self,
    ) -> List[OptimizationResult]:
        self.results.clear()
        total = len(
            self.population
        )
        for index, chromosome in enumerate(
            self.population,
            start=1,
        ):
            result = self.evaluate(
                chromosome
            )
            self.results.append(
                result
            )
            self.progress = (
                index
                /
                total
            ) * 100
        self.results.sort(
            key=lambda r: r.score,
            reverse=True,
        )
        if self.results:
            self.best_result = (
                self.results[0]
            )
        return self.results

    # ==========================================================
    # BEST RESULT
    # ==========================================================

    def best(
        self,
    ) -> Optional[OptimizationResult]:
        return self.best_result

    # ==========================================================
    # TOP RESULTS
    # ==========================================================

    def top_results(
        self,
        count: int = 10,
    ) -> List[OptimizationResult]:
        return self.results[:count]

    # ==========================================================
    # ELITE SELECTION
    # ==========================================================

    def elite_selection(
        self,
    ) -> List[Dict]:
        elites = []
        limit = min(
            self.config.elite_count,
            len(
                self.results
            ),
        )
        for result in self.results[:limit]:
            elites.append(
                dict(
                    result.parameters
                )
            )
        return elites

    # ==========================================================
    # TOURNAMENT SELECTION
    # ==========================================================

    def tournament_selection(
        self,
        size: int = 5,
    ) -> Dict:
        contestants = random.sample(
            self.results,
            min(
                size,
                len(
                    self.results
                ),
            ),
        )
        contestants.sort(
            key=lambda r: r.score,
            reverse=True,
        )
        return dict(
            contestants[0].parameters
        )

    # ==========================================================
    # ROULETTE WHEEL SELECTION
    # ==========================================================

    def roulette_selection(
        self,
    ) -> Dict:
        total_score = sum(
            max(
                result.score,
                0,
            )
            for result in self.results
        )
        if total_score <= 0:
            return self.tournament_selection()
        pick = random.uniform(
            0,
            total_score,
        )
        current = 0.0
        for result in self.results:
            current += max(
                result.score,
                0,
            )
            if current >= pick:
                return dict(
                    result.parameters
                )
        return dict(
            self.results[-1].parameters
        )

    # ==========================================================
    # SELECT PARENT
    # ==========================================================

    def select_parent(
        self,
    ) -> Dict:
        if (
            self.config.method
            ==
            OptimizationMethod.GENETIC
        ):
            return self.tournament_selection()
        return self.roulette_selection()

    # ==========================================================
    # CACHE RESULTS
    # ==========================================================

    def build_cache(
        self,
    ) -> Dict:
        cache = {}
        for result in self.results:
            key = tuple(
                sorted(
                    result.parameters.items()
                )
            )
            cache[key] = result
        return cache

    # ==========================================================
    # LOOKUP CACHE
    # ==========================================================

    def cached_result(
        self,
        chromosome: Dict,
        cache: Dict,
    ) -> Optional[OptimizationResult]:
        key = tuple(
            sorted(
                chromosome.items()
            )
        )
        return cache.get(
            key
        )

    # ==========================================================
    # SINGLE POINT CROSSOVER
    # ==========================================================

    def single_point_crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        keys = list(parent1.keys())
        if len(keys) < 2:
            return dict(parent1), dict(parent2)
        point = random.randint(
            1,
            len(keys) - 1,
        )
        child1 = {}
        child2 = {}
        for index, key in enumerate(keys):
            if index < point:
                child1[key] = parent1[key]
                child2[key] = parent2[key]
            else:
                child1[key] = parent2[key]
                child2[key] = parent1[key]
        return child1, child2

    # ==========================================================
    # TWO POINT CROSSOVER
    # ==========================================================

    def two_point_crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        keys = list(parent1.keys())
        if len(keys) < 3:
            return self.single_point_crossover(
                parent1,
                parent2,
            )
        p1 = random.randint(
            1,
            len(keys) - 2,
        )
        p2 = random.randint(
            p1 + 1,
            len(keys) - 1,
        )
        child1 = {}
        child2 = {}
        for index, key in enumerate(keys):
            if p1 <= index < p2:
                child1[key] = parent2[key]
                child2[key] = parent1[key]
            else:
                child1[key] = parent1[key]
                child2[key] = parent2[key]
        return child1, child2

    # ==========================================================
    # UNIFORM CROSSOVER
    # ==========================================================

    def uniform_crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        child1 = {}
        child2 = {}
        for key in parent1:
            if random.random() < 0.5:
                child1[key] = parent1[key]
                child2[key] = parent2[key]
            else:
                child1[key] = parent2[key]
                child2[key] = parent1[key]
        return child1, child2

    # ==========================================================
    # MUTATE CHROMOSOME
    # ==========================================================

    def mutate(
        self,
        chromosome: Dict[str, Any],
    ) -> Dict[str, Any]:
        child = dict(chromosome)
        for parameter in self.parameters:
            if random.random() <= self.config.mutation_rate:
                child[
                    parameter.name
                ] = self.random_value(
                    parameter
                )
        return child

    # ==========================================================
    # REPAIR CHROMOSOME
    # ==========================================================

    def repair(
        self,
        chromosome: Dict[str, Any],
    ) -> Dict[str, Any]:
        repaired = dict(chromosome)
        for parameter in self.parameters:
            value = repaired.get(
                parameter.name,
                parameter.default,
            )
            if value < parameter.minimum:
                value = parameter.minimum
            if value > parameter.maximum:
                value = parameter.maximum
            if parameter.parameter_type is int:
                value = int(value)
            elif parameter.parameter_type is float:
                value = float(value)
            repaired[
                parameter.name
            ] = value
        return repaired

    # ==========================================================
    # CREATE OFFSPRING
    # ==========================================================

    def create_offspring(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        if random.random() > self.config.crossover_rate:
            return (
                dict(parent1),
                dict(parent2),
            )
        child1, child2 = self.uniform_crossover(
            parent1,
            parent2,
        )
        child1 = self.mutate(child1)
        child2 = self.mutate(child2)
        child1 = self.repair(child1)
        child2 = self.repair(child2)
        return child1, child2

    # ==========================================================
    # NEXT GENERATION
    # ==========================================================

    def next_generation(
        self,
    ) -> List[Dict]:
        new_population = self.elite_selection()
        while len(new_population) < self.config.population_size:
            parent1 = self.select_parent()
            parent2 = self.select_parent()
            child1, child2 = self.create_offspring(
                parent1,
                parent2,
            )
            new_population.append(child1)
            if len(new_population) < self.config.population_size:
                new_population.append(child2)
        self.population = new_population
        return self.population

    # ==========================================================
    # EVOLVE ONE GENERATION
    # ==========================================================

    def evolve_generation(
        self,
    ) -> OptimizationResult:
        self.evaluate_population()
        self.next_generation()
        self.evaluate_population()
        return self.best_result

    # ==========================================================
    # GRID SEARCH OPTIMIZATION
    # ==========================================================

    def grid_search(
        self,
    ) -> OptimizationResult:
        self.validate_parameters()
        names = []
        values = []
        for parameter in self.parameters:
            names.append(
                parameter.name
            )
            parameter_values = []
            value = parameter.minimum
            while value <= parameter.maximum:
                if parameter.parameter_type is int:
                    parameter_values.append(
                        int(value)
                    )
                else:
                    parameter_values.append(
                        float(value)
                    )
                value += parameter.step
            values.append(
                parameter_values
            )
        self.results.clear()
        combinations = list(
            itertools.product(
                *values
            )
        )
        total = len(
            combinations
        )
        for index, combination in enumerate(
            combinations,
            start=1,
        ):
            chromosome = dict(
                zip(
                    names,
                    combination,
                )
            )
            result = self.evaluate(
                chromosome
            )
            self.results.append(
                result
            )
            self.progress = (
                index
                /
                total
            ) * 100
        self.results.sort(
            key=lambda r: r.score,
            reverse=True,
        )
        self.best_result = self.results[0]
        return self.best_result

    # ==========================================================
    # RANDOM SEARCH
    # ==========================================================

    def random_search(
        self,
        iterations: int = 100,
    ) -> OptimizationResult:
        self.results.clear()
        for i in range(
            iterations
        ):
            chromosome = (
                self.random_chromosome()
            )
            result = self.evaluate(
                chromosome
            )
            self.results.append(
                result
            )
            self.progress = (
                (
                    i + 1
                )
                /
                iterations
            ) * 100
        self.results.sort(
            key=lambda r: r.score,
            reverse=True,
        )
        self.best_result = (
            self.results[0]
        )
        return self.best_result

    # ==========================================================
    # GENETIC OPTIMIZATION
    # ==========================================================

    def genetic_search(
        self,
    ) -> OptimizationResult:
        self.initialize_population()
        self.results.clear()
        self.best_result = None
        for generation in range(
            self.config.generations
        ):
            self.evaluate_population()
            if (
                self.best_result is None
                or
                self.results[0].score
                >
                self.best_result.score
            ):
                self.best_result = (
                    self.results[0]
                )
            self.next_generation()
            self.progress = (
                (
                    generation + 1
                )
                /
                self.config.generations
            ) * 100
        return self.best_result

    # ==========================================================
    # BAYESIAN PLACEHOLDER
    # ==========================================================

    def bayesian_search(
        self,
    ) -> OptimizationResult:
        return self.random_search(
            iterations=150
        )

    # ==========================================================
    # AI OPTIMIZATION
    # ==========================================================

    def ai_search(
        self,
    ) -> OptimizationResult:
        return self.genetic_search()

    # ==========================================================
    # EARLY STOPPING
    # ==========================================================

    def early_stop(
        self,
        threshold: float,
    ) -> bool:
        if self.best_result is None:
            return False
        return (
            self.best_result.score
            >=
            threshold
        )

    # ==========================================================
    # HISTORY
    # ==========================================================

    def optimization_history(
        self,
    ) -> List[OptimizationResult]:
        return list(
            self.results
        )

    # ==========================================================
    # MAIN OPTIMIZER
    # ==========================================================

    def optimize(
        self,
    ) -> OptimizationResult:
        self.running = True
        self.progress = 0
        try:
            if (
                self.config.method
                ==
                OptimizationMethod.GRID_SEARCH
            ):
                return self.grid_search()
            elif (
                self.config.method
                ==
                OptimizationMethod.RANDOM_SEARCH
            ):
                return self.random_search()
            elif (
                self.config.method
                ==
                OptimizationMethod.BAYESIAN
            ):
                return self.bayesian_search()
            elif (
                self.config.method
                ==
                OptimizationMethod.AI
            ):
                return self.ai_search()
            else:
                return self.genetic_search()
        finally:
            self.running = False
            self.progress = 100

    # ==========================================================
    # EVALUATE POPULATION (PARALLEL)
    # ==========================================================

    def evaluate_population_parallel(
        self,
        max_workers: Optional[int] = None,
    ) -> List[OptimizationResult]:
        workers = (
            max_workers
            or
            self.config.max_workers
        )
        self.results.clear()
        total = len(
            self.population
        )
        completed = 0
        with ThreadPoolExecutor(
            max_workers=workers
        ) as executor:
            futures = [
                executor.submit(
                    self.evaluate,
                    chromosome,
                )
                for chromosome in self.population
            ]
            for future in as_completed(
                futures
            ):
                result = future.result()
                self.results.append(
                    result
                )
                completed += 1
                self.progress = (
                    completed
                    /
                    total
                ) * 100
        self.results.sort(
            key=lambda x: x.score,
            reverse=True,
        )
        if self.results:
            self.best_result = (
                self.results[0]
            )
        return self.results

    # ==========================================================
    # REMOVE DUPLICATES
    # ==========================================================

    def remove_duplicates(
        self,
    ) -> None:
        unique = []
        seen = set()
        for chromosome in self.population:
            key = tuple(
                sorted(
                    chromosome.items()
                )
            )
            if key not in seen:
                seen.add(
                    key
                )
                unique.append(
                    chromosome
                )
        while len(unique) < self.config.population_size:
            unique.append(
                self.random_chromosome()
            )
        self.population = unique

    # ==========================================================
    # POPULATION CACHE
    # ==========================================================

    def cache_population(
        self,
    ) -> Dict:
        cache = {}
        for result in self.results:
            key = tuple(
                sorted(
                    result.parameters.items()
                )
            )
            cache[key] = result
        return cache

    # ==========================================================
    # CACHE LOOKUP
    # ==========================================================

    def evaluate_cached(
        self,
        chromosome: Dict,
        cache: Dict,
    ) -> OptimizationResult:
        key = tuple(
            sorted(
                chromosome.items()
            )
        )
        if key in cache:
            return cache[key]
        result = self.evaluate(
            chromosome
        )
        cache[key] = result
        return result

    # ==========================================================
    # SAVE CHECKPOINT
    # ==========================================================

    def save_checkpoint(
        self,
        filename: str,
    ) -> None:
        checkpoint = {
            "config": {
                "population_size":
                    self.config.population_size,
                "generations":
                    self.config.generations,
                "mutation_rate":
                    self.config.mutation_rate,
                "crossover_rate":
                    self.config.crossover_rate,
            },
            "population":
                self.population,
            "progress":
                self.progress,
            "best_result":
                self.best_result.parameters
                if self.best_result
                else None,
            "results": [
                {
                    "parameters":
                        r.parameters,
                    "score":
                        r.score
                }
                for r in self.results
            ]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=4)