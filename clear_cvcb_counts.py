#!/usr/bin/env python3
"""
Script to clear violation counts for project CVC-B pages
"""

import sys
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "auto_a11y"

def clear_project_page_counts(project_name: str):
    """Clear violation/warning counts for all pages in a project"""

    print(f"🔍 Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    try:
        # Find the project
        print(f"🔍 Looking for project: {project_name}")
        project = db.projects.find_one({"name": project_name})

        if not project:
            print(f"❌ Project '{project_name}' not found")
            return False

        project_id = str(project["_id"])
        print(f"✅ Found project: {project_name} (ID: {project_id})")

        # Get all websites for this project
        print(f"🔍 Finding websites for project...")
        websites = list(db.websites.find({"project_id": project_id}))
        print(f"✅ Found {len(websites)} website(s)")

        if not websites:
            print("⚠️  No websites found for this project")
            return True

        # Collect all page IDs for these websites
        all_page_ids = []
        for website in websites:
            website_id = str(website["_id"])
            website_url = website.get("url", "unknown")
            print(f"   📄 Website: {website_url}")

            # Get pages for this website
            pages = list(db.pages.find({"website_id": website_id}))
            page_ids = [str(page["_id"]) for page in pages]
            all_page_ids.extend(page_ids)
            print(f"      Found {len(page_ids)} pages")

        print(f"\n📊 Total pages across all websites: {len(all_page_ids)}")

        if not all_page_ids:
            print("⚠️  No pages found")
            return True

        # Clear violation counts on all pages
        print(f"\n🔄 Clearing violation counts on all pages...")
        update_result = db.pages.update_many(
            {"_id": {"$in": [ObjectId(page_id) for page_id in all_page_ids]}},
            {
                "$set": {
                    "violation_count": 0,
                    "warning_count": 0,
                    "info_count": 0,
                    "pass_count": 0
                }
            }
        )
        print(f"✅ Cleared counts on {update_result.modified_count} page(s)")

        print(f"\n✅ All operations completed successfully!")
        print(f"\nSummary:")
        print(f"  • Cleared counts on {update_result.modified_count} pages")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.close()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    print("=" * 60)
    print("Clear Violation Counts for Project CVC-B")
    print("=" * 60)
    print()

    success = clear_project_page_counts("CVC-B")

    if success:
        print("\n✅ Operation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Operation failed")
        sys.exit(1)
