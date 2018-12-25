class Solution:
    def letterCasePermutation(self, S):
        """
        :type S: str
        :rtype: List[str]
        """
        result = [""]
        for s in S:
            if s.isdigit():
                for i in range(result.__len__()):
                    result[i] = result[i] + s
            else:
                temp = []
                for i in range(result.__len__()):
                    temp.append(result[i] + s.upper())
                    temp.append(result[i] + s.lower())
                result = temp
        return result


if __name__ == '__main__':
    ss = "a1b2"
    S = Solution()
    print(S.letterCasePermutation(ss))
