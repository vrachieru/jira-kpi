import argparse

from collections import Counter, defaultdict
from statistics import mean

from model import Project
from utils import title, seconds_to_human

def run(path):
    project = Project(path)

    issues_grouped_by_type = project.group_issues_by_type(project.issues)
    issues_grouped_by_status = project.group_issues_by_status(project.issues)

    # Level of detail
    for issue_type, issue_type_list in issues_grouped_by_type.items():
        title('%s (%s)' % (issue_type, len(issue_type_list)))

        average_description_size = round(mean([issue.get_size_of_description() for issue in issue_type_list]), 2)
        average_acceptance_criteria_size = round(mean([issue.get_size_of_acceptance_criteria() for issue in issue_type_list]), 2)
        average_how_to_test_size = round(mean([issue.get_size_of_how_to_test() for issue in issue_type_list]), 2)

        print('Average description size: %s lines' % average_description_size)
        print('Average acceptance criteria size: %s lines' % average_acceptance_criteria_size)
        print('Average how to test size: %s lines' % average_how_to_test_size)

    # Type and status distribution
    title('Issue distribution by status (overall)')
    issue_status_distribution = { issue_type:len(issue_type_list) for issue_type, issue_type_list in issues_grouped_by_status.items()}
    for issue, count in issue_status_distribution.items():
        print('- %s: %s' % (issue, count))

    title('Issue distribution by type and status')
    for issue_type, issue_type_list in issues_grouped_by_type.items():
        print('+ %s: %s' % (issue_type, len(issue_type_list)))
        issue_type_status_distribution = project.group_issues_by_status(issue_type_list)
        for issue, count in issue_type_status_distribution.items():
            print(' - %s: %s' % (issue, len(count)))

    # Activity distribution by status
    description_updates = Counter()
    acceptance_criteria_updates = Counter()
    how_to_test_updates = Counter()
    comments = Counter()

    for issue in project.issues:
        description_updates += Counter(issue.get_description_update_by_status_distribution())
        acceptance_criteria_updates += Counter(issue.get_acceptance_criteria_update_by_status_distribution())
        how_to_test_updates += Counter(issue.get_how_to_test_update_by_status_distribution())
        comments += Counter(issue.get_comments_by_status_distribution())

    # Update distribution
    title('Number of updates in status')
    def display_updates(title, counter):
        print('+ %s' % title)
        for k,v in dict(counter).items():
            print(' - %s: %s' % (k,v))

    display_updates('Description', description_updates)
    display_updates('Acceptance criteria', acceptance_criteria_updates)
    display_updates('How to test', how_to_test_updates)
    display_updates('Comments', comments)


    # Time distribution

    # Filter only issues that have been through 'Todo', meaning they were ready to be dragged into 'In Progress'
    issues = [issue for issue in project.issues if 'Todo' in issue.get_status_flow()]
    issues_grouped_by_type = project.group_issues_by_type(issues)

    title('Average time spent in status')
    for issue_type, issue_type_list in issues_grouped_by_type.items():
        status_date_distributions = [issue.get_status_date_distribution() for issue in issue_type_list]
        dd = defaultdict(list)
        for d in status_date_distributions:
            for key, value in d.items():
                dd[key].append(value)

        print('+ %s' % issue_type)
        for key, value in project.sort_issue_status(dd).items():
            print(' - %s: %s' % (key, seconds_to_human(round(mean(value), 2))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', type=str, default='./project', help='Project path')

    args = parser.parse_args()

    run(args.project)