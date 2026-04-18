from app.database import SessionLocal, engine
from app.models import Role, User, Base
from app.auth import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    roles_data = [
        {"name": "Admin", "permissions": "Full access"},
        {"name": "Financial Analyst", "permissions": "Upload and edit documents"},
        {"name": "Auditor", "permissions": "Review documents"},
        {"name": "Client", "permissions": "View company documents"}
    ]
    
    for role_info in roles_data:
        role = db.query(Role).filter(Role.name == role_info["name"]).first()
        if not role:
            new_role = Role(name=role_info["name"], permissions=role_info["permissions"])
            db.add(new_role)
    
    db.commit()

    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed_password = get_password_hash("admin123")
        admin_user = User(username="admin", hashed_password=hashed_password)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        admin_user.roles.append(admin_role)
        db.commit()
        
    db.close()
    print("Database seeded with default roles and admin user (admin/admin123).")

if __name__ == "__main__":
    seed_db()
