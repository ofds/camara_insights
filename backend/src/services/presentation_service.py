import logging

"""
Presentation service for displaying AI analysis results.
This separates the presentation logic from data access, following SRP.
"""

import json
from typing import List, Tuple, Any


class PresentationService:
    """Service responsible for formatting and displaying data to users."""
    
    @staticmethod
    def display_ai_results(results: List[Tuple[Any, Any]], format_type: str = "console") -> str:
        """
        Display AI analysis results in the specified format.
        
        Args:
            results: List of tuples containing (ai_data, proposition)
            format_type: Output format ("console", "json", "csv")
            
        Returns:
            Formatted string representation of the results
        """
        if format_type == "console":
            return PresentationService._format_console(results)
        elif format_type == "json":
            return PresentationService._format_json(results)
        elif format_type == "csv":
            return PresentationService._format_csv(results)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    @staticmethod
    def _format_console(results: List[Tuple[Any, Any]]) -> str:
        """Format results for console display."""
        if not results:
            return "No AI analysis results found in the database."
        
        output = []
        output.append("--- Latest AI Analysis Results ---")
        
        for ai_data, proposicao in results:
            output.append("\n" + "=" * 80)
            output.append(f"Analysis for Proposition ID: {ai_data.proposicao_id} ({proposicao.siglaTipo} {proposicao.numero}/{proposicao.ano})")
            output.append(f"Original Summary: {proposicao.ementa}")
            output.append("-" * 80)
            output.append(f"Model Used: {ai_data.model_version}")
            output.append(f"Impact Score (Calculated): {ai_data.impact_score}")
            output.append(f"Score (LLM Estimate): {ai_data.llm_impact_estimate}")
            output.append(f"Summary: {ai_data.summary}")
            output.append(f"Scope: {ai_data.scope}")
            output.append(f"Magnitude: {ai_data.magnitude}")
            output.append(f"Tags: {json.dumps(ai_data.tags, indent=2, ensure_ascii=False)}")
            output.append("=" * 80)
        
        return "\n".join(output)
    
    @staticmethod
    def _format_json(results: List[Tuple[Any, Any]]) -> str:
        """Format results as JSON."""
        data = []
        for ai_data, proposicao in results:
            data.append({
                "proposicao_id": ai_data.proposicao_id,
                "proposicao": {
                    "siglaTipo": proposicao.siglaTipo,
                    "numero": proposicao.numero,
                    "ano": proposicao.ano,
                    "ementa": proposicao.ementa
                },
                "analysis": {
                    "model_version": ai_data.model_version,
                    "impact_score": ai_data.impact_score,
                    "llm_impact_estimate": ai_data.llm_impact_estimate,
                    "summary": ai_data.summary,
                    "scope": ai_data.scope,
                    "magnitude": ai_data.magnitude,
                    "tags": ai_data.tags
                }
            })
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _format_csv(results: List[Tuple[Any, Any]]) -> str:
        """Format results as CSV."""
        if not results:
            return "proposicao_id,siglaTipo,numero,ano,impact_score,llm_impact_estimate,summary\n"
        
        lines = ["proposicao_id,siglaTipo,numero,ano,impact_score,llm_impact_estimate,summary"]
        
        for ai_data, proposicao in results:
            summary = str(ai_data.summary or "").replace('"', '""')
            lines.append(f"{ai_data.proposicao_id},{proposicao.siglaTipo},{proposicao.numero},{proposicao.ano},{ai_data.impact_score},{ai_data.llm_impact_estimate},\"{summary}\"")
        
        return "\n".join(lines)