package com.spotifydesk.echo;

public final class RetryPolicyTest {
    private static void check(boolean ok) {
        if (!ok) throw new AssertionError("Retry policy assertion failed");
    }
    public static void main(String[] args) {
        long[] expected = {2000, 4000, 8000, 15000, 30000, 30000};
        for (int i = 0; i < expected.length; i++) check(RetryPolicy.delayMillis(i) == expected[i]);
        check(RetryPolicy.delayMillis(-1) == 2000);
        check(RetryPolicy.delayMillis(Integer.MAX_VALUE) == 30000);
        check(RetryPolicy.MAX_ATTEMPT == 4);
        for (int s : new int[]{500, 502, 503, 504}) check(RetryPolicy.retryableHttp(s));
        for (int s : new int[]{200, 303, 400, 401, 403, 404, 429, 501, 505}) check(!RetryPolicy.retryableHttp(s));
        for (int i : new int[]{0, 1, 2}) check(RetryPolicy.quietRetry(i));
        for (int i : new int[]{-1, 3, 4, Integer.MAX_VALUE}) check(!RetryPolicy.quietRetry(i));
        System.out.println("RetryPolicy: 28 checks passed");
    }
}
