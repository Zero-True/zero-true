# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.
Communicate with the maintainers of the repo and let us know what you're planning on doing! We will have to maintain the features in the long run so we have to carefully consider what
to add and what to leave as an external dependency. We are working on creating a way for users to create external components and plugins that can be installed... stay tuned for 
instructions on how to do that! 

Please note we have a code of conduct, please follow it in all your interactions with the project.

# Welcome to GitHub Docs Contributing Guide

Thank you for investing your time in contributing to our project! Any contribution you make will be reflected in zero-true!

Read our [Code of Conduct](#code-of-conduct) to keep our community approachable and respectable.

In this guide you will get an overview of the contribution workflow from opening an issue, creating a PR, reviewing, and merging the PR.

## Table of Contents

- [New Contributor Guide](#new-contributor-guide)
- [Getting Started](#getting-started)
- [Issues](#issues)

## New Contributor Guide

To get an overview of the project, read the README file. Here are some resources to help you get started with open source contributions if this is something completely new to you:

- [Finding ways to contribute to open source on GitHub](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github)
- [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git)
- [Collaborating with pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests)

## Getting Started

To navigate our codebase with confidence, learn more about pydantic (for type safety of the python side),fastapi, sphynx (for building docs), pytest/selenium for testing
and Vuetify for our frontend.

When you pip install zero-true it is packaged with two cli utilities:
```bash
zero-true notebook
```
```bash
zero-true-dev notebook
```

When you type zero-true in your terminal it will open a regular notebook. On the other hand zero-true-dev is the cli we use when we want to be able to 
hot reload and see any changes to the interface or backend during development. This makes testing any changes that you make quick and easy. In order to use 
the dev cli you need to have access to the source code which means you need to fork and then clone our repo. Then clone the code you've forked, navigate into
the directory with the source code and simply run zero-true-dev from the cli. The steps to do this are included below:

```bash
git clone https://github.com/[YOUR-USERNAME]/zero-true.git 
cd zero-true
zero-true-dev notebook
```

This will launch a notebook in dev mode. Make changes to either the frontend or backend and watch the changes hot reload. 

## Issues

If you run into any issues that you suspect are bugs please check the issues in our repo to see if we have any open issues about already and if so please contribute to that discussion. 
It is always helful to have a minimal reproducible example so that anyone debugging can spin up a notebook, run your code in it and then try to diagnose the problem. 

### Solve an Issue

If you'd like to solve one of our open issues please get in touch first! As we noted above not every issue/feature request is something that we can actively maintain! 