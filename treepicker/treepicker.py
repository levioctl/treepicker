import os

import keybind
import linescanner
import treeprinter
import cursesswitch
import treepickermodel
from cursesswitch import printer


class TreePicker(object):
    _MODE_NAVIGATION = 'navigation'
    _NON_INTERACTIVE_SEARCH = 'search'
    _MODE_INTERACTIVE_SEARCH = 'interactive search'
    _MODE_RETURN = 'return'
    _MODE_QUIT = 'quit'

    BUILTIN_HEADER = ("Navigation: [Ctrl+]h,j,k,l, First: g, Last: G, Search: /, Non-interactive search: Ctrl+/, "
                      "Quit: q")

    def __init__(self, tree, including_root=True, header="", max_nr_lines=None):
        self._picker = treepickermodel.TreePickerModel(tree, header, max_nr_lines)
        self._header = (header + '\n' + self.BUILTIN_HEADER).strip()
        self._line_scanner = linescanner.LineScanner()
        self._navigation_actions = keybind.KeyBind()
        self._register_keybind_actions()
        self._populate_keybind()
        self._tree_printer = treeprinter.TreePrinter(tree, max_nr_lines, including_root=including_root)
        self._mode = self._MODE_NAVIGATION

    def pick_one(self):
        choices = self.pick()
        return None if not choices else choices[0]

    def pick(self):
        print_tree_once = True
        picked = None
        while picked is None and self._mode != self._MODE_QUIT:
            if print_tree_once:
                self._print_tree()
            print_tree_once = True
            if self._mode == self._MODE_NAVIGATION:
                previous_state = self._capture_state()
                self._navigation_actions.do_one_action()
                current_state = self._capture_state()
                print_tree_once = previous_state != current_state
            elif self._mode == self._NON_INTERACTIVE_SEARCH:
                result = self._line_scanner.scan_char()
                if result == linescanner.LineScanner.STATE_EDIT_ENDED:
                    self._mode = self._MODE_NAVIGATION
                    self._update_search_pattern()
            elif self._mode == self._MODE_INTERACTIVE_SEARCH:
                result = self._line_scanner.scan_char()
                self._update_search_pattern()
                if result == linescanner.LineScanner.STATE_EDIT_ENDED:
                    self._mode = self._MODE_NAVIGATION
            elif self._mode == self._MODE_RETURN:
                picked = self._picker.get_picked_nodes()
                picked = [self._get_node_data(node) for node in picked.values()]
            elif self._mode == self._MODE_QUIT:
                picked = list()
            else:
                raise ValueError(self._mode)
        return picked

    def _start_non_interactive_search(self):
        self._mode = self._NON_INTERACTIVE_SEARCH
        # Reset tree search results
        self._line_scanner.clear_line()

    def start_interactive_search(self):
        self._mode = self._MODE_INTERACTIVE_SEARCH
        # Reset tree search results
        self._line_scanner.clear_line()
        self._update_search_pattern()

    def quit(self):
        self._mode = self._MODE_QUIT

    def return_picked_nodes(self):
        picked = self._picker.get_picked_nodes()
        if picked:
            self._mode = self._MODE_RETURN

    def _update_search_pattern(self):
        search_pattern = self._line_scanner.get_line()
        self._picker.update_search_pattern(search_pattern)

    def _print_tree(self):
        selected_node = self._picker.get_selected_node()
        search_pattern = self._line_scanner.get_line()
        picked = self._picker.get_picked_nodes()
        print len(picked)
        self._tree_printer.calculate_lines_to_print(selected_node, picked, search_pattern)
        printer.clear_screen()
        if self._header is not None:
            printer.print_string(self._header + "\n")
        self._tree_printer.print_tree()
        footer = ""
        is_search_pattern_being_edited = self._mode in (self._NON_INTERACTIVE_SEARCH,
                                                        self._MODE_INTERACTIVE_SEARCH)
        if is_search_pattern_being_edited:
            footer = '\nInsert Search filter: %s|' % (search_pattern,)
            color = "magenta"
        elif search_pattern:
            footer = '\nCurrent Search filter: %s' % (search_pattern,)
            color = "yellow"
        if footer:
            printer.print_string(footer, color)

    def _register_keybind_actions(self):
        self._navigation_actions.add_action('next', self._picker.next)
        self._navigation_actions.add_action('previous', self._picker.previous)
        self._navigation_actions.add_action('explore', self._picker.explore)
        self._navigation_actions.add_action('up', self._picker.go_up)
        self._navigation_actions.add_action('last_node', self._picker.last_node)
        self._navigation_actions.add_action('first_node', self._picker.first_node)
        self._navigation_actions.add_action('quit', self.quit)
        self._navigation_actions.add_action('start_non_interactive_search', self._start_non_interactive_search)
        self._navigation_actions.add_action('start_interactive_search', self.start_interactive_search)
        self._navigation_actions.add_action('return_picked_nodes', self.return_picked_nodes)
        self._navigation_actions.add_action('toggle', self._picker.toggle)
        self._navigation_actions.add_action('page_up', self._picker.page_up)
        self._navigation_actions.add_action('page_down', self._picker.page_down)
        self._navigation_actions.add_action('next_leaf', self._picker.next_leaf)
        self._navigation_actions.add_action('prev_leaf', self._picker.prev_leaf)
        self._navigation_actions.add_action('go_to_root', self._picker.go_to_root)
        self._navigation_actions.add_action('explore_deepest_child', self._picker.explore_deepest_child)

    def _populate_keybind(self):
        self._navigation_actions.bind('j', 'next')
        self._navigation_actions.bind('k', 'previous')
        self._navigation_actions.bind('l', 'explore')
        self._navigation_actions.bind('h', 'up')
        self._navigation_actions.bind('q', 'quit')
        self._navigation_actions.bind('G', 'last_node')
        self._navigation_actions.bind('g', 'first_node')
        self._navigation_actions.bind(chr(3), 'quit')  # Ctrl-c
        self._navigation_actions.bind('/', 'start_interactive_search')
        self._navigation_actions.bind(chr(16), 'start_interactive_search')  # Ctrl-p
        self._navigation_actions.bind(chr(13), 'return_picked_nodes')  # Return
        self._navigation_actions.bind(chr(31), 'start_non_interactive_search')  # Ctrl-/
        self._navigation_actions.bind(chr(32), 'toggle')  # Space
        self._navigation_actions.bind(chr(4), 'page_down')  # Ctrl-d
        self._navigation_actions.bind(chr(21), 'page_up')  # Ctrl-u
        self._navigation_actions.bind('u', 'page_up')
        self._navigation_actions.bind('d', 'page_down')
        self._navigation_actions.bind(chr(10), 'next_leaf')  # Ctrl-j
        self._navigation_actions.bind(chr(11), 'prev_leaf')  # Ctrl-k
        self._navigation_actions.bind(chr(8), 'go_to_root')  # Ctrl-h
        self._navigation_actions.bind(chr(12), 'explore_deepest_child')  # Ctrl-h

    def _capture_state(self):
        picked = self._picker.get_picked_nodes()
        picked = hash(str(picked.keys()))
        return (picked, self._picker.get_selected_node(), self._mode)

    @staticmethod
    def _get_node_data(node):
        return node.data if hasattr(node, 'data') else node.tag


if __name__ == '__main__':
    from exampletree import tree
    treepicker = TreePicker(tree, header='stuff:', max_nr_lines=25)
    cursesswitch.wrapper(treepicker.pick)
