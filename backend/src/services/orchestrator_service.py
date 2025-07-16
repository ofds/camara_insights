"""
Data-driven orchestrator service for managing ETL flows.
This follows the Open/Closed Principle by allowing new tasks to be added without modifying existing code.
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from prefect import task, flow
from dataclasses import dataclass


@dataclass
class TaskConfig:
    """Configuration for a single ETL task."""
    name: str
    function: Callable
    dependencies: List[str] = None
    parameters: Dict[str, Any] = None
    retries: int = 2
    retry_delay_seconds: int = 60


class OrchestratorService:
    """Service for orchestrating ETL tasks in a data-driven manner."""
    
    def __init__(self):
        self.tasks: Dict[str, TaskConfig] = {}
        self.task_registry: Dict[str, Callable] = {}
    
    def register_task(self, name: str, function: Callable, **kwargs):
        """Register a new task with the orchestrator."""
        self.task_registry[name] = function
        
        config = TaskConfig(
            name=name,
            function=function,
            dependencies=kwargs.get('dependencies', []),
            parameters=kwargs.get('parameters', {}),
            retries=kwargs.get('retries', 2),
            retry_delay_seconds=kwargs.get('retry_delay_seconds', 60)
        )
        self.tasks[name] = config
    
    def create_prefect_task(self, task_config: TaskConfig):
        """Create a Prefect task from a TaskConfig."""
        @task(
            name=task_config.name,
            retries=task_config.retries,
            retry_delay_seconds=task_config.retry_delay_seconds
        )
        async def prefect_task(**kwargs):
            # Merge task parameters with runtime parameters
            merged_params = {**task_config.parameters, **kwargs}
            return await task_config.function(**merged_params)
        
        return prefect_task
    
    def build_flow(self, flow_name: str = "ETL Câmara Insights") -> Callable:
        """Build a Prefect flow from registered tasks."""
        
        @flow(name=flow_name, log_prints=True)
        async def etl_flow(**flow_kwargs):
            print(f"🚀 Starting {flow_name}...")
            
            # Track task futures for dependency management
            task_futures = {}
            
            # Process tasks in dependency order
            processed_tasks = set()
            remaining_tasks = set(self.tasks.keys())
            
            while remaining_tasks:
                ready_tasks = [
                    task_name for task_name in remaining_tasks
                    if all(dep in processed_tasks for dep in self.tasks[task_name].dependencies)
                ]
                
                if not ready_tasks:
                    raise ValueError("Circular dependencies detected in tasks")
                
                for task_name in ready_tasks:
                    task_config = self.tasks[task_name]
                    prefect_task = self.create_prefect_task(task_config)
                    
                    # Get dependencies
                    dependencies = [
                        task_futures[dep] 
                        for dep in task_config.dependencies 
                        if dep in task_futures
                    ]
                    
                    # Submit task with dependencies
                    if dependencies:
                        task_futures[task_name] = prefect_task.submit(
                            wait_for=dependencies,
                            **flow_kwargs
                        )
                    else:
                        task_futures[task_name] = prefect_task.submit(**flow_kwargs)
                    
                    processed_tasks.add(task_name)
                    remaining_tasks.remove(task_name)
            
            print("✅ All tasks submitted. Flow will wait for completion.")
        
        return etl_flow
    
    def get_available_tasks(self) -> List[str]:
        """Get list of available task names."""
        return list(self.tasks.keys())
    
    def validate_dependencies(self) -> bool:
        """Validate that all task dependencies exist."""
        for task_name, config in self.tasks.items():
            for dep in config.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Task '{task_name}' depends on unknown task '{dep}'")
        return True


# Global orchestrator instance
orchestrator = OrchestratorService()