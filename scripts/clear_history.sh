#!/bin/bash

# Script to remove all commit history from a Git repository and start fresh
# WARNING: This is a destructive operation. Backup your repository first!

set -e  # Exit on any error

# Variables
REPO_DIR="$(pwd)"
BACKUP_DIR="../domdb_backup_$(date +%Y%m%d_%H%M%S)"
DEFAULT_BRANCH="master"

echo "Starting commit history removal process..."

# Step 1: Backup the repository
echo "Creating backup at $BACKUP_DIR..."
git clone . "$BACKUP_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Backup failed. Aborting."
    exit 1
fi

# Step 2: Create an orphan branch with no history
echo "Creating orphan branch..."
git checkout --orphan temp_branch

# Step 3: Add all files and create a new initial commit
echo "Adding all files and creating new initial commit..."
git add -A
git commit -m "Initial commit"

# Step 4: Delete the old default branch
echo "Deleting old branch $DEFAULT_BRANCH..."
git branch -D "$DEFAULT_BRANCH"

# Step 5: Rename the new branch to the default branch
echo "Renaming temp_branch to $DEFAULT_BRANCH..."
git branch -m "$DEFAULT_BRANCH"

# Step 6: Force-push to GitHub
echo "Force-pushing to GitHub (this will overwrite remote history)..."
git push -f origin "$DEFAULT_BRANCH"
if [ $? -ne 0 ]; then
    echo "Error: Force-push failed. Check your permissions or branch protection settings."
    exit 1
fi

# Step 7: Clean up old Git objects locally
echo "Cleaning up old Git objects..."
git gc --aggressive --prune=all

echo "Commit history removed successfully!"
echo "Backup is available at $BACKUP_DIR."
echo "Notify collaborators to re-clone or reset their local repositories."
