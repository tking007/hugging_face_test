from collections import defaultdict


#
# 代码中的类名、方法名、参数名已经指定，请勿修改，直接返回方法规定的值即可
#
#
# @param indexArray int整型二维数组
# @param n int整型
# @return int整型
#
class Solution:
    def maxConnectedTrianglesSize(self, indexArray: List[List[int]], n: int) -> int:
        # write code here
        gra = defaultdict(list)
        for i in range(n):
            for j in range(i + 1, n):
                if len(set(List[i]) & set(List[j])) == 2:
                    gra[i].append(j)
                    gra[j].append(i)

        def dfs(node, visited):
            visited.add(node)
            size = 1
            for neighbor in gra[node]:
                if neighbor not in visited:
                    size += dfs(neighbor, visited)
            return size

        max_size = 0
        visited = set()
        for i in range(n):
            if i not in visited:
                max_size = max(max_size, dfs(i, visited))
        return max_size