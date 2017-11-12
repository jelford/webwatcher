"""
Provides application-wide connection pooling
and http session management
"""
import requests as _requests

http_session = _requests.Session()
