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
        System.out.println("RetryPolicy: 22 checks passed");
    }
}
