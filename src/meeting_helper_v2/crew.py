from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class MeetingTool():
    """MeetingTool crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config['orchestrator'],
            verbose=False
        )

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['summarizer'],
            verbose=False
        )

    @agent
    def action_item_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['action_item_extractor'],
            verbose=False
        )

    @agent
    def decision_logger(self) -> Agent:
        return Agent(
            config=self.agents_config['decision_logger'],
            verbose=False
        )

    @agent
    def risk_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_finder'],
            verbose=False
        )

    # One task per specialist agent
    @task
    def summarize_task(self) -> Task:
        return Task(
            config=self.tasks_config['summarize_task'],
            agent=self.summarizer()
        )

    @task
    def action_item_task(self) -> Task:
        return Task(
            config=self.tasks_config['action_item_task'],
            agent=self.action_item_extractor()
        )

    @task
    def decision_task(self) -> Task:
        return Task(
            config=self.tasks_config['decision_task'],
            agent=self.decision_logger()
        )

    @task
    def risk_task(self) -> Task:
        return Task(
            config=self.tasks_config['risk_task'],
            agent=self.risk_finder()
        )

    @task
    def final_transcript_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_transcript_task'],
            agent=self.orchestrator(),
            # context pulls in all previous task outputs
            context=[
                self.summarize_task(),
                self.action_item_task(),
                self.decision_task(),
                self.risk_task()
            ]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.summarizer(),
                self.action_item_extractor(),
                self.decision_logger(),
                self.risk_finder(),
                self.orchestrator()
            ],
            tasks=self.tasks,  # auto-discovers all @task methods in order
            process=Process.sequential,
            verbose=False
        )
