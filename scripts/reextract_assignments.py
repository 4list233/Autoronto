#!/usr/bin/env python3
import csv
import json

csv_file = 'teamgantt_export_4336931.csv'  # In scripts folder
tasks_with_users = {}
all_names = set()
formats_seen = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Type'] != 'task':
            continue
        
        task_name = row['Name / Title']
        assigned = row.get('Assigned', '')
        
        if not assigned:
            continue
        
        users = []
        for person in assigned.split(','):
            person = person.strip()
            if not person:
                continue
            
            # Track format
            if len(formats_seen) < 20:
                formats_seen.append(person)
            
            # Remove ! prefix
            clean = person.replace('!', '').strip()
            
            # Skip PM
            if 'aUToronto PM' in clean or clean == 'PM':
                continue
            
            # Extract name
            name = None
            if ' - ' in clean:
                parts = clean.split(' - ')
                if len(parts) == 2:
                    # "Name - ROLE"
                    name = parts[0].strip()
                elif len(parts) >= 3:
                    # "TEAM - Name - ROLE"
                    name = parts[1].strip()
            else:
                name = clean
            
            if name and name not in ['MEM', 'LEAD', 'TD', 'LEAAD', 'Member']:
                users.append(name)
                all_names.add(name)
        
        if users:
            tasks_with_users[task_name] = list(set(users))

print(f"✓ Extracted {len(tasks_with_users)} tasks")
print(f"✓ Found {len(all_names)} unique names")
print()

# Check for the "missing" users
check_users = ['Alex You', 'Caroline Tian', 'Annie Rong', 'Belle Lu', 'David Xu', 'Eric Zhang', 
               'Cole Harstone', 'Jaden Dai', 'Joe Dai', 'Leo Choung']
print("Checking 'missing' users:")
for user in check_users:
    if user in all_names:
        count = sum(1 for users in tasks_with_users.values() if user in users)
        print(f"  ✓ {user}: {count} tasks")
    else:
        print(f"  ✗ {user}: NOT FOUND")

# Save
with open('/tmp/task_user_assignments_FIXED.json', 'w') as f:
    json.dump(tasks_with_users, f, indent=2)

print(f"\n✓ Saved to /tmp/task_user_assignments_FIXED.json")
