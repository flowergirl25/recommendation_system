from app.models.users_data import User
from app.auth.authentication import hash_password

class UserService:

    @staticmethod
    def update_user(email, new_name=None, new_password=None):
        """Update user profile details."""
        try:
            user = User.fetch_by_email(email)
            if not user:
                return {"success": False, "error": "User not found"}

            updates = {}
            if new_name:
                updates["name"] = new_name
            if new_password:
                updates["password"] = hash_password(new_password)

            if not updates:
                return {"success": False, "error": "No updates provided"}

            User.update_profile(email, **updates)
            return {"success": True, "message": "User updated successfully!"}

        except Exception as e:
            return {"success": False, "error": str(e)}
