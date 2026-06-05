"""
Service de génération du PDF de consentement éclairé NeuroCap.
Génère un PDF personnalisé avec le nom du patient, sans signature.
"""

import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer


def generate_consent_pdf(patient_name: str) -> bytes:
    """
    Génère le PDF de consentement éclairé personnalisé pour le patient.

    Args:
        patient_name: Nom complet du patient (ex: "Ahmed Benjelloun")

    Returns:
        bytes: Contenu du PDF prêt à être envoyé par email
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1a3a5c"),
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2b6cb0"),
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=16,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=11,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#1a3a5c"),
        fontName="Helvetica-Bold",
    )
    patient_style = ParagraphStyle(
        "Patient",
        parent=styles["Normal"],
        fontSize=12,
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2d3748"),
        fontName="Helvetica-Bold",
    )

    story = []

    # En-tête
    story.append(Paragraph("NEUROCAP", title_style))
    story.append(Paragraph("Système de Neurofeedback EEG Portable", subtitle_style))
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=colors.HexColor("#2b6cb0"), spaceAfter=16
        )
    )
    story.append(
        Paragraph(
            "FORMULAIRE DE CONSENTEMENT ÉCLAIRÉ",
            ParagraphStyle(
                "DocTitle",
                parent=styles["Normal"],
                fontSize=13,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
                spaceAfter=4,
                textColor=colors.HexColor("#1a3a5c"),
            ),
        )
    )
    story.append(
        Paragraph(
            f"Version 1.0 — {date.today().strftime('%d/%m/%Y')}",
            ParagraphStyle(
                "Version",
                parent=styles["Normal"],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.grey,
                spaceAfter=20,
            ),
        )
    )

    # Identification du participant
    story.append(Paragraph("PARTICIPANT :", section_style))
    story.append(Paragraph(patient_name, patient_style))
    story.append(Spacer(1, 12))
    story.append(
        HRFlowable(
            width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=12
        )
    )

    # 1. Présentation
    story.append(Paragraph("1. PRÉSENTATION DE L'ÉTUDE", section_style))
    story.append(
        Paragraph(
            "Vous êtes invité(e) à participer à une étude portant sur l'utilisation d'un "
            "système de neurofeedback EEG portable (NeuroCap) destiné à la régulation du "
            "stress et à l'amélioration de la concentration. Ce système acquiert et analyse "
            "votre signal électroencéphalographique (EEG) en temps réel à l'aide d'une "
            "électrode frontale non invasive.",
            body_style,
        )
    )

    # 2. Objectifs
    story.append(Paragraph("2. OBJECTIFS", section_style))
    story.append(
        Paragraph(
            "L'objectif de cette étude est d'évaluer l'efficacité d'un protocole de "
            "neurofeedback monocanal pour : (a) réduire les niveaux de stress subjectif "
            "et physiologique mesurés par EEG, (b) améliorer la concentration soutenue "
            "lors de tâches cognitives, et (c) valider les algorithmes de classification "
            "des états mentaux développés dans le cadre du projet NeuroCap.",
            body_style,
        )
    )

    # 3. Déroulement
    story.append(Paragraph("3. DÉROULEMENT DE L'ÉTUDE", section_style))
    story.append(Paragraph("Votre participation comprend :", body_style))
    story.append(
        Paragraph(
            "• <b>Séance de calibration (S1)</b> : 30 minutes. Mesure de votre profil EEG "
            "de référence (fréquence alpha individuelle, seuils de base).",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Séances de neurofeedback (S2 à S15)</b> : 20 à 30 minutes chacune, "
            "à raison de 1 à 2 séances par semaine sur 7 à 8 semaines.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Questionnaires</b> : Évaluation subjective avant et après chaque séance "
            "(stress perçu, niveau de concentration, qualité du feedback).",
            body_style,
        )
    )

    # 4. Données collectées
    story.append(Paragraph("4. DONNÉES COLLECTÉES", section_style))
    story.append(Paragraph("Les données suivantes seront collectées et traitées :", body_style))
    story.append(
        Paragraph(
            "• Signal EEG brut et filtré (électrode Fp2, 250 Hz, canal unique)", body_style
        )
    )
    story.append(
        Paragraph(
            "• Indicateurs spectraux dérivés (puissances alpha, bêta, thêta ; ratio TBR)",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• Scores de sessions et résultats de classification (état mental prédit)",
            body_style,
        )
    )
    story.append(Paragraph("• Réponses aux questionnaires de suivi", body_style))

    # 5. Confidentialité
    story.append(Paragraph("5. CONFIDENTIALITÉ ET PROTECTION DES DONNÉES", section_style))
    story.append(
        Paragraph(
            "Toutes les données collectées sont strictement confidentielles. Elles sont "
            "anonymisées avant tout traitement statistique ou publication. Aucune donnée "
            "permettant votre identification ne sera divulguée à des tiers. Les données "
            "sont stockées sur des serveurs sécurisés et seront supprimées à l'issue de "
            "l'étude, conformément à la réglementation en vigueur sur la protection des "
            "données personnelles.",
            body_style,
        )
    )

    # 6. Risques et bénéfices
    story.append(Paragraph("6. RISQUES ET BÉNÉFICES", section_style))
    story.append(
        Paragraph(
            "Le dispositif NeuroCap est non invasif. L'acquisition EEG ne présente aucun "
            "risque connu pour la santé. Les seuls inconforts possibles sont une légère "
            "pression mécanique des électrodes sur le cuir chevelu et une sensibilité au "
            "gel conducteur chez certaines personnes. Les bénéfices potentiels incluent "
            "une meilleure gestion du stress et un entraînement à la concentration.",
            body_style,
        )
    )

    # 7. Participation volontaire
    story.append(Paragraph("7. PARTICIPATION VOLONTAIRE", section_style))
    story.append(
        Paragraph(
            "Votre participation est entièrement volontaire. Vous pouvez vous retirer de "
            "l'étude à tout moment, sans justification et sans aucune conséquence. "
            "Le retrait de votre consentement entraînera la suppression immédiate de "
            "toutes les données vous concernant.",
            body_style,
        )
    )

    # 8. Consentement
    story.append(Spacer(1, 16))
    story.append(
        HRFlowable(
            width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=12
        )
    )
    story.append(Paragraph("8. CONSENTEMENT DU PARTICIPANT", section_style))
    story.append(
        Paragraph(
            f"Je soussigné(e), <b>{patient_name}</b>, déclare avoir pris connaissance "
            "des informations ci-dessus concernant l'étude NeuroCap. J'ai eu la possibilité "
            "de poser toutes mes questions et j'ai reçu des réponses satisfaisantes. "
            "Je consens librement et volontairement à participer à cette étude, dans les "
            "conditions décrites.",
            body_style,
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            f"<b>Consentement enregistré électroniquement le : "
            f"{date.today().strftime('%d/%m/%Y')}</b>",
            ParagraphStyle(
                "DateConsentement",
                parent=styles["Normal"],
                fontSize=10,
                alignment=TA_LEFT,
                textColor=colors.HexColor("#2d3748"),
                spaceAfter=4,
            ),
        )
    )

    # Pied de page
    story.append(Spacer(1, 20))
    story.append(
        HRFlowable(
            width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8
        )
    )
    story.append(
        Paragraph(
            "Document généré automatiquement par le système NeuroCap — Usage confidentiel",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey,
            ),
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
