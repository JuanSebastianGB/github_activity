#!/usr/bin/env python

import os
import sys
import argparse
from random import randint
from subprocess import Popen
from datetime import datetime, timedelta


class GitRepository:
    def __init__(self, args):
        """
        Initialize the GitRepository class with command-line arguments.
        Args:
            args (argparse.Namespace): Parsed command-line arguments.
        """
        self.args = args
        self.curr_date = datetime.now()
        self.directory = self._determine_directory()
        self.commit_dates = self._generate_commit_dates()

    def setup(self):
        """
        Set up the Git repository, generate commits, and push to a remote repository if specified.
        """
        self._create_and_initialize_repository()
        for commit_time in self.commit_dates:
            self._contribute(commit_time)
        if self.args.repository:
            self._setup_remote_repository()
        print("\nRepository generation completed successfully!")

    def _determine_directory(self):
        """
        Determine the directory name for the repository.
        Returns:
            str: Directory name.
        """
        if self.args.repository:
            start = self.args.repository.rfind("/") + 1
            end = self.args.repository.rfind(".")
            return self.args.repository[start:end]
        return "repository-" + self.curr_date.strftime("%Y-%m-%d-%H-%M-%S")

    def _create_and_initialize_repository(self):
        """
        Create and initialize a new Git repository in the specified directory.
        """
        os.mkdir(self.directory)
        os.chdir(self.directory)
        self._run_command(["git", "init", "-b", "main"])

        if self.args.user_name:
            self._run_command(["git", "config", "user.name", self.args.user_name])
        if self.args.user_email:
            self._run_command(["git", "config", "user.email", self.args.user_email])

    def _generate_commit_dates(self):
        """
        Generate a list of commit dates based on the specified parameters.
        Returns:
            list: List of commit dates.
        """
        start_date = self.curr_date.replace(hour=20, minute=0) - timedelta(
            self.args.days_before
        )
        commit_dates = []

        for day in (
            start_date + timedelta(n)
            for n in range(self.args.days_before + self.args.days_after)
        ):
            if (not self.args.no_weekends or day.weekday() < 5) and randint(
                0, 100
            ) < self.args.frequency:
                for commit_time in (
                    day + timedelta(minutes=m)
                    for m in range(randint(1, self._contributions_per_day()))
                ):
                    commit_dates.append(commit_time)

        return commit_dates

    def _contribute(self, date):
        """
        Create a commit in the repository with the specified date.
        Args:
            date (datetime): The date of the commit.
        """
        with open(os.path.join(os.getcwd(), "README.md"), "a") as file:
            file.write(self._generate_commit_message(date) + "\n\n")
        self._run_command(["git", "add", "."])
        self._run_command(
            [
                "git",
                "commit",
                "-m",
                self._generate_commit_message(date),
                "--date",
                date.strftime('"%Y-%m-%d %H:%M:%S"'),
            ]
        )

    def _run_command(self, commands):
        """
        Run a shell command and wait for it to complete.
        Args:
            commands (list): List of command arguments.
        """
        Popen(commands).wait()

    def _generate_commit_message(self, date):
        """
        Generate a commit message based on the specified date.
        Args:
            date (datetime): The date of the commit.
        Returns:
            str: The commit message.
        """
        return date.strftime("Contribution: %Y-%m-%d %H:%M")

    def _setup_remote_repository(self):
        """
        Set up the remote repository and push the initial commits.
        """
        self._run_command(["git", "remote", "add", "origin", self.args.repository])
        self._run_command(["git", "branch", "-M", "main"])
        self._run_command(["git", "push", "-u", "origin", "main"])

    def _contributions_per_day(self):
        """
        Determine the number of contributions (commits) per day based on the specified parameters.
        Returns:
            int: Number of contributions per day.
        """
        max_commits = self.args.max_commits
        return randint(1, max(1, min(20, max_commits)))


def parse_arguments(argsval):
    """
    Parse command-line arguments.
    Args:
        argsval (list): List of command-line arguments.
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-nw",
        "--no_weekends",
        action="store_true",
        default=False,
        help="do not commit on weekends",
    )
    parser.add_argument(
        "-mc",
        "--max_commits",
        type=int,
        default=10,
        help="Maximum commits per day (1-20). Default is 10.",
    )
    parser.add_argument(
        "-fr",
        "--frequency",
        type=int,
        default=80,
        help="Percentage of days to commit. Default is 80%.",
    )
    parser.add_argument(
        "-r",
        "--repository",
        type=str,
        help="Remote git repository URL in SSH or HTTPS format.",
    )
    parser.add_argument(
        "-un", "--user_name", type=str, help="Overrides user.name git config."
    )
    parser.add_argument(
        "-ue", "--user_email", type=str, help="Overrides user.email git config."
    )
    parser.add_argument(
        "-db",
        "--days_before",
        type=int,
        default=365,
        help="Number of days before current date to start commits.",
    )
    parser.add_argument(
        "-da",
        "--days_after",
        type=int,
        default=0,
        help="Number of days after current date to end commits.",
    )
    return parser.parse_args(argsval)


if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])
    repo = GitRepository(args)
    repo.setup()
