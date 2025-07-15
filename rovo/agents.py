"""
Agentic components for ROVO Browser Agent
"""
from crewai import Agent, Task, Crew, Process
from agent_tools import NavigationTool, ElementDetectionTool, ClickTool, ScreenshotTool, PageInfoTool
from browser_manager import BrowserManager
from config import Config
import google.generativeai as genai

class BrowserAgents:
    """Factory class for creating browser automation agents"""
    
    def __init__(self, browser_manager: BrowserManager, config: Config):
        self.browser_manager = browser_manager
        self.config = config
        self._setup_llm()
        self._create_tools()
    
    def _setup_llm(self):
        """Setup LLM configuration"""
        api_key = self.config.get('google_api_key')
        if api_key:
            genai.configure(api_key=api_key)
    
    def _create_tools(self):
        """Create agent tools"""
        self.tools = [
            NavigationTool(self.browser_manager),
            ElementDetectionTool(self.browser_manager),
            ClickTool(self.browser_manager),
            ScreenshotTool(self.browser_manager),
            PageInfoTool(self.browser_manager)
        ]
    
    def create_navigation_agent(self) -> Agent:
        """Create navigation specialist agent"""
        return Agent(
            role='Browser Navigator',
            goal='Navigate websites efficiently and handle URL management',
            backstory="""You are an expert web navigator who specializes in 
            browser automation. You can navigate to any website, handle redirects, 
            and ensure pages load properly. You always validate URLs and provide 
            clear feedback about navigation success or failure.""",
            tools=[self.tools[0], self.tools[4]],  # Navigation and PageInfo tools
            verbose=self.config.get('verbose'),
            allow_delegation=False
        )
    
    def create_element_detection_agent(self) -> Agent:
        """Create element detection specialist agent"""
        return Agent(
            role='Element Detective',
            goal='Find and analyze interactive elements on web pages',
            backstory="""You are a specialist in web page analysis and element 
            detection. You can identify all clickable elements, buttons, links, 
            and interactive components on any webpage. You provide detailed 
            information about each element to help with automation decisions.""",
            tools=[self.tools[1], self.tools[4]],  # ElementDetection and PageInfo tools
            verbose=self.config.get('verbose'),
            allow_delegation=False
        )
    
    def create_interaction_agent(self) -> Agent:
        """Create interaction specialist agent"""
        return Agent(
            role='Interaction Specialist',
            goal='Perform precise interactions with web page elements',
            backstory="""You are an expert in web page interactions. You can 
            click buttons, links, and other interactive elements with precision. 
            You always verify that interactions are successful and provide 
            feedback about the results.""",
            tools=[self.tools[2], self.tools[3]],  # Click and Screenshot tools
            verbose=self.config.get('verbose'),
            allow_delegation=False
        )
    
    def create_analysis_agent(self) -> Agent:
        """Create page analysis agent"""
        return Agent(
            role='Web Analyst',
            goal='Analyze web pages and make intelligent decisions about next actions',
            backstory="""You are a web analysis expert who can understand page 
            content, identify important elements, and make strategic decisions 
            about what actions to take next. You help coordinate the overall 
            browsing strategy.""",
            tools=self.tools,  # All tools available
            verbose=self.config.get('verbose'),
            allow_delegation=True
        )

class BrowserCrew:
    """Main crew orchestrator for browser automation tasks"""
    
    def __init__(self, browser_manager: BrowserManager, config: Config):
        self.browser_manager = browser_manager
        self.config = config
        self.agents_factory = BrowserAgents(browser_manager, config)
        self._create_agents()
    
    def _create_agents(self):
        """Create all agents"""
        self.navigator = self.agents_factory.create_navigation_agent()
        self.detector = self.agents_factory.create_element_detection_agent()
        self.interactor = self.agents_factory.create_interaction_agent()
        self.analyst = self.agents_factory.create_analysis_agent()
    
    def create_navigation_task(self, url: str) -> Task:
        """Create navigation task"""
        return Task(
            description=f"""Navigate to the website: {url}
            
            Steps:
            1. Navigate to the URL: {url}
            2. Wait for the page to load completely
            3. Get page information (title, final URL)
            4. Report navigation success or any issues
            
            Provide a clear summary of the navigation result.""",
            agent=self.navigator,
            expected_output="Navigation result with page title and final URL"
        )
    
    def create_element_detection_task(self) -> Task:
        """Create element detection task"""
        return Task(
            description="""Find all clickable elements on the current page.
            
            Steps:
            1. Scan the page for all interactive elements
            2. Identify buttons, links, and clickable components
            3. Provide a numbered list of found elements
            4. Include element text and type information
            
            Focus on the most important and visible elements first.""",
            agent=self.detector,
            expected_output="Numbered list of clickable elements with descriptions"
        )
    
    def create_interaction_task(self, element_description: str) -> Task:
        """Create interaction task"""
        return Task(
            description=f"""Click on the element: {element_description}
            
            Steps:
            1. Identify the correct element based on the description
            2. Click on the element safely
            3. Take a screenshot after clicking
            4. Report the interaction result
            
            Be precise and careful with the interaction.""",
            agent=self.interactor,
            expected_output="Interaction result with confirmation of action taken"
        )
    
    def create_analysis_task(self, goal: str) -> Task:
        """Create analysis task"""
        return Task(
            description=f"""Analyze the current page to achieve this goal: {goal}
            
            Steps:
            1. Get current page information
            2. Find relevant elements for the goal
            3. Determine the best strategy to achieve the goal
            4. Recommend specific actions to take
            
            Provide a clear action plan with specific element recommendations.""",
            agent=self.analyst,
            expected_output="Strategic analysis with recommended actions"
        )
    
    def execute_simple_navigation(self, url: str) -> str:
        """Execute simple navigation workflow"""
        try:
            # Create tasks
            nav_task = self.create_navigation_task(url)
            detection_task = self.create_element_detection_task()
            
            # Create crew
            crew = Crew(
                agents=[self.navigator, self.detector],
                tasks=[nav_task, detection_task],
                process=Process.sequential,
                verbose=self.config.get('verbose')
            )
            
            # Execute
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            return f"Execution error: {str(e)}"
    
    def execute_goal_based_browsing(self, url: str, goal: str) -> str:
        """Execute goal-based browsing workflow"""
        try:
            # Create tasks
            nav_task = self.create_navigation_task(url)
            analysis_task = self.create_analysis_task(goal)
            
            # Create crew
            crew = Crew(
                agents=[self.navigator, self.analyst],
                tasks=[nav_task, analysis_task],
                process=Process.sequential,
                verbose=self.config.get('verbose')
            )
            
            # Execute
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            return f"Execution error: {str(e)}"
    
    def execute_full_automation(self, url: str, goal: str, element_to_click: str = None) -> str:
        """Execute full automation workflow"""
        try:
            # Create tasks
            tasks = [
                self.create_navigation_task(url),
                self.create_element_detection_task(),
                self.create_analysis_task(goal)
            ]
            
            # Add interaction task if element specified
            if element_to_click:
                tasks.append(self.create_interaction_task(element_to_click))
            
            # Create crew with all agents
            crew = Crew(
                agents=[self.navigator, self.detector, self.analyst, self.interactor],
                tasks=tasks,
                process=Process.sequential,
                verbose=self.config.get('verbose')
            )
            
            # Execute
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            return f"Execution error: {str(e)}"