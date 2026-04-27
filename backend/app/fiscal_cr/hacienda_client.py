import httpx


SANDBOX_AUTH = "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token"
PROD_AUTH = "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token"
SANDBOX_API = "https://api-sandbox.comprobanteselectronicos.go.cr/recepcion/v1/"
PROD_API = "https://api.comprobanteselectronicos.go.cr/recepcion/v1/"


class HaciendaClient:
    def __init__(self, environment: str, client_id: str | None, username: str | None, password: str | None):
        self.environment = environment
        self.client_id = client_id or "api-stag"
        self.username = username
        self.password = password
        self.auth_url = PROD_AUTH if environment == "production" else SANDBOX_AUTH
        self.api_url = PROD_API if environment == "production" else SANDBOX_API

    def token(self) -> str:
        if not self.username or not self.password:
            raise ValueError("Credenciales de Hacienda no configuradas")
        response = httpx.post(
            self.auth_url,
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "username": self.username,
                "password": self.password,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def send(self, payload: dict) -> dict:
        access_token = self.token()
        response = httpx.post(
            f"{self.api_url}recepcion",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=45,
        )
        return {"status_code": response.status_code, "body": response.text}

    def status(self, clave: str) -> dict:
        access_token = self.token()
        response = httpx.get(
            f"{self.api_url}recepcion/{clave}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        return {"status_code": response.status_code, "body": response.text}
