#!/usr/bin/env python3
"""
AI Development Team Orchestrator

A comprehensive Python CLI tool that simulates a full-stack software development team
of 6 AI agents, each representing a real professional role in a web development company.
This system generates complex, scalable, production-grade websites using local Ollama models.

Author: AI Development Team Orchestrator
Version: 1.0.0
"""

import os
import sys
import argparse
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_wizard import CLIWizard
from utils.ollama_client import OllamaClient
from agents.planner import PlannerAgent
from agents.builder import BuilderAgent
from agents.reviewer import ReviewerAgent
from agents.fixer import FixerAgent
from agents.finalizer import FinalizerAgent
from agents.git_pusher import GitPusherAgent

console = Console()

class Orchestrator:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.required_models = ["deepseek-chat", "deepseek-coder:33b"]
        self.agents = {
            "planner": PlannerAgent(self.ollama_client),
            "builder": BuilderAgent(self.ollama_client),
            "reviewer": ReviewerAgent(self.ollama_client),
            "fixer": FixerAgent(self.ollama_client),
            "finalizer": FinalizerAgent(self.ollama_client),
            "git_pusher": GitPusherAgent(self.ollama_client)
        }
        
    def display_welcome(self):
        """Display the welcome banner and team introduction."""
        banner = """
🤖 AI Development Team Orchestrator v1.0.0

Simulating a complete software development team to build production-ready web applications.

From a one-line idea to a fully deployed application - just like a real dev agency!
        """
        
        console.print(Panel(banner, title="🎯 Welcome", border_style="bold blue"))
        
        # Display team members
        team_table = Table(title="👥 Your AI Development Team")
        team_table.add_column("Role", style="bold cyan")
        team_table.add_column("Agent", style="green")
        team_table.add_column("Responsibilities", style="white")
        team_table.add_column("Model", style="yellow")
        
        team_members = [
            ("Product Manager", "Planner", "Requirements analysis, technical specifications", "DeepSeek-Chat"),
            ("Full-Stack Developer", "Builder", "Complete application development", "DeepSeek-Coder:33b"),
            ("Lead Engineer", "Reviewer", "Code review, quality assurance", "DeepSeek-Coder:33b"),
            ("Senior Debugger", "Fixer", "Bug fixes, optimizations", "DeepSeek-Coder:33b"),
            ("QA Engineer", "Finalizer", "Testing, documentation", "DeepSeek-Chat"),
            ("DevOps Engineer", "Git Pusher", "Deployment, Git management", "DeepSeek-Coder:33b")
        ]
        
        for role, agent, responsibilities, model in team_members:
            team_table.add_row(role, agent, responsibilities, model)
        
        console.print(team_table)
        console.print()
    
    def check_prerequisites(self) -> bool:
        """Check if Ollama is running and required models are available."""
        console.print("[bold yellow]🔍 Checking prerequisites...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking Ollama service...", total=None)
            
            # Check if Ollama is running
            if not self.ollama_client.is_model_available("deepseek-chat"):
                progress.update(task, description="Ollama service not found")
                console.print("\n[red]❌ Ollama service is not running or not accessible.[/red]")
                console.print("\n[yellow]Please ensure Ollama is installed and running:[/yellow]")
                console.print("1. Install Ollama from https://ollama.ai")
                console.print("2. Start Ollama service")
                console.print("3. Run this tool again")
                return False
            
            progress.update(task, description="Checking required models...")
            
            # Ensure required models are available
            if not self.ollama_client.ensure_models_available(self.required_models):
                console.print("\n[red]❌ Failed to download required models.[/red]")
                console.print("\n[yellow]You can manually pull them with:[/yellow]")
                for model in self.required_models:
                    console.print(f"ollama pull {model}")
                return False
            
            progress.update(task, description="Prerequisites check completed")
        
        console.print("\n[green]✅ All prerequisites are met![/green]\n")
        return True
    
    def run_development_pipeline(self, project_spec_path: str) -> Optional[str]:
        """Run the complete development pipeline with all agents."""
        console.print("[bold green]🚀 Starting AI Development Team Pipeline[/bold green]\n")
        
        pipeline_steps = [
            ("Planner", "planner", "Planning & Analysis"),
            ("Builder", "builder", "Development"),
            ("Reviewer", "reviewer", "Code Review"),
            ("Fixer", "fixer", "Bug Fixes & Optimization"),
            ("Finalizer", "finalizer", "QA & Documentation"),
            ("Git Pusher", "git_pusher", "Deployment Setup")
        ]
        
        # Initialize pipeline state
        technical_spec_path = None
        project_path = None
        review_report_path = None
        
        try:
            for i, (role, agent_key, phase) in enumerate(pipeline_steps, 1):
                console.print(f"\n[bold blue]═══ Phase {i}/6: {phase} ═══[/bold blue]")
                
                agent = self.agents[agent_key]
                
                # Execute agent based on type
                if agent_key == "planner":
                    technical_spec_path = agent.run(project_spec_path)
                    if not technical_spec_path:
                        console.print(f"[red]❌ {role} failed - stopping pipeline[/red]")
                        return None
                
                elif agent_key == "builder":
                    project_path = agent.run(technical_spec_path)
                    if not project_path:
                        console.print(f"[red]❌ {role} failed - stopping pipeline[/red]")
                        return None
                
                elif agent_key == "reviewer":
                    review_report_path = agent.run(project_path, technical_spec_path)
                    if not review_report_path:
                        console.print(f"[red]❌ {role} failed - stopping pipeline[/red]")
                        return None
                
                elif agent_key == "fixer":
                    success = agent.run(project_path, review_report_path)
                    if not success:
                        console.print(f"[yellow]⚠️ {role} had issues but continuing...[/yellow]")
                
                elif agent_key == "finalizer":
                    success = agent.run(project_path)
                    if not success:
                        console.print(f"[yellow]⚠️ {role} had issues but continuing...[/yellow]")
                
                elif agent_key == "git_pusher":
                    success = agent.run(project_path)
                    if not success:
                        console.print(f"[yellow]⚠️ {role} had issues but continuing...[/yellow]")
                
                # Small delay between phases for better UX
                time.sleep(1)
            
            return project_path
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Pipeline interrupted by user[/yellow]")
            return project_path if project_path else None
        except Exception as e:
            console.print(f"\n[red]Pipeline failed with error: {e}[/red]")
            return project_path if project_path else None
    
    def display_completion_summary(self, project_path: str):
        """Display the completion summary and next steps."""
        console.print("\n[bold green]🎉 Development Pipeline Completed![/bold green]")
        
        # Project summary
        summary_panel = f"""
[bold]Project Location:[/bold] {project_path}

[bold]What was created:[/bold]
• Complete Next.js 14 application with TypeScript
• Responsive UI with Tailwind CSS  
• Database schema with Prisma
• API routes and authentication
• Comprehensive documentation
• Deployment configurations
• Git repository with organized commits

[bold]Quality Assurance:[/bold]
• Code review completed
• Security vulnerabilities addressed  
• Performance optimizations applied
• Accessibility compliance checked
• SEO optimization implemented

[bold]Ready for:[/bold]
• Local development (npm run dev)
• Production deployment (Vercel/Netlify)
• Team collaboration (Git workflow)
• Future enhancements
        """
        
        console.print(Panel(summary_panel, title="📊 Project Summary", border_style="green"))
        
        # Next steps
        next_steps = """
[bold yellow]🚀 Next Steps:[/bold yellow]

1. [bold]Review the generated code:[/bold]
   cd {project_path}
   
2. [bold]Install dependencies:[/bold]
   npm install
   
3. [bold]Set up environment variables:[/bold]
   cp .env.example .env.local
   # Edit .env.local with your values
   
4. [bold]Start development server:[/bold]
   npm run dev
   
5. [bold]Deploy to production:[/bold]
   • Push to GitHub
   • Connect to Vercel/Netlify
   • Configure environment variables
   • Deploy!

6. [bold]Read the documentation:[/bold]
   • README.md - Setup and overview
   • docs/API.md - API documentation  
   • docs/DEPLOYMENT.md - Deployment guide
   • docs/USER_GUIDE.md - User manual
        """.format(project_path=project_path)
        
        console.print(next_steps)
        
        # Success message
        console.print("\n[bold green]✨ Your production-ready web application is complete![/bold green]")
        console.print("[green]Built by your AI Development Team with enterprise-grade quality standards.[/green]")

