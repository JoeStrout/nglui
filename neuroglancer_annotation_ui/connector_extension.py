import neuroglancer
from neuroglancer_annotation_ui import connections 
from neuroglancer_annotation_ui import annotation
from neuroglancer_annotation_ui.extensible_viewer import check_layer

class ConnectorExtension():
    def __init__(self, extensible_viewer ):
        self.data = connections.Connections()
        self.synapse = []
        self.index = None
        self.annotation_layer_name = None
        self.synapse_points = {'pre_pt':None, 'post_pt':None, 'ctr_pt':None}
        self.pre_lines = []
        self.post_lines = []
        self.viewer = extensible_viewer
        self.color_map = {'pre_pt':'#00ff24',
                          'post_pt':'#ff0000',
                          'ctr_pt':'#555555'}

        self.viewer.add_annotation_layer('synapses')
        #self.annotation_client = annotation_client

    def update_synapse_points( self, point_type, s):
        message_dict = {'pre_pt':'presynaptic point',
                        'post_pt':'postsynaptic point',
                        'ctr_pt': 'synapse point'}
        if self.synapse_points[point_type] is None:
            message = 'Assigned {}'.format(message_dict[point_type])
        else:
            message = 'Re-assigned {}'.format(message_dict[point_type])
        self.synapse_points[point_type] = self.add_point(s)
        self.viewer.add_annotation( message_dict[point_type],
                             [self.synapse_points[point_type]],
                             self.color_map[point_type] )
        self.viewer.update_message( message)

    @check_layer('synapses')
    def update_presynaptic_point( self, s):
        self.update_synapse_points( 'pre_pt', s)

    @check_layer('synapses')
    def update_postsynaptic_point( self, s):
        self.update_synapse_points( 'post_pt', s)

    @check_layer('synapses')
    def update_synapse( self, s ):
        if (self.synapse_points['pre_pt'] is None) or \
                    (self.synapse_points['post_pt'] is None):
            self.viewer.update_message("Pre and Post targets must be defined before \
                                        adding a synapse!")
            return

        self.update_synapse_points( 'ctr_pt', s )

        pre_line = self.add_line(self.synapse_points['pre_pt'].point, \
                                 self.synapse_points['ctr_pt'].point)
        post_line = self.add_line(self.synapse_points['post_pt'].point, \
                                  self.synapse_points['ctr_pt'].point)
        self.pre_lines.append(pre_line)
        self.post_lines.append(post_line)
        self.viewer.add_annotation('Post_connection', self.post_lines, '#ff0000')
        self.viewer.add_annotation('Pre_connection', self.pre_lines, '#00ff24')

        self.data.add_connection(self.synapse_points['pre_pt'].point.tolist(),
                                 self.synapse_points['post_pt'].point.tolist(),
                                 self.synapse_points['ctr_pt'].point.tolist())

        self.clear_segment(None)

    def add_point(self, s, description=None):
        pos = s.mouse_voxel_coordinates
        if pos is None:
            return
        if len(pos) is 3:  # FIXME: bad hack need to revisit
            id = neuroglancer.random_token.make_random_token()
            point = annotation.point_annotation(pos, id, description)
            return point
        else:
            return

    def add_line(self, a, b, description=None):
        id = neuroglancer.random_token.make_random_token()
        line = annotation.line_annotation(a, b, id)
        return line

    def delete_synapse(self, s):
        """ TODO
        Find nearest X,Y,Z point in radius of mouse position and remove index
        from list import scipy.spatial.KDTree ?? for lookup of xzy pos
        """
        self.update_message('Delete key pressed')

    def undo_last_point(self, s):
        try:
            with self.viewer.txn() as s:
                point_layer = s.layers[self.annotation_layer_name]
                point_layer.annotations = point_layer.annotations[:-1]
            del self.data.dataset[self.index]['synapses'][-1]
            self.synapse = self.synapse[:-1]
            self.update_message("Last Synapse removed!!!")
        except Exception as e:
            raise e

    def _update_view(self, pos):
        with self.viewer.txn() as s:
            s.voxel_coordinates = pos

    @check_layer('synapses')
    def clear_segment(self, s):
        self.synapse_points = {'pre_pt':None, 'post_pt':None, 'ctr_pt':None}
        self.viewer.update_message('Starting new synapse...')

    def activate_existing_state(self, index):
        if self.pre_id and self.post_id:
            return self.set_state_index(index)
        else:
            return self.viewer.state

    def set_state_index(self, index):
        if index in self.states:
            return self.viewer.set_state(self.states[index])
        else:
            return self.viewer.set_state(self.viewer.state)

    def save_json(self, s):
        """ Please delete this """
        self.data.save_json('example.json')
        self.update_message("JSON saved")

