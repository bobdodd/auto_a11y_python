"""One-time migration: add all existing users as members to all existing projects.

Run once before deploying permission-enforced code.

Usage:
    python migrate_add_project_members.py [--dry-run]
"""
import sys
from datetime import datetime
from auto_a11y.core.database import Database
from auto_a11y.models.app_user import UserRole
from config import Config

MIGRATION_NAME = "add_project_members_v1"


def run_migration(dry_run=False):
    config = Config()
    db = Database(config.MONGODB_URI, config.DATABASE_NAME)

    # Check if already run
    if db.db['_migrations'].find_one({"name": MIGRATION_NAME}):
        print(f"Migration '{MIGRATION_NAME}' already applied. Skipping.")
        return

    users = db.get_app_users()
    projects = db.get_all_projects()

    print(f"Found {len(users)} users and {len(projects)} projects")

    for project in projects:
        project_id = str(project._id)
        existing_member_ids = {m.user_id for m in project.members}
        added = 0

        for user in users:
            user_id = str(user.get_id())
            if user_id in existing_member_ids:
                continue

            if dry_run:
                print(f"  [DRY RUN] Would add {user.email} ({user.role.value}) to '{project.name}'")
            else:
                db.add_project_member(project_id, user_id, user.role)
            added += 1

        print(f"Project '{project.name}': added {added} members")

    if not dry_run:
        db.db['_migrations'].insert_one({
            "name": MIGRATION_NAME,
            "applied_at": datetime.utcnow(),
            "users_count": len(users),
            "projects_count": len(projects),
        })
        print(f"\nMigration '{MIGRATION_NAME}' applied successfully.")
    else:
        print("\n[DRY RUN] No changes made.")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    run_migration(dry_run=dry_run)
