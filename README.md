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

## Getting Started
*DO NOT SKIP THESE CRUCIAL SETUP STEPS*

a .env file should be made at the root of the project: SWEN356\.env
within this file you should declare your api key like API_KEY=apikeyherenoquotes

Download Docker Desktop if you don't have it
Open Docker Desktop

from: SWEN356

python src/cli.py init --framework=django --web-server=nginx --project-name=djangoproject

cd SWEN356\djangoproject

docker-compose build

docker-compose up -d
go to http://localhost:1337:80



## Documentation
[Coming soon]

