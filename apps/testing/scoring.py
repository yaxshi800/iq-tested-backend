import math
from statistics import NormalDist

POPULATION_MEAN = 100
POPULATION_SD = 15
MAX_DURATION_SECONDS = 40 * 60
BLEND_MEAN = 0.5
BLEND_SD = 0.20


def compute_result(session, answers):
    from .models import Question, UserAnswer

    questions = {q.id: q for q in Question.objects.all()}
    category_stats = {}
    total_weight = 0.0
    earned_weight = 0.0
    total_time = 0

    correct_count = 0
    wrong_count = 0
    unanswered_count = 0

    session.answers.all().delete()
    to_create = []

    for ans in answers:
        q = questions.get(ans["question_id"])
        if not q:
            continue

        selected = ans.get("selected_index")
        is_correct = selected == q.correct_index
        time_spent = ans.get("time_spent", 0)

        total_weight += q.difficulty
        total_time += time_spent

        if selected is None:
            unanswered_count += 1
        elif is_correct:
            correct_count += 1
            earned_weight += q.difficulty
        else:
            wrong_count += 1

        cat = category_stats.setdefault(
            q.category,
            {"correct": 0, "total": 0, "weight_earned": 0.0, "weight_total": 0.0},
        )
        cat["total"] += 1
        cat["weight_total"] += q.difficulty

        if is_correct:
            cat["correct"] += 1
            cat["weight_earned"] += q.difficulty

        to_create.append(
            UserAnswer(
                session=session,
                question=q,
                selected_index=selected,
                time_spent=time_spent,
                is_correct=is_correct,
            )
        )

    UserAnswer.objects.bulk_create(to_create, ignore_conflicts=True)

    accuracy = (earned_weight / total_weight) if total_weight else 0.0

    # IQ TEST UCHUN
    # Faqat sof IQ test uchun IQ hisoblanadi
    is_iq_test = (
        session.test_category is not None and session.test_category.code == "iq"
    )

    if is_iq_test:
        if total_time <= MAX_DURATION_SECONDS:
            time_efficiency = 1.0 - (total_time / MAX_DURATION_SECONDS) * 0.15
        else:
            time_efficiency = 0.85

        blended = 0.85 * accuracy + 0.15 * (accuracy * time_efficiency)
        z = (blended - BLEND_MEAN) / BLEND_SD
        iq = POPULATION_MEAN + POPULATION_SD * z
        iq = int(max(55, min(145, round(iq))))
        percentile = round(NormalDist(POPULATION_MEAN, POPULATION_SD).cdf(iq) * 100, 1)
    else:
        iq = None
        percentile = None

    breakdown = {}
    for cat, st in category_stats.items():
        pct = (
            (st["weight_earned"] / st["weight_total"] * 100)
            if st["weight_total"]
            else 0.0
        )
        breakdown[cat] = {
            "correct": st["correct"],
            "total": st["total"],
            "percentage": round(pct, 1),
        }

    return {
        "raw_score": round(earned_weight, 2),
        "accuracy": round(accuracy, 4),
        "iq_score": iq,
        "percentile": percentile,
        "category_breakdown": breakdown,
        "duration_seconds": total_time,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "unanswered_count": unanswered_count,
        "total_questions": len(questions),
    }
