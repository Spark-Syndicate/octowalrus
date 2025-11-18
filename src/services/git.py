import shutil
from pathlib import Path

import git  # type: ignore[import-unresolved]

from core.logging import get_logger

logger = get_logger(__name__)


class RepositoryCloneError(Exception):
    """Raised when repository cloning fails."""

    pass


def clone_repo(repo_url: str, clone_dir: str = "temp") -> git.Repo:
    """
    Clones the repository into CLONE_DIR.

    Args:
        repo_url: URL of the repository to clone.
        clone_dir: Directory path where the repository will be cloned to.

    Returns:
        git.Repo: The cloned repository object.

    Raises:
        RepositoryCloneError: If the repository cloning fails.
    """
    logger.info(f"Cloning repository from {repo_url} into {clone_dir}...")
    try:
        repo = git.Repo.clone_from(repo_url, clone_dir)
        logger.debug("Repository cloned successfully")
        return repo
    except git.exc.GitCommandError as e:
        logger.error(f"Failed to clone repository from {repo_url}")
        logger.exception("Repository clone failed")
        raise RepositoryCloneError(f"Failed to clone repository from {repo_url}") from e


def commit_repo(repo: git.Repo, file_to_add: str, commit_message: str) -> str:
    """Stages, commits, and pushes the changes to the remote repository."""
    if repo is None:
        return "Commit Failed: Repository not cloned."

    try:
        repo.index.add([file_to_add])
        repo.index.commit(commit_message)
        push_info = repo.remotes.origin.push(
            refspec="HEAD:main"
        )  # Assuming 'main' branch

        # Check for errors in push_info
        if push_info and push_info[0].flags & git.PushInfo.ERROR:
            return "Commit Failed during push!"
        else:
            return "Commit Successful! Data Imported Successfully!"
    except Exception as e:
        return f"An error occurred during commit/push: {e}"


def run_workflow(repo_url: str, csv_file_path: str, clone_dir: str = "temp") -> str:
    """Runs the full workflow: Clone, Convert, Commit/Push, and Cleanup.

    Args:
        repo_url: URL of the repository to clone
        csv_file_path: Path to the CSV file to convert
        clone_dir: Directory to clone the repository into

    Returns:
        str: Result message indicating success or failure
    """
    # 1. Clone the repository
    try:
        local_repo = clone_repo(repo_url, clone_dir)
    except RepositoryCloneError:
        return "Workflow Failed at: Repository Cloning."

    # 2. TODO: Convert CSV to JSON within the cloned directory
    # This function needs to be implemented
    # json_file_path = convert_csv_to_json(csv_file_path)
    # if json_file_path is None:
    #     return "Workflow Failed at: CSV to JSON conversion."

    # Get the filename relative to the clone_dir for git add
    json_filename = Path(csv_file_path).name

    # 3. Commit and Push the new JSON file
    result_message = commit_repo(local_repo, json_filename, f"Add {json_filename}")

    # 4. Clean up the temporary directory after the workflow
    try:
        shutil.rmtree(clone_dir)
        logger.info(f"Cleaned up {clone_dir} directory.")
    except Exception as e:
        logger.error(f"Error during cleanup of {clone_dir}: {e}")

    return result_message
