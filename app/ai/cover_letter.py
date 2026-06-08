from groq import Groq
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.models import Offer, UserProfile, UserExperience


def _format_experiences(experiences: list[UserExperience]) -> str:
    """Format user experiences into a readable string for the prompt."""
    if not experiences:
        return "Aucune expérience renseignée."

    type_labels = {
        "academic": "Formation",
        "professional": "Expérience professionnelle",
        "project": "Projet",
        "certification": "Certification",
    }

    lines = []
    for exp in experiences:
        label = type_labels.get(exp.type, exp.type)
        period = ""
        if exp.start_date and exp.end_date:
            period = f" ({exp.start_date} – {exp.end_date})"
        elif exp.start_date:
            period = f" ({exp.start_date})"

        entry = f"- [{label}] {exp.title}"
        if exp.institution:
            entry += f" — {exp.institution}"
        entry += period
        if exp.description:
            entry += f"\n  {exp.description}"
        lines.append(entry)

    return "\n".join(lines)


def generate_cover_letter(offer: Offer, profile: UserProfile) -> str:
    """Generate a professional cover letter in French using Groq API.

    Args:
        offer: The internship offer to apply for.
        profile: The user's profile with skills and details.

    Returns:
        The generated cover letter text.
    """
    # Fetch user experiences from the database
    db = SessionLocal()
    try:
        experiences = (
            db.query(UserExperience)
            .filter(UserExperience.user_id == profile.id)
            .all()
        )
    finally:
        db.close()

    experiences_text = _format_experiences(experiences)

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""Tu es un assistant expert en rédaction de lettres de motivation professionnelles en français.

Rédige une lettre de motivation personnalisée pour le stage suivant.

=== OFFRE DE STAGE ===
Titre : {offer.title}
Entreprise : {offer.company}
Lieu : {offer.location or "Non précisé"}
Description : {offer.description or "Non précisée"}

=== PROFIL DU CANDIDAT ===
Nom : {profile.name}
Spécialité : {profile.speciality}
Compétences : {profile.skills}
Type de stage : {profile.stage_type}
Localisation : {profile.location}
Langues : {profile.languages}

=== EXPÉRIENCES ET FORMATIONS ===
{experiences_text}

=== CONSIGNES ===
- La lettre doit être en français, professionnelle et bien structurée.
- Mets en avant les compétences du candidat qui correspondent à l'offre.
- Référence les expériences concrètes du candidat (stages, projets, formations) pour appuyer la candidature.
- Utilise un ton formel mais engageant.
- La lettre doit comporter : une accroche, un paragraphe sur la motivation, un paragraphe sur les compétences et expériences, et une conclusion avec formule de politesse.
- Ne mets pas de crochets ni de placeholders, utilise directement les informations fournies.
- Génère UNIQUEMENT la lettre, sans commentaire ni explication."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Tu es un expert en rédaction de lettres de motivation professionnelles en français pour des stages.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1500,
    )

    return chat_completion.choices[0].message.content
