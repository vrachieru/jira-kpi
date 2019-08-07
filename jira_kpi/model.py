import glob
import json
import itertools
import datetime

from utils import get_nested_key, pairwise, seconds_to_human, str_to_date

class Project:

    issues = []

    def __init__(self, path):
        self.load(path)

    def load(self, path):
        '''
        Load issues from persistent storage
        '''
        for issue_file in glob.glob(path + "/*.json", recursive=True):
            try:
                with open(issue_file, encoding='utf-8') as file:
                    self.issues.append(Issue(json.load(file)))
            except:
                pass

    def group_issues(self, issues, criteria):
        '''
        Group issues by provided criteria
        '''
        return { type:list(instances) for type, instances in itertools.groupby(sorted(issues, key=criteria), key=criteria) }

    def group_issues_by_type(self, issues):
        '''
        '''
        return self.sort_issue_type(self.group_issues(issues, lambda issue: issue.type))

    def group_issues_by_status(self, issues):
        '''
        Group issues by status
        '''
        return self.sort_issue_status(self.group_issues(issues, lambda issue: issue.status))

    def sort_issue_type(self, issues):
        '''
        Sort issues by type
        '''
        order = ['Epic', 'User Story', 'Task', 'Sub-Task', 'Dev Bug', 'Prod Bug']
        sorted_keys = sorted(issues, key=lambda type: order.index(type))
        return {key:issues[key] for key in sorted_keys}

    def sort_issue_status(self, issues):
        '''
        Sort issues by the natural flow of statuses
        '''
        order = ['Open', 'On Hold', 'Backlog', 'Todo', 'To Do', 'In Progress', 'Blocked', 'Ready for Review', 'In Review', 'Approval', 'Rejected', 'Done', 'Closed']
        sorted_keys = sorted(issues, key=lambda type: order.index(type))
        return {key:issues[key] for key in sorted_keys}


class Issue:

    def __init__(self, data):
        self.id = get_nested_key(data, 'key')
        self.type = get_nested_key(data, 'fields.issuetype.name')
        self.priority = get_nested_key(data, 'fields.priority.name')
        self.created = str_to_date(get_nested_key(data, 'fields.created'))
        self.status = get_nested_key(data, 'fields.status.name')
        self.creator = get_nested_key(data, 'fields.creator.displayName')
        self.assignee = get_nested_key(data, 'fields.assignee.displayName')
        self.description = get_nested_key(data, 'fields.description', '')
        self.acceptance_criteria = get_nested_key(data, 'fields.customfield_10741', '')
        self.how_to_test = get_nested_key(data, 'fields.customfield_10693', '')
        self.comments = get_nested_key(data, 'fields.comment.comments')
        self.changelog = get_nested_key(data, 'changelog.histories')

    def field_changes(self, field, items):
        '''
        Get changes done to a field
        '''
        return [item for item in items if item['field'] == field]

    def field_changed(self, field, items):
        '''
        Check if a field has been modified
        '''
        return self.field_changes(field, items) != []

    def get_changelog_for_field_only(self, field):
        '''
        Get changelog for field
        '''
        result = []
        for change in self.changelog:
            field_changes = self.field_changes(field, change['items'])
            if field_changes != []:
                change['items'] = field_changes
                result.append(change)

        return result

    def get_status_time_distribution(self):
        '''
        Get the amount of time spent in each status
        '''
        distribution = {}

        changelog = self.get_changelog_for_field_only('status')
        from_date = self.created
        to_date = self.created

        if changelog:
            # historical statuses
            for change in changelog:
                status = change['items'][0]['fromString']
                to_date = str_to_date(change['created'])

                if status not in distribution:
                    distribution[status] = []

                distribution[status].append((from_date, to_date))
                from_date = to_date

            # final/current status
            status = changelog[-1]['items'][0]['toString']
            if status not in distribution:
                distribution[status] = []
            
            distribution[status].append((from_date, datetime.datetime.now(from_date.tzinfo)))
        else:
            distribution[self.status] = [(from_date, datetime.datetime.now(from_date.tzinfo))]

        return distribution

    def get_status_date_distribution(self):
        '''
        Get date intervals for each status
        '''
        date_intervals_to_seconds = lambda intervals: sum([(to_date-from_date).total_seconds() for (from_date, to_date) in intervals])
        return {status:date_intervals_to_seconds(date_intervals) for status, date_intervals in self.get_status_time_distribution().items()}

    def get_status_flow(self):
        '''
        Get overall flow from one status to another
        '''
        changelog = self.get_changelog_for_field_only('status')
        if changelog:
            return [change['items'][0]['fromString'] for change in changelog] + [changelog[-1]['items'][0]['toString']]
        else:
            return []

    def get_rejection_count_from_status(self, searched_status):
        '''
        Get number of times an item has transitioned from searched_status to "In Progress"
        '''
        return len([a for a, b in pairwise(self.get_status_flow()) if a == searched_status and b == 'In Progress'])

    def get_rejections(self):
        '''
        Get number of times the issue has been rejected at review
        '''
        return {
            'In Review': self.get_rejection_count_from_status('In Review'),
            'Approval': self.get_rejection_count_from_status('Approval')
        }

    def get_status_at_point_in_time(self, date):
        '''
        Get the status the issue was in at a certain date
        '''
        status_time_distribution = self.get_status_time_distribution()
        for status, date_intervals in status_time_distribution.items():
            for (from_date, to_date) in date_intervals:
                if from_date <= date and to_date >= date:
                    return status

    def get_field_update_by_status_distribution(self, field):
        '''
        Get the number of times a field has been updated per status
        '''
        distribution = {}

        changelog = self.get_changelog_for_field_only(field)
        for change in changelog:
            status = self.get_status_at_point_in_time(str_to_date(change['created']))

            if status not in distribution:
                distribution[status] = 0

            distribution[status] += 1

        return distribution

    def get_description_update_by_status_distribution(self):
        '''
        Get the number of times the description has been updated in each status
        '''
        return self.get_field_update_by_status_distribution('description')

    def get_acceptance_criteria_update_by_status_distribution(self):
        '''
        Get the number of times the acceptance criteria has been updated in each status
        '''
        return self.get_field_update_by_status_distribution('Acceptance Criteria')

    def get_how_to_test_update_by_status_distribution(self):
        '''
        Get the number of times the testing criteria has been updated in each status
        '''
        return self.get_field_update_by_status_distribution('How to test')

    def get_comments_by_status_distribution(self):
        '''
        Get the number of comments posted in each status
        '''
        distribution = {}

        for comment in self.comments:
            status = self.get_status_at_point_in_time(str_to_date(comment['created']))

            if status not in distribution:
                distribution[status] = 0

            distribution[status] += 1            

        return distribution

    def get_assignees(self):
        '''
        Get list of users that have been assigned to the issue
        '''
        return [change['items'][0]['toString'] for change in self.get_changelog_for_field_only('assignee')]

    def get_size_of_description(self):
        '''
        Get the description size in number of lines
        '''
        return len(self.description.split('\r\n'))-1

    def get_size_of_acceptance_criteria(self):
        '''
        Get the acceptance criteria size in number of lines
        '''
        return len(self.acceptance_criteria.split('\r\n'))-1

    def get_size_of_how_to_test(self):
        '''
        Get the testing criteria size in number of lines
        '''
        return len (self.how_to_test.split('\r\n'))-1
