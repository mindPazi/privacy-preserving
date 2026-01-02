"""
Plotting utilities for privacy-utility trade-off visualization.

This module provides functions for creating scatter plots
and other visualizations of experimental results.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


class PrivacyUtilityPlotter:
    """
    Plotter for privacy-utility trade-off visualization.

    Creates scatter plots and other visualizations showing
    the relationship between privacy and utility scores.

    Attributes:
        figure_size: Default figure size (width, height).
        style: Matplotlib style to use.
        output_format: Default output format for saved figures.
    """

    def __init__(
        self,
        figure_size: Tuple[int, int] = (10, 8),
        style: str = "seaborn-v0_8-whitegrid",
        output_format: str = "png"
    ) -> None:
        """
        Initialize the plotter.

        Args:
            figure_size: Default figure size (width, height).
            style: Matplotlib style to use.
            output_format: Default output format for saved figures.
        """
        self.figure_size = figure_size
        self.style = style
        self.output_format = output_format
        try:
            plt.style.use(style)
        except:
            plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'ggplot')

    def create_scatter_plot(
        self,
        privacy_scores: List[float],
        utility_scores: List[float],
        labels: Optional[List[str]] = None,
        title: str = "Privacy-Utility Trade-off",
        xlabel: str = "Privacy Score",
        ylabel: str = "Utility Score"
    ) -> Any:
        """
        Create a scatter plot of privacy vs utility scores.

        Args:
            privacy_scores: List of privacy scores.
            utility_scores: List of utility scores.
            labels: Optional labels for each point.
            title: Plot title.
            xlabel: X-axis label.
            ylabel: Y-axis label.

        Returns:
            Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        if labels is not None:
            unique_labels = list(set(labels))
            colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
            color_map = {label: colors[i] for i, label in enumerate(unique_labels)}
            
            for label in unique_labels:
                indices = [i for i, l in enumerate(labels) if l == label]
                x = [privacy_scores[i] for i in indices]
                y = [utility_scores[i] for i in indices]
                ax.scatter(x, y, c=[color_map[label]], label=label, alpha=0.7, s=100)
            
            ax.legend()
        else:
            ax.scatter(privacy_scores, utility_scores, alpha=0.7, s=100)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        
        plt.tight_layout()
        return fig

    def create_grouped_scatter_plot(
        self,
        data: Dict[str, List[Tuple[float, float]]],
        title: str = "Privacy-Utility Trade-off by Obfuscation Level",
        xlabel: str = "Privacy Score",
        ylabel: str = "Utility Score"
    ) -> Any:
        """
        Create a scatter plot with groups (e.g., by obfuscation level).

        Args:
            data: Dictionary mapping group names to (privacy, utility) pairs.
            title: Plot title.
            xlabel: X-axis label.
            ylabel: Y-axis label.

        Returns:
            Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(data)))
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
        for i, (group_name, points) in enumerate(data.items()):
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            ax.scatter(x, y, c=[colors[i]], label=group_name, 
                      marker=markers[i % len(markers)], alpha=0.7, s=100)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        
        plt.tight_layout()
        return fig

    def add_trend_line(
        self,
        fig: Any,
        privacy_scores: List[float],
        utility_scores: List[float]
    ) -> Any:
        """
        Add a trend line to an existing plot.

        Args:
            fig: Existing matplotlib figure.
            privacy_scores: List of privacy scores.
            utility_scores: List of utility scores.

        Returns:
            Updated figure object.
        """
        ax = fig.axes[0]
        
        z = np.polyfit(privacy_scores, utility_scores, 1)
        p = np.poly1d(z)
        
        x_line = np.linspace(min(privacy_scores), max(privacy_scores), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, label='Trend line')
        ax.legend()
        
        return fig

    def add_pareto_frontier(
        self,
        fig: Any,
        privacy_scores: List[float],
        utility_scores: List[float]
    ) -> Any:
        """
        Add a Pareto frontier to an existing plot.

        Args:
            fig: Existing matplotlib figure.
            privacy_scores: List of privacy scores.
            utility_scores: List of utility scores.

        Returns:
            Updated figure object.
        """
        ax = fig.axes[0]
        
        points = list(zip(privacy_scores, utility_scores))
        points_sorted = sorted(points, key=lambda x: x[0])
        
        pareto_points = []
        max_utility = -float('inf')
        
        for point in points_sorted:
            if point[1] >= max_utility:
                pareto_points.append(point)
                max_utility = point[1]
        
        if pareto_points:
            pareto_x = [p[0] for p in pareto_points]
            pareto_y = [p[1] for p in pareto_points]
            ax.plot(pareto_x, pareto_y, 'g-', linewidth=2, label='Pareto frontier', alpha=0.8)
            ax.legend()
        
        return fig

    def save_figure(
        self,
        fig: Any,
        filepath: Path,
        dpi: int = 300
    ) -> None:
        """
        Save a figure to file.

        Args:
            fig: Matplotlib figure to save.
            filepath: Output file path.
            dpi: Resolution in dots per inch.
        """
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')

    def create_box_plot(
        self,
        data: Dict[str, List[float]],
        metric_name: str,
        title: str = "Score Distribution"
    ) -> Any:
        """
        Create a box plot comparing distributions.

        Args:
            data: Dictionary mapping group names to score lists.
            metric_name: Name of the metric being plotted.
            title: Plot title.

        Returns:
            Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        labels = list(data.keys())
        values = list(data.values())
        
        ax.boxplot(values, labels=labels)
        ax.set_ylabel(metric_name)
        ax.set_title(title)
        
        plt.tight_layout()
        return fig

    def create_heatmap(
        self,
        correlation_matrix: List[List[float]],
        labels: List[str],
        title: str = "Correlation Heatmap"
    ) -> Any:
        """
        Create a correlation heatmap.

        Args:
            correlation_matrix: 2D correlation matrix.
            labels: Labels for rows/columns.
            title: Plot title.

        Returns:
            Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        matrix = np.array(correlation_matrix)
        im = ax.imshow(matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)
        
        plt.colorbar(im)
        ax.set_title(title)
        
        plt.tight_layout()
        return fig

    def __repr__(self) -> str:
        """Return string representation of the plotter."""
        return f"PrivacyUtilityPlotter(figure_size={self.figure_size}, style='{self.style}')"
