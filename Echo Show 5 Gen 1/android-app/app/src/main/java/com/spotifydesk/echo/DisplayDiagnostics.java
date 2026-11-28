package com.spotifydesk.echo;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.pm.PackageManager;
import android.graphics.Rect;
import android.media.AudioManager;
import android.os.Build;
import android.os.Environment;
import android.os.PowerManager;
import android.os.StatFs;
import android.os.SystemClock;
import org.json.JSONException;
import org.json.JSONObject;

/** Read-only device-local diagnostics. No persistent identifiers or network requests. */
final class DisplayDiagnostics {
    private DisplayDiagnostics() {}

    private static JSONObject usage(long total, long available) throws JSONException {
        if (total <= 0 || available < 0 || available > total) return null;
        long used = total - available;
        return new JSONObject().put("total", total).put("used", used)
            .put("percent", 100.0 * used / total);
    }

    static JSONObject snapshot(Activity activity, AudioManager audio, float brightness) {
        JSONObject data = new JSONObject();
        try {
            data.put("model", Build.MODEL);
            data.put("android", Build.VERSION.RELEASE);
            data.put("sdk", Build.VERSION.SDK_INT);
            data.put("architecture", Build.SUPPORTED_ABIS.length > 0 ? Build.SUPPORTED_ABIS[0] : "Unknown");
            data.put("cores", Runtime.getRuntime().availableProcessors());
            data.put("uptime", SystemClock.elapsedRealtime() / 1000);
            ActivityManager manager = activity.getSystemService(ActivityManager.class);
            if (manager != null) {
                ActivityManager.MemoryInfo info = new ActivityManager.MemoryInfo();
                manager.getMemoryInfo(info);
                data.put("memory", usage(info.totalMem, info.availMem));
            }
            StatFs storage = new StatFs(Environment.getDataDirectory().getPath());
            data.put("storage", usage(storage.getTotalBytes(), storage.getAvailableBytes()));
            PowerManager power = activity.getSystemService(PowerManager.class);
            if (power != null) data.put("thermal", power.getCurrentThermalStatus());
            Rect bounds = activity.getWindowManager().getCurrentWindowMetrics().getBounds();
            data.put("width", bounds.width());
            data.put("height", bounds.height());
            if (brightness >= 0f && brightness <= 1f)
                data.put("brightness", Math.round(brightness * 100));
            if (audio != null) {
                boolean muted = audio.isStreamMute(AudioManager.STREAM_MUSIC);
                data.put("muted", muted);
                data.put("volume", VolumeScale.percent(audio.getStreamVolume(AudioManager.STREAM_MUSIC),
                    audio.getStreamMinVolume(AudioManager.STREAM_MUSIC),
                    audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC), muted));
            }
            try {
                data.put("version", activity.getPackageManager().getPackageInfo(activity.getPackageName(), 0).versionName);
            } catch (PackageManager.NameNotFoundException ignored) { }
        } catch (JSONException | RuntimeException ignored) {
            // Missing metrics remain unavailable. Keep the dashboard usable.
        }
        return data;
    }
}
