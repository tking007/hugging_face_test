from typing import List


import bisect

class Solution:
    def minOperations(self, nums: List[int]) -> int:
        nums = sorted(set(nums))
        l = len(nums)
        longest_subsequence = 1
        current_length = 1
        for i in range(1, l):
            if nums[i] == nums[i-1] + 1:
                current_length += 1
                longest_subsequence = max(longest_subsequence, current_length)
            else:
                current_length = 1
        return l - longest_subsequence


def test_minOperations():
    solution = Solution()
    print(solution.minOperations([8,10,16,18,10,10,16,13,13,16]))

test_minOperations()