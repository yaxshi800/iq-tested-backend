from django.core.management.base import BaseCommand
from apps.accounts.models import Achievement


class Command(BaseCommand):
    help = "Seed achievements"

    def handle(self, *args, **options):
        achievements = [
            {"code": "first_test", "name_uz": "Birinchi qadam", "description_uz": "Birinchi testni tugatdingiz", "icon": "Play", "color": "indigo", "points": 10, "order": 1},
            {"code": "perfect_score", "name_uz": "Mukammal natija", "description_uz": "100% natija", "icon": "Trophy", "color": "amber", "points": 100, "order": 2},
            {"code": "iq_master", "name_uz": "IQ ustasi", "description_uz": "IQ 120+", "icon": "Brain", "color": "violet", "points": 50, "order": 3},
            {"code": "seven_day_streak", "name_uz": "7 kunlik streak", "description_uz": "7 kun ketma-ket", "icon": "Flame", "color": "rose", "points": 70, "order": 4},
            {"code": "thirty_day_streak", "name_uz": "30 kunlik streak", "description_uz": "30 kun ketma-ket", "icon": "Flame", "color": "rose", "points": 300, "order": 5},
            {"code": "all_tests_done", "name_uz": "Barcha testlar", "description_uz": "5 ta test turini tugatdingiz", "icon": "Award", "color": "emerald", "points": 150, "order": 6},
            {"code": "hundred_questions", "name_uz": "100 savol", "description_uz": "100 ta savol yechdingiz", "icon": "BookOpen", "color": "cyan", "points": 80, "order": 7},
            {"code": "perfectionist", "name_uz": "Perfeksionist", "description_uz": "5 marta ketma-ket 100%", "icon": "Star", "color": "amber", "points": 200, "order": 8},
        ]

        for a in achievements:
            Achievement.objects.update_or_create(code=a["code"], defaults=a)
            self.stdout.write(f"✓ {a['name_uz']}")

        self.stdout.write(self.style.SUCCESS(f"Total: {Achievement.objects.count()}"))