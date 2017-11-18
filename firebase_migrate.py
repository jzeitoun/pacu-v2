import numpy as np
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pacu.core.io.scanbox.impl2 import ScanboxIO

def initialize_db():
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('/Users/blakjak/.pacu/scanbox/pacu-rois-firebase-adminsdk-adpl1-4312c1f516.json')

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pacu-rois.firebaseio.com/'
    })

    # Get references to each db location
    file_ref = db.reference('files')
    workspace_ref = db.reference('workspaces')
    rois_ref = db.reference('rois')

    return file_ref, workspace_ref, rois_ref

def polygon_to_points(polygon):
        points = [','.join(
            [str(point['x']), str(point['y'])]
            ) for point in polygon]
        return ','.join(points)

def migrate(file_ref, workspace_ref, rois_ref):
    for path, dirs, _ in os.walk(os.getcwd()):
        io_dirs = [io_dir for io_dir in dirs if io_dir.endswith('.io')]
        if len(io_dirs):
            for io_dir in io_dirs:
                full_path = os.path.join(path, io_dir)
                file_path = '/'.join(full_path.split('/')[4:])
                io = ScanboxIO(full_path)
                workspaces = io.condition.workspaces

                # Create db entry for this recording
                file_response = file_ref.push({'name': file_path})
                roi_count = []
                file_workspace_keys = []
                for workspace in workspaces:
                    workspace_name = os.path.join(file_path, workspace.name)
                    print('Migrating workspace: {}'.format(workspace_name))
                    workspace_response = workspace_ref.push({'name': workspace_name})
                    file_workspace_keys.append(workspace_response.key)

                    # Keep track of roi count
                    roi_count.append(len(workspace.rois))
                    workspace_roi_keys = []

                    # Push each roi belonging to this workspace to db
                    for roi in workspace.rois:
                        response = rois_ref.push(
                            {
                                'roi_id': roi.id,
                                'workspace': workspace_response.key,
                                'polygon': polygon_to_points(roi.polygon),
                                'lastComputedPolygon': '',
                                'neuropil_ratio': roi.neuropil_ratio,
                                'neuropil_factor': roi.neuropil_factor,
                                'neuropil_polygon': roi.neuropil_polygon,
                                'neuropil_enabled': roi.neuropil_enabled
                            }
                        )
                        workspace_roi_keys.append(response.key)

                    # Create dictionary of roi keys belonging to this workspace and push to db
                    workspace_rois = {key:True for key in workspace_roi_keys}
                    workspace_response.update({'rois': workspace_rois})

                # After migrating workspaces and rois,
                # add roi count and workspace keys to file db entry
                file_workspaces = {key:True for key in file_workspace_keys}
                file_response.update(
                    {
                        'roi_count': sum(roi_count),
                        'workspaces': file_workspaces
                    }
                )

                import ipdb; ipdb.set_trace()

def main():
    file_ref, workspace_ref, rois_ref = initialize_db()
    migrate(file_ref, workspace_ref, rois_ref)

if __name__ == '__main__':
    main()




