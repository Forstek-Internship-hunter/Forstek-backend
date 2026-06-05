from groq import Groq
from app.core.config import settings
from app.models.models import Offer, UserProfile


def generate_cover_letter(offer: Offer, profile: UserProfile) -> str:
    """Generate a professional cover letter in French using Groq API.

    Args:
        offer: The internship offer to apply for.
        profile: The user's profile with skills and details.

    Returns:
        The generated cover letter text.
    """
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

=== CONSIGNES ===
- La lettre doit être en français, professionnelle et bien structurée.
- Mets en avant les compétences du candidat qui correspondent à l'offre.
- Utilise un ton formel mais engageant.
- La lettre doit comporter : une accroche, un paragraphe sur la motivation, un paragraphe sur les compétences, et une conclusion avec formule de politesse.
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
