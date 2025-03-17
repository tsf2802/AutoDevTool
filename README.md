# AI-Powered DevOps Automation Platform

## Overview
This project focuses on automating the initial setup and deployment of software projects by integrating a comprehensive DevOps toolchain with generative AI-powered auto-documentation capabilities. The process begins with a form where project-specific details are inputted, such as project requirements, dependencies, and configurations. 

Upon submission, the system automatically generates the necessary project environment, including directory structures, package installations, and initial code templates. As you develop the project, Dockerfiles are auto-updated based on (initially the framework such as Django or Next.js), the project structure and downloaded packages. Additionally, the integration of generative AI ensures that documentation is created in real-time, reducing manual effort and enhancing project clarity. 

This solution aims to significantly accelerate project onboarding, improve consistency, and foster collaboration by providing a seamless, end-to-end setup process tailored to modern development workflows. It fills in the need to invest heavily in a DevOps (in terms of deploying) person for organizations that need fast-moving and flexible developers.

## Features
- Automated project environment setup
- Dynamic Dockerfile generation
- AI-powered documentation
- Framework-specific configurations
- Customizable project templates
- Enhanced team collaboration

## Prerequisites
- Docker Desktop
- Python environment
- Google Gemini API key

## Environment Setup
1. Create a `.env` file in the root directory (SWEN356/.env)
2. Add your API key:
   ```
   API_KEY=your_api_key_here
   ```
3. Ensure Docker Desktop is running

## Usage
1. Navigate to the project base folder
2. Run the initialization command:
   ```bash
   python src/cli.py init --framework=django --web-server=nginx --project-name=djangoproject
   ```
   Optional: Add project context with `--context="project description"`

## Deployment
1. Navigate to your project directory:
   ```bash
   cd SWEN356/djangoproject
   ```
2. Build and run the Docker containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
3. Access the application at `http://localhost:1337`

## Notes
- The project name can be customized, but ensure to update `.gitignore` accordingly
- For environment issues, consider using a fresh virtual environment with clean dependencies


