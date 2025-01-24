#!/bin/bash

echo "🚀 Preparing to push changes to GitHub..."

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ Not a git repository. Please run github_init.sh first."
    exit 1
fi

# Check if there are any changes to commit
if git diff-index --quiet HEAD --; then
    echo "✨ Working directory is clean. No changes to commit."
    
    # Check if there are any unpushed commits
    if git log origin/$(git branch --show-current)..HEAD 2>/dev/null | grep -q .; then
        echo "📤 There are unpushed commits. Proceeding with push..."
    else
        echo "✅ Everything is up to date!"
        exit 0
    fi
else
    # Show status of changes
    echo "📝 Current changes:"
    git status -s
    
    # Stage changes
    read -p "Do you want to stage all changes? (y/n): " stage_all
    if [ "$stage_all" = "y" ]; then
        git add .
    else
        echo "Please stage your changes manually and run this script again."
        exit 0
    fi
    
    # Commit changes
    read -p "Enter commit message: " commit_msg
    if [ -z "$commit_msg" ]; then
        echo "❌ Commit message cannot be empty"
        exit 1
    fi
    git commit -m "$commit_msg"
fi

# Check if remote exists
if ! git remote | grep -q "origin"; then
    echo "❌ No remote repository configured. Please run github_init.sh first."
    exit 1
fi

# Get current branch
current_branch=$(git branch --show-current)

# Function to handle authentication error
handle_auth_error() {
    echo "❌ Authentication failed. Please choose how to proceed:"
    echo "1) Configure HTTPS with Personal Access Token"
    echo "2) Configure SSH"
    echo "3) Exit"
    read -p "Enter your choice (1-3): " auth_choice

    case $auth_choice in
        1)
            echo "ℹ️  You'll need a Personal Access Token from GitHub."
            echo "To create one, go to: GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)"
            echo "Ensure it has 'repo' and 'workflow' scopes."
            read -p "Enter your GitHub username: " github_username
            read -p "Enter your Personal Access Token: " github_token
            
            # Store credentials
            git config --global credential.helper store
            echo "https://$github_username:$github_token@github.com" > ~/.git-credentials
            chmod 600 ~/.git-credentials
            
            # Update remote URL
            remote_url=$(git remote get-url origin)
            new_url=$(echo $remote_url | sed "s/https:\/\//https:\/\/$github_username:$github_token@/")
            git remote set-url origin "$new_url"
            
            echo "✅ HTTPS authentication configured!"
            ;;
        2)
            if [ ! -f ~/.ssh/id_ed25519 ]; then
                echo "🔑 Generating SSH key..."
                read -p "Enter your GitHub email: " github_email
                ssh-keygen -t ed25519 -C "$github_email" -f ~/.ssh/id_ed25519
                
                # Start ssh-agent and add key
                eval "$(ssh-agent -s)"
                ssh-add ~/.ssh/id_ed25519
                
                echo "ℹ️  Add this public key to your GitHub account:"
                cat ~/.ssh/id_ed25519.pub
                echo "Go to: GitHub -> Settings -> SSH and GPG keys -> New SSH key"
                read -p "Press Enter after adding the key to GitHub..."
                
                # Convert HTTPS to SSH URL
                remote_url=$(git remote get-url origin)
                if [[ $remote_url == https://github.com/* ]]; then
                    new_url=$(echo $remote_url | sed 's#https://github.com/#git@github.com:#')
                    git remote set-url origin "$new_url"
                fi
            else
                echo "✅ SSH key already exists!"
            fi
            ;;
        3)
            echo "Exiting..."
            exit 1
            ;;
        *)
            echo "Invalid choice. Exiting..."
            exit 1
            ;;
    esac
}

# Push changes
echo "📤 Pushing changes to remote repository..."
if ! git push origin "$current_branch" 2>&1 | tee /tmp/git_push_error.log; then
    if grep -q "403" /tmp/git_push_error.log || grep -q "Authentication failed" /tmp/git_push_error.log; then
        handle_auth_error
        # Try pushing again after authentication is configured
        if git push origin "$current_branch"; then
            echo "✅ Changes pushed successfully!"
        else
            echo "❌ Push failed again. Please check your credentials and try again."
            exit 1
        fi
    else
        echo "❌ Failed to push changes. Please check the error message above."
        exit 1
    fi
else
    echo "✅ Changes pushed successfully!"
fi

rm -f /tmp/git_push_error.log
exit 0 