from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import StudentProfile, Skill, StudentSkillSet
from faker import Faker
from datetime import datetime
import random

User = get_user_model()

# Initialize Faker with Indian locale
fake = Faker('en_IN')

TECH_STACKS = {
    'MERN': ['MongoDB', 'Express', 'React', 'Node.js', 'JavaScript'],
    'Data Science': ['Python', 'Pandas', 'SQL', 'Tableau', 'Machine Learning'],
    'Backend': ['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Redis'],
    'Java Core': ['Java', 'Spring Boot', 'Hibernate', 'MySQL'],
    'Frontend': ['HTML', 'CSS', 'React', 'Tailwind', 'JavaScript'],
    'AI/ML': ['Python', 'TensorFlow', 'NLP', 'Scikit-learn', 'OpenCV'],
    'Cybersecurity': ['Kali Linux', 'Wireshark', 'Python', 'Metasploit'],
    'Python Backend': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Celery'],
    'C++': ['C++', 'OOP', 'Data Structures', 'Algorithms'],
    'Data Analytics': ['Excel', 'PowerBI', 'SQL', 'Python', 'Tableau'],
    'DevOps': ['Git', 'Jenkins', 'Docker', 'Kubernetes', 'Ansible'],
    'MEAN': ['MongoDB', 'Express', 'Angular', 'Node.js'],
    'Android': ['Java', 'Kotlin', 'Firebase', 'Android Studio'],
    'Full Stack': ['Next.js', 'TypeScript', 'Prisma', 'PostgreSQL', 'Vercel'],
    'Blockchain': ['Solidity', 'Web3.js', 'Ethereum', 'Smart Contracts'],
    'Cloud': ['AWS', 'Linux', 'Docker', 'Bash', 'Terraform'],
}

ACHIEVEMENTS = [
    "Smart India Hackathon Finalist",
    "Published paper in IEEE",
    "TCS CodeVita Round 2",
    "1st place Web UI Contest",
    "AWS Cloud Practitioner",
    "Kaggle Top 10%",
    "Found 3 CVEs",
    "Completed 500 LeetCode problems",
    "Codeforces Specialist",
    "Data-Thon Winner",
    "Open Source Contributor",
    "Dean's Merit List",
    "Google Play App Published",
    "Hacktoberfest Finisher",
    "EthIndia Finalist",
    "Hackathon Winner",
    "Research Paper Published",
    "Microsoft Certified",
    "Google Certified",
    "Campus Ambassador",
]

PROJECTS = [
    "Campus Event Tracker",
    "Sales Predictor",
    "Library Management System",
    "E-commerce Storefront",
    "Auto-scaling Web Cluster",
    "Sentiment Analysis Engine",
    "Network Sniffer",
    "Blog Platform API",
    "Pathfinding Visualizer",
    "Retail Dashboard",
    "CI/CD Pipeline Setup",
    "Real-time Chat App",
    "Expense Tracker App",
    "Portfolio Generator",
    "Decentralized Voting App",
    "Task Management System",
    "Weather Forecasting App",
    "Social Media Dashboard",
    "Online Learning Platform",
    "Inventory Management",
]

class Command(BaseCommand):
    help = 'Generate realistic student data using Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of students to generate',
        )
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Only generate demo data when no student profiles exist',
        )

    def handle(self, *args, **options):
        count = options['count']
        only_if_empty = options['if_empty']

        if only_if_empty and StudentProfile.objects.exists():
            self.stdout.write('Skipping demo generation because student profiles already exist.')
            return

        self.stdout.write(f'Generating {count} realistic student profiles...')

        created_users = 0
        created_profiles = 0
        created_skills = 0
        created_skill_sets = 0

        for i in range(count):
            # Generate stable demo student data
            name = fake.name()
            email = f"demo_student_{i + 1}@example.com"
            phone = ''.join(str(random.randint(0, 9)) for _ in range(10))
            username = f"demo_student_{i + 1}"

            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': name.split()[0],
                    'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                    'is_tpo': False
                }
            )
            if user_created:
                created_users += 1

            # Generate profile data
            semester = random.randint(1, 8)
            section = str(random.randint(1, 3))
            cgpa = round(random.uniform(6.0, 9.8), 1)

            stack_name = random.choice(list(TECH_STACKS.keys()))
            skills_list = TECH_STACKS[stack_name]
            skill_count = len(skills_list)

            # Random achievements and projects
            num_achievements = random.randint(0, 3)
            achievements = random.sample(ACHIEVEMENTS, num_achievements) if num_achievements > 0 else []

            num_projects = random.randint(0, 2)
            projects = random.sample(PROJECTS, num_projects) if num_projects > 0 else []

            # Create or update student profile
            profile, profile_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': name,
                    'phone': phone,
                    'cgpa': cgpa,
                    'semester': semester,
                    'section': section,
                    'tech_stack': stack_name,
                    'achievements': '; '.join(achievements),
                    'projects': '; '.join(projects),
                    'updated_at': datetime.utcnow()
                }
            )
            
            # Update the profile with generated data (in case it was auto-created by signal)
            if not profile_created:
                profile.full_name = name
                profile.phone = phone
                profile.cgpa = cgpa
                profile.semester = semester
                profile.section = section
                profile.tech_stack = stack_name
                profile.achievements = '; '.join(achievements)
                profile.projects = '; '.join(projects)
                profile.updated_at = datetime.utcnow()
                profile.save()
            if profile_created:
                created_profiles += 1

            # Create skills and skill sets
            for skill_name in skills_list:
                # Create skill if doesn't exist
                skill, skill_created = Skill.objects.get_or_create(
                    skill_name=skill_name,
                    defaults={'category': stack_name}
                )
                if skill_created:
                    created_skills += 1

                # Create student skill set
                skill_set, skill_set_created = StudentSkillSet.objects.get_or_create(
                    student_profile=profile,
                    skill=skill,
                    defaults={'skill_level': random.randint(1, 5)}
                )
                if skill_set_created:
                    created_skill_sets += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Generation complete!\n'
                f'Created: {created_users} users, {created_profiles} profiles, '
                f'{created_skills} skills, {created_skill_sets} skill sets'
            )
        )