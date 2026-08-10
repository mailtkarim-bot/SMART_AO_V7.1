"""
SMART_AO V7 - dce_analyze_v6_compat.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Compatibilité V6 - Adaptateur pour les DCE au format V6
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import logging
import re
import json

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dce/v6", tags=["DCE V6 Compatibility"])


class V6Format(str, Enum):
    """Formats V6 supportés."""
    STANDARD = "standard"
    SIMPLIFIE = "simplifie"
    ETENDU = "etendu"
    MINIMAL = "minimal"


class V6Section(str, Enum):
    """Sections DCE V6."""
    DESCRIPTION = "description"
    CCTP = "cctp"
    DPGF = "dpgf"
    ACTE_ENGAGEMENT = "acte_engagement"
    REGLEMENT_CONSULTATION = "reglement_consultation"
    ANNEXES = "annexes"
    PIECES_JUSTIFICATIVES = "pieces_justificatives"


class V6DocumentInfo(BaseModel):
    """Informations sur un document DCE V6."""
    document_name: str
    document_type: str
    format_version: str
    page_count: int
    word_count: int
    has_table_of_contents: bool
    sections: List[str]
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)


class V6CompatibilityCheck(BaseModel):
    """Vérification de compatibilité V6."""
    mission_id: str
    document_id: Optional[str] = None
    is_compatible: bool
    format_detected: Optional[V6Format] = None
    compatibility_score: float = Field(ge=0.0, le=1.0)
    required_sections: List[str]
    missing_sections: List[str]
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class V6ConversionRequest(BaseModel):
    """Requête de conversion V6."""
    mission_id: str
    document_content: str
    target_format: Optional[V6Format] = None
    include_metadata: bool = Field(default=True)


class V6ConversionResult(BaseModel):
    """Résultat de conversion V6."""
    mission_id: str
    original_format: Optional[V6Format] = None
    target_format: V6Format
    converted_content: str
    conversion_report: Dict[str, Any]
    converted_at: datetime


class V6MigrationGuide(BaseModel):
    """Guide de migration V6."""
    from_version: str
    to_version: str
    steps: List[Dict[str, Any]]
    estimated_duration: str
    required_tools: List[str]
    common_issues: List[str]
    best_practices: List[str]


class V6DCEAnalyzer:
    """Analyseur de DCE au format V6."""
    
    V6_SECTION_PATTERNS = {
        V6Section.DESCRIPTION.value: [r'(?i)(description\s*(?:du\s*)?(?:projet|mission|ouvrage)|objet\s*du\s*marché)'],
        V6Section.CCTP.value: [r'(?i)(cctp|cahier\s*des\s*clauses\s*techniques\s*particulières)'],
        V6Section.DPGF.value: [r'(?i)(dpgf|décomposition\s*du\s*prix\s*global\s*et\s*forfaitaire)'],
        V6Section.ACTE_ENGAGEMENT.value: [r'(?i)(acte\s*d[\'\s]engagement|contrat)'],
        V6Section.REGLEMENT_CONSULTATION.value: [r'(?i)(règlement\s*de\s*la\s*consultation|rc)'],
        V6Section.ANNEXES.value: [r'(?i)(annexe[s]?|documents\s*complémentaires)'],
        V6Section.PIECES_JUSTIFICATIVES.value: [r'(?i)(pièce[s]?\s*justificative[s]?)']
    }
    
    REQUIRED_V6_SECTIONS = [
        V6Section.DESCRIPTION,
        V6Section.CCTP,
        V6Section.DPGF,
        V6Section.ACTE_ENGAGEMENT,
        V6Section.REGLEMENT_CONSULTATION
    ]
    
    def __init__(self):
        pass
    
    def detect_format(self, content: str) -> Optional[V6Format]:
        """Détecte le format V6 d'un document."""
        content_lower = content.lower()
        
        # Détection des formats étendus
        if "cahier des clauses administratives générales" in content_lower:
            return V6Format.ETENDU
        
        # Détection des formats simplifiés
        if "fascicule" in content_lower or "simplifié" in content_lower:
            return V6Format.SIMPLIFIE
        
        # Détection des formats minimaux
        if len(content) < 1000:  # Très court
            return V6Format.MINIMAL
        
        # Par défaut: standard
        return V6Format.STANDARD
    
    def check_compatibility(self, content: str, mission_id: str) -> V6CompatibilityCheck:
        """Vérifie la compatibilité V6 d'un document."""
        format_detected = self.detect_format(content)
        content_lower = content.lower()
        
        # Détecter les sections présentes
        detected_sections = []
        for section, patterns in self.V6_SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    detected_sections.append(section)
                    break
        
        # Calculer les sections manquantes
        missing_sections = [
            s.value for s in self.REQUIRED_V6_SECTIONS 
            if s.value not in detected_sections
        ]
        
        # Calculer le score de compatibilité
        required_count = len(self.REQUIRED_V6_SECTIONS)
        present_count = len([s for s in self.REQUIRED_V6_SECTIONS if s.value in detected_sections])
        compatibility_score = present_count / required_count if required_count > 0 else 1.0
        
        # Détecter les erreurs
        errors = []
        warnings = []
        recommendations = []
        
        if not format_detected:
            errors.append("Format V6 non détecté")
            compatibility_score = 0.0
        
        if missing_sections:
            errors.append(f"Sections manquantes: {', '.join(missing_sections)}")
        
        # Vérifications supplémentaires
        if "euro" not in content_lower and "€" not in content:
            warnings.append("Aucune mention de devise (€/euro) détectée dans le DPGF")
        
        if "lot" not in content_lower and "alloti" not in content_lower:
            warnings.append("Aucune mention d'allotissement détectée")
        
        # Générer des recommandations
        if missing_sections:
            recommendations.append(f"Ajouter les sections manquantes: {', '.join(missing_sections)}")
        
        if format_detected == V6Format.MINIMAL:
            recommendations.append("Convertir vers un format V6 standard pour une meilleure compatibilité")
        
        if compatibility_score >= 0.8:
            recommendations.append("Document compatible V6 - validation recommandée")
        elif compatibility_score >= 0.5:
            recommendations.append("Document partiellement compatible - révision nécessaire")
        else:
            recommendations.append("Document non compatible - conversion requise")
        
        is_compatible = compatibility_score >= 0.8
        
        return V6CompatibilityCheck(
            mission_id=mission_id,
            document_id=None,
            is_compatible=is_compatible,
            format_detected=format_detected,
            compatibility_score=round(compatibility_score, 2),
            required_sections=[s.value for s in self.REQUIRED_V6_SECTIONS],
            missing_sections=missing_sections,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations
        )
    
    def convert_to_v6(
        self,
        content: str,
        mission_id: str,
        target_format: V6Format = V6Format.STANDARD
    ) -> V6ConversionResult:
        """Convertit un document vers le format V6."""
        original_format = self.detect_format(content)
        
        # Pour la démo: simuler une conversion simple
        # En production: implémenter une conversion réelle
        converted_content = f"""# DCE V6 - Mission {mission_id}
## Format: {target_format.value.upper()}
## Date de conversion: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

---

### 1. DESCRIPTION DU PROJET
{self._extract_section(content, 'description')}

### 2. CAHIER DES CLAUSES TECHNIQUES PARTICULIÈRES (CCTP)
{self._extract_section(content, 'cctp')}

### 3. DÉCOMPOSITION DU PRIX GLOBAL ET FORFAITAIRE (DPGF)
{self._extract_section(content, 'dpgf')}

### 4. ACTE D'ENGAGEMENT
{self._extract_section(content, 'acte_engagement')}

### 5. RÈGLEMENT DE LA CONSULTATION
{self._extract_section(content, 'reglement_consultation')}

---

*Document converti automatiquement depuis le format {original_format.value if original_format else 'inconnu'}
"""
        
        conversion_report = {
            "original_format": original_format.value if original_format else None,
            "target_format": target_format.value,
            "conversion_success": True,
            "warnings": [],
            "changes_made": [
                "Ajout des en-têtes de sections V6",
                "Standardisation de la structure",
                "Ajout des métadonnées de conversion"
            ]
        }
        
        if original_format:
            if original_format != target_format:
                conversion_report["changes_made"].append(
                    f"Conversion de {original_format.value} vers {target_format.value}"
                )
        
        return V6ConversionResult(
            mission_id=mission_id,
            original_format=original_format,
            target_format=target_format,
            converted_content=converted_content,
            conversion_report=conversion_report,
            converted_at=datetime.utcnow()
        )
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extrait une section spécifique du contenu."""
        content_lower = content.lower()
        
        for pattern in self.V6_SECTION_PATTERNS.get(section_name, []):
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                start = match.start()
                # Trouver la fin de la section (prochaine section ou fin du document)
                next_sections = []
                for sec, pats in self.V6_SECTION_PATTERNS.items():
                    if sec != section_name:
                        for pat in pats:
                            next_match = re.search(pat, content[start+10:], re.IGNORECASE)
                            if next_match:
                                next_sections.append(start + 10 + next_match.start())
                
                end = min(next_sections) if next_sections else len(content)
                return content[start:end].strip()
        
        return "[Section non trouvée - à compléter]"
    
    def generate_migration_guide(self, from_version: str, to_version: str = "7.0") -> V6MigrationGuide:
        """Génère un guide de migration."""
        steps = []
        
        if from_version.startswith("5"):
            steps = [
                {"step": 1, "description": "Audit complet du DCE existant", "duration": "1-2 jours"},
                {"step": 2, "description": "Identification des sections manquantes", "duration": "0.5 jour"},
                {"step": 3, "description": "Conversion des sections existantes", "duration": "2-3 jours"},
                {"step": 4, "description": "Ajout des nouvelles sections V6", "duration": "1-2 jours"},
                {"step": 5, "description": "Validation et tests", "duration": "1 jour"}
            ]
            estimated_duration = "1-2 semaines"
            common_issues = [
                "Structure des sections différente",
                "Terminologie obsolète",
                "Informations manquantes pour V6"
            ]
        elif from_version.startswith("6"):
            steps = [
                {"step": 1, "description": "Vérification de la compatibilité V6", "duration": "0.5 jour"},
                {"step": 2, "description": "Mise à jour des métadonnées", "duration": "0.5 jour"},
                {"step": 3, "description": "Validation finale", "duration": "0.5 jour"}
            ]
            estimated_duration = "1-2 jours"
            common_issues = [
                "Format déjà compatible",
                "Métadonnées manquantes",
                "Sections optionnelles absentes"
            ]
        else:
            steps = [
                {"step": 1, "description": "Analyse du document source", "duration": "1 jour"},
                {"step": 2, "description": "Conversion manuelle requise", "duration": "Variable"}
            ]
            estimated_duration = "Variable"
            common_issues = ["Format non reconnu", "Conversion complexe"]
        
        best_practices = [
            "Sauvegarder le document original",
            "Valider chaque section après conversion",
            "Tester avec plusieurs documents",
            "Documenter les décisions de conversion"
        ]
        
        required_tools = ["SMART_AO V7", "Éditeur de texte", "Visualiseur PDF"]
        
        return V6MigrationGuide(
            from_version=from_version,
            to_version=to_version,
            steps=steps,
            estimated_duration=estimated_duration,
            required_tools=required_tools,
            common_issues=common_issues,
            best_practices=best_practices
        )


analyzer = V6DCEAnalyzer()


@router.post("/check", response_model=V6CompatibilityCheck)
async def check_v6_compatibility(
    mission_id: str,
    document_content: str,
    document_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifie la compatibilité V6 d'un document.
    
    Analyse un document DCE et vérifie s'il est compatible avec le format V6.
    """
    logger.info(f"Vérification compatibilité V6 pour mission {mission_id} par {current_user.user_id}")
    
    result = analyzer.check_compatibility(document_content, mission_id)
    
    if document_id:
        result.document_id = document_id
    
    return result


