import treelib
import treepicker


def main():
    # Create the following tree
    # root
    # +-- child1
    # +-- child2
    #     +-- grandson1
    tree = treelib.Tree()
    tree.create_node('root')
    tree.create_node('child1', parent=tree.root)
    child2 = tree.create_node('child2', parent=tree.root)
    tree.create_node('grandson1', parent=child2.identifier)

    # Pick
    treepicker.TreePicker(tree).pick()


if __name__ == "__main__":
    # Pick without using curses
    main()

    # Pick using curses (full screen in terminal)
    import cursesswitch
    cursesswitch.wrapper(main)
