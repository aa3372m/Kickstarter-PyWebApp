#!/bin/bash

echo "🚀 Initializing GitHub Repository Setup..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if directory is already a git repository
if [ -d .git ]; then
    echo "⚠️  Git repository already exists!"
    read -p "Do you want to reinitialize? (y/n): " reinit
    if [ "$reinit" != "y" ]; then
        echo "Exiting..."
        exit 0
    fi
    rm -rf .git
fi

# Initialize git repository
echo "📁 Initializing git repository..."
git init

# Configure git if not already configured
if [ -z "$(git config --global user.name)" ]; then
    echo "🔧 Git user name not configured."
    read -p "Enter your name for git config: " git_name
    git config --global user.name "$git_name"
fi

if [ -z "$(git config --global user.email)" ]; then
    echo "🔧 Git email not configured."
    read -p "Enter your email for git config: " git_email
    git config --global user.email "$git_email"
fi

# Configure GitHub authentication
echo "🔐 Setting up GitHub authentication..."
echo "1) HTTPS (with Personal Access Token)"
echo "2) SSH"
read -p "Choose authentication method (1/2): " auth_method

case $auth_method in
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
        
        echo "✅ HTTPS authentication configured!"
        ;;
    2)
        # Check if SSH key exists
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
        else
            echo "✅ SSH key already exists!"
        fi
        ;;
    *)
        echo "❌ Invalid choice. Using HTTPS by default."
        ;;
esac

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore file..."
    cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Flask
instance/
.webassets-cache

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOL
fi

# Stage all files
echo "📦 Staging files..."
git add .

# Initial commit
echo "💾 Creating initial commit..."
read -p "Enter commit message (default: 'Initial commit'): " commit_msg
commit_msg=${commit_msg:-"Initial commit"}
git commit -m "$commit_msg"

# Add remote origin
echo "🌐 Setting up remote repository..."
read -p "Do you want to add a remote origin? (y/n): " add_remote
if [ "$add_remote" = "y" ]; then
    read -p "Enter your GitHub repository URL: " repo_url
    if [ ! -z "$repo_url" ]; then
        # Modify URL if using HTTPS with token
        if [ "$auth_method" = "1" ]; then
            repo_url=$(echo $repo_url | sed "s/https:\/\//https:\/\/$github_username:$github_token@/")
        fi
        git remote add origin "$repo_url"
        echo "✅ Remote origin added successfully!"
    fi
fi

echo "🎉 Git repository initialized successfully!"
echo "ℹ️  Use ./scripts/git_push.sh to push your changes to GitHub"

# Make git_push.sh executable
chmod +x scripts/git_push.sh

exit 0 