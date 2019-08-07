<p align="center">
    <img src="https://user-images.githubusercontent.com/5860071/62618046-f3613380-b91b-11e9-8a30-4e5f661d0c5f.png" width="200px" border="0" />
    <br/>
    <a href="https://github.com/vrachieru/jira-kpi/releases/latest">
        <img src="https://img.shields.io/badge/version-1.0.0-brightgreen.svg?style=flat-square" alt="Version">
    </a>
    <a href="https://travis-ci.org/vrachieru/jira-kpi">
        <img src="https://img.shields.io/travis/vrachieru/jira-kpi.svg?style=flat-square" alt="CI">
    </a>
    <br/>
    Trying to make sense of what's happening in a team via JIRA activity.
</p>

## About

Make use of JIRA activity to extract an overview of what a project looks like and identify possible issues.

## Usage

Currently there is no integration with the JIRA REST API so collection of issues has to be done somewhat manually.  

You'll have to obtain your cookie from the browser and then use something like the bash script below to fetch a series of issues on which you want to run the analysis.

```
PROJECT="PROJ"
ISSUE_RANGE=$(seq 99 200)

for i in $ISSUE_RANGE; do
    curl "https://jira.domain.com/rest/api/latest/issue/${PROJECT}-${i}?expand=changelog" \
        -H "Cookie: <cookie>" \
        -o "${PROJECT}-${i}.json"
done
```

Then just point the script to the location you've downloaded your issues.

```
$ python main.py --project ./project
```

## Example

The output looks something like the following example:

```
Epic (51)
---------
Average description size: 0.27 lines
Average acceptance criteria size: 0.02 lines
Average how to test size: 0 lines

User Story (464)
----------------
Average description size: 4.65 lines
Average acceptance criteria size: 0.05 lines
Average how to test size: 0 lines

Task (30)
---------
Average description size: 2.83 lines
Average acceptance criteria size: 0 lines
Average how to test size: 0 lines

Sub-Task (497)
--------------
Average description size: 0.78 lines
Average acceptance criteria size: 0 lines
Average how to test size: 0 lines

Dev Bug (9)
-----------
Average description size: 2.67 lines
Average acceptance criteria size: 0 lines
Average how to test size: 0 lines

Issue distribution by status (overall)
--------------------------------------
- On Hold: 8
- Backlog: 7
- Todo: 230
- In Progress: 16
- Blocked: 5
- In Review: 13
- Closed: 772

Issue distribution by type and status
-------------------------------------
+ Epic: 51
 - Todo: 50
 - In Progress: 1
+ User Story: 464
 - On Hold: 4
 - Backlog: 7
 - Todo: 135
 - In Progress: 14
 - Blocked: 3
 - In Review: 10
 - Closed: 291
+ Task: 30
 - Closed: 30
+ Sub-Task: 497
 - On Hold: 4
 - Todo: 44
 - In Progress: 1
 - Blocked: 2
 - In Review: 3
 - Closed: 443
+ Dev Bug: 9
 - Todo: 1
 - Closed: 8

Number of updates in status
---------------------------
+ Description
 - Todo: 518
 - In Progress: 57
 - In Review: 14
 - Closed: 6
 - On Hold: 5
 - To Do: 4
+ Acceptance criteria
 - Todo: 1
+ How to test
+ Comments
 - In Progress: 351
 - In Review: 114
 - Todo: 175
 - Closed: 76
 - On Hold: 34
 - Blocked: 15
 - Ready for Review: 1
 - To Do: 1
 - Backlog: 1

Average time spent in status
----------------------------
+ Epic
 - Backlog: 1M 1w
 - Todo: 2M 3w
 - In Progress: 1M 3w
 - Closed: 9s
+ User Story
 - On Hold: 1w 3d
 - Backlog: 3M 3w
 - Todo: 2w 6d
 - To Do: 5M 1w
 - In Progress: 1w 3d
 - Blocked: 3w 2d
 - Ready for Review: 2M 1d
 - In Review: 1w 12h
 - Closed: 5M 3w
+ Task
 - Todo: 1w 5d
 - To Do: 1M 3d
 - In Progress: 2w 2d
 - Closed: 10M 5d
+ Sub-Task
 - On Hold: 2w 4d
 - Backlog: 1M 4d
 - Todo: 1w 5d
 - To Do: 2w 17h
 - In Progress: 5d 20h
 - Blocked: 2w 2d
 - In Review: 6d 15h
 - Closed: 6M 3w
+ Dev Bug
 - Todo: 8h 41m
 - In Progress: 3d 18h
 - In Review: 3d 11h
 - Closed: 3M 2w
```


## License

MIT
