from django.core.management.base import BaseCommand
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = 'Seeds initial courses and lessons into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding sample courses and lessons...'))

        sample_courses = [
            {
                'title': 'Python Programming',
                'description': 'Master the fundamentals of Python programming from scratch. Learn syntax, data types, logic control, functions, and standard libraries.',
                'instructor': 'Dr. Alan Turing',
                'category': 'Programming',
                'duration': '6 Hours',
                'lessons': [
                    {
                        'title': 'Introduction to Python',
                        'content': 'Python is a high-level, interpreted programming language created by Guido van Rossum. It is renowned for its clean syntax, readability, and versatile application in web development, data science, and AI.\n\nTo write your first Python code, use the print() function:\n\n```python\nprint("Hello, World!")\n```\n\nPython relies on indentation (spaces or tabs) to define code blocks.',
                        'video_url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8',
                    },
                    {
                        'title': 'Variables and Data Types',
                        'content': 'In Python, variables are created when you assign a value to them:\n\n- Integers: x = 10\n- Floats: y = 3.14\n- Strings: name = "Alice"\n- Booleans: is_active = True\n\nPython is dynamically typed, meaning you do not need to explicitly declare variable types.',
                        'video_url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8',
                    },
                    {
                        'title': 'Conditional Statements',
                        'content': 'Control the execution flow using if, elif, and else statements:\n\n```python\nage = 20\nif age >= 18:\n    print("Adult")\nelif age >= 13:\n    print("Teenager")\nelse:\n    print("Child")\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'Loops',
                        'content': 'Python offers two primary loop structures:\n\n1. For Loop: Iterate over a sequence (list, tuple, range).\n```python\nfor i in range(5):\n    print(i)\n```\n\n2. While Loop: Repeat as long as a condition remains True.\n```python\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'Functions',
                        'content': 'Functions allow you to block code into reusable units using the `def` keyword:\n\n```python\ndef greet(name):\n    return f"Hello, {name}!"\n\nmessage = greet("Student")\nprint(message)\n```',
                        'video_url': '',
                    },
                ]
            },
            {
                'title': 'Web Development',
                'description': 'Learn how to build beautiful, modern websites using HTML5, CSS3, and JavaScript. Understand document structures, layout styles, and interactive scripts.',
                'instructor': 'Sarah Jenkins',
                'category': 'Web Development',
                'duration': '8 Hours',
                'lessons': [
                    {
                        'title': 'Introduction to Web',
                        'content': 'Web development revolves around three primary frontend technologies:\n\n1. HTML: Provides the structural skeleton.\n2. CSS: Styles the presentation and layout.\n3. JavaScript: Adds interactive behavior.',
                        'video_url': '',
                    },
                    {
                        'title': 'HTML Fundamentals',
                        'content': 'HTML uses tags to structure Web pages:\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n  <title>My First Page</title>\n</head>\n<body>\n  <h1>Welcome</h1>\n  <p>This is a paragraph.</p>\n</body>\n</html>\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'CSS Styling',
                        'content': 'CSS controls visual presentation. You can apply styles using element selectors, class selectors, and ID selectors:\n\n```css\nbody {\n  font-family: Arial, sans-serif;\n  background-color: #f4f6f9;\n  color: #333;\n}\n.card {\n  border-radius: 8px;\n  padding: 16px;\n}\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'JavaScript Basics',
                        'content': 'JavaScript executes in the browser to manipulate the DOM and respond to user events:\n\n```javascript\ndocument.querySelector("button").addEventListener("click", function() {\n  alert("Button clicked!");\n});\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'Responsive Design',
                        'content': 'Responsive web design ensures websites look great on mobile phones, tablets, and desktop screens using media queries:\n\n```css\n@media (max-width: 768px) {\n  .navbar {\n    flex-direction: column;\n  }\n}\n```',
                        'video_url': '',
                    },
                ]
            },
            {
                'title': 'Database Fundamentals',
                'description': 'Understand relational database concepts, entity relationships, normalization, and standard SQL queries using SQLite and PostgreSQL principles.',
                'instructor': 'Prof. Michael Stone',
                'category': 'Databases',
                'duration': '5 Hours',
                'lessons': [
                    {
                        'title': 'Introduction to Databases',
                        'content': 'A database is an organized collection of structured information or data. Relational Database Management Systems (RDBMS) store data in tables composed of rows and columns.',
                        'video_url': '',
                    },
                    {
                        'title': 'SQL Basics',
                        'content': 'Structured Query Language (SQL) is used to communicate with databases. Main operations include SELECT, INSERT, UPDATE, and DELETE:\n\n```sql\nSELECT * FROM courses WHERE is_published = 1;\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'Tables and Schemas',
                        'content': 'Database tables define fields with data types (INTEGER, VARCHAR, DATETIME) and constraints such as PRIMARY KEY and NOT NULL.',
                        'video_url': '',
                    },
                    {
                        'title': 'Relationships and Foreign Keys',
                        'content': 'Relational databases establish connections using Foreign Keys:\n- One-to-Many (e.g. One Course has Many Lessons)\n- Many-to-Many (e.g. Students enrolled in Courses)',
                        'video_url': '',
                    },
                    {
                        'title': 'Advanced SQL Queries',
                        'content': 'Combine tables using JOIN clauses and aggregate data using GROUP BY and COUNT():\n\n```sql\nSELECT courses.title, COUNT(lessons.id) \nFROM courses \nLEFT JOIN lessons ON courses.id = lessons.course_id \nGROUP BY courses.id;\n```',
                        'video_url': '',
                    },
                ]
            },
            {
                'title': 'Java Programming',
                'description': 'A foundational course in Java programming covering syntax, object-oriented principles, classes, inheritance, polymorphism, and standard I/O.',
                'instructor': 'James Gosling',
                'category': 'Programming',
                'duration': '7 Hours',
                'lessons': [
                    {
                        'title': 'Introduction to Java',
                        'content': 'Java is a robust, object-oriented, cross-platform programming language. Java code compiles into bytecode executed by the Java Virtual Machine (JVM).',
                        'video_url': '',
                    },
                    {
                        'title': 'Variables & Operators',
                        'content': 'Java is strongly typed. Declare variable types explicitly:\n\n```java\nint count = 10;\ndouble price = 19.99;\nString message = "Java Programming";\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'Control Flow',
                        'content': 'Control application flow with if-else and switch statements:\n\n```java\nif (score >= 50) {\n    System.out.println("Passed");\n} else {\n    System.out.println("Failed");\n}\n```',
                        'video_url': '',
                    },
                    {
                        'title': 'Object-Oriented Programming (OOP)',
                        'content': 'Java revolves around four core OOP principles:\n1. Encapsulation\n2. Inheritance\n3. Polymorphism\n4. Abstraction',
                        'video_url': '',
                    },
                    {
                        'title': 'Methods and Arrays',
                        'content': 'Methods define reusable logic within classes, while arrays store fixed-size sequential elements of the same type.',
                        'video_url': '',
                    },
                ]
            },
            {
                'title': 'Computer Networking',
                'description': 'Understand how data traverses global networks. Learn about the OSI model, TCP/IP stack, IP routing, switches, routers, and cybersecurity basics.',
                'instructor': 'Dr. Robert Kahn',
                'category': 'Networking',
                'duration': '6 Hours',
                'lessons': [
                    {
                        'title': 'Networking Basics',
                        'content': 'Computer networking connects nodes (computers, servers, routers) to share resources and communicate. Key concepts include Local Area Networks (LAN) and Wide Area Networks (WAN).',
                        'video_url': '',
                    },
                    {
                        'title': 'IP Addresses and Subnetting',
                        'content': 'An IP address uniquely identifies a device on a network. IPv4 uses 32-bit addresses (e.g., 192.168.1.1), while IPv6 uses 128-bit hexadecimal addresses.',
                        'video_url': '',
                    },
                    {
                        'title': 'TCP/IP Model & Protocols',
                        'content': 'The TCP/IP model has 4 layers: Application (HTTP, DNS), Transport (TCP, UDP), Internet (IP), and Network Access (Ethernet).',
                        'video_url': '',
                    },
                    {
                        'title': 'Network Routing & Switching',
                        'content': 'Switches operate at Layer 2 (Data Link) using MAC addresses. Routers operate at Layer 3 (Network) using IP addresses to route packets across networks.',
                        'video_url': '',
                    },
                    {
                        'title': 'Network Security Fundamentals',
                        'content': 'Protect networks using Firewalls, Encryption (TLS/SSL), Intrusion Detection Systems (IDS), and VPNs to ensure confidentiality, integrity, and availability (CIA triad).',
                        'video_url': '',
                    },
                ]
            },
        ]

        created_courses_count = 0
        created_lessons_count = 0

        for c_data in sample_courses:
            lessons_data = c_data.pop('lessons')
            course, created = Course.objects.get_or_create(
                title=c_data['title'],
                defaults=c_data
            )
            if created:
                created_courses_count += 1

            for idx, l_data in enumerate(lessons_data, start=1):
                lesson, l_created = Lesson.objects.get_or_create(
                    course=course,
                    order=idx,
                    defaults={
                        'title': l_data['title'],
                        'content': l_data['content'],
                        'video_url': l_data.get('video_url', ''),
                    }
                )
                if l_created:
                    created_lessons_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {created_courses_count} courses and {created_lessons_count} lessons!'
            )
        )
