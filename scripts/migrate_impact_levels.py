#!/usr/bin/env python3
"""
Migration script to update impact levels from old format to new format
Old: critical, serious, moderate, minor
New: high, medium, low
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from datetime import datetime

def migrate_impact_levels():
    """Migrate impact levels in existing test results"""
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client.auto_a11y
    
    # Impact level mapping
    impact_mapping = {
        'critical': 'high',
        'serious': 'high',
        'moderate': 'medium',
        'minor': 'low'
    }
    
    # Counter for tracking updates
    total_results = 0
    updated_results = 0
    updated_violations = 0
    updated_warnings = 0
    updated_info = 0
    updated_discovery = 0
    updated_ai_findings = 0
    
    print("Starting impact level migration...")
    print(f"Mapping: {impact_mapping}")
    
    # Find all test results
    test_results = db.test_results.find({})
    
    for result in test_results:
        total_results += 1
        needs_update = False
        
        # Update violations
        if 'violations' in result:
            for violation in result['violations']:
                if 'impact' in violation and violation['impact'] in impact_mapping:
                    violation['impact'] = impact_mapping[violation['impact']]
                    needs_update = True
                    updated_violations += 1
        
        # Update warnings
        if 'warnings' in result:
            for warning in result['warnings']:
                if 'impact' in warning and warning['impact'] in impact_mapping:
                    warning['impact'] = impact_mapping[warning['impact']]
                    needs_update = True
                    updated_warnings += 1
        
        # Update info
        if 'info' in result:
            for info in result['info']:
                if 'impact' in info and info['impact'] in impact_mapping:
                    info['impact'] = impact_mapping[info['impact']]
                    needs_update = True
                    updated_info += 1
        
        # Update discovery
        if 'discovery' in result:
            for discovery in result['discovery']:
                if 'impact' in discovery and discovery['impact'] in impact_mapping:
                    discovery['impact'] = impact_mapping[discovery['impact']]
                    needs_update = True
                    updated_discovery += 1
        
        # Update AI findings
        if 'ai_findings' in result:
            for finding in result['ai_findings']:
                if 'severity' in finding and finding['severity'] in impact_mapping:
                    finding['severity'] = impact_mapping[finding['severity']]
                    needs_update = True
                    updated_ai_findings += 1
        
        # Save updated document
        if needs_update:
            db.test_results.replace_one({'_id': result['_id']}, result)
            updated_results += 1
            if updated_results % 10 == 0:
                print(f"  Updated {updated_results} test results...")
    
    print("\n✅ Migration completed!")
    print(f"Total test results: {total_results}")
    print(f"Updated test results: {updated_results}")
    print(f"Updated violations: {updated_violations}")
    print(f"Updated warnings: {updated_warnings}")
    print(f"Updated info items: {updated_info}")
    print(f"Updated discovery items: {updated_discovery}")
    print(f"Updated AI findings: {updated_ai_findings}")
    
    return True

if __name__ == "__main__":
    try:
        migrate_impact_levels()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)