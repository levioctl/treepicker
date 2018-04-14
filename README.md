# Demo
[![asciicast](https://asciinema.org/a/176226.png)](https://asciinema.org/a/176226)

# Usage
```python
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


# Pick without using curses
main()

# Pick using curses (full screen in terminal)
import cursesswitch
cursesswitch.wrapper(main)
```
