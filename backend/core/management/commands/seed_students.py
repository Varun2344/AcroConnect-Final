from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import StudentProfile, Skill, StudentSkillSet
from datetime import datetime
import csv
import io

User = get_user_model()

SAMPLE_DATA = """profile_id,user_id,name,email,phone,semester,section,cgpa,tech_stack,skill_count,skills,achievements,projects,updated_at
7,7,Rahul Sharma,rahul.s@gmail.com,9876543210,6,1,8.2,MERN,5,"MongoDB, Express, React, Node.js, JavaScript","Smart India Hackathon Finalist","Campus Event Tracker",2026-04-28T10:00:00.000000Z
8,8,Priya Patel,priyap@yahoo.com,8765432109,6,2,9.1,Data Science,4,"Python, Pandas, SQL, Tableau","Published paper in IEEE","Sales Predictor",2026-04-28T10:05:00.000000Z
9,9,Amit Kumar,amit.k@gmail.com,7654321098,5,1,7.5,Core Java,3,"Java, Spring Boot, MySQL","TCS CodeVita Round 2","Library Management System",2026-04-28T10:10:00.000000Z
10,10,Sneha Desai,snehad@gmail.com,6543210987,7,3,8.8,Frontend,4,"HTML, CSS, React, Tailwind","1st place Web UI Contest","E-commerce Storefront",2026-04-28T10:15:00.000000Z
11,11,Rohan Gupta,rohang@hotmail.com,9988776655,8,2,6.9,Cloud,4,"AWS, Linux, Docker, Bash","AWS Cloud Practitioner","Auto-scaling Web Cluster",2026-04-28T10:20:00.000000Z
12,12,Ananya Singh,ananyas@gmail.com,8877665544,5,1,9.4,AI/ML,5,"Python, TensorFlow, NLP, Scikit-learn, OpenCV","Kaggle Top 10%","Sentiment Analysis Engine",2026-04-28T10:25:00.000000Z
13,13,Vikram Reddy,vikram.r@gmail.com,7766554433,6,3,7.1,Cybersecurity,3,"Kali Linux, Wireshark, Python","Found 3 CVEs","Network Sniffer",2026-04-28T10:30:00.000000Z
14,14,Pooja Verma,poojav@gmail.com,6655443322,7,2,8.5,Python Backend,4,"Python, Django, PostgreSQL, Redis","Completed 500 LeetCode problems","Blog Platform API",2026-04-28T10:35:00.000000Z
15,15,Karan Malhotra,karanm@gmail.com,5544332211,8,1,7.8,C++,3,"C++, OOP, Data Structures","Codeforces Specialist","Pathfinding Visualizer",2026-04-28T10:40:00.000000Z
16,16,Nisha Tiwari,nishat@yahoo.com,9123456780,5,2,8.0,Data Analytics,4,"Excel, PowerBI, SQL, Python","Data-Thon Winner","Retail Dashboard",2026-04-28T10:45:00.000000Z
17,17,Aditya Joshi,adityaj@gmail.com,8234567890,6,1,7.4,DevOps,5,"Git, Jenkins, Docker, Kubernetes, Ansible","Open Source Contributor","CI/CD Pipeline Setup",2026-04-28T10:50:00.000000Z
18,18,Meera Nair,meeran@gmail.com,7345678901,7,3,9.0,MEAN,4,"MongoDB, Express, Angular, Node.js","Dean's Merit List","Real-time Chat App",2026-04-28T10:55:00.000000Z
19,19,Sanjay Das,sanjayd@gmail.com,6456789012,8,2,6.5,Android,3,"Java, Kotlin, Firebase","Google Play App Published","Expense Tracker App",2026-04-28T11:00:00.000000Z
20,20,Ritu Chauhan,rituc@gmail.com,9567890123,5,3,8.7,Full Stack,5,"Next.js, TypeScript, Prisma, PostgreSQL, Vercel","Hacktoberfest Finisher","Portfolio Generator",2026-04-28T11:05:00.000000Z
21,21,Tarun Agarwal,taruna@gmail.com,8678901234,6,1,7.9,Blockchain,3,"Solidity, Web3.js, Ethereum","EthIndia Finalist","Decentralized Voting App",2026-04-28T11:10:00.000000Z"""

class Command(BaseCommand):
    help = 'Seed the database with sample student data'

    def handle(self, *args, **options):
        # Parse CSV data
        csv_reader = csv.DictReader(io.StringIO(SAMPLE_DATA))
        rows = list(csv_reader)

        self.stdout.write(f'Found {len(rows)} student records to process...')

        created_users = 0
        created_profiles = 0
        created_skills = 0
        created_skill_sets = 0

        for row in rows:
            user_id = int(row['user_id'])
            profile_id = int(row['profile_id'])

            # Create user if doesn't exist
            user, user_created = User.objects.get_or_create(
                id=user_id,
                defaults={
                    'username': row['email'].split('@')[0],  # Use email prefix as username
                    'email': row['email'],
                    'first_name': row['name'].split()[0],
                    'last_name': ' '.join(row['name'].split()[1:]) if len(row['name'].split()) > 1 else '',
                    'is_tpo': False
                }
            )
            if user_created:
                created_users += 1
                self.stdout.write(f'Created user: {user.username} ({user.email})')

            # Create student profile
            profile, profile_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': row['name'],
                    'phone': row['phone'],
                    'cgpa': float(row['cgpa']),
                    'semester': int(row['semester']),
                    'section': row['section'],
                    'tech_stack': row['tech_stack'],
                    'achievements': row['achievements'],
                    'projects': row['projects'],
                    'updated_at': datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00'))
                }
            )
            if profile_created:
                created_profiles += 1
                self.stdout.write(f'Created profile: {profile.full_name}')

            # Process skills
            skills_str = row['skills']
            if skills_str:
                skill_names = [s.strip() for s in skills_str.split(',')]
                for skill_name in skill_names:
                    # Create skill if doesn't exist
                    skill, skill_created = Skill.objects.get_or_create(
                        skill_name=skill_name,
                        defaults={'category': row['tech_stack']}
                    )
                    if skill_created:
                        created_skills += 1

                    # Create student skill set
                    skill_set, skill_set_created = StudentSkillSet.objects.get_or_create(
                        student_profile=profile,
                        skill=skill,
                        defaults={'skill_level': 3}  # Default skill level
                    )
                    if skill_set_created:
                        created_skill_sets += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeding complete!\n'
                f'Created: {created_users} users, {created_profiles} profiles, '
                f'{created_skills} skills, {created_skill_sets} skill sets'
            )
        )