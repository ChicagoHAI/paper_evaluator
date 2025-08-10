# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a paper evaluator project that is currently in its initial state. It should be written in python. The goal is to implement an LLM as a judge according to guidelines.

## Development Setup

* Write the project in python
* Use OpenRouter to call LLM APIs
* resource/ has review_form.txt and review_guidelines.txt that you should use to write the key prompts for the LLM as a judge. Write the key prompt in a separate file in the src folder.
* In the src folder, write a main function that takes a latex file or a pdf file and a config file, and run the LLM as judge and output the review in a text file.
* The config file should specify which judges to use, specify an openrouter key. Generate an empty one with 'moonshotai/kimi-k2:free' and 'z-ai/glm-4.5-air:free' as examples. Generate another .local one that will actually be used but will be ignored in .gitignore.
* Update README once you are done.
