import redis
import uuid

from datetime import timedelta


class RedisSessionManager:
    def __init__(self, app_config):
        self.ttl = app_config.get("PERMANENT_SESSION_LIFETIME", timedelta(minutes=30))
        self._setup_redis_client()

    def _setup_redis_client(self):
        try:
            self.redis_client = redis.StrictRedis(
                host="localhost", port=6379, db=0, decode_responses=True
            )
            self.redis_client.ping() # Test connection
            print("Successfully connected to Redis!")
        except Exception as exc:
            print(f"Could not connect to Redis: {exc}")
            print("Please ensure Redis server is running and accessible.")
            exit(1) # Exit if Redis is not available


    def generate_session_id(self):
        """Generates a unique, random session ID."""
        return str(uuid.uuid4())


    def set_session_cookie(self, response, session_id):
        """Sets the session ID in an HttpOnly cookie."""
        # Ensure HttpOnly is True for security
        # secure=True should be used in production with HTTPS
        response.set_cookie(
            "session_id",
            session_id,
            max_age=int(self.ttl.total_seconds()),
            httponly=True,
            samesite='Lax' # Helps prevent some CSRF attacks; 'Strict' is even stronger
        )


    def get_user_from_session(self, session_id):
        """Retrieves user data from Redis based on session ID."""
        # Redis stores session data as a hash (hmset) or a string (json.dumps)
        # For simplicity, we'll store user_id directly as the value of the session_id key
        # A more robust solution might store a JSON blob with more session details.
        user_id = self.redis_client.get(f"session:{session_id}")
        if user_id:
            # In a real app, you'd fetch full user details from your main user database
            # based on user_id. For this demo, we'll just return the user_id.
            return user_id
        return None


    def store_session_in_redis(self, session_id, user_id):
        """Stores session data in Redis with an expiry."""
        # Key format: session:{session_id}
        # Value: user_id (or a JSON string of more session data)
        # EX: Set expiry time in seconds
        self.redis_client.setex(
            f"session:{session_id}",
            int(self.ttl.total_seconds()),
            user_id
        )


    def delete_session_from_redis(self, session_id):
        """Deletes a session from Redis."""
        self.redis_client.delete(f"session:{session_id}")

    
