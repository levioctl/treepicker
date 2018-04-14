import treelib

import treesearch
import treenavigator


class TreePickerModel(object):
    def __init__(self, tree, including_root=True, header="", min_nr_options=1, max_nr_options=None):
        self._tree = tree
        self._min_nr_options = min_nr_options
        self._max_nr_options = len(self._tree) if max_nr_options is None else max_nr_options
        self._picked = dict()
        self._tree_search = treesearch.TreeSearch(self._tree)
        self._tree_navigator = treenavigator.TreeNavigator(self._tree, including_root)
        self._search_pattern_when_navigator_tree_was_last_updated = None
        self._search_pattern = None

    def get_selected_node(self):
        return self._tree_navigator.get_selected_node()

    def next(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_relative(distance=1)

    def previous(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_relative(distance=-1)

    def last_node(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_absolute(index=-1)

        self._validate_navigator_tree()
    def first_node(self):
        self._tree_navigator.move_selection_absolute(index=0)

    def page_down(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_relative(distance=4)

    def page_up(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_relative(distance=-4)

    def next_leaf(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_relative_leaf(self._tree_navigator.DIRECTION_NEXT)

    def prev_leaf(self):
        self._validate_navigator_tree()
        self._tree_navigator.move_selection_relative_leaf(self._tree_navigator.DIRECTION_PREV)

    def explore(self):
        self._validate_navigator_tree()
        self._tree_navigator.explore()

    def go_up(self):
        self._validate_navigator_tree()
        self._tree_navigator.go_up()

    def go_to_root(self):
        self._validate_navigator_tree()
        self._tree_navigator.go_to_root()

    def explore_deepest_child(self, direction=treenavigator.TreeNavigator.DIRECTION_NEXT):
        self._validate_navigator_tree()
        self._tree_navigator.explore_deepest_child()

    def toggle(self):
        self._validate_navigator_tree()
        selected_node = self._tree_navigator.get_selected_node()
        # No toggle with only one option
        if self._min_nr_options == self._max_nr_options == 1:
            return
        is_picked = selected_node.identifier in self._picked
        toggle_node = self._unpick_node if is_picked else self._pick_node
        toggle_node(selected_node)
        for node in self._tree.subtree(selected_node.identifier).nodes.itervalues():
            toggle_node(node)

    def get_picked_nodes(self):
        self._validate_navigator_tree()
        picked = dict()
        if self._min_nr_options == self._max_nr_options == 1:
            selected_node = self._tree_navigator.get_selected_node()
            self._picked = {selected_node: selected_node}
            picked = self._picked
        elif self._min_nr_options <= len(self._picked) <= self._max_nr_options:
            picked = self._picked
        return picked

    def update_search_pattern(self, search_pattern):
        self._search_pattern = search_pattern
        self._tree_search.get_filtered_tree(search_pattern)

    def _validate_navigator_tree(self):
        if self._search_pattern != self._search_pattern_when_navigator_tree_was_last_updated:
            self._search_pattern_when_navigator_tree_was_last_updated = self._search_pattern
            tree = treelib.Tree()
            root_node = self._tree.get_node(self._tree.root)
            bfs_queue = [root_node]
            while bfs_queue:
                node = bfs_queue.pop(0)
                if not hasattr(node, 'matching'):
                    node.matching = True
                if node == root_node or node.matching:
                    new_node = tree.create_node(identifier=node.identifier, tag=node.tag, data=node.data,
                                                parent=node.bpointer)
                    new_node.matching = node.matching
                    new_node.original_matching = node.original_matching
                bfs_queue.extend(self._tree.children(node.identifier))
            self._tree_navigator.set_tree(tree)

    def _pick_node(self, node):
        if len(self._picked) < self._max_nr_options:
            self._picked[node.identifier] = node

    def _unpick_node(self, node):
        if node.identifier in self._picked:
            del self._picked[node.identifier]
