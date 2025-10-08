#!/usr/bin/env python3
"""
Script to delete test results for project CVC-B
This will help resolve MongoDB document size issues
"""

import sys
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "auto_a11y"

def delete_project_test_results(project_name: str, skip_confirmation: bool = False):
    """Delete all test results for a specific project"""

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
            print("⚠️  No pages found - no test results to delete")
            return True

        # Count test results before deletion
        print(f"\n🔍 Counting test results...")
        test_result_count = db.test_results.count_documents({
            "page_id": {"$in": all_page_ids}
        })
        print(f"📊 Found {test_result_count} test result(s) to delete")

        if test_result_count == 0:
            print("✅ No test results to delete")
            return True

        # Confirm deletion
        print(f"\n⚠️  WARNING: About to delete {test_result_count} test results")
        print(f"   Project: {project_name}")
        print(f"   Websites: {len(websites)}")
        print(f"   Pages: {len(all_page_ids)}")

        if not skip_confirmation:
            response = input("\nProceed with deletion? (yes/no): ").strip().lower()
            if response != 'yes':
                print("❌ Deletion cancelled")
                return False
        else:
            print("\n✅ Auto-confirming deletion (skip_confirmation=True)")

        # Delete test results
        print(f"\n🗑️  Deleting test results...")
        result = db.test_results.delete_many({
            "page_id": {"$in": all_page_ids}
        })

        print(f"✅ Successfully deleted {result.deleted_count} test result(s)")

        # Update page statuses to reset them and clear violation counts
        print(f"\n🔄 Resetting page statuses and clearing violation counts...")
        update_result = db.pages.update_many(
            {"_id": {"$in": [ObjectId(page_id) for page_id in all_page_ids]}},
            {
                "$set": {
                    "status": "discovered",
                    "last_tested": None,
                    "test_result_id": None,
                    "violation_count": 0,
                    "warning_count": 0,
                    "info_count": 0,
                    "pass_count": 0
                }
            }
        )
        print(f"✅ Reset {update_result.modified_count} page(s) and cleared all counts")

        # Update website stats
        print(f"\n🔄 Updating website statistics...")
        for website in websites:
            website_id = str(website["_id"])
            pages_count = db.pages.count_documents({"website_id": website_id})

            db.websites.update_one(
                {"_id": ObjectId(website_id)},
                {
                    "$set": {
                        "last_tested": None,
                        "page_count": pages_count
                    }
                }
            )
        print(f"✅ Updated {len(websites)} website(s)")

        print(f"\n✅ All operations completed successfully!")
        print(f"\nSummary:")
        print(f"  • Deleted {result.deleted_count} test results")
        print(f"  • Reset {update_result.modified_count} pages")
        print(f"  • Updated {len(websites)} websites")

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
    print("Delete Test Results for Project CVC-B")
    print("=" * 60)
    print()

    # Check if --yes flag is provided
    skip_confirmation = "--yes" in sys.argv or "-y" in sys.argv

    success = delete_project_test_results("CVC-B", skip_confirmation=skip_confirmation)

    if success:
        print("\n✅ Operation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Operation failed or was cancelled")
        sys.exit(1)
