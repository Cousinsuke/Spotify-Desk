package com.spotifydesk.echo;

/** Bounded retry rate for transient main-frame failures. No TLS exception handling. */
final class RetryPolicy {
    private static final long[] DELAYS = {2000, 4000, 8000, 15000, 30000};
    static final int MAX_ATTEMPT = DELAYS.length - 1;

    static long delayMillis(int attempt) {
        return DELAYS[Math.max(0, Math.min(attempt, MAX_ATTEMPT))];
    }

    // The first three transient failures use a calm reconnecting screen.
    static boolean quietRetry(int attempt) {
        return attempt >= 0 && attempt < 3;
    }

    static boolean retryableHttp(int status) {
        return status == 500 || status == 502 || status == 503 || status == 504;
    }
}
