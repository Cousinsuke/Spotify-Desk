package com.spotifydesk.echo;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

/** Activity-local, display-only OSD. No overlay permission or web bridge. */
final class LocalVolumeOverlay {
    private final LinearLayout panel;
    private final ProgressBar bar;
    private final TextView value;
    private final TextView label;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable dismiss = this::hide;

    LocalVolumeOverlay(Context context, FrameLayout root) {
        float density = context.getResources().getDisplayMetrics().density;
        panel = new LinearLayout(context);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(density,16), dp(density,10), dp(density,16), dp(density,10));
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(16,17,18));
        background.setCornerRadius(dp(density,16));
        background.setStroke(dp(density,1), Color.rgb(66,69,70));
        panel.setBackground(background);
        panel.setElevation(dp(density,8));
        panel.setClickable(false);
        panel.setFocusable(false);
        panel.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS);

        label = new TextView(context);
        label.setText("Echo Show volume");
        label.setTextColor(Color.rgb(208,210,210));
        label.setTextSize(12);
        panel.addView(label);
        LinearLayout row = new LinearLayout(context);
        row.setGravity(Gravity.CENTER_VERTICAL);
        bar = new ProgressBar(context, null, android.R.attr.progressBarStyleHorizontal);
        bar.setMax(100);
        bar.setProgressTintList(ColorStateList.valueOf(Color.WHITE));
        bar.setProgressBackgroundTintList(ColorStateList.valueOf(Color.rgb(66,69,70)));
        row.addView(bar, new LinearLayout.LayoutParams(0, dp(density,12), 1));
        value = new TextView(context);
        value.setTextColor(Color.WHITE);
        value.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        value.setTextSize(16);
        value.setGravity(Gravity.END | Gravity.CENTER_VERTICAL);
        LinearLayout.LayoutParams number = new LinearLayout.LayoutParams(dp(density,54), -2);
        number.leftMargin = dp(density,12);
        row.addView(value, number);
        panel.addView(row, new LinearLayout.LayoutParams(-1, -2));
        FrameLayout.LayoutParams position = new FrameLayout.LayoutParams(
            Math.min(dp(density,300), context.getResources().getDisplayMetrics().widthPixels - dp(density,32)),
            -2, Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        position.topMargin = dp(density,12);
        root.addView(panel, position);
        panel.setVisibility(View.GONE);
    }

    private static int dp(float density, int n) { return Math.round(n * density); }

    void show(int current, int min, int max, boolean muted) {
        int percent = VolumeScale.percent(current, min, max, muted);
        label.setText(muted ? "Echo Show volume (muted)" : "Echo Show volume");
        bar.setProgress(percent);
        value.setText(percent + "%");
        panel.setVisibility(View.VISIBLE);
        handler.removeCallbacks(dismiss);
        handler.postDelayed(dismiss, 2000);
    }

    void hide() {
        handler.removeCallbacks(dismiss);
        panel.setVisibility(View.GONE);
    }
}
