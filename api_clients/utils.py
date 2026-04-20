import requests
import logging

from adminuser.utils import access_token_helper, CustomRequestException, ExternalServiceError
logger = logging.getLogger(__name__)

# Error message constants
ERR_FETCHING = "Error fetching"
ERR_CREATING = "Error creating"
ERR_UPDATING = "Error updating"
ERR_DELETING = "Error deleting"
ERR_TIMEOUT = "Request timed out"
ERR_CONNECTION = "Connection error"
ERR_HTTP = "HTTP error"
ERR_UNEXPECTED = "Unexpected error"

def _auth_headers(request):
    token = access_token_helper(request.adminuser)
    return {"Authorization": f"Bearer {token}"}


class APIClient:
    def __init__(self, request, base_url):
        self.request = request
        self.headers = _auth_headers(request)
        self.base_url = base_url

    def get(self, url,params=None,stream=False):
        logger.info(f"Fetching from {self.base_url}/{url}")
        try:
            response = requests.get(
                f"{self.base_url}/{url}",
                headers=self.headers,
                params=params,
                timeout=40,
                stream=stream
            )
            response.raise_for_status()
            if stream:
                return response
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(ERR_TIMEOUT)
            raise ExternalServiceError(ERR_TIMEOUT, 504, {"detail": ERR_TIMEOUT})
        except requests.exceptions.ConnectionError:
            logger.error(ERR_CONNECTION)
            raise ExternalServiceError(ERR_CONNECTION, 503, {"detail": ERR_CONNECTION})
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_HTTP}: {e}")
            raise ExternalServiceError(ERR_HTTP, status_code, e.response)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"TEST ------{ERR_FETCHING}: {e}")
            raise CustomRequestException(ERR_FETCHING, status_code, e.response)
        except Exception as e:
            logger.error(f"{ERR_UNEXPECTED}: {e}")
            raise ExternalServiceError(ERR_UNEXPECTED, 500, {"detail": ERR_UNEXPECTED})
    def post(self, url, data):
        try:
            response = requests.post(
                f"{self.base_url}/{url}",
                json=data,
                headers=self.headers,
                timeout=40
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(ERR_TIMEOUT)
            raise ExternalServiceError(ERR_TIMEOUT, 504, {"detail": ERR_TIMEOUT})
        except requests.exceptions.ConnectionError:
            logger.error(ERR_CONNECTION)
            raise ExternalServiceError(ERR_CONNECTION, 503, {"detail": ERR_CONNECTION})
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_HTTP}: {e}")
            raise ExternalServiceError(ERR_HTTP, status_code, e.response)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_CREATING}: {e}")
            raise CustomRequestException(ERR_CREATING, status_code, e.response)
        except Exception as e:
            logger.error(f"{ERR_UNEXPECTED}: {e}")
            raise ExternalServiceError(ERR_UNEXPECTED, 500, {"detail": ERR_UNEXPECTED})
    
    def patch(self, url, data):
        try:
            print("TEST ------", self.base_url)
            print("TEST ------", url)
            print("TEST ------", data)
            print("TEST ------", self.headers)
            response = requests.patch(
                f"{self.base_url}/{url}",
                json=data,
                headers=self.headers,
                timeout=40
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(ERR_TIMEOUT)
            raise ExternalServiceError(ERR_TIMEOUT, 504, None)
        except requests.exceptions.ConnectionError:
            logger.error(ERR_CONNECTION)
            raise ExternalServiceError(ERR_CONNECTION, 503, None)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_HTTP}: {e}")
            raise ExternalServiceError(ERR_HTTP, status_code, e.response)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response else 500
            if e.response:
                print("TEST ------", e.response.status_code)
                print("TEST ------", e.response.text)
            logger.error(f"{ERR_UPDATING}: {e}")
            raise CustomRequestException(ERR_UPDATING, status_code, e.response)
        except Exception as e:
            logger.error(f"{ERR_UNEXPECTED}: {e}")
            raise ExternalServiceError(ERR_UNEXPECTED, 500, None)
    def put(self, url, data):
        try:
            response = requests.put(
                f"{self.base_url}/{url}",
                json=data,
                headers=self.headers,
                timeout=40
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(ERR_TIMEOUT)
            raise ExternalServiceError(ERR_TIMEOUT, 504, None)
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            raise ExternalServiceError("Connection error", 503, None)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"HTTP error: {e}")
            raise ExternalServiceError("HTTP error", status_code, e.response)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_UPDATING}: {e}")
            raise CustomRequestException(ERR_UPDATING, status_code, e.response)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ExternalServiceError("Unexpected error", 500, None)

    def delete(self, url):
        try:
            response = requests.delete(
                f"{self.base_url}/{url}",
                headers=self.headers,
                timeout=40
            )
            response.raise_for_status()
            return True
        except requests.exceptions.Timeout:
            logger.error(ERR_TIMEOUT)
            raise ExternalServiceError(ERR_TIMEOUT, 504, None)
        except requests.exceptions.ConnectionError:
            logger.error(ERR_CONNECTION)
            raise ExternalServiceError(ERR_CONNECTION, 503, None)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_HTTP}: {e}")
            raise ExternalServiceError(ERR_HTTP, status_code, e.response)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"{ERR_DELETING}: {e}")
            raise CustomRequestException(ERR_DELETING, status_code, e.response)
        except Exception as e:
            logger.error(f"{ERR_UNEXPECTED}: {e}")
            raise ExternalServiceError(ERR_UNEXPECTED, 500, None)
