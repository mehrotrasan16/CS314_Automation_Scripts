# Travis API script.

import requests as r
import urllib
from datetime import datetime, timedelta
import re
from csv import DictWriter
import os
import settings
import sys

class TravisReporter:
    """The TravisReporter class.
    Used to generate a sprint report in the form of a CSV
    about the state of Travis.
    """

    # Some static parameters to use in requests
    # The limit will be set to 100 by Travis pagination
    _req_params = {'limit': '500', 'sort_by': 'finished_at:desc'}

    # Resulting CSV headers
    _csv_header = ['Team', 'Average_Success_Duration', 'Test_Count', 'Failed_Tests', 'Errored_Tests', 'Skipped_Tests', 'Successful_Builds', 'Failed_Builds', 'Errored_Builds', 'Canceled_Builds', 'Jest_tests_count', 'Jest_skipped']

    def __init__(self, travis_token, org_name=settings.ORG_NAME, sprint_start=(datetime.utcnow() - timedelta(days=21)), sprint_end=datetime.utcnow()):
        """Constructor.
        See https://developer.travis-ci.com/authentication for more info
        on getting your Travis access token.
        Args:
        travis_token (str): Your Travis authentication token.
        org_name (str): The name of the GitHub organization (defaults to fall 2018's org).
        sprint_start (datetime): The date of the start of the sprint, UTC time. Defaults to 21 days ago.
        sprint_end (datetime): The date of the end of the sprint, UTC time. Defaults to now.
        """
        # Initialize our headers with the token we passed
        self._headers = {'Authorization': 'token {}'.format(travis_token), 'Travis-API-Version': '3'}
        self._org = org_name
        # Final list that can be output to CSV
        self.org_results = {}

        # Set start and end times for the sprint
        self._start_date = sprint_start
        self._end_date = sprint_end
        
        
        print(travis_token,org_name,sprint_start,sprint_end)
        print("\n\n\n\n\n\n\n\n\n\n\n\n")

    def get_metrics(self, num_teams=settings.NUM_TEAMS):
        """Get the Travis metrics for the entire organization.
        Args:
        num_teams (int): An optional argument for the total number of teams, 0 to n-1, defaults to 25.
        num_teams (int): An optional argument for the total number of teams, 0 to n-1, defaults to 25.
        """
        # For each team...
        for i in range(num_teams):
            print('\n\nTeam t{:02d}'.format(i))
            # Call out to get a single team's metrics appended
            # NOTE: This assumes we use a format of t[\d][\d] for team/repository name
            self.get_single_team_metrics('t{:02d}'.format(i))
        print('Done analyzing all relevant builds for all teams')

    def get_single_team_metrics(self, team):
        """Get the Travis metrics for a single team.
        Args:
        team (str): The team/repository for which to generate metrics.
        """
        # Initialize this team's results dict
        self.org_results.setdefault(team, {'Team': team})

        # Now get the list of builds
        try:
            all_builds = self._get_builds(team)
        except Exception as e:
            print('Failed to get builds for team {}'.format(team))
            print('Exception was {} with message of {}'.format(type(e), str(e)))
            return

        # Filter the builds based on date
        print('Filtering builds to timeframe...')
        all_builds = [build for build in all_builds if self._filter_on_date(build)]

        # Now analyze the builds for the most recently added (this) team...
        self._analyze_builds(team, all_builds)

    def output_metrics(self):
        """Output any gathered metrics to a CSV file."""
        print('Writing statistics to new CSV...')
        # Get the current date for the title
        today = str(datetime.now().date())
        f = open('./Travis-Report{}.csv'.format(today), 'w', newline='')
        dw = DictWriter(f, fieldnames=self._csv_header)
        dw.writeheader()
        for stats in self.org_results.values():
            dw.writerow(stats)
        f.close()

    def _get_builds(self, team):
        """Get all of the builds for a team.
        TODO: What happens when we have far too many builds? There is not a way
        to limit based on time, so we should implement a "max number of builds
        to fetch" parameter.
        Args:
        team (str): The team's repository name.
        Returns: A list of dicts that represent every build the team has made.
        """
        # First assemble their Travis repository api request url
        # This must be url-encoded for the 'slug' part of the url (e.g. 'csu18fa314%2Ft00')
        repo_url = urllib.parse.quote('{}/{}'.format(self._org, team), safe='')
        full_url = 'https://api.travis-ci.com/repo/' + repo_url + '/builds'
        print('Fetching all builds from ' + full_url)

        # Now perform the fetch
        response = r.get(url=full_url, headers=self._headers, params=self._req_params).json()
        all_builds = response['builds']

        # Append more builds if necessary (thanks to pagination)
        # TODO: This could get dicey if we have a lot, lot, lot of builds.
        while not response['@pagination']['is_last']:
            # Use the API response to get the next page's path
            next_url = 'https://api.travis-ci.com' + response['@pagination']['next']['@href']
            # Update response
            response = r.get(url=next_url, headers=self._headers).json()
            # Extend builds
            all_builds.extend(response['builds'])

        return all_builds

    def _analyze_builds(self, team, builds):
        """Perform analysis of all of the builds for a team in a time interval.
        Extract and track key information from the build, fetching logs where
        necessary.
        Args:
        team (str): The team's name/repository.
        builds: (list of dict): The list of build dicts fetched from Travis.
        """
        print('Analyzing {} builds for team {}'.format(len(builds), team))

        # These are our main metrics across ALL builds
        success_builds = 0
        failure_builds = 0
        errored_builds = 0
        canceled_builds = 0

        # Successful build total duration
        cumulative_successtime = 0

        # First, fetch the log of the most recent build that has JUnit output, to
        # determine how many tests there were and their outcome.
        for b in builds:
            if self._analyze_log(team, b):
                break

        # Now we simply iterate to count up the different states of PRs
        for b in builds:
            state = b['state']

            # No final 'else' here, since there are more than just these states
            if state == 'passed':
                success_builds += 1
                # Also extract the duration of the successful build
                cumulative_successtime += b.get('duration', 0)
            elif state == 'failed':
                failure_builds += 1
            elif state == 'errored':
                errored_builds += 1
            elif state == 'canceled':
                canceled_builds += 1

        # Capture our results
        self.org_results[team]['Successful_Builds'] = success_builds
        self.org_results[team]['Failed_Builds'] = failure_builds
        self.org_results[team]['Errored_Builds'] = errored_builds
        self.org_results[team]['Canceled_Builds'] = canceled_builds

        # Average duration of successful build
        if success_builds > 0:
            self.org_results[team]['Average_Success_Duration'] = round(cumulative_successtime / success_builds)
        else:
            self.org_results[team]['Average_Success_Duration'] = 'N/A'

    def _analyze_log(self, team, build):
        """Analyze the log of a single build.
        Extracts key information about JUnit tests.
        Args:
        team (str): The team being analyzed.
        build (dict): The build to analyze.
        Returns: True if the log was successfully analyzed, False if
        another log should be analyzed.
        """
        # Fetch the log for this build
        # We assume that there was only one job
        job_id = build['jobs'][0]['id']
        print('Analyzing log for job with id {}'.format(job_id))

        # Account for a canceled build (and thus no log)
        if build['state'] == 'canceled':
            print('Build was canceled, no log to analyze')
            return False
        log = r.get('https://api.travis-ci.com/job/{}/log'.format(job_id), headers=self._headers).json()['content']
        
        # def escape_ansi(line):
        #     ansi_regex = r'\x1b(' \
        #      r'(\[\??\d+[hl])|' \
        #      r'([=<>a-kzNM78])|' \
        #      r'([\(\)][a-b0-2])|' \
        #      r'(\[\d{0,2}[ma-dgkjqi])|' \
        #      r'(\[\d+;\d+[hfy]?)|' \
        #      r'(\[;?[hf])|' \
        #      r'(#[3-68])|' \
        #      r'([01356]n)|' \
        #      r'(O[mlnp-z]?)|' \
        #      r'(/Z)|' \
        #      r'(\d+)|' \
        #      r'(\[\?\d;\d0c)|' \
        #      r'(\d;\dR))'
        #     ansi_escape = re.compile(ansi_regex, flags=re.IGNORECASE)

        #     #ansi_escape = re.compile(r'(?:\x1b[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        #     return ansi_escape.sub('', line)
        

        # Regular expressions to match log output for tests
        junit_regex = re.compile('Results:[\r\n]+.*[\r\n]+.*Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)') #re.compile(r'.*Results:[\r\n]+.*[\r\n]+.*Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)') #re.compile(r'Results:[\r\n]+Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)')
        jest_regex = re.compile('Tests:.* \d+ total') #re.compile(r'Tests:[ A-z0-9,]+, \d+ total')

        #log = escape_ansi(log)

        # Search for the test results string, will be the last (and hopefully first) in this list
        junit = junit_regex.findall(log)
        jest = jest_regex.findall(log)

        junit = re.findall('Results:[\r\n]+.*[\r\n]+.*Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)',log)
        jest = re.findall('Tests:.* \d+ total',log)

        if len(junit) is 0:
            print('Failed to find JUnit test output.')
            return False
        elif len(jest) is 0:
            print('Failed to find Jest test output.')
            return False

        # Reassign to the lines we care about
        # JUnit will be in the order (run, failed, errors, skipped)
        junit = junit[-1]
        jest = jest[-1]

        # Now let's split it to get the numbers
        jest_total = re.findall(r'(\d+) total', jest)
        jest_skipped = re.findall(r'(\d+) skipped', jest)

        # Update team's dict
        self.org_results[team]['Test_Count'] = junit[0]
        self.org_results[team]['Failed_Tests'] = junit[1]
        self.org_results[team]['Errored_Tests'] = junit[2]
        self.org_results[team]['Skipped_Tests'] = junit[3]
        self.org_results[team]['Jest_tests_count'] = jest_total[0]
        # Jest may or may not note skipped tests
        self.org_results[team]['Jest_skipped'] = jest_skipped[0] if len(jest_skipped) > 0 else 0

        # Report that the log was successfully analyzed
        return True

    def _filter_on_date(self, build):
        """Custom filter function for filtering builds by date.
        Utilizes the instance variables _start_date and _end_date
        to determine if the build is within the appropriate range.
        Args:
        build (dict): The build dict to decide on.
        Returns: A boolean of whether to include or not.
        """
        # Use the common format used by Travis
        # This may be None in the case that the build errored
        finished_at = build.get('finished_at')
        if finished_at is None:
            return False

        # Else, strip the time
        build_time = datetime.strptime(finished_at, '%Y-%m-%dT%H:%M:%SZ')
        return self._start_date < build_time < self._end_date

# Entry point for one-off script
if __name__ == '__main__':

    # All times are in UTC
    sprint_num = os.getenv("SPRINT_NUM")
    sprint_start, sprint_end = datetime.strptime('2020-09-15 00:00:00', '%Y-%m-%d %H:%M:%S'), datetime.strptime('2020-10-01 22:00:00', '%Y-%m-%d %H:%M:%S')#settings.getSprintDates(sprint_num)
    if not sprint_start or not sprint_end:
        print("[travis-api.py] Error, couldn't get valid sprint data, check the values in settings.SPRINT_DATES.")
        sys.exit(1)

    # Use the TRAVIS_TOKEN set in your environment variables
    rep = TravisReporter(os.getenv('TRAVIS_TOKEN'), 'csucs314f20', sprint_start, sprint_end)

    # Get all metrics
    rep.get_metrics()

    # Get only metrics for a single team, given their repository name
    # rep.get_single_team_metrics('d24')
    rep.output_metrics()
