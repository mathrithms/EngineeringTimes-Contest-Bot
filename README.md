# EngineeringTimes-Contest-Bot


## Table of Contents

1. General Info
2. Technology used
3. Scope of Functionalities
4. Commands

### 1. General Info

This bot application is focused on sending reminders about coding contests from some popular coding websites to discord servers in well-arranged and easy-to-read embeds. 
This is part an open source project for the discord server of an organization.


### 2. Technology Used
* Selenium and Chrome webdriver
* discord.py
* Postgres database


### 3. Scope of Functionalities
The main function of the bot is to send reminders about coding contest every few hours.
It also includes several commands, such as the editorials command which gives a list of all the recently updated editorials of codechef contests with links.

### 4. Commands
**NOTE**: All commands must be prefixed by '!' for them to work.

* *codeforces*: Gives all the codeforces contests listed on the website
* *codechef present/future*: Gives the present or future contest form Codechef. Long contests which last for several months or years are not included.
* *codechef all*: Gives all the long contests from Codechef website.
* *editorials*: Gives a links to all the recently ended contest editorials (Codechef).
* *help*: Gives a list of commands users can call.
* *setup*: Users can make a separate channel and call this command in it to make sure all reminder embeds go to that particular channel. In case of an already setup, users can use this command in another channel to update their reminder channel.