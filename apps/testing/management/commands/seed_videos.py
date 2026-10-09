from django.core.management.base import BaseCommand
from apps.testing.models import Question


# ═══════════════════════════════════════════
# VIDEO MA'LUMOTLARI
# Har bir kategoriya uchun 3 xil video
# ═══════════════════════════════════════════

VIDEO_LIBRARY = {
    # ═══════════ IQ TEST ═══════════
    "pattern": [
        {
            "title": "Pattern Recognition - IQ Test Practice",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "8:15"
        },
        {
            "title": "Abstract Reasoning - Complete Guide",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "12:30"
        },
        {
            "title": "How to Solve Matrix Reasoning",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "6:45"
        },
    ],
    "spatial": [
        {
            "title": "Spatial Visualization Practice",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "7:20"
        },
        {
            "title": "3D Rotation Techniques",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "9:50"
        },
        {
            "title": "Spatial Reasoning Tips",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "5:15"
        },
    ],
    "numerical": [
        {
            "title": "Number Sequences Explained",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "6:30"
        },
        {
            "title": "Fibonacci & Arithmetic Sequences",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "10:45"
        },
        {
            "title": "Number Pattern Tricks",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "8:00"
        },
    ],
    "abstract": [
        {
            "title": "Abstract Reasoning Masterclass",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "11:20"
        },
        {
            "title": "Logical Deduction Techniques",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "7:55"
        },
        {
            "title": "Abstract Thinking Exercises",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:10"
        },
    ],

    # ═══════════ MATEMATIKA ═══════════
    "algebra": [
        {
            "title": "Solving Linear Equations",
            "url": "https://www.youtube.com/embed/I3XzepN03KQ",
            "duration": "8:30"
        },
        {
            "title": "Equations with Variables on Both Sides",
            "url": "https://www.youtube.com/embed/76E9K3JzjDM",
            "duration": "6:15"
        },
        {
            "title": "Two-Step Equations Practice",
            "url": "https://www.youtube.com/embed/LDliYKYwdA",
            "duration": "5:40"
        },
    ],
    "geometry": [
        {
            "title": "Geometry Basics - Area & Perimeter",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:20"
        },
        {
            "title": "Triangles & Pythagorean Theorem",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "11:05"
        },
        {
            "title": "Circles - Radius, Diameter, Area",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "7:45"
        },
    ],
    "arithmetic": [
        {
            "title": "Basic Arithmetic Operations",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "6:20"
        },
        {
            "title": "Fractions & Decimals",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "8:50"
        },
        {
            "title": "Percentages Made Easy",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "5:30"
        },
    ],
    "logic": [
        {
            "title": "Math Logic Problems",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "7:10"
        },
        {
            "title": "Word Problems - Distance, Rate, Time",
            "url": "https://www.youtube.com/embed/4Ru1suvxv6o",
            "duration": "9:25"
        },
        {
            "title": "Mixture & Work Problems",
            "url": "https://www.youtube.com/embed/NCqijoOw3Ck",
            "duration": "8:15"
        },
    ],

    # ═══════════ INGLIZ TILI ═══════════
    "grammar": [
        {
            "title": "Present Simple Tense - Complete Guide",
            "url": "https://www.youtube.com/embed/p5P4-J_zfJc",
            "duration": "7:45"
        },
        {
            "title": "Past Simple vs Present Perfect",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:30"
        },
        {
            "title": "English Grammar - Conditionals",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "11:00"
        },
    ],
    "vocabulary": [
        {
            "title": "100 Most Common English Words",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "12:15"
        },
        {
            "title": "Synonyms & Antonyms",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "8:40"
        },
        {
            "title": "Advanced English Vocabulary",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "10:20"
        },
    ],
    "reading": [
        {
            "title": "English Reading Comprehension",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:15"
        },
        {
            "title": "Speed Reading Techniques",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "7:30"
        },
        {
            "title": "IELTS Reading Strategies",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "13:00"
        },
    ],

    # ═══════════ ONA TILI ═══════════
    "grammar_uz": [
        {
            "title": "O'zbek tili grammatikasi - Bo'g'inlar",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "8:20"
        },
        {
            "title": "So'z turkumlari - Ot, Sifat, Fe'l",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "10:15"
        },
        {
            "title": "Kelishiklar va qo'shimchalar",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "7:40"
        },
    ],
    "literature": [
        {
            "title": "Alisher Navoiy - Hayoti va ijodi",
            "url": "https://www.youtube.com/embed/EnmWmrNdjzE",
            "duration": "11:30"
        },
        {
            "title": "O'zbek adabiyoti tarixi",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:45"
        },
        {
            "title": "Abdulla Qodiriy - O'tkan kunlar",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "8:55"
        },
    ],
    "ortography": [
        {
            "title": "O'zbek tili orfografiyasi",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "6:50"
        },
        {
            "title": "To'g'ri yozish qoidalari",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "9:20"
        },
        {
            "title": "Tinish belgilari",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "7:15"
        },
    ],
    "analysis": [
        {
            "title": "So'z tahlili",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "8:35"
        },
        {
            "title": "Matn tahlili usullari",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "10:00"
        },
        {
            "title": "Badiiy asar tahlili",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:10"
        },
    ],

    # ═══════════ RUS TILI ═══════════
    "grammar_ru": [
        {
            "title": "Русская грамматика - Глаголы",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:20"
        },
        {
            "title": "Русский язык - Падежи",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "11:15"
        },
        {
            "title": "Времена глаголов в русском языке",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "8:45"
        },
    ],
    "vocabulary_ru": [
        {
            "title": "Русская лексика - Синонимы",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "7:30"
        },
        {
            "title": "Русские антонимы",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "6:20"
        },
        {
            "title": "Богатство русского языка",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "12:00"
        },
    ],
    "reading_ru": [
        {
            "title": "Чтение на русском языке",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "8:10"
        },
        {
            "title": "Русская литература - Чтение",
            "url": "https://www.youtube.com/embed/EDi4ETHTG6s",
            "duration": "10:30"
        },
        {
            "title": "Понимание текста на русском",
            "url": "https://www.youtube.com/embed/Yy0NB3DrWRI",
            "duration": "9:00"
        },
    ],
}


class Command(BaseCommand):
    help = "Seed videos for questions"

    def handle(self, *args, **options):
        updated = 0
        for question in Question.objects.all():
            videos = VIDEO_LIBRARY.get(question.category, [])
            if videos:
                question.videos = videos
                question.save(update_fields=["videos"])
                updated += 1
                self.stdout.write(f"✓ Q{question.id} ({question.category}): {len(videos)} videos")

        self.stdout.write(self.style.SUCCESS(
            f"\nTotal: {updated} questions updated with videos"
        ))