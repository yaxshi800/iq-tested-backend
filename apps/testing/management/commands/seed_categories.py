from django.core.management.base import BaseCommand
from apps.testing.models import TestCategory


class Command(BaseCommand):
    help = "Seed test categories"

    def handle(self, *args, **options):
        categories = [
            {
                "code": "iq",
                "name_uz": "IQ Test",
                "name_en": "IQ Test",
                "name_ru": "IQ Тест",
                "description_uz": "40 savoldan iborat standartlashtirilgan IQ testi",
                "icon": "Brain",
                "color": "indigo",
                "order": 1,
            },
            {
                "code": "math",
                "name_uz": "Matematika",
                "name_en": "Mathematics",
                "name_ru": "Математика",
                "description_uz": "Algebra, geometriya, arifmetika",
                "icon": "Hash",
                "color": "emerald",
                "order": 2,
            },
            {
                "code": "english",
                "name_uz": "Ingliz tili",
                "name_en": "English",
                "name_ru": "Английский язык",
                "description_uz": "Grammar, vocabulary, reading",
                "icon": "BookOpen",
                "color": "violet",
                "order": 3,
            },
            {
                "code": "native",
                "name_uz": "Ona tili va Adabiyot",
                "name_en": "Native Language",
                "name_ru": "Родной язык",
                "description_uz": "O'zbek tili va adabiyoti",
                "icon": "Languages",
                "color": "amber",
                "order": 4,
            },
        ]

        for cat_data in categories:
            cat, created = TestCategory.objects.update_or_create(
                code=cat_data["code"],
                defaults=cat_data,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"{status}: {cat.name_uz}")

        self.stdout.write(self.style.SUCCESS(
            f"Total: {TestCategory.objects.count()} categories"
        ))