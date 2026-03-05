import os
from dotenv import load_dotenv

# 1. LOAD THE KEY FIRST
load_dotenv()

# 2. NOW IMPORT THE AGENTS
from crewai import Agent, Task, Crew, Process

# Debug check: This will tell us if the key is actually loading
print(f"DEBUG: API Key found: {os.getenv('OPENAI_API_KEY') is not None}")

# 1. The Product Manager Agent
pm_agent = Agent(
    role='Product Manager',
    goal='Refine the Student Module requirements for the Chinmaya Mission portal',
    backstory='Expert in educational gamification and community-driven platforms.',
    verbose=True
)

# 2. The Developer Agent
dev_agent = Agent(
    role='Senior Python Developer',
    goal='Implement the Student Module features like Curfews and Point Systems',
    backstory='Specialist in FastAPI and logic-heavy backend systems.',
    verbose=True
)

# 3. The QA Agent
qa_agent = Agent(
    role='Quality Assurance Engineer',
    goal='Ensure the code is bug-free and follows the safety rules of the mission',
    backstory='Detail-oriented tester focused on user safety and edge cases.',
    verbose=True
)

# Task 1: PM plans the roadmap
analyze_requirements = Task(
    description=(
        "Review the student requirements (Reminders, Points, Social Curfew). "
        "Create a structured technical specification for the Developer."
    ),
    expected_output="A structured technical specification document.",
    agent=pm_agent
)

# Task 2: Developer writes the database code
dev_task = Task(
    description=(
        "Create a new Python file called 'curfew_logic.py'. "
        "1. Import the 'SocialPost' model from 'models.py'. "
        "2. Write a function 'can_post(student_time)' that returns False "
        "   if the time is between 22:00 (10 PM) and 07:00 (7 AM). "
        "3. Write a function 'create_post(student_id, content)' that "
        "   checks 'can_post' before saving a SocialPost to the database."
    ),
    expected_output="A Python script (curfew_logic.py) that enforces the social curfew.",
    agent=dev_agent,
    context=[analyze_requirements] 
)

# --- UPDATED CREW ---
chinmaya_app_crew = Crew(
    agents=[pm_agent, dev_agent], 
    tasks=[analyze_requirements, dev_task], 
    process=Process.sequential 
)

# --- START THE WORK ---
result = chinmaya_app_crew.kickoff()

# Save the output to a new file instead of just printing it
with open("developer_output.md", "w") as f:
    f.write(str(result))

print("\n\n######################")
print("SUCCESS: The code has been saved to 'developer_output.md'!")
print("Check your file explorer on the left.")