#include <iostream>

using namespace std;
// F(i, j) is the expected profit if we bid i and j, i < j, i, j are in [900, 1000]
// We have N buyers and each choose a number between 900 and 1000
// They will choose the minimum bid that is more than their number
// F(i, 1000) = N * (1000 - i) * (i - 900 - 1) / 100
// F(900, j) = N * (1000 - j) * (j - 900 - 1) / 100
// F(i, j) = N * ((1000 - i) * (i - 900 - 1) / 100 + (1000 - j) * (j - i) / 100)


constexpr int N = 10;

double F(int i, int j) {
    if (i >= j) return 0;
    return 1.0 * N * ((1000 - i) * (i - 900 - 1) / 100 + (1000 - j) * (j - i) / 100);
}

int main() {
    pair<int, int> mx = {0, 0};
    for (int i = 901; i < 1000; ++i) {
        for (int j = i + 1; j <= 1000; ++j) {
            if (F(i, j) > F(mx.first, mx.second)) {
                mx = {i, j};
            }
        }
    }
    cout << mx.first << ' ' << mx.second << endl;
    return 0;
}