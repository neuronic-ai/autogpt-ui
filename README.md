# AutoGPT GUI by Neuronic AI 🚀

Welcome to the official repository of **Neuronic AI's, AutoGPT GUI**. This open-source project provides an intuitive and easy-to-use graphical interface for the powerful [AutoGPT Open Source AI Agent](https://github.com/Significant-Gravitas/Auto-GPT). Driven by GPT-3.5 & GPT-4, AutoGPT has the capability to chain together LLM "thoughts", enabling the AI to autonomously achieve whatever goal you set. 

## Demo

Click the image below to watch a demo of our GUI.

[![Demo Video](https://img.youtube.com/vi/HcbhtEIK2RE/0.jpg)](https://youtu.be/HcbhtEIK2RE)


### Table of Contents
1. [About the Project](#about-the-project)
2. [Features](#features)
3. [Upcoming Features](#upcoming-features)
4. [Installation](#installation)
5. [Contributing](#contributing)


## About the Project

 🧠 AutoGPT is an experimental open-source AI Agent application showcasing the capabilities of the GPT-3.5 & GPT-4 language model. One of the first examples of GPT-4 running fully autonomously, AutoGPT pushes the boundaries of what is possible with AI.

AutoGPT has fantastic potential that was locked behind a command-line interface, which for many users can be intimidating, difficult, inconvenient and/or limiting. We at Neuronic AI decided to develop a no non-sense opensource Graphical User Interface (GUI) for AutoGPT to bring this powerful technology closer to everyone and enable users to engage AutoGPT in a meaningful way. We also take the interface to another level by enabling multi-user support and the ability to integrate with existing websites.

Because (#1) setting up AutoGPT correctly can sometimes be difficult with various version conflicts and dependencies issues, and (#2) because how fast AutoGPT is changing which creates the potential need to re-factor or re-base code between releases, we embed a specific version of AutoGPT along with all of its dependencies and appropriately versioned stacks to support normal operation with our GUI.  The initial opensource release 1.0 is built on top of AutoGPT Stable 0.4.0.

## Features

## AI Settings File

:page_facing_up: To use the interface, we need to pass instructions via an AI settings file. These instructions could be as simple as a "Hello, World!" program or complex enough to write a full-stack Java application.

The standard format for instructions includes a name, a role, a set of goals each denoted by a dash (-) at the beginning of the instruction, and a budget to limit API consumption.

------------------------

# Fast and Smart Engines

:steam_locomotive: With our interface, you can choose the language model for your fast and smart engines. AutoGPT designed the fast model to handle the AI agent processing, and the smart model to handle the actual tasks the AI agent performs. 

Note that GPT3.5 can only handle up to 4000 tokens maximum, and GPT-4 max tokens is based on which version of GPT-4 you have access to (8k or 32k). You can use 3.5 for both or GPT-4 for both.

## Workspace Management

 💼 With the workspace management interface, you can view, download, or delete any files that are generated, along with uploading files for AutoGPT to work with. Preview support for most readable file types, best effort syntax highlighting, multi-directory support.

## Upcoming Features

:arrow_upper_right: We are constantly working on adding more features to make your experience even better. The next version will include:

1. **Support for Rapid Tasks**: Execute tasks in a rapid manner without any hassle.
2. **Plugins**: Add more functionalities to your interface.
3. **Mobile Interfaces**: Take your AI assistant anywhere with our mobile interface.
3. **Updates to max token handling**: More ways to prevent token overruns and budget overruns.

Stay tuned for these amazing features. We are excited to see what you will build with this!


## Installation

🔧 The build is using the Nuxt Framework and is containerized and intended to run on docker. The complete build will deploy the following containers

- auto-gpt-ui_api: Backend API enabled interface
- auto-gpt-ui_worker: To process all of our jobs
- auto-gpt-ui_frontend: The GUI
- traefik:v2.9: Web server/ proxy
- mysql: Necessary for multi-user support
- redis: Used for maintaining job state

Environment variables
Copy config files

- cp .env.example .env 
- cp env-backend.example.env env-backend.env 
- cp env-frontend.example.env env-frontend.env 
- cp env-mysql.example.env env-mysql.env 


#Copy the examples and set your env files up before building

Docker
Build and Deploy:

make all


The app will be exposed at port 8160


## Contributing 
🤝 This project exists thanks to all the people who contribute. Big shout out to:

- [EncryptShawn](https://github.com/EncryptShawn) - Design, Guidance, Funding, DevOps
- [Yolley](https://github.com/Yolley) - Initial Codebase

We welcome contributions! Please see `CONTRIBUTING.md` for details on how to contribute.


