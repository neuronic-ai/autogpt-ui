# AutoGPT GUI by Neuronic AI 🚀

Welcome to the official repository of **Neuronic AI's, AutoGPT GUI**. This open-source project provides an intuitive and easy-to-use graphical interface for the powerful [AutoGPT Open Source AI Agent](https://github.com/Significant-Gravitas/Auto-GPT). Driven by GPT-3.5 & GPT-4, AutoGPT has the capability to chain together LLM "thoughts", enabling the AI to autonomously achieve whatever goal you set. 

### Table of Contents
1. [Demo-Tutorial](#demo-tutorial)
2. [About the Project](#about-the-project)
3. [Features](#features)
4. [Installation](#installation)
5. [Contributing](#contributing)


### Demo-Tutorial
Various multimedia and content in support of using this code

Additionally, we have a puiblicly available free demo available online to try, however, it is signficantly restricted with no ablity to run code or administrative commands and you need to bring your own OpenAI API key. The demo can be accessed on No|App and it requires users to create a login and add an OpenAI API key to use but then is available online @ [https://noapp.ai](https://noapp.ai/apps/app.html?app=9). If you are not logged in it will forward you to login where you can choose to register with an email address or Google. Using your email to sign up versus Google will require you to verify your email. Once you have an account, go to the menu and select "unlock AI" and add your OpenAI API key, after this all the AI services on No|App will be available for you to use or demo.

#### Installation
Click the image below for a tutorial on installing AutoGPT-ui

[![Demo Video](https://img.youtube.com/vi/7Z7V03psycI/0.jpg)](https://www.youtube.com/watch?v=7Z7V03psycI)


#### Release 1.0:

Click the image below to watch a demo of our GUI.

[![Demo Video](https://img.youtube.com/vi/HcbhtEIK2RE/0.jpg)](https://youtu.be/HcbhtEIK2RE)


##### Release 1.2
In this release we add support for plugins, we add a "Rapid Goal" entry for fast single goal engagement while still supporting ai_settings files for complex instruction sets, we add support for GPT 3.5 16k, cleaned up the interface and added support for mobile.

Release 1.2: Desktop Interface
![Release 1.2 Desktop interface](https://github.com/neuronic-ai/autogpt-ui/blob/main/autogpt1-2-desktop.png)

Release 1.2: Mobile Interface
![Release 1.2 Mobile interface](https://github.com/neuronic-ai/autogpt-ui/blob/main/autogpt1-2-mobile.png)

Release 1.2: API Interface
![Release 1.2 API interface](https://github.com/neuronic-ai/autogpt-ui/blob/main/autogpt-api.png)

## About the Project

 🧠 AutoGPT is an experimental open-source AI Agent application showcasing the capabilities of the GPT-3.5 & GPT-4 language model. One of the first examples of GPT-4 running fully autonomously, AutoGPT pushes the boundaries of what is possible with AI.

AutoGPT has fantastic potential that was locked behind a command-line interface, which for many users can be intimidating, difficult, inconvenient and/or limiting. We at Neuronic AI decided to develop a no non-sense opensource Graphical User Interface (GUI) for AutoGPT to bring this powerful technology closer to everyone and enable users to engage AutoGPT in a meaningful way. We also take the interface to another level by enabling multi-user support and the ability to integrate with existing websites.

Because (#1) setting up AutoGPT correctly can sometimes be difficult with various version conflicts and dependencies issues, and (#2) because how fast AutoGPT is changing which creates the potential need to re-factor or re-base code between releases, we embed a specific version of AutoGPT along with all of its dependencies and appropriately versioned stacks to support normal operation with our GUI.  The initial opensource release 1.0 is built on top of AutoGPT Stable 0.4.0.

## Features
We have released 1.0 to the public and we are working on release 1.1 now and will be performing extensive testing to ensure that 1.1 is a near produciton ready software.

#### Release 1.0:
- Built on AutoGPT 0.4.0
- Desktop graphical interface for AutoGPT
- User specified AI_settings File
- Resume stopped processes where we left off
- Set fast and smart engine
- Set max tokens for smart and fast engine
- Set image size for Dalle image generation
- Semi-Continuous mode with batch authorization interface
- Workspace management with support for single file/directory or batch upload, download and delete
- Workspace file preview for major file tyes and best effort syntax highlighting
- Containerized with API backend, worker and frontend along with supporting containers

#### Release 1.2:
 - Built on AutoGPT 0.4.4
 - Can choose what AutoGPT branch to use on build
 - Supports everything that Release1.0 supports except for the resume function
 - Support for Rapid Tasks: Execute a single tasks in a rapid manner without any hassle.
 - Plugins: Add more functionalities to your interface with an array of popular plugins support
 - Updated Desktop interface: We level up the UI/UX some
 - Mobile Interfaces: Take your AI assistant anywhere with a powerful mobile interface.
 - Support for GPT 3.5 16k
 - Max Tokens: A lot more max token options now
 - File size in workspace management
 - API controls and documentation via http://x.x.x.x:8160/docs


## AI Settings File

:page_facing_up: To use the interface, we need to pass instructions via an AI settings file. These instructions could be as simple as a "Hello, World!" program or complex enough to write a full-stack Java application.

The standard format for instructions includes a name, a role, a set of goals each denoted by a dash (-) at the beginning of the instruction, and a budget to limit API consumption.

------------------------

## Fast and Smart Engines

:steam_locomotive: With our interface, you can choose the language model for your fast and smart engines. AutoGPT designed the fast model to handle the AI agent processing, and the smart model to handle the actual tasks the AI agent performs. 

Note that GPT3.5 can only handle up to 4000 tokens maximum (release 1.1 will support 3.5 16k) and GPT-4 max tokens is based on which version of GPT-4 you have access to (8k or 32k). You can use 3.5 for both or GPT-4 for both.

## Workspace Management

 💼 With the workspace management interface, you can view, download, or delete any files that are generated, along with uploading files for AutoGPT to work with. Preview support for most readable file types, best effort syntax highlighting, multi-directory support.


## Installation

🔧 The build is using the Nuxt Framework and is containerized and intended to run on docker. The complete build will deploy the following containers

- auto-gpt-ui_api: Backend API enabled interface
- auto-gpt-ui_worker: To process all of our jobs
- auto-gpt-ui_frontend: The GUI
- traefik:v2.9: Web server/ proxy
- mysql: Necessary for multi-user support
- redis: Used for maintaining job state

The app will be exposed at port 8160

(See video tutorial in the demo and tutorial section)

1. Install Ubuntu server (18 or newer)
2. Install build-essential (sudo apt install build-essential)
3. Install Docker and Docker-Compose (See how-to-docker.txt file)
4. Clone the repo down to your local machine
5. create .env,  env-frontend.env, env-backend.env and env-mysql.env files (use examples and/or env-guidance.txt for help)
6. Build the app with "sudo make all"
7. Check that all your containers are up with "docker ps -a" (If container(s) are down check their logs for an indication why "docker logs container_name_or_id")
8. Connect with your browser on port 8160. If installed on your local machine "https://localhost:8160 or otherwise use the IP of the machine its installed on

-------------------

Environment variables
Copy config files or create new ones using env-guidance

- cp .env.example .env 
- cp env-backend.example.env env-backend.env 
- cp env-frontend.example.env env-frontend.env 
- cp env-mysql.example.env env-mysql.env 

--------------------

## Contributing 
🤝 This project exists thanks to all the people who contribute. Big shout out to:

- [EncryptShawn](https://github.com/EncryptShawn) - Design, Guidance, Funding, DevOps
- [Yolley](https://github.com/Yolley) - Initial Codebase

We welcome contributions! Please see `CONTRIBUTING.md` for details on how to contribute.

