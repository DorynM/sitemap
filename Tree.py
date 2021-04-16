class Tree(object):
    """Класс Tree создает общее дерево

    Каждый лист дерева ялвыяется экземляром класса Tree

    Attributes
    ----------
    parent : Tree ot None
        хранит в себе ссылку на родителя
    children : list
        хранит в себе список детей
    value : any type
        хранит в себе значение вершины дерева
    number_leaves : int
        хранит в себе количество листьев
    Methods
    -------
    find_height(heights, height=-1)
        Функция рассчитывает высоту дерева
    find_leaf(val)
        Функция ищет лист
    add(value, parent_value)
        Функция добавляет новый лист в дерево
    printTree(par='')
        Функция вывода дерева в консоль
    """
    def __init__(self, val, parent=None):
        self.parent = parent
        self.children = []
        self.value = val
        self.number_leaves = 0
        self.__number_iter = 0

    def find_height(self, heights, height=-1):
        """
        Входным параметром является всегда set()

        Выходное значение - высота дерева
        """
        height += 1
        heights.add(height)
        if len(self.children):
            for child in self.children:
                child.find_height(height=height, heights=heights)
            return max(heights)
        else:
            return max(heights)

    def find_leaf(self, val):
        """
        Ищет лист

        Входной параметр - искомое значение

        Выходное значение - либо None, если лист не найден, либо лист
        """
        if self.value == val:
            return self

        if len(self.children):
            for child in self.children:
                if child.value == val:
                    return child
                else:
                    result = child.find_leaf(val)
                    if result is not None:
                        if result.value == val:
                            return result
                        else:
                            return None
        else:
            return None

    def add(self, value, parent_value):
        """
        Добавляет новый лист в дерево

        Входные параметры - значение листа и значение родителя
        """
        parent = self.find_leaf(parent_value)
        if parent is not None:
            self.number_leaves += 1
            parent.children.append(Tree(value, parent))
        else:
            raise ValueError

    def printTree(self, par=''):
        """
        Выводит дерево в консоль
        """
        print(par, self.value)
        par = ' |' + par
        for child in self.children:
            child.printTree(par)

    def __PreorderTraversal(self, step, root):
        result = self
        if step[0] < root.__number_iter:
            for child in self.children:
                if step[0] >= root.__number_iter:
                    break
                step[0] += 1
                result = child.__PreorderTraversal(step, root)
        return result

    def __next__(self):
        if self.__number_iter < self.number_leaves:
            b = self.__PreorderTraversal([0], self)
            self.__number_iter += 1
            return b
        else:
            raise StopIteration

    def __iter__(self):
        self.number_iter = 0
        return self
