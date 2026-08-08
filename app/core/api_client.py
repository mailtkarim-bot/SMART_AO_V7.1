"""
SMART_AO V7 - api_client.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


import httpx
from typing import Any, Dict, Optional, Union
from .config import settings


class APIClient:
    '''Client API pour les requêtes internes.'''
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"http://{settings.API_HOST}:{settings.API_PORT}{settings.API_ROOT_PATH}"
        self.client = httpx.AsyncClient()
    
    async def get(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête GET.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def post(
        self,
        endpoint: str,
        json: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        files: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête POST.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.post(
            url,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    
    async def put(
        self,
        endpoint: str,
        json: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête PUT.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.put(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def delete(
        self,
        endpoint: str,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête DELETE.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        '''Fermer la connexion.'''
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Instance singleton
api_client = APIClient()


def get_api_client() -> APIClient:
    return api_client
