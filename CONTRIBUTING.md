# Contribution Guide

Welcome to the Digital Wallet project repository. To maintain code quality and operational efficiency, all team members must strictly follow this workflow.

## General Rules

- **Language**: All code, comments, branch names, commit messages, pull requests, and documentation must be written in English.
- **GitHub Board**: If a task is not registered and assigned in the GitHub Project board, it does not exist. Do not work on unregistered tasks [(link)](https://github.com/orgs/unsa-semester-2026-A/projects/1/views/1).
- **WIP Limits**: Each team member is strictly limited to one task in the "In Progress" column at a time. Finish your current task before starting a new one.
- **Documentation**: Architecture decisions and API contracts must be documented in Zensical using User Story Mapping before coding begins.

## Git Workflow (Git Flow)

We implement the standard Git Flow branching model. Direct commits to `main` or `develop` branches are technically blocked. All changes must be integrated via Pull Requests (PR).

### Branch Naming Conventions

- **Features**: `feature/short-task-description`
- **Bugfixes**: `bugfix/issue-description`
- **Hotfixes**: `hotfix/urgent-fix-description`

### Development Steps

1. **Initialize Git Flow** on your local repository (first-time setup):
   Run the initialization command and simply press `Enter` at every prompt to accept all default values. Your terminal output should look exactly like this:

```bash
   git flow init

   Which branch should be used for bringing forth production releases?
      - main
   Branch name for production releases: [main] 
   Branch name for "next release" development: [develop] 

   How to name your supporting branch prefixes?
   Feature branches? [feature/] 
   Bugfix branches? [bugfix/] 
   Release branches? [release/] 
   Hotfix branches? [hotfix/] 
   Support branches? [support/] 
   Version tag prefix? [] 
   Hooks and filters directory? [.../.git/hooks]
```


## Project-Specific Rules

The development workflow, architectural constraints, testing strategies (such as co-located testing), and programming language styling are defined separately for each sub-project:

- **Backend (Python / FastAPI):** Detailed guidelines are located in [backend/README.md](file:///home/alvaro9rqc/1_Pacha/1-unsa/7_S/dis/final/backend/README.md).
- **Mobile Frontend (Dart / Flutter):** Detailed guidelines are located in [mobile/README.md](file:///home/alvaro9rqc/1_Pacha/1-unsa/7_S/dis/final/mobile/README.md).

All developers are expected to read and follow the respective project instructions before submitting pull requests.
