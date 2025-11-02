# -*- coding: utf-8 -*-
"""
Deep Think Mode for ChromaBuddy PRO
Multi-iteration analysis before code execution
"""

from typing import Dict, List, Any, Optional
from models.cohe import generate
from core.ui import get_ui, get_logger
import json


class DeepThinkMode:
    """
    Deep thinking system that performs multiple analysis iterations
    before executing code changes
    """
    
    def __init__(self, api_key: str, iterations: int = 3):
        """
        Initialize Deep Think Mode
        
        Args:
            api_key: Cohere API key
            iterations: Number of thinking iterations (default: 3)
        """
        self.api_key = api_key
        self.iterations = max(1, min(iterations, 5))  # Limit 1-5
        self.ui = get_ui()
        self.logger = get_logger()
    
    def think(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform deep thinking on user request
        
        Args:
            user_request: The user's request
            context: Additional context (files, project structure, etc)
            
        Returns:
            Dict with analysis results and recommendations
        """
        self.logger.info("Deep Think Mode activated")
        self.ui.rule("Deep Analysis")
        
        thoughts = []
        
        for i in range(self.iterations):
            with self.ui.spinner(f"Iteration {i+1}/{self.iterations}: Analyzing..."):
                thought = self._think_iteration(
                    user_request,
                    context,
                    previous_thoughts=thoughts,
                    iteration=i+1
                )
                thoughts.append(thought)
        
        # Final synthesis
        with self.ui.spinner("Synthesizing analysis..."):
            final_plan = self._synthesize(user_request, context, thoughts)
        
        self._display_results(final_plan)
        
        return final_plan
    
    def _think_iteration(
        self,
        user_request: str,
        context: Dict[str, Any],
        previous_thoughts: List[Dict],
        iteration: int
    ) -> Dict[str, Any]:
        """
        Perform single thinking iteration
        
        Args:
            user_request: User's request
            context: Context information
            previous_thoughts: Results from previous iterations
            iteration: Current iteration number
            
        Returns:
            Thought results for this iteration
        """
        prompt = self._build_iteration_prompt(
            user_request,
            context,
            previous_thoughts,
            iteration
        )
        
        try:
            response = generate(prompt, self.api_key)
            
            return {
                'iteration': iteration,
                'analysis': response,
                'timestamp': self._get_timestamp()
            }
        except Exception as e:
            self.logger.error(f"Iteration {iteration} failed: {e}")
            return {
                'iteration': iteration,
                'analysis': '',
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
    
    def _build_iteration_prompt(
        self,
        user_request: str,
        context: Dict[str, Any],
        previous_thoughts: List[Dict],
        iteration: int
    ) -> str:
        """Build prompt for thinking iteration"""
        
        if iteration == 1:
            # First iteration: understand the request
            return f"""Analyze the following user request in detail:

USER REQUEST: {user_request}

CONTEXT:
{json.dumps(context, indent=2)}

Task: Provide a thorough analysis covering:
1. What the user is trying to accomplish
2. What files/components are involved
3. Potential challenges or edge cases
4. Initial approach suggestions

Be specific and technical. Focus on understanding the full scope."""
        
        elif iteration == 2:
            # Second iteration: plan the implementation
            prev_analysis = previous_thoughts[0]['analysis'] if previous_thoughts else ''
            
            return f"""Based on the previous analysis, create a detailed implementation plan.

USER REQUEST: {user_request}

PREVIOUS ANALYSIS:
{prev_analysis}

CONTEXT:
{json.dumps(context, indent=2)}

Task: Provide:
1. Step-by-step implementation plan
2. Specific code changes needed
3. Testing strategy
4. Potential risks and mitigation
5. Alternative approaches (if any)

Be concrete and actionable."""
        
        else:
            # Third+ iteration: refine and validate
            prev_analyses = '\n\n'.join([
                f"Iteration {t['iteration']}:\n{t['analysis']}"
                for t in previous_thoughts
            ])
            
            return f"""Review and refine the implementation plan.

USER REQUEST: {user_request}

PREVIOUS ITERATIONS:
{prev_analyses}

CONTEXT:
{json.dumps(context, indent=2)}

Task: Perform final validation:
1. Check for any missed edge cases
2. Verify the plan is complete and correct
3. Identify any potential issues
4. Provide final recommendations
5. Rate confidence level (1-10)

Be critical and thorough."""
    
    def _synthesize(
        self,
        user_request: str,
        context: Dict[str, Any],
        thoughts: List[Dict]
    ) -> Dict[str, Any]:
        """
        Synthesize all thinking iterations into final plan
        
        Args:
            user_request: User's request
            context: Context information
            thoughts: All iteration results
            
        Returns:
            Final execution plan
        """
        all_analyses = '\n\n'.join([
            f"ITERATION {t['iteration']}:\n{t['analysis']}"
            for t in thoughts
        ])
        
        synthesis_prompt = f"""Synthesize the following deep analysis into a final execution plan.

USER REQUEST: {user_request}

ALL ANALYSES:
{all_analyses}

Task: Create a final, actionable plan with:
1. Summary of what will be done
2. Exact files to modify
3. Key changes for each file
4. Testing approach
5. Confidence level (1-10)
6. Any warnings or caveats

Output as structured JSON with keys:
- summary (string)
- files (list of strings)
- changes (list of dicts with file, action, details)
- tests (list of strings)
- confidence (number 1-10)
- warnings (list of strings)

Be precise and ready for execution."""
        
        try:
            response = generate(synthesis_prompt, self.api_key)
            
            # Try to parse as JSON
            try:
                plan = json.loads(response)
            except:
                # If not JSON, create structured response
                plan = {
                    'summary': response[:500],
                    'files': [],
                    'changes': [],
                    'tests': [],
                    'confidence': 7,
                    'warnings': [],
                    'raw_response': response
                }
            
            plan['iterations'] = thoughts
            return plan
            
        except Exception as e:
            self.logger.error(f"Synthesis failed: {e}")
            return {
                'summary': 'Synthesis failed',
                'files': [],
                'changes': [],
                'tests': [],
                'confidence': 0,
                'warnings': [str(e)],
                'iterations': thoughts,
                'error': str(e)
            }
    
    def _display_results(self, plan: Dict[str, Any]) -> None:
        """Display analysis results to user"""
        self.ui.rule("Analysis Complete", style="green")
        
        # Summary
        self.ui.panel(
            plan.get('summary', 'No summary available'),
            title="Summary",
            border_style="cyan"
        )
        
        # Confidence
        confidence = plan.get('confidence', 0)
        confidence_color = "green" if confidence >= 8 else "yellow" if confidence >= 6 else "red"
        self.ui.print(f"\n[bold]Confidence Level:[/bold] [{confidence_color}]{confidence}/10[/{confidence_color}]")
        
        # Files
        files = plan.get('files', [])
        if files:
            self.ui.print(f"\n[bold]Files to modify:[/bold] {len(files)}")
            for file in files:
                self.ui.print(f"  - {file}")
        
        # Warnings
        warnings = plan.get('warnings', [])
        if warnings:
            self.ui.print("\n[bold yellow]Warnings:[/bold yellow]")
            for warning in warnings:
                self.ui.warning(warning)
        
        self.ui.rule()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
