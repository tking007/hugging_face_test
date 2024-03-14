import heapq


def solve(n, x, y, songs):
    # Convert the list of songs to a max heap
    songs = [-s for s in songs]
    heapq.heapify(songs)

    # Simulate the process of singing songs
    for _ in range(y):
        singers = []
        for _ in range(min(x, len(songs))):
            singer = -heapq.heappop(songs)
            singer -= 1
            if singer > 0:
                singers.append(-singer)
        for singer in singers:
            heapq.heappush(songs, singer)
        if len(songs) == 0:
            break

    # Check if there are any songs left to sing
    return "YES" if len(songs) == 0 else "NO"


if __name__ == "__main__":
    T = int(input().split())
    for _ in range(T):
        n, x, y = map(int, input().strip().split())
        songs = []
        for _ in range(n):
            a = list(map(int, input().strip().split()))
            songs.append(a[0])
        print(solve(n, x, y, songs))
