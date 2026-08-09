"""
SMART_AO V7 - Excel MCP Tools
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Excel MCP - Outils MCP pour la manipulation des fichiers Excel dans SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §4.5
"""

import logging
import tempfile
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from mcp.server.fastmcp import FastMCP

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="SMART_AO_Excel_MCP",
    version="7.1.0",
    description="Outils MCP pour lecture, écriture et analyse de fichiers Excel"
)


@mcp.tool()
async def read_excel_file(
    file_path: str,
    sheet_name: Optional[str] = None,
    header_row: int = 0
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Lire un fichier Excel et retourner les données sous forme de dictionnaires."""
    logger.info(f"Lecture du fichier Excel: {file_path}")
    
    if not PANDAS_AVAILABLE:
        return {"error": "pandas non installé", "suggestion": "pip install pandas openpyxl"}
    
    if not os.path.exists(file_path):
        return {"error": "Fichier non trouvé", "path": file_path}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Erreur lecture Excel: {e}")
        return {"error": str(e)}


@mcp.tool()
async def read_excel_sheets(file_path: str) -> List[str]:
    """Lister toutes les feuilles d'un fichier Excel."""
    logger.info(f"Liste des feuilles Excel: {file_path}")
    
    if not PANDAS_AVAILABLE:
        return ["error: pandas non installé"]
    
    if not os.path.exists(file_path):
        return ["error: fichier non trouvé"]
    
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        logger.error(f"Erreur liste feuilles: {e}")
        return [f"error: {str(e)}"]


@mcp.tool()
async def write_excel_file(
    data: List[Dict[str, Any]],
    output_path: str,
    sheet_name: str = "Data",
    include_index: bool = False
) -> Dict[str, Any]:
    """Écrire des données dans un fichier Excel."""
    logger.info(f"Écriture Excel: {output_path}")
    
    if not PANDAS_AVAILABLE:
        return {"error": "pandas non installé"}
    
    try:
        # S'assurer que le répertoire existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df = pd.DataFrame(data)
        df.to_excel(output_path, sheet_name=sheet_name, index=include_index)
        
        return {
            "success": True,
            "path": output_path,
            "rows_written": len(data),
            "message": "Fichier Excel créé avec succès"
        }
    except Exception as e:
        logger.error(f"Erreur écriture Excel: {e}")
        return {"error": str(e)}


@mcp.tool()
async def excel_to_dict(
    file_path: str,
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convertir un fichier Excel en dictionnaire structuré."""
    logger.info(f"Conversion Excel to dict: {file_path}")
    
    if not PANDAS_AVAILABLE:
        return {"error": "pandas non installé"}
    
    if not os.path.exists(file_path):
        return {"error": "Fichier non trouvé"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Retourner un dict avec metadata et données
        return {
            "metadata": {
                "file": file_path,
                "sheet": sheet_name or df.columns[0],
                "rows": len(df),
                "columns": len(df.columns)
            },
            "headers": df.columns.tolist(),
            "data": df.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def validate_excel_structure(
    file_path: str,
    required_columns: List[str]
) -> Dict[str, Any]:
    """Valider la structure d'un fichier Excel."""
    logger.info(f"Validation structure Excel: {file_path}")
    
    if not PANDAS_AVAILABLE:
        return {"error": "pandas non installé"}
    
    if not os.path.exists(file_path):
        return {"error": "Fichier non trouvé"}
    
    try:
        df = pd.read_excel(file_path)
        actual_columns = set(df.columns.tolist())
        required_set = set(required_columns)
        
        missing = list(required_set - actual_columns)
        extra = list(actual_columns - required_set)
        
        return {
            "valid": len(missing) == 0,
            "missing_columns": missing,
            "extra_columns": extra,
            "actual_columns": df.columns.tolist(),
            "total_rows": len(df)
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def create_excel_template(
    columns: List[str],
    output_path: str,
    sample_rows: int = 3
) -> Dict[str, Any]:
    """Créer un template Excel vide avec les colonnes spécifiées."""
    logger.info(f"Création template Excel: {output_path}")
    
    if not PANDAS_AVAILABLE:
        return {"error": "pandas non installé"}
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Créer un DataFrame vide avec les colonnes
        df = pd.DataFrame(columns=columns)
        
        # Ajouter des lignes d'exemple
        if sample_rows > 0:
            sample_data = []
            for i in range(sample_rows):
                row = {col: f"exemple_{col}_{i}" for col in columns}
                sample_data.append(row)
            df = pd.DataFrame(sample_data, columns=columns)
        
        df.to_excel(output_path, index=False)
        
        return {
            "success": True,
            "path": output_path,
            "columns": columns,
            "message": "Template Excel créé avec succès"
        }
    except Exception as e:
        logger.error(f"Erreur création template: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    logger.info("Démarrage du serveur Excel MCP...")
    mcp.run()


