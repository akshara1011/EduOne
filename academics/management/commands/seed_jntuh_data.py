"""
Management command: seed_jntuh_data

Seeds the database with JNTUH CSE academic data:
- JNTUH University
- R22 Regulation
- CSE Branch
- Semesters 1-8
- Core CSE subjects with units and topics

Usage: python manage.py seed_jntuh_data
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from academics.models import University, Regulation, Branch, Semester, Subject, Unit, Topic


# â”€â”€ JNTUH CSE Subject Data â”€â”€
JNTUH_CSE_DATA = {
    # Semester 1
    1: [
        {
            'code': 'MA101', 'name': 'Mathematics - I', 'credits': 4,
            'units': [
                {'num': 1, 'name': 'Matrices and Linear Algebra', 'topics': [
                    'Introduction to Matrices', 'Types of Matrices', 'Matrix Operations',
                    'Rank of a Matrix', 'System of Linear Equations', 'Eigenvalues and Eigenvectors'
                ]},
                {'num': 2, 'name': 'Differential Calculus', 'topics': [
                    'Limits and Continuity', 'Differentiation', 'Chain Rule',
                    'Mean Value Theorems', 'Maxima and Minima', "Taylor's Theorem"
                ]},
                {'num': 3, 'name': 'Integral Calculus', 'topics': [
                    'Definite Integrals', 'Applications of Integration',
                    'Double Integrals', 'Triple Integrals', "Gamma and Beta Functions"
                ]},
                {'num': 4, 'name': 'Differential Equations', 'topics': [
                    'First Order ODEs', 'Second Order Linear ODEs',
                    'Homogeneous Equations', 'Particular Integrals', 'Applications'
                ]},
                {'num': 5, 'name': 'Vector Calculus', 'topics': [
                    'Gradient, Divergence, Curl', 'Line Integrals',
                    "Green's Theorem", "Stoke's Theorem", "Gauss's Divergence Theorem"
                ]},
            ]
        },
    ],
    # Semester 3
    3: [
        {
            'code': 'CS301', 'name': 'Data Structures', 'credits': 4,
            'units': [
                {'num': 1, 'name': 'Arrays and Linked Lists', 'topics': [
                    'Introduction to Data Structures', 'Arrays', 'Linked Lists',
                    'Singly Linked List', 'Doubly Linked List', 'Circular Linked List'
                ]},
                {'num': 2, 'name': 'Stacks and Queues', 'topics': [
                    'Stack - Array Implementation', 'Stack - Linked List Implementation',
                    'Applications of Stack', 'Queue Types', 'Circular Queue', 'Deque', 'Priority Queue'
                ]},
                {'num': 3, 'name': 'Trees', 'topics': [
                    'Binary Trees', 'Binary Search Trees', 'Tree Traversals',
                    'AVL Trees', 'Heap Trees', 'B Trees', 'B+ Trees'
                ]},
                {'num': 4, 'name': 'Graphs', 'topics': [
                    'Graph Terminology', 'Graph Representations', 'BFS', 'DFS',
                    "Dijkstra's Algorithm", "Prim's Algorithm", "Kruskal's Algorithm"
                ]},
                {'num': 5, 'name': 'Searching and Sorting', 'topics': [
                    'Linear Search', 'Binary Search', 'Bubble Sort', 'Selection Sort',
                    'Insertion Sort', 'Quick Sort', 'Merge Sort', 'Hashing'
                ]},
            ]
        },
        {
            'code': 'CS302', 'name': 'Database Management Systems', 'credits': 4,
            'units': [
                {'num': 1, 'name': 'Introduction to DBMS', 'topics': [
                    'Database Concepts', 'Database Users', 'DBMS Architecture',
                    'Data Models', 'ER Model', 'ER Diagrams', 'EER Model'
                ]},
                {'num': 2, 'name': 'Relational Model and SQL', 'topics': [
                    'Relational Model Concepts', 'Relational Algebra', 'SQL Basics',
                    'DDL Commands', 'DML Commands', 'Aggregate Functions', 'Joins', 'Subqueries'
                ]},
                {'num': 3, 'name': 'Normalization', 'topics': [
                    'Functional Dependencies', 'First Normal Form (1NF)', 'Second Normal Form (2NF)',
                    'Third Normal Form (3NF)', 'BCNF', 'Fourth Normal Form (4NF)', 'Decomposition'
                ]},
                {'num': 4, 'name': 'Transactions and Concurrency', 'topics': [
                    'Transaction Concepts', 'ACID Properties', 'Schedules',
                    'Concurrency Control', 'Two-Phase Locking', 'Deadlock', 'Recovery Techniques'
                ]},
                {'num': 5, 'name': 'File Organization and Indexing', 'topics': [
                    'File Organization Methods', 'Indexing Concepts', 'B-Tree Indexing',
                    'Hash Indexing', 'Query Processing', 'Query Optimization'
                ]},
            ]
        },
        {
            'code': 'CS303', 'name': 'Operating Systems', 'credits': 4,
            'units': [
                {'num': 1, 'name': 'Introduction and Process Management', 'topics': [
                    'OS Concepts', 'OS Types', 'Process Concept', 'Process States',
                    'Process Control Block', 'Process Scheduling', 'Context Switching'
                ]},
                {'num': 2, 'name': 'CPU Scheduling', 'topics': [
                    'Scheduling Criteria', 'FCFS Scheduling', 'SJF Scheduling',
                    'Priority Scheduling', 'Round Robin', 'Multilevel Queue', 'Real-time Scheduling'
                ]},
                {'num': 3, 'name': 'Memory Management', 'topics': [
                    'Memory Management Background', 'Contiguous Allocation',
                    'Paging', 'Segmentation', 'Virtual Memory', 'Demand Paging', 'Page Replacement'
                ]},
                {'num': 4, 'name': 'Deadlocks', 'topics': [
                    'Deadlock Characterization', 'System Resource-Allocation Graph',
                    'Deadlock Prevention', 'Deadlock Avoidance', "Banker's Algorithm",
                    'Deadlock Detection', 'Recovery from Deadlock'
                ]},
                {'num': 5, 'name': 'File Systems and I/O', 'topics': [
                    'File Concept', 'File System Structure', 'Allocation Methods',
                    'Free Space Management', 'Disk Scheduling', 'I/O Systems', 'Protection'
                ]},
            ]
        },
        {
            'code': 'CS304', 'name': 'Computer Networks', 'credits': 4,
            'units': [
                {'num': 1, 'name': 'Introduction and Physical Layer', 'topics': [
                    'Network Types', 'Network Topologies', 'OSI Model', 'TCP/IP Model',
                    'Physical Layer Concepts', 'Transmission Media', 'Encoding Techniques'
                ]},
                {'num': 2, 'name': 'Data Link Layer', 'topics': [
                    'Framing', 'Error Detection and Correction', 'Flow Control',
                    'HDLC', 'PPP', 'MAC Sublayer', 'Ethernet', 'IEEE Standards'
                ]},
                {'num': 3, 'name': 'Network Layer', 'topics': [
                    'IP Addressing', 'Subnetting', 'Routing Algorithms',
                    'Distance Vector Routing', 'Link State Routing', 'IPv6', 'NAT'
                ]},
                {'num': 4, 'name': 'Transport Layer', 'topics': [
                    'Transport Layer Services', 'UDP', 'TCP', 'Three-way Handshake',
                    'Flow Control', 'Congestion Control', 'Socket Programming'
                ]},
                {'num': 5, 'name': 'Application Layer', 'topics': [
                    'DNS', 'HTTP and HTTPS', 'FTP', 'Email Protocols (SMTP/IMAP/POP3)',
                    'SNMP', 'Network Security Basics', 'Cryptography Fundamentals'
                ]},
            ]
        },
    ],
    # Semester 5
    5: [
        {
            'code': 'CS501', 'name': 'Machine Learning', 'credits': 4,
            'units': [
                {'num': 1, 'name': 'Introduction to Machine Learning', 'topics': [
                    'What is Machine Learning', 'Types of ML', 'Supervised Learning',
                    'Unsupervised Learning', 'Reinforcement Learning', 'ML Workflow', 'Python for ML'
                ]},
                {'num': 2, 'name': 'Regression', 'topics': [
                    'Linear Regression', 'Multiple Linear Regression',
                    'Polynomial Regression', 'Ridge and Lasso', 'Evaluation Metrics'
                ]},
                {'num': 3, 'name': 'Classification', 'topics': [
                    'Logistic Regression', 'K-Nearest Neighbors', 'Decision Trees',
                    'Random Forests', 'SVM', 'Naive Bayes', 'Confusion Matrix'
                ]},
                {'num': 4, 'name': 'Clustering', 'topics': [
                    'K-Means Clustering', 'Hierarchical Clustering', 'DBSCAN',
                    'Dimensionality Reduction', 'PCA', 'Evaluation Metrics'
                ]},
                {'num': 5, 'name': 'Neural Networks', 'topics': [
                    'Perceptron', 'Multi-layer Perceptron', 'Backpropagation',
                    'Activation Functions', 'Introduction to Deep Learning', 'CNNs', 'RNNs'
                ]},
            ]
        },
        {
            'code': 'CS502', 'name': 'Software Engineering', 'credits': 3,
            'units': [
                {'num': 1, 'name': 'Introduction to SE', 'topics': [
                    'Software Process', 'Software Development Life Cycle',
                    'Waterfall Model', 'Agile Model', 'Spiral Model', 'Requirements Engineering'
                ]},
                {'num': 2, 'name': 'Design and Architecture', 'topics': [
                    'Software Design Principles', 'Coupling and Cohesion',
                    'Architectural Patterns', 'UML Diagrams', 'Object-Oriented Design'
                ]},
                {'num': 3, 'name': 'Software Testing', 'topics': [
                    'Testing Levels', 'Unit Testing', 'Integration Testing',
                    'System Testing', 'Black Box Testing', 'White Box Testing', 'Test Cases'
                ]},
                {'num': 4, 'name': 'Project Management', 'topics': [
                    'Project Planning', 'Cost Estimation', 'COCOMO Model',
                    'Function Point Analysis', 'Risk Management', 'Software Metrics'
                ]},
                {'num': 5, 'name': 'Quality and Maintenance', 'topics': [
                    'Software Quality', 'ISO Standards', 'CMM Levels',
                    'Software Maintenance Types', 'Configuration Management'
                ]},
            ]
        },
    ],
}


class Command(BaseCommand):
    help = 'Seed the database with JNTUH CSE academic data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding JNTUH CSE data...'))

        with transaction.atomic():
            # 1. University
            university, created = University.objects.get_or_create(
                short_name='JNTUH',
                defaults={
                    'name': 'Jawaharlal Nehru Technological University Hyderabad',
                    'state': 'Telangana',
                    'website': 'https://jntuh.ac.in',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  [OK] Created University: {university}')

            # 2. Regulation
            regulation, created = Regulation.objects.get_or_create(
                university=university,
                name='R22',
                defaults={'year': 2022, 'description': 'JNTUH R22 Regulation', 'is_active': True}
            )
            if created:
                self.stdout.write(f'  [OK] Created Regulation: {regulation}')

            # 3. Branch - CSE
            branch, created = Branch.objects.get_or_create(
                short_name='CSE',
                defaults={
                    'name': 'Computer Science and Engineering',
                    'description': 'B.Tech Computer Science and Engineering',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  [OK] Created Branch: {branch}')

            # Also create common branches
            for bname, bshort in [
                ('Electronics and Communication Engineering', 'ECE'),
                ('Mechanical Engineering', 'ME'),
                ('Civil Engineering', 'CE'),
                ('Electrical and Electronics Engineering', 'EEE'),
            ]:
                Branch.objects.get_or_create(
                    short_name=bshort,
                    defaults={'name': bname, 'is_active': True}
                )

            # 4. Semesters 1-8
            for sem_num in range(1, 9):
                year = (sem_num + 1) // 2
                sem, created = Semester.objects.get_or_create(
                    regulation=regulation,
                    branch=branch,
                    semester_number=sem_num,
                    defaults={'year_of_study': year}
                )
                if created:
                    self.stdout.write(f'  âœ… Created Semester {sem_num}')

            # 5. Subjects, Units, Topics
            subjects_created = 0
            units_created = 0
            topics_created = 0

            for sem_num, subjects_data in JNTUH_CSE_DATA.items():
                semester = Semester.objects.get(
                    regulation=regulation,
                    branch=branch,
                    semester_number=sem_num
                )

                for subj_data in subjects_data:
                    subject, created = Subject.objects.get_or_create(
                        subject_code=subj_data['code'],
                        defaults={
                            'name': subj_data['name'],
                            'semester': semester,
                            'credits': subj_data['credits'],
                            'subject_type': 'theory',
                            'is_active': True,
                        }
                    )
                    if created:
                        subjects_created += 1

                    for unit_data in subj_data['units']:
                        unit, ucreated = Unit.objects.get_or_create(
                            subject=subject,
                            unit_number=unit_data['num'],
                            defaults={'name': unit_data['name']}
                        )
                        if ucreated:
                            units_created += 1

                        for i, topic_name in enumerate(unit_data['topics']):
                            topic, tcreated = Topic.objects.get_or_create(
                                unit=unit,
                                name=topic_name,
                                defaults={'order': i + 1}
                            )
                            if tcreated:
                                topics_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nðŸŽ‰ Seeding complete!\n'
            f'   University: JNTUH\n'
            f'   Regulation: R22\n'
            f'   Branch: CSE\n'
            f'   Subjects created: {subjects_created}\n'
            f'   Units created: {units_created}\n'
            f'   Topics created: {topics_created}\n\n'
            f'You can now:\n'
            f'  1. Run: python manage.py createsuperuser\n'
            f'  2. Visit: http://127.0.0.1:8000/admin/\n'
            f'  3. Register as student, select JNTUH â†’ CSE â†’ Sem 3 or 5\n'
        ))

