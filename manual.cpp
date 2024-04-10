#include <iostream>

using namespace std;
// F(i, j) is the expected profit if we bid i and j, i < j, i, j are in [900, 1000]
// We have N buyers and each choose a number between 900 and 1000
// They will choose the minimum bid that is more than their number
// F(i, 1000) = N * (1000 - i) * (i - 900 - 1) / 100
// F(900, j) = N * (1000 - j) * (j - 900 - 1) / 100
// F(i, j) = N * ((1000 - i) * (i - 900 - 1) / 100 + (1000 - j) * (j - i) / 100)


constexpr long long int N = 10000000;

double m = 0.2;
long long int total_probability = m * 5050;

double F(int i, int j) {
    if (i >= j) return 0;
    i -= 900; j -= 900;
    long long int sum_i = 1ll * i * (i - 1) / 2;
    long long int sum_j = 1ll * j * (j - 1) / 2;
    double prob_i = 1.0 * sum_i / total_probability;
    double prob_j = 1.0 * (sum_j - sum_i + i - j)  / total_probability;
    i += 900; j += 900;
    return 1.0 * N * ((1000 - i) * prob_i + (1000 - j) * prob_j);
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