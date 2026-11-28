package com.spotifydesk.echo;

final class VolumeScale {
    private VolumeScale() {}
    static int percent(int current, int min, int max, boolean muted) {
        if (muted || max <= min) return 0;
        return Math.max(0, Math.min(100, Math.round(100f * (current - min) / (max - min))));
    }
}
