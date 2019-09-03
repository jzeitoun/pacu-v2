"""Summary
"""

from anytree import AnyNode, Resolver, RenderTree
from anytree.exporter import JsonExporter
from werkzeug.security import generate_password_hash, check_password_hash

import pacu.core.addons.mongo_api.models as models

def user_register_db(username: str, password: str, **kwargs):
    """Adds a user to the mongodb. See model.users.user for more details on the db entry.

    Args:
        username (str): Username
        password (str): Password hash
        **kwargs: Additional fields to add to User db entry.

    Returns:
        User: User mongoengine object
    """

    if models.User.objects(username=username).first():
        raise ValueError ('User already exists.')
    else:
        password = generate_password_hash(password, method='sha256')
        user = models.User(username, password, **kwargs)
        user.save()

    return user


def authenticate(username: str, password: str):
    """Authenticates user by compparing a given password against the stored hash.

    Args:
        username (str): Username
        password (str): raw string password. Not hashed.

    Returns:
        User: User mongoengine object
    """
    user = models.User.objects(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return None

    return user


def project_new_db(owner: models.User, name: str, **kwargs):
    """Adds a new project to the mongodb. See model.users.Project for more details on the db entry.

    Args:
        owner (User): User object to set as owner
        name (str): name of project

    Returns:
        Workspace: Project mongoengine object
    """
    if models.Project.objects(owner=owner, name=name).first():
        raise ValueError(f'A Project with name {name} already exists.')
    else:
        project = models.Project(owner = owner, name = name, **kwargs)
        project.save()
    return project


def experiment_new_db(owner: models.User, name: str, project: str, **kwargs):
    """Adds a new experiment to the mongodb. See model.users.Experiment for more details on the db entry.

    Args:
        owner (User): User object to set as owner
        name (str): name of project
        project (str): mongodb id corresponding to parent project

    Returns:
        Workspace: Experiment mongoengine object
    """
    if models.Experiment.objects(owner=owner, name=name, project=project).first():
        raise ValueError(f'An Experiment with name {name} already exists in this project.')
    else:
        exp = models.Experiment(owner = owner, name = name, project = project, **kwargs)
        exp.save()

    return exp


def workspace_new_db(owner: models.User, name: str, experiment: str, **kwargs):
    """Adds a new workspace to the mongodb. See model.users.workspace for more details on the db entry.

    Args:
        owner (User): User object to set as owner
        name (str): name of workspace
        experiment (str): mongodb id corresponding to parent experiment
        **kwargs: additional fields to add to Workspace entry

    Returns:
        Workspace: Workspace mongoengine object
    """
    if models.Workspace.objects(owner=owner, name=name, experiment=experiment).first():
        raise ValueError(f'A workspace with name {name} already exists already exists in this experiment.')
    else:
        ws = models.Workspace(owner = owner, name = name, experiment = experiment, **kwargs)
        ws.save()

    return ws



def workspace_get_db(owner: models.User, id: str, dereference = True):
    """ Retrieves workspace entry from mongodb. 
    See model.users.workspace for more details on the db entry.

    Args:
        owner (User): User object to set as owner
        id (str): id of workspace

    Returns:
        Workspace: Workspace mongoengine object
    """

    ws = models.Workspace.objects.get(owner=owner, id=id)

    return ws


def folder_workspace_new_db(owner: models.User, name: str, parent_folder: str = None):
    """Adds a new workspace folder to the mongodb.
    See model.users.workspaceFolder for more details on the db entry.

    Args:
        owner (User): User object to set as owner
        name (str): name of workspace
        parent_folder (str): mongodb id corresponding to parent folder

    Returns:
        Workspace: Workspace mongoengine object
    """
    folder = models.FolderWorkspace(owner = owner, name = name, parent_folder = parent_folder)
    folder.save()

    return folder


def project_tree_json(owner: models.User):
    """Renders a workspace JSON tree corresponding to a mongodb prject.experiment.workspace tree.

    Args:
        owner (User): User object to set as owner
        **kwargs: additional fields to add to Workspace entry

    Returns:
        JSON: Workspace mongoengine object
    """
    root = AnyNode(id=None,
                   name='Root',
                   type='Root')

    for p in models.Project.objects(owner=owner):
        p_node = AnyNode(parent=root,
                type=p.__class__.__name__,
                **p.to_dict())

        for e in models.Experiment.objects(owner=owner, project = p):
            e_node= AnyNode(parent=p_node,
                    type=e.__class__.__name__,
                    **e.to_dict())

            for w in models.Workspace.objects(owner=owner, experiment=e):
                AnyNode(parent=e_node,
                        type=w.__class__.__name__, 
                        **w.to_dict())

    exporter = JsonExporter(indent=2, sort_keys=True)

    return exporter.export(root)