@router.post("/convert", response_model=V6ConversionResult)
async def convert_to_v6(
    request: V6ConversionRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Convertit un document vers le format V6.
    
    Convertit un DCE existant vers le format V6 standard.
    """
    logger.info(f"Conversion V6 pour mission {request.mission_id} par {current_user.user_id}")
    
    result = analyzer.convert_to_v6(
        content=request.document_content,
        mission_id=request.mission_id,
        target_format=request.target_format or V6Format.STANDARD
    )
    
    return result


@router.get("/migration-guide", response_model=V6MigrationGuide)
async def get_migration_guide(
    from_version: str = "5.x",
    to_version: str = "7.0",
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère un guide de migration vers V6/V7.
    
    Fournit des instructions détaillées pour migrer des documents
    depuis une version antérieure vers V6 ou V7.
    """
    logger.info(f"Guide migration V6: {from_version} -> {to_version} par {current_user.user_id}")
    
    guide = analyzer.generate_migration_guide(from_version, to_version)
    
    return guide


@router.post("/detect-format", response_model=V6DocumentInfo)
async def detect_document_format(
    document_content: str,
    document_name: str = "document",
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Détecte le format d'un document DCE.
    
    Analyse un document et détermine son format actuel.
    """
    logger.info(f"Détection format document: {document_name} par {current_user.user_id}")
    
    format_detected = analyzer.detect_format(document_content)
    
    # Compter les mots et pages (estimation)
    word_count = len(document_content.split())
    page_count = max(1, word_count // 500)  # Estimation: 500 mots par page
    
    # Détecter les sections présentes
    content_lower = document_content.lower()
    detected_sections = []
    for section, patterns in analyzer.V6_SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                detected_sections.append(section)
                break
    
    # Vérifier les erreurs de validation
    validation_errors = []
    if not format_detected:
        validation_errors.append("Format non reconnu")
    
    # Vérifier la présence des sections obligatoires
    for section in analyzer.REQUIRED_V6_SECTIONS:
        if section.value not in detected_sections:
            validation_errors.append(f"Section manquantes: {section.value}")
    
    return V6DocumentInfo(
        document_name=document_name,
        document_type="dce",
        format_version=format_detected.value if format_detected else "inconnu",
        page_count=page_count,
        word_count=word_count,
        has_table_of_contents="table des matières" in content_lower or "sommaire" in content_lower,
        sections=detected_sections,
        is_valid=len(validation_errors) == 0,
        validation_errors=validation_errors
    )


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "dce_v6_compat",
        "version": "1.0.0",
        "supported_formats": [f.value for f in V6Format],
        "timestamp": datetime.utcnow().isoformat()
    }