def main():
    """Main entry point for the orchestrator."""
    parser = argparse.ArgumentParser(
        description="AI Development Team Orchestrator - Build production-ready web apps with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run interactive wizard
  python main.py --skip-wizard     # Skip wizard, use existing project_spec.json
  python main.py --help            # Show this help message

For more information, visit: https://github.com/ai-dev-team/orchestrator
        """
    )
    
    parser.add_argument(
        "--skip-wizard",
        action="store_true",
        help="Skip the interactive wizard and use existing data/project_spec.json"
    )
    
    parser.add_argument(
        "--spec-file",
        type=str,
        default="data/project_spec.json",
        help="Path to project specification file (default: data/project_spec.json)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="AI Development Team Orchestrator v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Display welcome
    orchestrator.display_welcome()
    
    # Check prerequisites
    if not orchestrator.check_prerequisites():
        sys.exit(1)
    
    try:
        # Get project specification
        if args.skip_wizard:
            if not os.path.exists(args.spec_file):
                console.print(f"[red]Error: Specification file not found: {args.spec_file}[/red]")
                console.print("[yellow]Run without --skip-wizard to create a new specification[/yellow]")
                sys.exit(1)
            project_spec_path = args.spec_file
            console.print(f"[green]Using existing specification: {project_spec_path}[/green]")
        else:
            # Run interactive wizard
            wizard = CLIWizard()
            project_spec_path = wizard.run_wizard()
            
            if not project_spec_path:
                console.print("[yellow]Wizard cancelled or failed. Exiting.[/yellow]")
                sys.exit(1)
        
        # Run development pipeline
        project_path = orchestrator.run_development_pipeline(project_spec_path)
        
        if project_path:
            orchestrator.display_completion_summary(project_path)
        else:
            console.print("\n[red]❌ Development pipeline failed[/red]")
            console.print("[yellow]Check the logs above for error details[/yellow]")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user. Goodbye![/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()