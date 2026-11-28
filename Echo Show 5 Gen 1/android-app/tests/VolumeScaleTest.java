package com.spotifydesk.echo;

public final class VolumeScaleTest {
    public static void main(String[] args) {
        int[][] cases = {{0,0,15,0},{1,0,15,7},{8,0,15,53},{15,0,15,100},
            {-1,0,15,0},{16,0,15,100},{3,1,5,50},{0,0,0,0}};
        for (int[] c : cases)
            if (VolumeScale.percent(c[0],c[1],c[2],false) != c[3])
                throw new AssertionError("volume percentage");
        if (VolumeScale.percent(15,0,15,true) != 0) throw new AssertionError("muted");
        System.out.println("VolumeScale: 9 checks passed");
    }
}
